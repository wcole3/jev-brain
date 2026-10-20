import pytest

from gateway.calibration import Calibration
from gateway.layouts import load_layouts
from gateway.questions import render_question
from gateway.schema import Question
from scripts.offline import Arm, chosen_reads, evaluate, keyed, markdown, scored

LAYOUTS = load_layouts()
ROW = {
    "id": "r1", "source": "jevbench", "family": "f", "state": "s",
    "questions": {
        "c": {"type": "choice", "instructions": "pick", "criteria": {"a": None, "b": None, "c": None}},
        "n": {"type": "noul", "instructions": "is it?"},
    },
    "gold": {"c": "b", "n": True},
}
# identity favours shown position 0 (=a); reversed shows c,b,a and favours position 1 (=b) more strongly
REC = {
    "id": "r1", "layout": "decider_chat", "status": "ok",
    "questions": {
        "c": [{"perm": [0, 1, 2], "logprobs": [0.0, -1.0, -5.0]}, {"perm": [2, 1, 0], "logprobs": [-5.0, 0.0, -2.0]}],
        "n": [{"perm": [0, 1], "logprobs": [-2.0, 0.0]}, {"perm": [1, 0], "logprobs": [0.0, -2.0]}],
    },
}


def test_identity_arm_uses_one_order():
    items = scored(REC, ROW, Arm(), LAYOUTS)
    choice = next(i for i in items if i.type == "choice")
    assert choice.gold == 1 and choice.pred == 0 and not choice.correct


def test_reversed_arm_averages_both_orders():
    items = scored(REC, ROW, Arm(orders="identity+reversed"), LAYOUTS)
    choice = next(i for i in items if i.type == "choice")
    assert choice.pred == 1 and choice.probs[1] > choice.probs[0] > choice.probs[2]
    assert sum(choice.probs) == pytest.approx(1.0)


def test_noul_gold_and_temperature():
    cold = next(i for i in scored(REC, ROW, Arm(), LAYOUTS) if i.type == "noul")
    warm = next(i for i in scored(REC, ROW, Arm(calibration=Calibration({"choice": 1, "score": 1, "noul": 4.0})), LAYOUTS)
                if i.type == "noul")
    assert cold.gold == 1 and cold.correct and warm.probs[1] < cold.probs[1]


def test_yes_offset_reaches_offline_arms():
    base = next(i for i in scored(REC, ROW, Arm(), LAYOUTS) if i.type == "noul")
    cal = Calibration({"choice": 1, "score": 1, "noul": 1}, b=2.0)
    pushed = next(i for i in scored(REC, ROW, Arm(calibration=cal), LAYOUTS) if i.type == "noul")
    assert pushed.probs[1] > base.probs[1]


def test_unsupported_and_other_layouts_are_not_scored():
    assert scored(REC | {"status": "unsupported"}, ROW, Arm(), LAYOUTS) == []
    assert scored(REC, ROW, Arm(layout="header"), LAYOUTS) == []


def test_evaluate_reports_status_counts_and_renders():
    refused = {"id": "r2", "layout": "decider_chat", "status": "unsupported"}
    report = evaluate([REC, refused], {"r1": ROW, "r2": ROW | {"id": "r2"}}, Arm())
    assert report["status"] == {"ok": 1, "unsupported": 1}
    assert report["overall"]["n"] == 2 and set(report["by_type"]) == {"choice", "noul"}
    assert "| choice |" in markdown(report)


def test_all_rows_accuracy_counts_refused_questions_as_wrong():
    refused = {"id": "r2", "layout": "decider_chat", "status": "unsupported"}
    other_layout = refused | {"layout": "header"}
    rows = {"r1": ROW, "r2": ROW | {"id": "r2", "gold": {"c": "a", "n": None}}}
    report = evaluate([REC, refused, other_layout], rows, Arm())
    assert report["overall"]["accuracy"] == 0.5  # identity misses the choice, gets the noul
    assert report["all_rows"] == {"n": 3, "refused": 1, "accuracy": pytest.approx(1 / 3)}
    assert "All rows (refused questions count as wrong): n 3, refused 1, accuracy 0.333" in markdown(report)


def test_arm_refuses_uncollected_orders():
    with pytest.raises(ValueError, match="r1/c: arm cyclic:3 needs 3 orders, collected 1"):
        scored(REC, ROW, Arm(orders="cyclic:3"), LAYOUTS)


def test_chosen_reads_picks_the_arm_orders_and_refuses_missing_ones():
    q = render_question(Question(**ROW["questions"]["c"]), LAYOUTS["decider_chat"])
    assert chosen_reads(q, REC["questions"]["c"], "identity") == [([0.0, -1.0, -5.0], [0, 1, 2])]
    assert len(chosen_reads(q, REC["questions"]["c"], "identity+reversed")) == 2
    with pytest.raises(ValueError, match="arm cyclic:3 needs 3 orders, collected 1"):
        chosen_reads(q, REC["questions"]["c"], "cyclic:3")


def test_chosen_reads_top_p_adds_reversed_under_tau():
    q = render_question(Question(**ROW["questions"]["c"]), LAYOUTS["decider_chat"])
    reads = REC["questions"]["c"]
    assert len(chosen_reads(q, reads, "top_p:0.9+reversed", 1.0)) == 2  # identity top prob ~0.72
    assert len(chosen_reads(q, reads, "top_p:0.5+reversed", 1.0)) == 1
    assert len(chosen_reads(q, reads, "top_p:0.9+reversed", 0.1)) == 1  # sharp at T = 0.1


def test_chosen_reads_gated_without_gate_T_raises():
    q = render_question(Question(**ROW["questions"]["c"]), LAYOUTS["decider_chat"])
    with pytest.raises(ValueError, match="gate_T"):
        chosen_reads(q, REC["questions"]["c"], "top_p:0.9+reversed")


def test_keyed_maps_row_and_question_to_scored():
    got = keyed([REC], {"r1": ROW}, Arm(), LAYOUTS)
    assert set(got) == {("r1", "c"), ("r1", "n")}
    assert got[("r1", "c")].type == "choice" and got[("r1", "n")].type == "noul"


def test_keyed_skips_other_layouts_and_refusals():
    other = REC | {"layout": "header"}
    refused = REC | {"id": "r2", "status": "unsupported"}
    assert keyed([other, refused], {"r1": ROW, "r2": ROW}, Arm(), LAYOUTS) == {}
