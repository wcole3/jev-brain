"""Read the log-probabilities of each row's option labels at its last position, via vLLM /v1/completions."""

import httpx

from gateway.schema import RequestError

MAX_LABEL_IDS = 128  # vLLM's cap on logprob_token_ids per request (MAX_LOGPROB_TOKEN_IDS)


class Readout:
    def __init__(self, client: httpx.AsyncClient, model: str, warm_min_prefix_tokens: int = 512):
        self.client = client
        self.model = model
        self.warm_min_prefix_tokens = warm_min_prefix_tokens

    async def letter_logprobs(
        self, prompts: list[list[int]], label_ids: list[list[int]], shared_len: int
    ) -> list[list[float]]:
        """One list per prompt, in the order of that prompt's label_ids."""
        if len(prompts) > 1 and shared_len >= self.warm_min_prefix_tokens:
            # compute the long shared prefix once so the other rows hit vLLM's prefix cache
            first = await self._read(prompts[:1], label_ids[:1])
            return first + await self._read(prompts[1:], label_ids[1:])
        return await self._read(prompts, label_ids)

    async def _read(self, prompts: list[list[int]], label_ids: list[list[int]]) -> list[list[float]]:
        """Label ids go in chunks of 128; each chunk is sent only with the rows that read one of its ids."""
        wanted = sorted({i for ids in label_ids for i in ids})
        found: list[dict[int, float]] = [{} for _ in prompts]
        for start in range(0, len(wanted), MAX_LABEL_IDS):
            chunk = wanted[start : start + MAX_LABEL_IDS]
            in_chunk = set(chunk)
            rows = [k for k, ids in enumerate(label_ids) if not in_chunk.isdisjoint(ids)]
            got = await self._call([prompts[k] for k in rows], chunk)
            for k, logprobs in zip(rows, got, strict=True):
                found[k].update(logprobs)
        return [[row[i] for i in ids] for row, ids in zip(found, label_ids)]

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
        r = await self.client.post("/v1/completions", json=payload)
        if r.status_code == 400 and "maximum context length" in r.text:
            raise RequestError("prompt is longer than the maximum context length")
        r.raise_for_status()
        choices = sorted(r.json()["choices"], key=lambda c: c["index"])
        return [
            {int(k.removeprefix("token_id:")): v for k, v in c["logprobs"]["top_logprobs"][0].items()} for c in choices
        ]
