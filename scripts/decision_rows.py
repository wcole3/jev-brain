"""Every labelled source as one decision-row shape, so collect and evaluate never branch on the source."""

import hashlib

from gateway.questions import render_state
from scripts.bench_data import jevbench_request, jevbench_rows


def state_key(state) -> str:
    """Same text after whitespace and case are normalised = same key; used to dedupe across sources."""
    text = " ".join(render_state(state).split()).casefold()
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def jevbench_gold(question: dict, label: str):
    if question["type"] == "noul":
        return label == "yes"
    if question["type"] == "score":
        return int(label)
    return label


def jevbench() -> list[dict]:
    """JevBench gold rows (pinned in bench_data); one question per row."""
    rows = []
    for r in jevbench_rows():
        request, label = jevbench_request(r)
        question = request["questions"]["q"]
        rows.append({
            "id": f"jevbench:{r['id']}",
            "source": "jevbench",
            "family": r["domain"],
            "state": r["state"],
            "questions": {"q": question},
            "gold": {"q": jevbench_gold(question, label)},
            "meta": {"eval_metric": r["eval_metric"], "upstream_source": r["source"]},
        })
    return rows
