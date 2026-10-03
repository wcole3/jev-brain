"""Benchmark through the gateway (so it measures what clients see), or JevBench against the official Jev API.

usage: uv run python scripts/bench.py --profile qwen3.6-27b [--gateway URL] [--vllm URL] [--quick] [--jevbench-only] [--chat]
       uv run python scripts/bench.py --target jev [--quick]   (JevBench against the official Jev API)
"""

import argparse
import asyncio
import contextlib
import datetime
import json
import os
import random
import subprocess
import time

import httpx
from transformers import AutoTokenizer

from gateway.config import ROOT, Settings
from scripts import host_info
from scripts.bench_data import (
    JEVBENCH_SHA,
    jevbench_request,
    jevbench_rows,
    prediction,
    probabilities,
    synthetic_request,
)
from scripts.bench_report import provenance, summary
from scripts.bench_vllm import Vllm

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
JEV_URL = "https://api.typesafe.ai"
JEV_KEY_FILE = ROOT / "secrets" / ".jev-key"
CHAT_PROMPTS = {
    "short": "Name three prime numbers.",
    "long": "Explain step by step how a hash map resolves collisions, with an example.",
}


PREFIX_KEYS = ("prefix_pad", "prefix_block", "prefix_pad_always", "warm_min_prefix_tokens", "warm_up")
CACHE_LABEL_KEYS = (
    "cache_dtype",
    "mamba_cache_dtype",
    "mamba_ssm_cache_dtype",
    "mamba_block_size",
    "mamba_cache_mode",
    "enable_prefix_caching",
)


async def timed_post(client: httpx.AsyncClient, body: dict) -> tuple[float, dict]:
    start = time.perf_counter()
    r = await client.post("/v1/systemone", json=body)
    r.raise_for_status()
    return (time.perf_counter() - start) * 1000, r.json()


async def sweep(client, tok, rng, grid: dict, warm: bool, records: list) -> None:
    """Sequential latency per (state length, questions, options); warm repeats one state."""
    for n_tok in grid["state_tokens"]:
        for n_q in grid["questions"]:
            for n_opt in grid["options"]:
                fixed = synthetic_request(tok, rng, n_tok, n_q, n_opt, nonce=False)
                test = "warm" if warm else "cold"
                try:
                    _, out = await timed_post(client, fixed)
                    records.append({"test": "warmup", "phase": test, "input_tokens": out["usage"]["input_tokens"]})
                except httpx.HTTPError as e:
                    records.append({"test": test, "error": type(e).__name__})
                for _ in range(grid["repeats"]):
                    body = fixed if warm else synthetic_request(tok, rng, n_tok, n_q, n_opt)
                    try:
                        ms, out = await timed_post(client, body)
                    except httpx.HTTPError as e:
                        records.append({"test": test, "error": type(e).__name__})
                        continue
                    records.append(
                        {
                            "test": test,
                            "phase": test,
                            "state_tokens": n_tok,
                            "questions": n_q,
                            "options": n_opt,
                            "ms": ms,
                            "input_tokens": out["usage"]["input_tokens"],
                        }
                    )


async def throughput(client, tok, rng, workers: int, seconds: int, records: list) -> None:
    done, input_tokens = 0, 0
    stop = time.perf_counter() + seconds

    async def worker():
        nonlocal done, input_tokens
        while time.perf_counter() < stop:
            # A transient failure shouldn't abort the run; record it and keep going.
            try:
                _, out = await timed_post(client, synthetic_request(tok, rng, 2048, 16, 26))
                done += 1
                input_tokens += out["usage"]["input_tokens"]
            except httpx.HTTPError as e:
                records.append({"test": "throughput", "error": type(e).__name__})

    start = time.perf_counter()
    await asyncio.gather(*(worker() for _ in range(workers)))
    records.append(
        {
            "test": "throughput",
            "phase": f"throughput x{workers}",
            "workers": workers,
            "requests_per_s": done / (time.perf_counter() - start),
            "input_tokens": input_tokens,
        }
    )


def run_suffix(started: datetime.datetime, quick: bool, jevbench_only: bool) -> str:
    """UTC start time, e.g. 2026-09-29T210957Z-quick."""
    return started.strftime("%Y-%m-%dT%H%M%SZ") + ("-quick" if quick else "") + ("-jevbench" if jevbench_only else "")


async def jevbench(client, rows: list[dict], records: list) -> None:
    for row in rows:
        body, gold = jevbench_request(row)
        record = {
            "test": "jevbench",
            "phase": "jevbench",
            "id": row["id"],
            "type": row["type"],
            "eval_metric": row["eval_metric"],
        }
        try:
            ms, out = await timed_post(client, body)
        except httpx.HTTPError as e:
            records.append(record | {"gold": gold, "pred": None, "correct": False, "error": type(e).__name__})
            continue
        answer = out["answers"]["q"]
        pred = prediction(answer)
        result = {"gold": gold, "pred": pred, "correct": pred == gold, "ms": ms, "model": out.get("model")}
        result |= {"probabilities": probabilities(answer)}
        if "confidence" in answer:
            result["confidence"] = answer["confidence"]
        records.append(record | result | {"input_tokens": out["usage"]["input_tokens"]})


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
                _, out = await timed_post(client, synthetic_request(tok, rng, 2048, 16, 26))
                records.append({"test": "chat_load", "phase": "chat", "input_tokens": out["usage"]["input_tokens"]})
            except httpx.HTTPError as e:
                records.append({"test": "chat_load", "error": type(e).__name__})

    load = [asyncio.create_task(decisions()) for _ in range(4)]
    for label, prompt in CHAT_PROMPTS.items():
        ttft, tps = await chat_once(client, served, prompt)
        records.append({"test": "chat", "load": "4 systemone", "prompt": label, "ttft_ms": ttft, "chunks_per_s": tps})
    stop.set()
    await asyncio.gather(*load)


def git_revision() -> str:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()

    # Uncommitted results from earlier runs don't make the code dirty.
    dirty = git("status", "--porcelain", "--", ".", ":(exclude)docs/results")
    return git("rev-parse", "--short", "HEAD") + ("-dirty" if dirty else "")


def jev_key() -> str:
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key and JEV_KEY_FILE.exists():
        key = JEV_KEY_FILE.read_text().strip()
    if not key:
        raise SystemExit(f"--target jev needs an API key: set TYPESAFE_API_KEY or write it to {JEV_KEY_FILE}")
    return key


def connection(args) -> tuple[str, dict]:
    """(base url, auth headers); the key is never printed or recorded."""
    if args.target == "jev":
        return JEV_URL, {"Authorization": f"Bearer {jev_key()}"}
    key = os.environ.get("GATEWAY_API_KEY")
    return args.gateway, {"Authorization": f"Bearer {key}"} if key else {}


async def gateway_health(client, profile: str) -> dict:
    health = (await client.get("/health")).json()
    if health["profile"] != profile:
        raise SystemExit(f"gateway serves profile {health['profile']!r} but --profile is {profile!r}")
    return health


async def main(args) -> None:
    jev, revision = args.target == "jev", git_revision()
    jevbench_only = jev or args.jevbench_only
    base_url, headers = connection(args)
    started = datetime.datetime.now(datetime.UTC)
    suffix = run_suffix(started, args.quick, jevbench_only)
    grid, rng = (QUICK if args.quick else FULL), random.Random(0)
    records: list = []
    vllm = None if jev else Vllm(args.vllm, records)
    phase = vllm.watch if vllm else lambda name: contextlib.nullcontext()
    name = "jev" if jev else args.profile
    out = ROOT / "docs" / "results" / ("archive" if args.quick else "") / name / suffix
    # TypeSafe's terms forbid using Jev outputs for training or calibration, so keep them out of the repo.
    raw = ROOT / ".cache" / "jev-results" / suffix if jev else out
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=600) as client:
        meta = {"timestamp": started.isoformat(), "repo commit": revision, "host": host_info.summary(),
                "target": args.target}
        if not jev:
            health = await gateway_health(client, args.profile)
        gold_rows = jevbench_rows()
        rows = gold_rows[: grid["jevbench"]]
        meta |= {"JevBench SHA": JEVBENCH_SHA, "gold rows available": len(gold_rows), "rows run": len(rows)}
        if jev:
            meta["base URL"] = base_url
        else:
            keys = ("profile", "hf_model", "hf_revision", "prompt_layout", "option_orders", "vllm_version")
            meta |= {key: health.get(key) for key in keys}
            meta |= {key: health[key] for key in PREFIX_KEYS if key in health}
            if labels := await vllm.cache_labels():
                meta["KV cache"] = f"{labels['num_gpu_blocks']} blocks × {labels['block_size']} tokens"
                meta |= {key: labels[key] for key in CACHE_LABEL_KEYS if key in labels}
        try:
            if not jevbench_only or args.chat:
                s = Settings.from_profile(args.profile)
                tok = AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
            if not jevbench_only:
                async with phase("cold"):
                    await sweep(client, tok, rng, grid, warm=False, records=records)
                warm_grid = grid | {"state_tokens": (2048,), "questions": (16,), "options": (26,)}
                async with phase("warm"):
                    await sweep(client, tok, rng, warm_grid, warm=True, records=records)
                for workers in (1, 4, 16):
                    async with phase(f"throughput x{workers}"):
                        await throughput(client, tok, rng, workers, grid["seconds"], records)
            async with phase("jevbench"):
                await jevbench(client, rows, records)
            if args.chat:
                async with phase("chat"):
                    await chat_under_load(client, tok, rng, s.served_model, records)
        finally:
            if vllm:
                await vllm.aclose()
            # Write whatever we collected even if a step above raised, so no run is a total loss.
            if jev:
                meta["models returned"] = sorted({r["model"] for r in records if r.get("model")})
            raw.mkdir(parents=True, exist_ok=True)
            (raw / "raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
            size = "quick" if args.quick else "full"
            scope = "JevBench only" if jevbench_only else "with chat" if args.chat else "systemone only"
            out.mkdir(parents=True, exist_ok=True)
            (out / "summary.md").write_text(
                f"# {name} benchmark ({size}, {scope})\n\n{provenance(meta)}\n{summary(records, jev)}"
            )
    print((out / "summary.md").read_text())


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=("gateway", "jev"), default="gateway")
    parser.add_argument("--profile")
    parser.add_argument("--gateway", default="http://127.0.0.1:9000")
    parser.add_argument("--vllm", default=os.environ.get("VLLM_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--jevbench-only", action="store_true")
    # Chat-vs-systemone contention testing waits on a scheduling fix (DS-007); off by default.
    parser.add_argument("--chat", action="store_true")
    args = parser.parse_args(argv)
    if args.target == "gateway" and not args.profile:
        parser.error("--profile is required with --target gateway")
    if args.target == "jev" and args.chat:
        parser.error("--chat needs the gateway target")
    return args


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
