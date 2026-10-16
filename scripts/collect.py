"""Raw letter logprobs for every row, layout and option order, read from vLLM with the gateway's own code.

usage: uv run python scripts/collect.py --profile qwen3.6-27b --split calib [--layouts decider_chat,header]
       [--vllm http://127.0.0.1:8000] [--concurrency 8] [--limit N] [--max-len N]
Needs the stack up and idle (owner ok: this is a long run). Resumes where it stopped.
"""

import argparse
import asyncio
import dataclasses
import gzip
import json
import os
import zlib
from collections.abc import Iterator

import httpx
from pydantic import ValidationError

from gateway.app import load_engine, vllm_client
from gateway.calibration import stamp_for
from gateway.config import ROOT, Settings
from gateway.decide import read_rows
from gateway.orders import option_orders
from gateway.schema import RequestError, SystemOneRequest
from scripts.splits import rows_for

COLLECT = ROOT / ".cache" / "collect"
ARMS = ("identity", "identity+reversed", "cyclic:2", "cyclic:3", "cyclic:4")
ATTEMPTS = 3
BACKOFF = 2.0  # seconds before the first retry, doubling after


def all_orders(n: int) -> list[list[int]]:
    """Every order an experiment arm can use, once each, so one pass serves all arms."""
    out: list[list[int]] = []
    for arm in ARMS:
        out += [perm for perm in option_orders(n, arm) if perm not in out]
    return out


def stamp(engine, layout: str) -> dict:
    """The calibration stamp (what a fit depends on) plus the settings that shape a collected read."""
    s = engine.settings
    return stamp_for(engine.tokenizer, engine.layouts[layout], s) | {
        "profile": s.profile,
        "prefix_pad_always": s.prefix_pad_always,
        "warm_up": s.warm_up,
        "systemone_max_len": s.systemone_max_len,
    }


async def collect_one(engine, row: dict, layout: str) -> dict:
    rec = {"id": row["id"], "layout": layout, "stamp": stamp(engine, layout)}
    try:
        request = SystemOneRequest.model_validate(
            {"state": row["state"], "questions": row["questions"], "layout": layout}
        )
        # pad as the live default request would (one identity row per question), so offline matches live
        r = await read_rows(engine, request, all_orders, pad_rows=len(request.questions))
    except ValidationError as e:
        return rec | {"status": "invalid", "error": str(e).splitlines()[0]}
    except RequestError as e:
        return rec | {"status": "unsupported", "error": str(e)}
    questions = {qid: [{"perm": perm, "logprobs": lp} for lp, perm in reads] for qid, reads in r.reads.items()}
    return rec | {"status": "ok", "input_tokens": r.input_tokens, "questions": questions}


async def collect_retrying(engine, row: dict, layout: str) -> dict:
    """vLLM hiccups (5xx, dropped connections) get retried with backoff; a lasting one stops the run."""
    for attempt in range(ATTEMPTS - 1):
        try:
            return await collect_one(engine, row, layout)
        except httpx.HTTPError:
            await asyncio.sleep(BACKOFF * 2**attempt)
    return await collect_one(engine, row, layout)


def records(path) -> Iterator[dict]:
    """Every complete record; a run killed mid-write leaves a truncated tail, which is skipped."""
    if not path.exists():
        return
    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                if line.endswith("\n"):
                    yield json.loads(line)
    except (EOFError, gzip.BadGzipFile, zlib.error):
        return


def done_keys(path) -> set[tuple[str, str]]:
    return {(r["id"], r["layout"]) for r in records(path)}


def repair(path, stamps: dict[str, dict], ignore: tuple[str, ...] = ()) -> set[tuple[str, str]]:
    """Rewrite the readable records to a fresh file, so new appends never sit behind a truncated tail.
    Refuses records of these layouts collected under other settings; the `ignore` stamp keys may differ."""
    done: set[tuple[str, str]] = set()
    tmp = path.with_name(path.name + ".tmp")
    try:
        with gzip.open(tmp, "wt", encoding="utf-8") as out:
            for r in records(path):
                want = stamps.get(r["layout"], r["stamp"])
                keys = (want.keys() | r["stamp"].keys()) - set(ignore)
                if diff := sorted(k for k in keys if r["stamp"].get(k) != want.get(k)):
                    raise SystemExit(f"{path}: {r['layout']} records were collected with other {diff}")
                out.write(json.dumps(r) + "\n")
                done.add((r["id"], r["layout"]))
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
    return done


async def collect(engine, rows: list[dict], layouts: list[str], path, concurrency: int = 8) -> int:
    if engine.settings.option_orders != "identity":  # pad_rows mirrors the identity live arm
        raise SystemExit(f"option_orders is {engine.settings.option_orders!r}: collect needs an identity profile")
    path.parent.mkdir(parents=True, exist_ok=True)
    done = repair(path, {layout: stamp(engine, layout) for layout in layouts})
    todo = [(row, layout) for row in rows for layout in layouts if (row["id"], layout) not in done]
    gate = asyncio.Semaphore(concurrency)

    async def one(row, layout):
        async with gate:
            return await collect_retrying(engine, row, layout)

    with gzip.open(path, "at", encoding="utf-8") as out:
        for start in range(0, len(todo), 500):  # write in chunks so a crash loses at most one chunk
            for rec in await asyncio.gather(*(one(r, lay) for r, lay in todo[start : start + 500])):
                out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"{min(start + 500, len(todo))}/{len(todo)}", flush=True)
    return len(todo)


async def main(args) -> None:
    s = dataclasses.replace(
        Settings.from_profile(args.profile), vllm_url=args.vllm, vllm_api_key=os.environ.get("VLLM_API_KEY") or None
    )
    if args.max_len:
        s = dataclasses.replace(s, systemone_max_len=args.max_len)
    async with vllm_client(s, None) as client:
        served = [m["id"] for m in (await client.get("/v1/models")).json()["data"]]
        if s.served_model not in served:
            raise SystemExit(f"vLLM serves {served}, not {s.served_model}: start the {args.profile} profile first")
        engine = load_engine(s, client, calibrated=False)  # collect never applies calibration
        rows = rows_for(args.split)[: args.limit]
        layouts = args.layouts.split(",") if args.layouts else sorted(engine.layouts)
        suffix = f"-len{args.max_len}" if args.max_len else ""
        path = COLLECT / args.profile / f"{args.split}{suffix}.jsonl.gz"
        print(f"wrote {await collect(engine, rows, layouts, path, args.concurrency)} records to {path}")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--split", required=True, choices=("calib", "eval", "index-dev", "latency-v1"))
    p.add_argument("--layouts")
    p.add_argument("--vllm", default=os.environ.get("VLLM_URL", "http://127.0.0.1:8000"))
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--limit", type=int)
    p.add_argument("--max-len", type=int, help="decision cap override (length study); must be <= MAX_MODEL_LEN")
    return p.parse_args(argv)


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
