from scripts.ties import tie_stats


def row(group, probs, dataset="ToolRet", status="ok"):
    answers = {f"doc_{i}": {"type": "choice", "probabilities": {"no": 1 - p, "yes": p}} for i, p in enumerate(probs)}
    return {"dataset": dataset, "group_id": group, "status": status, "response": {"answers": answers}}


def test_tie_stats_counts_tied_and_saturated_docs_per_group():
    rows = [row("g1", [1.0, 1.0, 0.5]), row("g1", [0.25]), row("g2", [0.0, 0.3]), row("g3", [0.9], status="error"),
            row("g4", [0.5, 0.5], dataset="MMLU")]
    got = tie_stats(rows)
    assert got["ToolRet"] == {"groups": 2, "docs": 6, "tied_docs": 2, "saturated_docs": 3}
    assert "MMLU" not in got
