"""Raw letter logprobs for every row, layout and option order, read from vLLM with the gateway's own code.

usage: uv run python scripts/collect.py --profile qwen3.6-27b --split calib [--layouts decider_chat,header]
       [--layout-file prompts/experiments/X.toml] [--orders identity|identity+reversed|all] [--label L]
       [--vllm http://127.0.0.1:8000] [--concurrency 8] [--limit N] [--max-len N]
--label writes <split>-<label>.jsonl.gz (needed with --layout-file or a reduced --orders); --orders all (default)
reads every arm's orders.
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
from pathlib import Path

import httpx
from pydantic import ValidationError

from gateway.app import load_engine, vllm_client
from gateway.calibration import stamp_for
from gateway.config import ROOT, Settings
from gateway.decide import OrderFn, read_rows
from gateway.orders import live_rows, option_orders
from gateway.questions import render_question
from gateway.schema import RequestError, SystemOneRequest
from scripts.experiment_layouts import add_layout_file, label_tags, repo_relative
from scripts.splits import rows_for

COLLECT = ROOT / ".cache" / "collect"
ARMS = ("identity", "identity+reversed", "cyclic:2", "cyclic:3", "cyclic:4")
ORDERS = ("identity", "identity+reversed", "all")
SPLITS = ("calib", "eval", "index-dev", "latency-v1", "index-dev-2k", "calib-600")
ATTEMPTS = 3
BACKOFF = 2.0  # seconds before the first retry, doubling after


def all_orders(n: int) -> list[list[int]]:
    """Every order an experiment arm can use, once each, so one pass serves all arms."""
    out: list[list[int]] = []
    for arm in ARMS:
        out += [perm for perm in option_orders(n, arm) if perm not in out]
    return out


def orders_for(name: str) -> OrderFn:
    """all: every arm's orders in one pass; otherwise that one arm's orders."""
    return all_orders if name == "all" else lambda n: option_orders(n, name)


def stamp(engine, layout: str) -> dict:
    """The calibration stamp (what a fit depends on) plus the settings that shape a collected read."""
    s = engine.settings
    return stamp_for(engine.tokenizer, engine.layouts[layout], s) | {
        "profile": s.profile,
        "prefix_pad_always": s.prefix_pad_always,
        "warm_up": s.warm_up,
        "systemone_max_len": s.systemone_max_len,
    }


def live_pad_rows(engine, request: SystemOneRequest, layout: str) -> int:
    """Rows the live first pass would read, so the collected pad matches live."""
    counts = [len(render_question(q, engine.layouts[layout]).options) for q in request.questions.values()]
    return live_rows(counts, engine.settings.option_orders)


async def collect_one(engine, row: dict, layout: str, rec_stamp: dict | None = None,
                      orders: OrderFn = all_orders) -> dict:
    rec = {"id": row["id"], "layout": layout, "stamp": rec_stamp or stamp(engine, layout)}
    try:
        request = SystemOneRequest.model_validate(
            {"state": row["state"], "questions": row["questions"], "layout": layout}
        )
        r = await read_rows(engine, request, orders, pad_rows=live_pad_rows(engine, request, layout))
    except ValidationError as e:
        return rec | {"status": "invalid", "error": str(e).splitlines()[0]}
    except RequestError as e:
        return rec | {"status": "unsupported", "error": str(e)}
    questions = {qid: [{"perm": perm, "logprobs": lp} for lp, perm in reads] for qid, reads in r.reads.items()}
    ok = {"status": "ok", "input_tokens": r.input_tokens, "questions": questions}
    return rec | ok | label_tags(engine, layout, r.batch)


async def collect_retrying(engine, row: dict, layout: str, *args) -> dict:
    """vLLM hiccups (5xx, dropped connections) get retried with backoff; a lasting one stops the run."""
    for attempt in range(ATTEMPTS - 1):
        try:
            return await collect_one(engine, row, layout, *args)
        except httpx.HTTPError:
            await asyncio.sleep(BACKOFF * 2**attempt)
    return await collect_one(engine, row, layout, *args)


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


def repair(
    path, stamps: dict[str, dict], ignore: tuple[str, ...] = (), other: dict | None = None
) -> set[tuple[str, str]]:
    """Rewrite the readable records to a fresh file, so new appends never sit behind a truncated tail.
    Refuses records collected under other settings (other layouts': `other`, if given); `ignore` keys may differ."""
    done: set[tuple[str, str]] = set()
    tmp = path.with_name(path.name + ".tmp")
    try:
        with gzip.open(tmp, "wt", encoding="utf-8") as out:
            for r in records(path):
                want = stamps.get(r["layout"], other or r["stamp"])
                keys = (want.keys() | r["stamp"].keys()) - set(ignore)
                if diff := sorted(k for k in keys if r["stamp"].get(k) != want.get(k)):
                    raise SystemExit(f"{path}: {r['layout']} records were collected with other {diff}")
                out.write(json.dumps(r) + "\n")
                done.add((r["id"], r["layout"]))
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)
    return done


async def collect(engine, rows: list[dict], layouts: list[str], path, concurrency: int = 8, orders: str = "all",
                  extra: dict | None = None) -> int:
    """extra: stamp keys an experiment layout adds; its file then holds that one layout only."""
    path.parent.mkdir(parents=True, exist_ok=True)
    extra = (extra or {}) | ({} if orders == "all" else {"orders": orders})
    stamps = {layout: stamp(engine, layout) | extra for layout in layouts}
    done = repair(path, stamps, other=stamps[layouts[0]] if "layout_file" in extra else None)
    todo = [(row, layout) for row in rows for layout in layouts if (row["id"], layout) not in done]
    gate = asyncio.Semaphore(concurrency)

    async def one(row, layout):
        async with gate:
            return await collect_retrying(engine, row, layout, stamps[layout], orders_for(orders))

    with gzip.open(path, "at", encoding="utf-8") as out:
        for start in range(0, len(todo), 500):  # write in chunks so a crash loses at most one chunk
            for rec in await asyncio.gather(*(one(r, lay) for r, lay in todo[start : start + 500])):
                out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"{min(start + 500, len(todo))}/{len(todo)}", flush=True)
    return len(todo)


async def main(args, transport: httpx.AsyncBaseTransport | None = None) -> None:
    s = dataclasses.replace(
        Settings.from_profile(args.profile), vllm_url=args.vllm, vllm_api_key=os.environ.get("VLLM_API_KEY") or None
    )
    if args.max_len:
        s = dataclasses.replace(s, systemone_max_len=args.max_len)
    async with vllm_client(s, transport) as client:
        served = [m["id"] for m in (await client.get("/v1/models")).json()["data"]]
        if s.served_model not in served:
            raise SystemExit(f"vLLM serves {served}, not {s.served_model}: start the {args.profile} profile first")
        engine = load_engine(s, client, calibrated=False)  # collect never applies calibration
        extra = {}
        if args.layout_file:
            extra = {"labels_sha256": add_layout_file(engine, Path(args.layout_file)),
                     "layout_file": repo_relative(args.layout_file)}
            layouts = [Path(args.layout_file).stem]
        else:
            layouts = args.layouts.split(",") if args.layouts else sorted(engine.layouts)
        rows = rows_for(args.split)[: args.limit]
        suffix = (f"-len{args.max_len}" if args.max_len else "") + (f"-{args.label}" if args.label else "")
        path = COLLECT / args.profile / f"{args.split}{suffix}.jsonl.gz"
        n = await collect(engine, rows, layouts, path, args.concurrency, args.orders, extra)
        print(f"wrote {n} records to {path}")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--split", required=True, choices=SPLITS)
    which = p.add_mutually_exclusive_group()
    which.add_argument("--layouts")
    which.add_argument("--layout-file", help="an experiment layout .toml kept outside prompts/ (needs --label)")
    p.add_argument("--orders", default="all", choices=ORDERS)
    p.add_argument("--label", help="output <split>-<label>.jsonl.gz")
    p.add_argument("--vllm", default=os.environ.get("VLLM_URL", "http://127.0.0.1:8000"))
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--limit", type=int)
    p.add_argument("--max-len", type=int, help="decision cap override (length study); must be <= MAX_MODEL_LEN")
    args = p.parse_args(argv)
    if args.layout_file and not args.label:
        p.error("--layout-file needs --label")
    if args.orders != "all" and not args.label:  # never the <split>.jsonl.gz calibrate.py reads
        p.error("--orders other than all needs --label")
    return args


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
