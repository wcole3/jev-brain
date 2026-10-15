"""Answer agreement between two Index runs: top-answer flips and |dp| per question.

usage: uv run python scripts/index_agreement.py BEFORE/merged/results.jsonl AFTER/merged/results.jsonl
Exits 1 when a flip has a before top-two gap > 0.10 (the repo's stability rule).
"""

import argparse
import gzip
import json
import statistics
from collections import Counter

GAP_LIMIT = 0.10


def load(path: str) -> dict[str, dict]:
    """Answers per run_id of the ok rows; the last line of a run_id is the one that counts."""
    opener = gzip.open if path.endswith(".gz") else open
    latest = {}
    with opener(path, "rt", encoding="utf-8") as f:
        for text in f:
            if text.strip():
                row = json.loads(text)
                latest[row["run_id"]] = row
    ok = (row for row in latest.values() if row["status"] == "ok")
    return {row["run_id"]: _response(row)["answers"] for row in ok}


def _response(row: dict) -> dict:
    response = row["response"]
    return json.loads(response) if isinstance(response, str) else response


def probabilities(answer: dict) -> dict[str, float]:
    """Option probabilities; a noul answer as {true, false}."""
    if "probabilities" in answer:
        return answer["probabilities"]
    if "noul" in answer:
        return {"true": answer["noul"], "false": 1 - answer["noul"]}
    return {}


def top_two_gap(p: dict[str, float]) -> float:
    top = sorted(p.values(), reverse=True)
    return top[0] - (top[1] if len(top) > 1 else 0.0)


def agreement(before: dict, after: dict) -> dict:
    shared = sorted(before.keys() & after.keys())
    by_type: Counter[str] = Counter()
    deltas, flips, flips_over_gap = [], 0, 0
    for run_id in shared:
        for question_id, answer in before[run_id].items():
            p, q = probabilities(answer), probabilities(after[run_id].get(question_id, {}))
            if not p or p.keys() != q.keys():
                continue
            by_type[answer["type"]] += 1
            deltas.append(max(abs(p[k] - q[k]) for k in p))
            if max(p, key=p.get) != max(q, key=q.get):
                flips += 1
                flips_over_gap += top_two_gap(p) > GAP_LIMIT
    return {
        "rows": len(shared),
        "questions": len(deltas),
        "flips": flips,
        "flips_over_gap": flips_over_gap,
        "max_dp": max(deltas, default=0.0),
        "median_dp": statistics.median(deltas) if deltas else 0.0,
        "by_type": dict(by_type),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("before")
    parser.add_argument("after")
    args = parser.parse_args(argv)
    result = agreement(load(args.before), load(args.after))
    print(f"rows compared: {result['rows']}")
    print(f"questions compared: {result['questions']} {result['by_type']}")
    print(f"top-answer flips: {result['flips']}")
    print(f"flips with before top-two gap > {GAP_LIMIT:.2f}: {result['flips_over_gap']}")
    print(f"|dp|: median {result['median_dp']:.4f}, max {result['max_dp']:.4f}")
    return 1 if result["flips_over_gap"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
