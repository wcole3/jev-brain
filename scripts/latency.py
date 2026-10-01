"""latency-v1's design against the gateway: one sequential client, 10 warm-up rows, then 750 timed rows.

usage: uv run python scripts/latency.py --profile P [--gateway URL] [--layout L] [--option-orders O]
The board's own sample is private; ours follows its published design (data/splits/latency-v1.json).
"""

import argparse
import json
import time
from collections import defaultdict

import httpx

from scripts.bench import git_revision
from scripts.bench_report import percentile, provenance
from scripts.board import BOARD, MATCHES
from scripts.evaluate import gateway_headers, now, results_dir
from scripts.splits import load_split, rows_for


def time_rows(client: httpx.Client, rows: list[dict], extra: dict) -> list[dict]:
    out = []
    for row in rows:
        body = {"model": "jev-latest", "state": row["state"], "questions": row["questions"], **extra}
        start = time.perf_counter()
        r = client.post("/v1/systemone", json=body)
        ms = (time.perf_counter() - start) * 1000
        out.append({"id": row["id"], "catalog_id": row["meta"]["catalog_id"], "status": r.status_code, "ms": ms})
    return out


def summarize(records: list[dict]) -> dict:
    """Median and p95 over rows that returned an answer; per-benchmark medians only with >= 5 rows (as the board)."""
    ok = [r for r in records if r["status"] == 200]
    by: dict[int, list[float]] = defaultdict(list)
    for r in ok:
        by[r["catalog_id"]].append(r["ms"])
    return {
        "n": len(records),
        "answered": len(ok),
        "median_ms": percentile([r["ms"] for r in ok], 0.5) if ok else None,
        "p95_ms": percentile([r["ms"] for r in ok], 0.95) if ok else None,
        "by_catalog": {c: percentile(ms, 0.5) for c, ms in sorted(by.items()) if len(ms) >= 5},
    }


def main(args) -> None:
    split = load_split("latency-v1")
    rows = rows_for("latency-v1")
    warm, timed = rows[: len(split["warmup"])], rows[len(split["warmup"]) :]
    extra = {k: v for k, v in (("layout", args.layout), ("option_orders", args.option_orders)) if v}
    with httpx.Client(base_url=args.gateway, headers=gateway_headers(), timeout=600) as client:
        health = client.get("/health").json()
        if health["profile"] != args.profile:
            raise SystemExit(f"gateway serves {health['profile']!r}, not {args.profile!r}")
        time_rows(client, warm, extra)
        records = time_rows(client, timed, extra)
    s = summarize(records)
    if s["answered"] == 0:
        raise SystemExit("no timed row returned an answer; nothing to summarize")
    stamp = now()
    out = results_dir(args.profile, f"{stamp}-latency{'-' + '-'.join(extra.values()) if extra else ''}")
    (out / "raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    board = [
        f"| {BOARD[k]['name']} (board, its own sample) | {BOARD[k]['median_ms']:.1f} | n/a |"
        for k in [*MATCHES.get(args.profile, []), "jev"]
    ]
    meta = {"timestamp": stamp, "repo commit": git_revision(), "design": split["meta"]["design"], **extra}
    meta |= {k: health.get(k) for k in ("profile", "hf_revision", "prompt_layout", "option_orders", "vllm_version")}
    table = [
        "| entry | median ms | p95 ms |",
        "|---|---|---|",
        f"| **ours** | {s['median_ms']:.1f} | {s['p95_ms']:.1f} |",
        *board,
    ]
    per = ["| catalog | median ms |", "|---|---|", *(f"| {c} | {m:.1f} |" for c, m in s["by_catalog"].items())]
    body = "\n".join([*table, "", f"Answered {s['answered']} of {s['n']} timed rows.", "", *per])
    (out / "summary.md").write_text(f"# {args.profile} latency (latency-v1 design)\n\n{provenance(meta)}\n{body}\n")
    print(out / "summary.md")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--gateway", default="http://127.0.0.1:9000")
    p.add_argument("--layout")
    p.add_argument("--option-orders")
    return p.parse_args(argv)


if __name__ == "__main__":
    main(parse_args())
