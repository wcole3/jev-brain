import math

import pytest

from gateway.calibration import UNCALIBRATED
from gateway.layouts import load_layouts
from scripts.collect import all_orders
from scripts.metrics import Scored
from scripts.order_stats import (
    disagreement_auroc,
    flip_rate,
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
    assert h["3-5"]["chosen"] == [0, 0, 1, 0, 0]


def test_position_histogram_width_is_fixed_whatever_the_item_order():
    k3, k5 = s(0, [0.8, 0.1, 0.1]), s(4, [0.0, 0.0, 0.0, 0.1, 0.9])
    for items in ([k3, k5], [k5, k3]):
        h = position_histogram(items)["3-5"]
        assert h == {"chosen": [1, 0, 0, 0, 1], "gold": [1, 0, 0, 0, 1]}


def test_position_histogram_truncates_the_27_plus_bucket():
    probs = [0.0] * 30
    probs[28] = 1.0
    h = position_histogram([s(28, probs), s(1, [0.0, 1.0] + [0.0] * 28)])["27+"]
    assert len(h["chosen"]) == 27 and h["chosen"][1] == 1 and sum(h["chosen"]) == 1
    assert h["gold"][1] == 1 and sum(h["gold"]) == 1


def test_flip_rate_ignores_noul():
    ident = {("a", "n"): s(1, [0.2, 0.8], "noul"), ("a", "q"): s(0, [0.6, 0.4])}
    rev = {("a", "n"): s(1, [0.8, 0.2], "noul"), ("a", "q"): s(0, [0.7, 0.3])}
    assert flip_rate(ident, rev) == 0.0


def test_auroc_counts_equal_disagreement_as_half():
    ident = {("a", "q"): s(0, [0.9, 0.1]), ("b", "q"): s(0, [0.9, 0.1])}
    rev = {("a", "q"): s(0, [0.5, 0.5]), ("b", "q"): s(0, [0.5, 0.5])}
    avg = {("a", "q"): s(0, [0.9, 0.1]), ("b", "q"): s(0, [0.4, 0.6])}
    assert disagreement_auroc(ident, rev, avg) == 0.5


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


def two_option_row(row_id: str, logprobs: dict) -> tuple[dict, dict]:
    """A two-option choice row and a record holding every collected order, with logprobs per perm."""
    row = {"id": row_id, "source": "index", "family": "f", "state": "s", "gold": {"c": "a"},
           "questions": {"c": {"type": "choice", "instructions": "pick", "criteria": {"a": None, "b": None}}}}
    reads = [{"perm": perm, "logprobs": logprobs[tuple(perm)]} for perm in all_orders(2)]
    return row, {"id": row_id, "layout": "decider_chat", "status": "ok", "questions": {"c": reads}}


def test_pride_divides_the_calib_prior_out_of_identity_reads():
    calib_row, calib_rec = two_option_row("c1", {(0, 1): [0.0, -1.0], (1, 0): [0.0, -1.0]})
    plain_row, plain_rec = two_option_row("r1", {(0, 1): [0.0, 0.0], (1, 0): [0.0, 0.0]})

    prior = pride_prior([calib_rec], {"c1": calib_row}, "decider_chat", UNCALIBRATED, LAYOUTS, min_questions=1)
    p0 = 1 / (1 + 2.718281828459045**-1)
    assert prior == {2: pytest.approx([p0, 1 - p0])}
    assert pride_prior([calib_rec], {"c1": calib_row}, "decider_chat", UNCALIBRATED, LAYOUTS) == {}

    keyed = pride_keyed([plain_rec], {"r1": plain_row}, "decider_chat", UNCALIBRATED, prior, LAYOUTS)
    assert list(keyed) == [("r1", "c")]
    assert keyed[("r1", "c")].probs == pytest.approx([1 - p0, p0])
    assert pride_keyed([plain_rec], {"r1": plain_row}, "decider_chat", UNCALIBRATED, {}, LAYOUTS)[("r1", "c")].probs == [
        0.5, 0.5]


def test_reversed_keyed_maps_the_reversed_read_back_to_caller_order():
    row, rec = two_option_row("r1", {(0, 1): [0.0, -5.0], (1, 0): [0.0, -5.0]})
    out = reversed_keyed([rec], {"r1": row}, "decider_chat", UNCALIBRATED, LAYOUTS)
    assert out[("r1", "c")].probs == pytest.approx([1 / (1 + math.exp(5)), 1 / (1 + math.exp(-5))])
