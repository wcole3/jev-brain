"""Compare the JevBench rows of two bench result folders: accuracy, answer flips, probability drift."""

import argparse
import json
from pathlib import Path

from scripts.bench_report import ece


def load_rows(folder: Path) -> dict[str, dict]:
    """JevBench rows of a run keyed by id; rows without an id (old runs) are dropped."""
    records = [json.loads(line) for line in (folder / "raw.jsonl").read_text().splitlines() if line]
    return {r["id"]: r for r in records if r.get("test") == "jevbench" and "id" in r}


def top_two_gap(probabilities: dict[str, float]) -> float:
    top = sorted(probabilities.values(), reverse=True)
    return top[0] - (top[1] if len(top) > 1 else 0.0)


def accuracy(rows: list[dict]) -> float:
    return 100 * sum(r["correct"] for r in rows) / len(rows)


def flip_kind(base: dict, cand: dict) -> str:
    if base["correct"] and not cand["correct"]:
        return "right→wrong"
    return "wrong→right" if cand["correct"] else "wrong→wrong"


def flips(pairs: list[tuple[dict, dict]]) -> list[tuple[dict, dict]]:
    return [(b, c) for b, c in pairs if b["pred"] != c["pred"]]


def drift(pairs: list[tuple[dict, dict]]) -> tuple[float, float]:
    """(max, mean) |Δp| over the probability keys both runs report."""
    deltas = [
        abs(b["probabilities"][k] - c["probabilities"][k])
        for b, c in pairs
        for k in b["probabilities"]
        if k in c["probabilities"]
    ]
    return max(deltas), sum(deltas) / len(deltas)


def flip_table(title: str, flipped: list[tuple[dict, dict]]) -> list[str]:
    lines = [f"### {title}", "", "| id | gold | baseline | candidate | baseline gap |", "|---|---|---|---|---|"]
    for b, c in flipped:
        lines.append(f"| {b['id']} | {b['gold']} | {b['pred']} | {c['pred']} | {top_two_gap(b['probabilities']):.3f} |")
    return lines + [""]


def report(baseline: dict[str, dict], candidate: dict[str, dict]) -> str:
    shared = sorted(baseline.keys() & candidate.keys())
    if not shared:
        return "# Run comparison\n\nNo rows in common (old runs without `id`?).\n"
    pairs = [(baseline[i], candidate[i]) for i in shared]
    base_rows, cand_rows = [b for b, _ in pairs], [c for _, c in pairs]
    changed = flips(pairs)
    kinds = [flip_kind(b, c) for b, c in changed]
    out = [
        "# Run comparison",
        "",
        f"- rows in common: {len(shared)}",
        (
            f"- accuracy baseline: {accuracy(base_rows):.1f}%, candidate: {accuracy(cand_rows):.1f}%, "
            f"delta: {accuracy(cand_rows) - accuracy(base_rows):+.1f} points"
        ),
        (
            f"- answer flips: {len(changed)} ({100 * len(changed) / len(shared):.1f}%): "
            + ", ".join(f"{k} {kinds.count(k)}" for k in ("wrong→right", "right→wrong", "wrong→wrong"))
        ),
        "",
    ]
    both = [(b, c) for b, c in pairs if "probabilities" in b and "probabilities" in c]
    if not both:
        return "\n".join(out + ["Probability sections skipped: no rows carry `probabilities` in both runs.", ""])
    biggest, mean = drift(both)
    out += [
        f"- rows with probabilities in both: {len(both)}",
        f"- max |Δp|: {biggest:.4f}, mean |Δp|: {mean:.4f}",
        f"- ECE baseline: {ece([b for b, _ in both]):.4f}, candidate: {ece([c for _, c in both]):.4f}",
        "",
    ]
    ranked = sorted((p for p in flips(both)), key=lambda p: top_two_gap(p[0]["probabilities"]))
    out += flip_table("Flips with the smallest baseline top-two gap", ranked[:10])
    out += flip_table("Flips with the largest baseline top-two gap (large gap = bug signal)", ranked[::-1][:5])
    return "\n".join(out)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    text = report(load_rows(args.baseline), load_rows(args.candidate))
    if args.out:
        args.out.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
