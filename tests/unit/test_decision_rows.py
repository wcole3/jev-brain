import json

from scripts import decision_rows

JEV = [
    {"id": "panoramic:invoices:1", "source": "panoramic", "domain": "invoices", "type": "noul", "state": "s1",
     "question": {"type": "noul", "instructions": "Total matches?"}, "label": "yes", "eval_metric": "exact"},
    {"id": "banking:3", "source": "banking77", "domain": "banking", "type": "choice", "state": "s2",
     "question": {"type": "choice", "instructions": "Intent?", "options": {"a": "A", "b": "B"}}, "label": "b",
     "eval_metric": "exact"},
    {"id": "typed_decisions:cs:9", "source": "typed_decisions", "domain": "customer_service", "type": "score",
     "state": "s3", "question": {"type": "score", "instructions": "Urgency?", "levels": ["lo", "mid", "hi"]},
     "label": "2", "eval_metric": "ordinal"},
]


def test_jevbench_rows_become_decision_rows(monkeypatch):
    monkeypatch.setattr(decision_rows, "jevbench_rows", lambda: JEV)
    rows = decision_rows.jevbench()
    assert [r["gold"]["q"] for r in rows] == [True, "b", 2]
    assert rows[0]["id"] == "jevbench:panoramic:invoices:1"
    assert rows[0]["source"] == "jevbench" and rows[0]["family"] == "invoices"
    assert rows[1]["questions"]["q"]["criteria"] == {"a": "A", "b": "B"}
    assert rows[2]["meta"] == {"eval_metric": "ordinal", "upstream_source": "typed_decisions"}


def test_state_key_ignores_whitespace_and_case():
    assert decision_rows.state_key("Hello  World\n") == decision_rows.state_key("hello world")
    assert decision_rows.state_key({"a": 1}) != decision_rows.state_key({"a": 2})


def rec(primitive, candidates, gold, source=None, **extra):
    return {
        "row_id": "r1", "task_id": f"dom/fam/{primitive}/task", "primitive": primitive,
        "reasoning_required": extra.pop("reasoning", False), "instruction": "Decide.",
        "state_json": json.dumps({"text": "hello"}), "candidates_json": json.dumps(candidates),
        "gold_candidate_id": gold, "source_json": json.dumps(source or {"source": {"dataset": "x/y"}}),
    }


def cand(cid, label, ordinal=None, description=None):
    return {"id": cid, "label": label, "description": description, "ordinal_value": ordinal}


def test_filters_drop_synthetic_unlicensed_and_index_sources():
    keep = decision_rows.keep_decisionbench
    assert keep(rec("candidate_selection", [], "c0"))
    assert not keep(rec("candidate_selection", [], "c0", {"kind": "synthetic_from_public_decision_contract"}))
    assert not keep(rec("candidate_selection", [], "c0", {"license": "No license declared"}))
    assert not keep(rec("candidate_selection", [], "c0", {"source": {"dataset": "PolyAI/banking77"}}))


def test_choice_row():
    row = decision_rows.decisionbench_row(
        rec("candidate_selection", [cand("c0", "Billing"), cand("c1", "Tech", description="Bugs")], "c1"))
    assert row["questions"]["q"] == {"type": "choice", "instructions": "Decide.",
                                     "criteria": {"c0": "Billing", "c1": "Tech: Bugs"}}
    assert row["gold"]["q"] == "c1" and row["id"] == "decisionbench:r1" and row["family"] == "dom/fam/candidate_selection/task"


def test_unambiguous_binary_becomes_noul():
    row = decision_rows.decisionbench_row(rec("binary_classification", [cand("c0", "No"), cand("c1", "Yes")], "c1"))
    assert row["questions"]["q"] == {"type": "noul", "instructions": "Decide."} and row["gold"]["q"] is True


def test_ambiguous_binary_stays_a_two_option_choice():
    row = decision_rows.decisionbench_row(
        rec("binary_classification", [cand("c0", "Reject"), cand("c1", "Approve")], "c0"))
    assert row["questions"]["q"]["type"] == "choice" and row["gold"]["q"] == "c0"


def test_ordinal_levels_are_sorted_by_value():
    cands = [cand("c0", "Low", 1.0), cand("c1", "High", 2.0), cand("c2", "None", 0.0)]
    row = decision_rows.decisionbench_row(rec("ordinal_scoring", cands, "c1"))
    assert row["questions"]["q"]["criteria"] == ["None", "Low", "High"] and row["gold"]["q"] == 2


def test_reasoning_rows_are_flagged():
    row = decision_rows.decisionbench_row(
        rec("candidate_selection", [cand("c0", "A"), cand("c1", "B")], "c0", reasoning=True))
    assert row["meta"]["reasoning"] is True
