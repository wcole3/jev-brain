"""Rounding ties in p(yes) across ToolRet/BRIGHT ranking groups of an Index results.jsonl.

usage: uv run python scripts/ties.py --profile P --run MERGED_DIR [--dry-run]
"""

import argparse
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path

from scripts.bench import git_revision
from scripts.bench_report import provenance
from scripts.evaluate import now, results_dir
from scripts.index_run import last_attempts

DATASETS = ("ToolRet", "BRIGHT")


def read_rows(path: Path) -> Iterable[dict]:
    """The last attempt per run_id of a results.jsonl, without an unflushed crash tail (the harness's rule)."""
    return last_attempts([path]).values()


def tie_stats(results: Iterable[dict], datasets=DATASETS) -> dict[str, dict]:
    """Per dataset: groups, docs, docs sharing p(yes) with a group mate, docs at 0.0 or 1.0."""
    groups = defaultdict(list)
    for r in results:
        if r.get("status") == "ok" and r.get("dataset") in datasets:
            answers = r["response"]["answers"].values()
            groups[(r["dataset"], r["group_id"])] += [a["probabilities"]["yes"] for a in answers]
    stats = {}
    for (dataset, _), yes in groups.items():
        counts = Counter(yes)
        s = stats.setdefault(dataset, {"groups": 0, "docs": 0, "tied_docs": 0, "saturated_docs": 0})
        s["groups"] += 1
        s["docs"] += len(yes)
        s["tied_docs"] += sum(counts[p] > 1 for p in yes)
        s["saturated_docs"] += sum(p in (0.0, 1.0) for p in yes)
    return stats


def markdown(stats: dict[str, dict], meta: dict) -> str:
    lines = ["| dataset | groups | docs | tied | saturated |", "|---|---|---|---|---|"]
    for dataset, s in sorted(stats.items()):
        lines.append(f"| {dataset} | {s['groups']} | {s['docs']} | "
                     f"{s['tied_docs'] / s['docs']:.1%} | {s['saturated_docs'] / s['docs']:.1%} |")
    return f"# Rounding ties in p(yes)\n\n{provenance(meta)}\n" + "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--run", required=True, help="an Index run's merged/ dir")
    ap.add_argument("--dry-run", action="store_true", help="print the summary, write nothing")
    args = ap.parse_args()
    meta = {"timestamp": now(), "repo commit": git_revision(), "profile": args.profile, "run": args.run}
    text = markdown(tie_stats(read_rows(Path(args.run) / "results.jsonl")), meta)
    if args.dry_run:
        print(text)
        return
    out = results_dir(args.profile, f"{meta['timestamp']}-ties") / "summary.md"
    out.write_text(text)
    print(out)


if __name__ == "__main__":
    main()
