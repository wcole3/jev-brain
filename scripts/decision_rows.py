"""Every labelled source as one decision-row shape, so collect and evaluate never branch on the source."""

import gzip
import hashlib
import json
from pathlib import Path

from huggingface_hub import hf_hub_download

from gateway.questions import render_state
from gateway.schema import MAX_LEVELS
from scripts.bench_data import jevbench_request, jevbench_rows
from scripts.index_suite import EXPORT

DECISIONBENCH_REPO = "Hanno-Labs/decision-bench"
DECISIONBENCH_SHA = "071b7b2d2e1504c89e1e5a811a3f82e1bfe3aedb"
DECISIONBENCH_FILE = "data/eval-00000-of-00001.parquet"
DECISIONBENCH_SHA256 = "d9dd5be8e0944a7ceadfcac6cf8f9d17aab256093acff23c6de6a037ad6e55f6"  # confirmed in Task 5 Step 6
DROPPED_LICENCES = {"No license declared", "MIT with additional rider", "Functional Source License 1.1"}
INDEX_SOURCES = {"PolyAI/banking77", "clinc/clinc_oos", "tasksource/esci"}  # also Decision Index benchmarks


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


def keep_decisionbench(rec: dict) -> bool:
    """Public-gold rows only: no rows synthesised by Qwen3.8-27B-NVFP4, no unclear licences, no Index sources."""
    source = json.loads(rec["source_json"])
    upstream = source.get("source")
    dataset = upstream.get("dataset") if isinstance(upstream, dict) else None
    return "kind" not in source and source.get("license") not in DROPPED_LICENCES and dataset not in INDEX_SOURCES


def candidate_text(c: dict) -> str:
    return c["label"] if c.get("description") in (None, "") else f"{c['label']}: {c['description']}"


def binary_ids(cands: list[dict]) -> tuple[str, str] | None:
    """(false id, true id) when the two candidates clearly mean no/yes (DecisionBench's public_hf rule)."""
    by_id = {c["id"].casefold(): c["id"] for c in cands}
    for no, yes in (("false", "true"), ("label-0", "label-1")):
        if set(by_id) == {no, yes}:
            return by_id[no], by_id[yes]
    by_label = {c["label"].strip().casefold(): c["id"] for c in cands}
    no, yes = by_label.get("no") or by_label.get("false"), by_label.get("yes") or by_label.get("true")
    return (no, yes) if no and yes and no != yes else None


def decisionbench_question(rec: dict, cands: list[dict]) -> tuple[dict, object]:
    instructions, gold = rec["instruction"], rec["gold_candidate_id"]
    if rec["primitive"] == "binary_classification" and (ids := binary_ids(cands)):
        return {"type": "noul", "instructions": instructions}, gold == ids[1]
    if rec["primitive"] == "ordinal_scoring" and 2 <= len(cands) <= MAX_LEVELS:
        ordered = sorted(cands, key=lambda c: float(c["ordinal_value"] or 0.0))
        levels = [candidate_text(c) for c in ordered]
        return {"type": "score", "instructions": instructions, "criteria": levels}, [c["id"] for c in ordered].index(gold)
    criteria = {c["id"]: candidate_text(c) for c in cands}
    return {"type": "choice", "instructions": instructions, "criteria": criteria}, gold


def decisionbench_row(rec: dict) -> dict | None:
    if not rec.get("gold_candidate_id"):
        return None
    question, gold = decisionbench_question(rec, json.loads(rec["candidates_json"]))
    upstream = json.loads(rec["source_json"]).get("source")
    return {
        "id": f"decisionbench:{rec['row_id']}",
        "source": "decisionbench",
        "family": rec["task_id"],
        "state": json.loads(rec["state_json"]),
        "questions": {"q": question},
        "gold": {"q": gold},
        "meta": {
            "primitive": rec["primitive"],
            "reasoning": bool(rec["reasoning_required"]),
            "dataset": upstream.get("dataset") if isinstance(upstream, dict) else None,
        },
    }


def decisionbench() -> list[dict]:
    """The filtered rows at the pinned revision; the parquet is cached by huggingface_hub and hash-checked."""
    import pyarrow.parquet as pq  # dev-only dependency, only needed here

    path = hf_hub_download(DECISIONBENCH_REPO, DECISIONBENCH_FILE, repo_type="dataset", revision=DECISIONBENCH_SHA)
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != DECISIONBENCH_SHA256:
        raise SystemExit(f"DecisionBench parquet sha256 {digest} != pinned {DECISIONBENCH_SHA256}")
    records = pq.read_table(path).to_pylist()
    return [row for rec in records if keep_decisionbench(rec) and (row := decisionbench_row(rec))]


def index_gold(question: dict, expected):
    """Single gold answers only: a choice key in the criteria, or yes/no. Rankings and multi-answers are None."""
    if question["type"] == "noul":
        return {"yes": True, "no": False, "true": True, "false": False}.get(str(expected).casefold())
    if question["type"] == "choice" and isinstance(expected, str) and expected in (question.get("criteria") or {}):
        return expected
    return None


def index_row(raw: dict) -> dict:
    e, questions = raw["_evaluation"], raw["questions"]
    expected = raw.get("expected") or {}
    return {
        "id": e["run_id"],
        "source": "index",
        "family": e["dataset"],
        "state": raw["state"],
        "questions": questions,
        "gold": {k: index_gold(q, expected.get(k)) for k, q in questions.items()},
        "meta": {
            "catalog_id": e["catalog_id"],
            "group_id": e["group_id"],
            "proxy_tokens": e.get("proxy_tokens"),
            "payload_chars": len(json.dumps({"state": raw["state"], "questions": questions}, ensure_ascii=False)),
        },
    }


def read_export(path=EXPORT):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def index_rows(ids: set[str] | None = None, path=EXPORT) -> list[dict]:
    return [index_row(raw) for raw in read_export(path) if ids is None or raw["_evaluation"]["run_id"] in ids]


def index_meta(path=EXPORT) -> list[dict]:
    """Every Index row without its text (the full export is GBs), plus the state key for dedupe."""
    rows = []
    for raw in read_export(path):
        row = index_row(raw)
        key = state_key(row.pop("state"))
        del row["questions"]
        rows.append(row | {"state_key": key})
    return rows
