"""Read the log-probabilities of each row's option labels at its last position, via vLLM."""

import asyncio
from itertools import count

import httpx

from gateway.governor import Governor
from gateway.schema import RequestError

MAX_LABEL_IDS = 128  # vLLM's cap on logprob_token_ids per request (MAX_LOGPROB_TOKEN_IDS)
IMAGE_LABEL_IDS = MAX_LABEL_IDS - 1  # an image call also asks for one spare id
GENERATE_PATH = "/inference/v1/generate"  # token-in endpoint; /v1/completions silently drops images


class Readout:
    def __init__(
        self,
        client: httpx.AsyncClient,
        model: str,
        warm_min_prefix_tokens: int = 512,
        warm_up: str = "row",
        priority: int = 0,
        governor: Governor | None = None,
    ):
        self.client = client
        self.model = model
        self.warm_min_prefix_tokens = warm_min_prefix_tokens
        if warm_up not in ("row", "prefix", "off"):
            raise ValueError(f"WARM_UP must be 'row', 'prefix' or 'off', not {warm_up!r}")
        self.warm_up = warm_up
        self.priority = priority
        self.governor = governor or Governor()

    async def letter_logprobs(
        self, prompts: list[list[int]], label_ids: list[list[int]], shared_len: int
    ) -> list[list[float]]:
        """One list per prompt, in the order of that prompt's label_ids."""
        warm = len(prompts) > 1 and shared_len >= self.warm_min_prefix_tokens
        if warm and self.warm_up == "row":
            # compute the long shared prefix once (with row 1) so the other rows hit vLLM's prefix cache
            first = await self._read(prompts[:1], label_ids[:1])
            return first + await self._read(prompts[1:], label_ids[1:])
        if warm and self.warm_up == "prefix":
            await self.governor.call(lambda: self._warm_prefix(prompts[0][:shared_len]))
        return await self._read(prompts, label_ids)

    async def image_logprobs(
        self,
        prompts: list[list[int]],
        label_ids: list[list[int]],
        shared_len: int,
        shared_tokens: int,
        parts: list[dict],
        prefix_parts: list[dict],
    ) -> list[list[float]]:
        """Like letter_logprobs, one call per row. shared_tokens counts the expanded image tokens."""
        warm = len(prompts) > 1 and shared_tokens >= self.warm_min_prefix_tokens
        if warm and self.warm_up == "row":
            first = await self._read_images(prompts[:1], label_ids[:1], parts)
            return first + await self._read_images(prompts[1:], label_ids[1:], parts)
        if warm and self.warm_up == "prefix":
            await self.governor.call(lambda: self._warm_image_prefix(prompts[0][:shared_len], prefix_parts))
        return await self._read_images(prompts, label_ids, parts)

    async def _read_images(
        self, prompts: list[list[int]], label_ids: list[list[int]], parts: list[dict]
    ) -> list[list[float]]:
        """Rows go together in waves; a row's label chunks go one after another."""
        wave = self.governor.wave_size() or max(len(prompts), 1)
        out: list[list[float]] = []
        for start in range(0, len(prompts), wave):
            rows = zip(prompts[start : start + wave], label_ids[start : start + wave], strict=True)
            out += await asyncio.gather(*(self._generate_row(prompt, ids, parts) for prompt, ids in rows))
        return out

    async def _generate_row(self, prompt: list[int], ids: list[int], parts: list[dict]) -> list[float]:
        wanted = sorted(set(ids))
        found: dict[int, float] = {}
        for start in range(0, len(wanted), IMAGE_LABEL_IDS):
            chunk = wanted[start : start + IMAGE_LABEL_IDS]
            found |= await self.governor.call(lambda chunk=chunk: self._generate(prompt, chunk, parts))
        return [found[i] for i in ids]

    async def _warm_image_prefix(self, prefix: list[int], prefix_parts: list[dict]) -> None:
        """Send the shared prefix and its images alone, so they are cached before the rows arrive."""
        sampling = {"max_tokens": 1, "temperature": 0}
        payload = {"model": self.model, "token_ids": prefix, "content_parts": prefix_parts, "sampling_params": sampling}
        await self._post(payload, GENERATE_PATH)

    async def _generate(self, prompt: list[int], chunk: list[int], parts: list[dict]) -> dict[int, float]:
        """vLLM cuts one entry from the answer, so the request also asks for a spare id that is no label."""
        ids = [*chunk, next(i for i in count() if i not in chunk)]
        sampling = {"max_tokens": 1, "temperature": 0, "logprobs": len(ids), "logprob_token_ids": ids}
        payload = {"model": self.model, "token_ids": prompt, "content_parts": parts, "sampling_params": sampling}
        top = (await self._post(payload, GENERATE_PATH)).json()["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
        got = {int(e["token"].removeprefix("token_id:")): e["logprob"] for e in top}
        for i in chunk:
            if i not in got:
                raise RuntimeError(f"vLLM returned no logprob for label id {i}")
        return got

    async def _read(self, prompts: list[list[int]], label_ids: list[list[int]]) -> list[list[float]]:
        """Label ids go in chunks of 128; each chunk is sent only with the rows that read one of its ids."""
        wanted = sorted({i for ids in label_ids for i in ids})
        found: list[dict[int, float]] = [{} for _ in prompts]
        for start in range(0, len(wanted), MAX_LABEL_IDS):
            chunk = wanted[start : start + MAX_LABEL_IDS]
            in_chunk = set(chunk)
            rows = [k for k, ids in enumerate(label_ids) if not in_chunk.isdisjoint(ids)]
            wave = self.governor.wave_size() or len(rows)  # while a chat decodes, send a few rows at a time
            for w in range(0, len(rows), wave):
                wave_rows = rows[w : w + wave]
                batch = [prompts[k] for k in wave_rows]
                got = await self.governor.call(lambda batch=batch, chunk=chunk: self._call(batch, chunk))
                for k, logprobs in zip(wave_rows, got, strict=True):
                    found[k].update(logprobs)
        return [[row[i] for i in ids] for row, ids in zip(found, label_ids)]

    async def _warm_prefix(self, prefix: list[int]) -> None:
        """Send the shared prefix alone, so it is cached before the rows that need it arrive."""
        payload = {"model": self.model, "prompt": [prefix], "max_tokens": 1, "temperature": 0, "add_special_tokens": False}
        await self._post(payload)

    async def _call(self, prompts: list[list[int]], ids: list[int]) -> list[dict[int, float]]:
        payload = {
            "model": self.model,
            "prompt": prompts,
            "max_tokens": 1,
            "temperature": 0,
            "logprobs": 0,
            "logprob_token_ids": ids,
            "return_tokens_as_token_ids": True,
            "add_special_tokens": False,
        }
        choices = sorted((await self._post(payload)).json()["choices"], key=lambda c: c["index"])
        return [
            {int(k.removeprefix("token_id:")): v for k, v in c["logprobs"]["top_logprobs"][0].items()} for c in choices
        ]

    async def _post(self, payload: dict, path: str = "/v1/completions") -> httpx.Response:
        if self.priority:
            payload["priority"] = self.priority  # only sent when set: vLLM refuses it without --scheduling-policy priority
        r = await self.client.post(path, json=payload)
        if r.status_code == 400 and "maximum context length" in r.text:
            raise RequestError("prompt is longer than the maximum context length")
        r.raise_for_status()
        return r
