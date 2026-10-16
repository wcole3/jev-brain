"""Vision suite results: latency, calibration, status counts, and the result folder (shared by gateway and stock runs).

usage: python3 -m scripts.vision_summary RUN_DIR SUITE_DIR OUT_DIR TITLE   (stdlib only, runs on the vast boxes)
"""

import gzip
import json
import shutil
import statistics
import sys
from collections import Counter
from pathlib import Path

from scripts.bench_report import percentile
from scripts.metrics import ece_of


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def ok_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["status"] == "ok"]


def latency(rows: list[dict]) -> dict | None:
    """Median, mean and p80 of model_request_wall_ms over ok rows; None without any."""
    ms = [r["model_request_wall_ms"] for r in ok_rows(rows)]
    if not ms:
        return None
    return {"median": statistics.median(ms), "mean": statistics.fmean(ms), "p80": percentile(ms, 0.8)}


def calibration(rows: list[dict], expected: dict[str, str]) -> dict:
    """ECE of the top probability against the gold letter, over ok rows with a gold label."""
    confidences, correct = [], []
    for r in ok_rows(rows):
        gold = expected.get(r["run_id"])
        if gold is None:
            continue
        probs = r["response"]["answers"]["answer"]["probabilities"]
        top = max(probs, key=probs.__getitem__)
        confidences.append(probs[top])
        correct.append(top == gold)
    if not confidences:
        return {"ece": None, "accuracy": None, "n": 0}
    return {"ece": ece_of(confidences, correct), "accuracy": sum(correct) / len(correct), "n": len(correct)}


def status_counts(rows: list[dict]) -> dict[str, int]:
    return dict(Counter(r["status"] for r in rows))


def last_per_run(rows: list[dict]) -> list[dict]:
    """The kit appends a retry after an error, so the last row per run_id wins."""
    return list({r["run_id"]: r for r in rows}.values())


def summary_markdown(title: str, summary: dict, scores: dict) -> str:
    lines = [f"# {title}", "", f"Public Vision Index: {scores['public_vision_index']:.2f} (complete: {scores['complete']})", ""]
    lines += ["| benchmark | rows | accuracy |", "|---|---|---|"]
    lines += [f"| {b} | {v['rows']} | {v['accuracy']:.3f} |" for b, v in scores["benchmarks"].items()]
    lat, cal = summary["latency_ms"], summary["calibration"]
    lines += ["", f"Status: {summary['status']}"]
    if lat:
        lines.append(f"Latency ms: median {lat['median']:.0f}, mean {lat['mean']:.0f}, p80 {lat['p80']:.0f}")
    if cal["n"]:
        lines.append(f"Calibration: ECE {cal['ece']:.4f}, accuracy {cal['accuracy']:.3f} over {cal['n']} rows")
    return "\n".join(lines) + "\n"


def write_folder(run_dir: Path, suite_dir: Path, out: Path, title: str) -> dict:
    """results.jsonl.gz, vision-scores.json, summary.json and summary.md in out."""
    out.mkdir(parents=True, exist_ok=True)
    rows = last_per_run(read_jsonl(run_dir / "results.jsonl"))
    expected = {r["id"]: r["expected"]["answer"] for r in read_jsonl(suite_dir / "vision-rows.jsonl")}
    scores = json.loads((run_dir / "vision-scores.json").read_text())
    summary = {"status": status_counts(rows), "latency_ms": latency(rows), "calibration": calibration(rows, expected)}
    with (run_dir / "results.jsonl").open("rb") as src, gzip.open(out / "results.jsonl.gz", "wb") as dst:
        shutil.copyfileobj(src, dst)
    shutil.copy(run_dir / "vision-scores.json", out / "vision-scores.json")
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out / "summary.md").write_text(summary_markdown(title, summary, scores))
    return summary


if __name__ == "__main__":
    run, suite, out, title = sys.argv[1:5]
    write_folder(Path(run), Path(suite), Path(out), title)
