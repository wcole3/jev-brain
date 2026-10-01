"""Phase-2 evaluation CLI.

usage:
  uv run python scripts/evaluate.py offline --profile P --split S [--layout L] [--orders O] [--uncalibrated]
  uv run python scripts/evaluate.py index --profile P [--gateway URL] [--shards 8] [--ids FILE] [--chat-probe]
  uv run python scripts/evaluate.py lengths --profile P [--near 0.5]
  uv run python scripts/evaluate.py replace --profile P --base RUN_DIR --override RUN_DIR
Index runs and collect are long runs: get the owner's ok first.
"""

import argparse
import asyncio
import datetime
import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path

import httpx

from gateway.app import load_engine
from gateway.calibration import load_temperatures
from gateway.config import ROOT, Settings
from scripts import board, index_run, metrics
from scripts.bench import CHAT_PROMPTS, chat_once, git_revision
from scripts.bench_report import percentile, provenance
from scripts.bench_vllm import Vllm
from scripts.collect import COLLECT, records
from scripts.decision_rows import index_meta, index_rows
from scripts.index_suite import EDITION, EXPORT, HARNESS_SHA, harness_env
from scripts.lengths import NAMES, bucket_counts, real_lengths
from scripts.offline import UNCALIBRATED, Arm, evaluate, markdown
from scripts.splits import SPLITS, rows_for

RUNS = ROOT / ".cache" / "index-runs"


def now() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")


def results_dir(profile: str, name: str) -> Path:
    out = ROOT / "docs" / "results" / profile / name
    out.mkdir(parents=True, exist_ok=True)
    return out


def gateway_headers() -> dict[str, str]:
    """Auth for the gateway's chat endpoint; the key is never printed or recorded."""
    key = os.environ.get("GATEWAY_API_KEY")
    return {"Authorization": f"Bearer {key}"} if key else {}


def cmd_offline(args) -> None:
    s = Settings.from_profile(args.profile)
    temps = dict(UNCALIBRATED) if args.uncalibrated else load_temperatures(s.data_dir(args.layout) / "calibration.json")
    arm = Arm(args.layout, args.orders, temps)
    rows = {r["id"]: r for r in rows_for(args.split)}
    collected = COLLECT / args.profile / f"{args.split}.jsonl.gz"
    report = evaluate(records(collected), rows, arm)
    stamp = now()
    meta = {"timestamp": stamp, "repo commit": git_revision(), "profile": args.profile, "split": args.split,
            "collected": str(collected.relative_to(ROOT))}
    out = results_dir(args.profile, f"{stamp}-offline-{args.split}-{args.layout}-{args.orders.replace(':', '')}")
    (out / "summary.md").write_text(f"# {args.profile} offline: {args.split}\n\n{provenance(meta)}\n{markdown(report)}")
    print(out / "summary.md")


async def probe_chat(client: httpx.AsyncClient, served: str) -> dict:
    """One short streaming chat. Failures are recorded, never raised, so the Index results still get scored."""
    try:
        ttft, rate = await chat_once(client, served, CHAT_PROMPTS["short"])
    except httpx.HTTPError as e:
        return {"error": type(e).__name__}
    except TypeError:  # chat_once found no chunk to time
        return {"error": "no chunks streamed"}
    return {"ttft_ms": ttft, "chunks_per_s": rate}


async def chat_probe(client: httpx.AsyncClient, served: str, stop: asyncio.Event, samples: list) -> None:
    """One short streaming chat at a time while the Index runs: what a chat user sees meanwhile."""
    while not stop.is_set():
        samples.append(await probe_chat(client, served))
        await asyncio.sleep(2)


async def idle_chats(client: httpx.AsyncClient, served: str, n: int = 3) -> list[dict]:
    return [await probe_chat(client, served) for _ in range(n)]


async def run_index(args, run: Path, health: dict) -> dict:
    ids = set(json.loads(Path(args.ids).read_text())["ids"]) if args.ids else None
    shards = sorted(run.glob("shard-*.jsonl.gz")) or index_run.write_shards(EXPORT, args.shards, run, ids)
    env = harness_env()
    if key := os.environ.get("GATEWAY_API_KEY"):
        env["DECISION_INDEX_API_KEY"] = key
    commands = [index_run.shard_command(s, run / s.name.removesuffix(".jsonl.gz"), args.gateway) for s in shards]
    vllm_records: list = []
    vllm = Vllm(args.vllm, vllm_records)
    stop, idle, busy = asyncio.Event(), [], []
    served = health["served_model"]
    async with httpx.AsyncClient(base_url=args.gateway, headers=gateway_headers(), timeout=600) as client:
        if args.chat_probe:
            idle = await idle_chats(client, served)
        probe = asyncio.create_task(chat_probe(client, served, stop, busy)) if args.chat_probe else None
        started = time.perf_counter()
        async with vllm.watch("index"):
            codes = await index_run.run_all(commands, env)
        seconds = time.perf_counter() - started
        stop.set()
        if probe:
            await probe
    await vllm.aclose()
    return {"codes": codes, "seconds": seconds, "vllm": vllm_records, "idle": idle, "busy": busy}


def score(merged: Path) -> dict:
    subprocess.run(index_run.score_command(merged / "results.jsonl", merged), cwd=index_run.SRC, env=harness_env(),
                   check=True)
    return json.loads((merged / "scores.json").read_text())


def load(merged: Path) -> list[dict]:
    return [json.loads(x) for x in (merged / "results.jsonl").read_text().splitlines() if x.strip()]


def unjudged_reason(counts: dict, scores: dict, reason: str | None = None) -> str | None:
    """Why the parity gate can't judge this run, or None. The harness counts error rows as unanswered."""
    reasons = [reason] if reason else []
    if counts.get("error"):
        reasons.append(f"{counts['error']} error rows: resume with --run-dir")
    if not scores["complete"]:
        reasons.append(f"run incomplete: {scores['completed']} rows")
    return "; ".join(reasons) or None


def index_summary(profile: str, scores: dict, merged: Path, extra: list[str], unjudged: str | None = None) -> str:
    """Subset, partial and error-holed runs get no parity verdict: their Index is not comparable to the board."""
    results = load(merged)
    counts = dict(Counter(r["status"] for r in results))
    rows = {r["id"]: r for r in index_rows({r["run_id"] for r in results})}
    items = index_run.index_scored(merged / "results.jsonl", rows)
    ms = [r["total_wall_ms"] for r in results if r["status"] == "ok"]
    total = len(results)
    ours = {"index": scores["decision_index"], "ece": metrics.ece(items) if items else None,
            "median_ms": percentile(ms, 0.5) if ms else None, "coverage": counts.get("ok", 0) / total if total else None}
    areas = ["| area | skill | raw | coverage | n |", "|---|---|---|---|---|"]
    areas += [f"| {a['id']} | {100 * a['skill']:.1f} | {100 * a['raw']:.1f} | {a['coverage']:.3f} | {a['n']} |"
              for a in scores["areas"]]
    notes = [
        ("- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals);"
         " the board's ECE uses its own row set, so compare loosely."),
        ("- median ms: the harness's per-request wall time with all shards running at once, not latency-v1;"
         " see the latency report for the comparable figure."),
    ]
    status = f"Status: {counts}; harness complete: {scores['complete']}, completed: {scores['completed']}"
    verdict = unjudged_reason(counts, scores, unjudged)
    lines = [*board.comparison(profile, ours, verdict), "", *areas, "", status, "", *notes, *extra]
    return "\n".join(lines) + "\n"


def run_notes(outcome: dict) -> list[str]:
    """Shard exit codes, vLLM's KV and queue during the run, and chat latency idle vs during it."""
    notes = [f"- shard exit codes: {outcome['codes']}, wall {outcome['seconds'] / 60:.1f} min"]
    if outcome["vllm"]:
        v = outcome["vllm"][0]  # the phase summary; per-sample records follow it
        notes.append(f"- vLLM during the run: KV peak {100 * v['kv_peak']:.1f}%, mean {100 * v['kv_mean']:.1f}%,"
                     f" waiting peak {v['waiting_peak']:.0f}, preemptions {v['preemptions']}")
    for label, samples in (("idle", outcome["idle"]), ("during run", outcome["busy"])):
        ok = [s for s in samples if "error" not in s]
        failed = len(samples) - len(ok)
        if ok:
            ttft = percentile([s["ttft_ms"] for s in ok], 0.5)
            rate = percentile([s["chunks_per_s"] for s in ok], 0.5)
            notes.append(f"- chat {label}: median TTFT {ttft:.0f} ms, {rate:.1f} chunks/s"
                         f" ({len(ok)} samples, {failed} failed)")
        elif samples:
            notes.append(f"- chat {label}: {failed} of {len(samples)} probes failed")
    return notes


async def cmd_index(args) -> None:
    async with httpx.AsyncClient(base_url=args.gateway, timeout=30) as client:
        health = (await client.get("/health")).json()
    if health["profile"] != args.profile:
        raise SystemExit(f"gateway serves {health['profile']!r}, not {args.profile!r}")
    run = Path(args.run_dir).resolve() if args.run_dir else RUNS / args.profile / now()
    run.mkdir(parents=True, exist_ok=True)
    outcome = await run_index(args, run, health)
    index_run.merge(sorted(p for p in run.glob("shard-*") if p.is_dir()), run / "merged")
    scores = score(run / "merged")
    keys = ("profile", "hf_model", "hf_revision", "prompt_layout", "option_orders", "systemone_max_len", "temperatures",
            "vllm_version")
    meta = {"timestamp": now(), "repo commit": git_revision(), "harness": HARNESS_SHA, "edition": EDITION,
            "run dir": str(run.relative_to(ROOT)), "shards": len(outcome["codes"]), "ids": args.ids or "full suite"}
    meta |= {k: health.get(k) for k in keys}
    out = results_dir(args.profile, f"{run.name}-index{'-subset' if args.ids else ''}")
    body = index_summary(args.profile, scores, run / "merged", run_notes(outcome), "subset run" if args.ids else None)
    (out / "summary.md").write_text(f"# {args.profile} Decision Index {EDITION}\n\n{provenance(meta)}\n{body}")
    print(out / "summary.md")


async def cmd_lengths(args) -> None:
    s = Settings.from_profile(args.profile)
    meta = index_meta()
    counts = bucket_counts(meta)
    near = {m["id"] for m in meta if (m["meta"]["proxy_tokens"] or 0) >= args.near * s.systemone_max_len}
    engine = load_engine(s, None)
    longest = await real_lengths(engine, index_rows(near))
    over = sorted(i for i, n in longest.items() if n >= s.systemone_max_len)
    split = {"meta": {"profile": args.profile, "cap": s.systemone_max_len, "max_model_len": s.max_model_len,
                      "near": args.near}, "ids": over, "longest": {i: longest[i] for i in over}}
    SPLITS.mkdir(parents=True, exist_ok=True)
    (SPLITS / f"long-rows-{args.profile}.json").write_text(json.dumps(split, indent=0) + "\n")
    lines = ["| proxy tokens | rows | benchmarks |", "|---|---|---|"]
    order = [*NAMES, "unknown"]
    lines += [f"| {b} | {sum(counts[b].values())} | {len(counts[b])} |" for b in order if b in counts]
    fits = sum(longest[i] < s.max_model_len for i in over)
    lines += ["", (f"At or over the decision cap ({s.systemone_max_len}): {len(over)} rows; "
                   f"{fits} of them fit under MAX_MODEL_LEN ({s.max_model_len}).")]
    out = results_dir(args.profile, f"{now()}-lengths")
    meta_lines = {"timestamp": now(), "repo commit": git_revision(), "profile": args.profile}
    (out / "summary.md").write_text(
        f"# {args.profile} decision lengths\n\n{provenance(meta_lines)}\n" + "\n".join(lines) + "\n")
    print(out / "summary.md")


def cmd_replace(args) -> None:
    base, override = Path(args.base).resolve(), Path(args.override).resolve()
    out = base.parent / f"{base.name}+{override.name}"
    swapped = index_run.replace(base / "merged" / "results.jsonl", override / "merged" / "results.jsonl", out / "merged")
    scores = score(out / "merged")
    meta = {"timestamp": now(), "repo commit": git_revision(), "base": str(base.relative_to(ROOT)),
            "override": str(override.relative_to(ROOT)), "rows swapped": swapped}
    body = index_summary(args.profile, scores, out / "merged", [], "long rows rerun at a higher cap")
    target = results_dir(args.profile, f"{out.name}-index-replaced")
    (target / "summary.md").write_text(f"# {args.profile} Decision Index, long rows rerun\n\n{provenance(meta)}\n{body}")
    print(target / "summary.md")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    o = sub.add_parser("offline")
    o.add_argument("--profile", required=True)
    o.add_argument("--split", required=True, choices=("calib", "eval", "index-dev", "latency-v1"))
    o.add_argument("--layout", default="decider_chat")
    o.add_argument("--orders", default="identity")
    o.add_argument("--uncalibrated", action="store_true", help="T = 1 for every type instead of calibration.json")
    i = sub.add_parser("index")
    i.add_argument("--profile", required=True)
    i.add_argument("--gateway", default="http://127.0.0.1:9000")
    i.add_argument("--vllm", default=os.environ.get("VLLM_URL", "http://127.0.0.1:8000"))
    i.add_argument("--shards", type=int, default=8)
    i.add_argument("--ids", help="JSON file with an 'ids' list: run only those rows")
    i.add_argument("--run-dir", help="resume this run directory")
    i.add_argument("--chat-probe", action="store_true")
    n = sub.add_parser("lengths")
    n.add_argument("--profile", required=True)
    n.add_argument("--near", type=float, default=0.5, help="measure real tokens for rows with proxy >= near * cap")
    r = sub.add_parser("replace")
    r.add_argument("--profile", required=True)
    r.add_argument("--base", required=True)
    r.add_argument("--override", required=True)
    return p.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    if args.command == "offline":
        cmd_offline(args)
    elif args.command == "index":
        asyncio.run(cmd_index(args))
    elif args.command == "lengths":
        asyncio.run(cmd_lengths(args))
    else:
        cmd_replace(args)


if __name__ == "__main__":
    main()
