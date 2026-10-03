import json

from scripts.ties import read_rows, tie_stats


def row(group, probs, dataset="ToolRet", status="ok", run_id=None):
    answers = {f"doc_{i}": {"type": "choice", "probabilities": {"no": 1 - p, "yes": p}} for i, p in enumerate(probs)}
    return {"run_id": run_id or f"{group}-{probs}", "dataset": dataset, "group_id": group, "status": status,
            "response": {"answers": answers}}


def test_tie_stats_counts_tied_and_saturated_docs_per_group():
    rows = [row("g1", [1.0, 1.0, 0.5]), row("g1", [0.25]), row("g2", [0.0, 0.3]), row("g3", [0.9], status="error"),
            row("g4", [0.5, 0.5], dataset="MMLU")]
    got = tie_stats(rows)
    assert got["ToolRet"] == {"groups": 2, "docs": 6, "tied_docs": 2, "saturated_docs": 3}
    assert "MMLU" not in got


def test_a_tie_counts_across_rows_of_one_group():
    got = tie_stats([row("g1", [0.5, 0.2]), row("g1", [0.5, 0.7]), row("g2", [0.2])])
    assert got["ToolRet"] == {"groups": 2, "docs": 5, "tied_docs": 2, "saturated_docs": 0}


def test_read_rows_keeps_the_last_attempt_and_drops_a_crash_tail(tmp_path):
    first, retry = row("g1", [0.5], status="error", run_id="r1"), row("g1", [0.5], run_id="r1")
    lines = [json.dumps(first), json.dumps(retry), json.dumps(row("g1", [0.4], run_id="r2"))]
    path = tmp_path / "results.jsonl"
    path.write_text("\n".join(lines) + '\n{"run_id": "r3", "dat')
    got = list(read_rows(path))
    assert [r["run_id"] for r in got] == ["r1", "r2"] and got[0]["status"] == "ok"
    assert tie_stats(got)["ToolRet"]["tied_docs"] == 0
