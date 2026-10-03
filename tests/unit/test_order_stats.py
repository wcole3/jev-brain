import pytest

from gateway.calibration import UNCALIBRATED
from gateway.layouts import load_layouts
from scripts.collect import all_orders
from scripts.metrics import Scored
from scripts.order_stats import (
    disagreement_auroc,
    flip_rate,
    in_prior_slice,
    noul_lean,
    position_histogram,
    pride_keyed,
    pride_prior,
    reversed_keyed,
)

LAYOUTS = load_layouts()


def s(gold, probs, t="choice"):
    return Scored("index", "f", t, gold, probs)


def test_flip_rate_counts_changed_top_answers():
    ident = {("r1", "q"): s(0, [0.6, 0.4]), ("r2", "q"): s(0, [0.6, 0.4])}
    rev = {("r1", "q"): s(0, [0.3, 0.7]), ("r2", "q"): s(0, [0.9, 0.1])}
    assert flip_rate(ident, rev) == 0.5


def test_position_histogram_by_bucket():
    h = position_histogram([s(1, [0.7, 0.3]), s(0, [0.8, 0.2]), s(2, [0.1, 0.1, 0.8])])
    assert h["2"] == {"chosen": [2, 0], "gold": [1, 1]}
    assert h["3-5"]["chosen"] == [0, 0, 1]


def test_auroc_is_one_when_disagreement_marks_every_error():
    ident = {("a", "q"): s(0, [0.9, 0.1]), ("b", "q"): s(0, [0.9, 0.1])}
    rev = {("a", "q"): s(0, [0.9, 0.1]), ("b", "q"): s(0, [0.1, 0.9])}
    avg = {("a", "q"): s(0, [0.9, 0.1]), ("b", "q"): s(0, [0.4, 0.6])}
    assert disagreement_auroc(ident, rev, avg) == 1.0
    assert disagreement_auroc(ident, ident, ident) is None


def test_noul_lean():
    ident = {("a", "n"): s(1, [0.2, 0.8], "noul")}
    rev = {("a", "n"): s(1, [0.4, 0.6], "noul")}
    assert noul_lean(ident, rev) == {"n": 1, "p_yes_identity": 0.8, "p_yes_reversed": 0.6, "gold_yes": 1.0}


def test_prior_slice_is_stable_and_about_five_percent():
    share = sum(in_prior_slice(f"row{i}") for i in range(4000)) / 4000
    assert 0.03 < share < 0.07 and in_prior_slice("row7") == in_prior_slice("row7")


def first_id(in_slice: bool) -> str:
    return next(f"row{i}" for i in range(1000) if in_prior_slice(f"row{i}") == in_slice)


def two_option_row(row_id: str, logprobs: dict) -> tuple[dict, dict]:
    """A two-option choice row and a record holding every collected order, with logprobs per perm."""
    row = {"id": row_id, "source": "index", "family": "f", "state": "s", "gold": {"c": "a"},
           "questions": {"c": {"type": "choice", "instructions": "pick", "criteria": {"a": None, "b": None}}}}
    reads = [{"perm": perm, "logprobs": logprobs[tuple(perm)]} for perm in all_orders(2)]
    return row, {"id": row_id, "layout": "decider_chat", "status": "ok", "questions": {"c": reads}}


def test_pride_divides_the_slice_prior_out_of_identity_reads():
    slice_row, slice_rec = two_option_row(first_id(True), {(0, 1): [0.0, -1.0], (1, 0): [0.0, -1.0]})
    plain_row, plain_rec = two_option_row(first_id(False), {(0, 1): [0.0, 0.0], (1, 0): [0.0, 0.0]})
    rows = {slice_row["id"]: slice_row, plain_row["id"]: plain_row}
    recs = [slice_rec, plain_rec]

    prior = pride_prior(recs, rows, "decider_chat", UNCALIBRATED, LAYOUTS, min_questions=1)
    p0 = 1 / (1 + 2.718281828459045**-1)
    assert prior == {2: pytest.approx([p0, 1 - p0])}
    assert pride_prior(recs, rows, "decider_chat", UNCALIBRATED, LAYOUTS) == {}

    keyed = pride_keyed(recs, rows, "decider_chat", UNCALIBRATED, prior, LAYOUTS)
    assert list(keyed) == [(plain_row["id"], "c")]
    assert keyed[(plain_row["id"], "c")].probs == pytest.approx([1 - p0, p0])
    assert pride_keyed(recs, rows, "decider_chat", UNCALIBRATED, {}, LAYOUTS)[(plain_row["id"], "c")].probs == [0.5, 0.5]


def test_reversed_keyed_maps_the_reversed_read_back_to_caller_order():
    row, rec = two_option_row("r1", {(0, 1): [0.0, -5.0], (1, 0): [0.0, -5.0]})
    out = reversed_keyed([rec], {"r1": row}, "decider_chat", UNCALIBRATED, LAYOUTS)
    assert out[("r1", "c")].probs[1] > 0.9
