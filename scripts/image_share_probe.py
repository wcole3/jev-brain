"""Within-request prompt sharing for image decisions: all rows at once vs the image prefix first, on cold requests.

usage: uv run python scripts/image_share_probe.py --profile P [--vllm URL]   (stack up and idle; env VLLM_API_KEY)
Writes docs/results/archive/<profile>/<UTC>-image-sharing/ with results.json and summary.md.
"""

import argparse
import asyncio
import base64
import io
import json
import os
import random
import statistics
import time
import uuid

import httpx
import PIL.Image

from gateway.app import load_engine
from gateway.config import Settings
from gateway.decide import build_batch
from gateway.schema import SystemOneRequest
from scripts.bench import git_revision
from scripts.bench_data import state_text
from scripts.evaluate import now, results_dir

GENERATE_PATH = "/inference/v1/generate"
IMAGE_SIZE = (1280, 1092)
STATE_TOKENS = 200
QUESTIONS = (4, 16)
REPS = 3
ARMS = ("all", "prefix")
COUNTERS = {"vllm:prompt_tokens_total": "prompt", "vllm:prompt_tokens_cached_total": "cached"}


def fresh_png() -> str:
    """A PNG no earlier request sent: a random colour and one random pixel give it a new cache key."""
    seed = uuid.uuid4().bytes
    im = PIL.Image.new("RGB", IMAGE_SIZE, tuple(seed[:3]))
    im.putpixel((0, 0), tuple(seed[3:6]))
    out = io.BytesIO()
    im.save(out, format="PNG")
    return "data:image/png;base64," + base64.b64encode(out.getvalue()).decode()


def probe_request(tok, rng: random.Random, n_questions: int) -> SystemOneRequest:
    questions = {f"q{i}": {"type": "noul", "instructions": f"The image shows at least {i + 1} objects"}
                 for i in range(n_questions)}
    state = state_text(tok, rng, STATE_TOKENS, nonce=True)
    return SystemOneRequest.model_validate({"images": [fresh_png()], "state": state, "questions": questions})


def counters(text: str) -> dict[str, float]:
    """Sum each prompt-token counter over its label sets in a Prometheus /metrics page."""
    totals = dict.fromkeys(COUNTERS.values(), 0.0)
    for line in text.splitlines():
        name = line.split("{", 1)[0].split(" ", 1)[0]
        if name in COUNTERS:
            totals[COUNTERS[name]] += float(line.split()[-1])
    return totals


def summarize(records: list[dict]) -> list[dict]:
    """Median computed/usage ratio and wall ms per arm and question count, in run order."""
    groups: dict[tuple[str, int], list[dict]] = {}
    for r in records:
        groups.setdefault((r["arm"], r["questions"]), []).append(r)
    return [{"arm": arm, "questions": q, "reps": len(rs), "ratio": statistics.median(r["ratio"] for r in rs),
             "ms": statistics.median(r["ms"] for r in rs)} for (arm, q), rs in groups.items()]


def summary_markdown(profile: str, rows: list[dict]) -> str:
    lines = [f"# Image prompt sharing, {profile}", "",
             "ratio = computed / usage tokens, medians over reps. computed includes the prefix pad; usage does not.",
             "",
             "| arm | questions | reps | ratio | ms |", "|---|---|---|---|---|"]
    lines += [f"| {r['arm']} | {r['questions']} | {r['reps']} | {r['ratio']:.2f} | {r['ms']:.0f} |" for r in rows]
    return "\n".join(lines) + "\n"


class Probe:
    def __init__(self, http: httpx.AsyncClient, model: str):
        self.http, self.model = http, model

    async def metrics(self) -> dict[str, float]:
        r = await self.http.get("/metrics")
        r.raise_for_status()
        return counters(r.text)

    async def generate(self, ids: list[int], parts: list[dict]) -> None:
        payload = {"model": self.model, "token_ids": ids, "content_parts": parts,
                   "sampling_params": {"max_tokens": 1, "temperature": 0}}
        (await self.http.post(GENERATE_PATH, json=payload)).raise_for_status()

    async def call_set(self, batch, arm: str) -> dict:
        """One arm's calls for one request, with the prompt-token counter deltas and wall time around them."""
        parts = [image.part() for image in batch.images.images]
        rows = [row.ids for row in batch.rows]
        before, start = await self.metrics(), time.perf_counter()
        if arm == "prefix":
            await self.generate(rows[0][: batch.shared_len], parts if batch.images_shared else [])
        await asyncio.gather(*(self.generate(ids, parts) for ids in rows))
        ms = (time.perf_counter() - start) * 1000
        after = await self.metrics()
        prompt, cached = after["prompt"] - before["prompt"], after["cached"] - before["cached"]
        usage = batch.input_tokens
        return {"rows": len(rows), "shared_len": batch.shared_len, "unpadded_len": batch.unpadded_len,
                "shared_tokens": batch.shared_tokens, "images_shared": batch.images_shared, "added": batch.added,
                "usage": usage, "prompt": prompt, "cached": cached, "computed": prompt - cached,
                "ratio": (prompt - cached) / usage, "ms": ms}


async def run(s: Settings, vllm: str) -> list[dict]:
    key = os.environ.get("VLLM_API_KEY")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    async with httpx.AsyncClient() as engine_client, httpx.AsyncClient(base_url=vllm, headers=headers,
                                                                       timeout=900) as http:
        engine = load_engine(s, engine_client, calibrated=False)
        if engine.vision is None:
            raise SystemExit(f"{s.profile} serves text only (SYSTEMONE_IMAGES is not 1)")
        probe, rng, records = Probe(http, s.served_model), random.Random(1000), []
        for n_questions in QUESTIONS:
            for rep in range(REPS):
                for arm in ARMS:
                    _, _, batch = await build_batch(engine, probe_request(engine.tokenizer, rng, n_questions))
                    r = {"questions": n_questions, "rep": rep, "arm": arm, **await probe.call_set(batch, arm)}
                    records.append(r)
                    print(f"x{n_questions:2} {arm:6} rep {rep} usage {r['usage']:6} computed {r['computed']:7.0f} "
                          f"ratio {r['ratio']:5.2f} ms {r['ms']:7.0f}", flush=True)
    return records


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--vllm", default="http://127.0.0.1:8000")
    args = p.parse_args()
    s = Settings.from_profile(args.profile)
    records = asyncio.run(run(s, args.vllm))
    out = results_dir(args.profile, f"{now()}-image-sharing", archive=True)
    settings = {"warm_up": s.warm_up, "warm_min_prefix_tokens": s.warm_min_prefix_tokens,
                "prefix_block": s.prefix_block, "commit": git_revision()}
    result = {"profile": args.profile, "settings": settings, "image_size": IMAGE_SIZE, "state_tokens": STATE_TOKENS,
              "records": records}
    (out / "results.json").write_text(json.dumps(result, indent=1) + "\n")
    (out / "summary.md").write_text(summary_markdown(args.profile, summarize(records)))
    print(out)


if __name__ == "__main__":
    main()
