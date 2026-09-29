"""Latency benchmark through the gateway, so it measures what clients see.

usage: uv run python scripts/bench.py --profile qwen3.6-27b [--gateway URL] [--quick] [--chat]
"""

import argparse
import asyncio
import datetime
import json
import random
import time

import httpx
from transformers import AutoTokenizer

from gateway.config import ROOT, Settings
from scripts.bench_data import jevbench_request, jevbench_rows, prediction, synthetic_request

FULL = {
    "state_tokens": (256, 2048, 8192),
    "questions": (1, 4, 16, 64),
    "options": (2, 26, 255),
    "repeats": 5,
    "seconds": 30,
    "jevbench": None,
}
QUICK = {
    "state_tokens": (256, 2048),
    "questions": (1, 16),
    "options": (2, 26),
    "repeats": 2,
    "seconds": 10,
    "jevbench": 50,
}
CHAT_PROMPTS = {
    "short": "Name three prime numbers.",
    "long": "Explain step by step how a hash map resolves collisions, with an example.",
}


async def timed_post(client: httpx.AsyncClient, body: dict) -> tuple[float, dict]:
    start = time.perf_counter()
    r = await client.post("/v1/systemone", json=body)
    r.raise_for_status()
    return (time.perf_counter() - start) * 1000, r.json()


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


async def sweep(client, tok, rng, grid: dict, warm: bool, records: list) -> None:
    """Sequential latency per (state length, questions, options); warm repeats one state."""
    for n_tok in grid["state_tokens"]:
        for n_q in grid["questions"]:
            for n_opt in grid["options"]:
                fixed = synthetic_request(tok, rng, n_tok, n_q, n_opt, nonce=False)
                await timed_post(client, fixed)
                for _ in range(grid["repeats"]):
                    body = fixed if warm else synthetic_request(tok, rng, n_tok, n_q, n_opt)
                    ms, _ = await timed_post(client, body)
                    records.append(
                        {
                            "test": "warm" if warm else "cold",
                            "state_tokens": n_tok,
                            "questions": n_q,
                            "options": n_opt,
                            "ms": ms,
                        }
                    )


async def throughput(client, tok, rng, workers: int, seconds: int, records: list) -> None:
    done = 0
    stop = time.perf_counter() + seconds

    async def worker():
        nonlocal done
        while time.perf_counter() < stop:
            # A transient failure shouldn't abort the run; record it and keep going.
            try:
                await timed_post(client, synthetic_request(tok, rng, 2048, 16, 26))
                done += 1
            except httpx.HTTPError as e:
                records.append({"test": "throughput", "error": type(e).__name__})

    start = time.perf_counter()
    await asyncio.gather(*(worker() for _ in range(workers)))
    records.append({"test": "throughput", "workers": workers, "requests_per_s": done / (time.perf_counter() - start)})


async def jevbench(client, limit: int | None, records: list) -> None:
    for row in jevbench_rows()[:limit]:
        body, gold = jevbench_request(row)
        ms, out = await timed_post(client, body)
        records.append(
            {"test": "jevbench", "type": row["type"], "ms": ms, "correct": prediction(out["answers"]["q"]) == gold}
        )


async def chat_once(client, served: str, prompt: str) -> tuple[float, float]:
    """(time to first token in ms, streamed chunks per second after it)."""
    body = {"model": served, "messages": [{"role": "user", "content": prompt}], "stream": True, "max_tokens": 512}
    start, first, chunks = time.perf_counter(), None, 0
    async with client.stream("POST", "/v1/chat/completions", json=body) as r:
        async for line in r.aiter_lines():
            if line.startswith("data: ") and line != "data: [DONE]":
                chunks += 1
                first = first or time.perf_counter()
    end = time.perf_counter()
    return (first - start) * 1000, chunks / max(end - first, 1e-9)


async def chat_under_load(client, tok, rng, served: str, records: list) -> None:
    for label, prompt in CHAT_PROMPTS.items():
        ttft, tps = await chat_once(client, served, prompt)
        records.append({"test": "chat", "load": "none", "prompt": label, "ttft_ms": ttft, "chunks_per_s": tps})
    stop = asyncio.Event()

    async def decisions():
        while not stop.is_set():
            # Same rationale as throughput()'s worker: don't let one failure kill the load.
            try:
                await timed_post(client, synthetic_request(tok, rng, 2048, 16, 26))
            except httpx.HTTPError as e:
                records.append({"test": "chat_load", "error": type(e).__name__})

    load = [asyncio.create_task(decisions()) for _ in range(4)]
    for label, prompt in CHAT_PROMPTS.items():
        ttft, tps = await chat_once(client, served, prompt)
        records.append({"test": "chat", "load": "4 systemone", "prompt": label, "ttft_ms": ttft, "chunks_per_s": tps})
    stop.set()
    await asyncio.gather(*load)


def summary(records: list) -> str:
    lines = ["| test | state tokens | questions | options | p50 ms | p95 ms |", "|---|---|---|---|---|---|"]
    ok = [r for r in records if "error" not in r]  # error records carry no ms/workers/ttft to tabulate
    groups: dict[tuple, list] = {}
    for r in ok:
        if r["test"] in ("cold", "warm"):
            groups.setdefault((r["test"], r["state_tokens"], r["questions"], r["options"]), []).append(r["ms"])
    for key, ms in groups.items():
        lines.append(f"| {' | '.join(map(str, key))} | {percentile(ms, 0.5):.0f} | {percentile(ms, 0.95):.0f} |")
    lines += ["", "| workers | requests/s |", "|---|---|"]
    lines += [f"| {r['workers']} | {r['requests_per_s']:.1f} |" for r in ok if r["test"] == "throughput"]
    bench = [r for r in ok if r["test"] == "jevbench"]
    if bench:
        ms = [r["ms"] for r in bench]
        accuracy = sum(r["correct"] for r in bench) / len(bench)
        lines += [
            "",
            (
                f"JevBench gold: {len(bench)} rows, accuracy {accuracy:.3f} (uncalibrated sanity check), "
                f"p50 {percentile(ms, 0.5):.0f} ms, p95 {percentile(ms, 0.95):.0f} ms"
            ),
        ]
    chat = [r for r in ok if r["test"] == "chat"]
    if chat:
        lines += ["", "| chat prompt | load | TTFT ms | chunks/s |", "|---|---|---|---|"]
        lines += [f"| {r['prompt']} | {r['load']} | {r['ttft_ms']:.0f} | {r['chunks_per_s']:.1f} |" for r in chat]
    errors = [r for r in records if "error" in r]
    if errors:
        counts: dict[str, int] = {}
        for r in errors:
            counts[r["test"]] = counts.get(r["test"], 0) + 1
        lines += ["", "Errors: " + ", ".join(f"{test} {n}" for test, n in sorted(counts.items()))]
    return "\n".join(lines) + "\n"


async def main(args) -> None:
    s = Settings.from_profile(args.profile)
    tok = AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
    grid, rng, records = (QUICK if args.quick else FULL), random.Random(0), []
    out = ROOT / "docs" / "results" / s.profile / datetime.datetime.now().astimezone().date().isoformat()
    try:
        async with httpx.AsyncClient(base_url=args.gateway, timeout=600) as client:
            await sweep(client, tok, rng, grid, warm=False, records=records)
            await sweep(
                client,
                tok,
                rng,
                grid | {"state_tokens": (2048,), "questions": (16,), "options": (26,)},
                warm=True,
                records=records,
            )
            for workers in (1, 4, 16):
                await throughput(client, tok, rng, workers, grid["seconds"], records)
            await jevbench(client, grid["jevbench"], records)
            if args.chat:
                await chat_under_load(client, tok, rng, s.served_model, records)
    finally:
        # Write whatever we collected even if a step above raised, so no run is a total loss.
        out.mkdir(parents=True, exist_ok=True)
        (out / "raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
        size = "quick" if args.quick else "full"
        scope = "with chat" if args.chat else "systemone only"
        (out / "summary.md").write_text(f"# {s.profile} benchmark ({size}, {scope})\n\n" + summary(records))
    print((out / "summary.md").read_text())


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--gateway", default="http://127.0.0.1:9000")
    parser.add_argument("--quick", action="store_true")
    # Chat-vs-systemone contention testing waits on a scheduling fix (DS-007); off by default.
    parser.add_argument("--chat", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
