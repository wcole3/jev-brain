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
