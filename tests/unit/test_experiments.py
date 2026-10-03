import random

from gateway.layouts import load_layouts
from scripts import calibrate, metrics
from scripts import fit as fits
from scripts.experiments import compare, fit_arm, is_long, length_bucket, option_bucket, paired
from scripts.metrics import Scored
from scripts.offline import questions
from tests.unit.test_offline import REC, ROW

LAYOUTS = load_layouts()


def s(gold, probs, t="choice", source="index", family="f"):
    return Scored(source, family, t, gold, probs)


def test_buckets():
    assert [option_bucket(k) for k in (2, 3, 5, 6, 26, 27)] == ["2", "3-5", "3-5", "6-26", "6-26", "27+"]
    assert [length_bucket(n) for n in (10, 511, 512, 2047, 2048, 8191, 8192)] == [
        "<512", "<512", "512-2k", "512-2k", "2k-8k", "2k-8k", ">8k"]


def test_long_slice():
    assert is_long("index", "ContractNLI", 100) and is_long("jevbench", "invoices", 100)
    assert is_long("decisionbench", "x", 2001) and not is_long("decisionbench", "x", 2000)
    assert not is_long("index", "MMLU", 50_000)


def test_paired_uses_shared_keys_in_order_and_keep_filter():
    a = {("r1", "q"): s(0, [0.9, 0.1]), ("r2", "q"): s(0, [0.4, 0.6])}
    b = {("r2", "q"): s(0, [0.7, 0.3]), ("r3", "q"): s(0, [0.5, 0.5])}
    xa, xb = paired(a, b)
    assert len(xa) == len(xb) == 1 and xa[0].probs == [0.4, 0.6] and xb[0].probs == [0.7, 0.3]
    assert paired(a, b, keep=lambda key, item: key[0] != "r2") == ([], [])


def test_compare_reports_b_minus_a():
    a = {(f"r{i}", "q"): s(0, [0.4, 0.6]) for i in range(40)}
    b = {(f"r{i}", "q"): s(0, [0.8, 0.2]) for i in range(40)}
    got = compare(a, b)
    assert got["n"] == 40 and got["accuracy"][0] == 1.0 and got["nll"][0] < 0


def test_compare_matches_fit_bootstrap_diff_exactly():
    rng = random.Random(1)
    a, b = {}, {}
    for i in range(60):
        k, gold = rng.choice([2, 3, 7]), rng.randrange(2)
        for arm in (a, b):
            raw = [rng.random() for _ in range(k)]
            arm[(f"r{i}", "q")] = s(gold, [x / sum(raw) for x in raw], t="noul" if k == 2 and i % 2 else "choice")
    xa, xb = paired(a, b)
    got = compare(a, b)
    assert got["accuracy"] == fits.bootstrap_diff(xa, xb, metrics.accuracy)
    assert got["ece"] == fits.bootstrap_diff(xa, xb, metrics.ece)
    assert got["nll"] == fits.bootstrap_diff(xa, xb, metrics.nll)


def test_compare_of_nothing_is_none():
    assert compare({}, {}) == {"n": 0, "accuracy": None, "ece": None, "nll": None}


def calib_record(i: int) -> tuple[dict, dict]:
    return ROW | {"id": f"r{i}"}, REC | {"id": f"r{i}", "stamp": {}}


def test_fit_arm_fits_each_type_on_calib_without_the_gate(monkeypatch):
    monkeypatch.setattr(calibrate, "MIN_QUESTIONS", 1)
    rows, recs = zip(*(calib_record(i) for i in range(3)), strict=True)
    cal = fit_arm(list(recs), {r["id"]: r for r in rows}, "decider_chat", "identity+reversed")
    assert cal.orders == "identity+reversed" and cal.source == "calib fit decider_chat identity+reversed"
    assert cal.b == 0.0
    noul = [(chosen, gold) for rec, row in zip(recs, rows, strict=True)
            for _, t, chosen, gold in questions(rec, row, "decider_chat", "identity+reversed", LAYOUTS) if t == "noul"]
    assert len(noul) == 3 and cal.T["noul"] == fits.fit_temperature(noul)


def test_fit_arm_keeps_t_one_below_the_minimum():
    row, rec = calib_record(0)
    cal = fit_arm([rec], {"r0": row}, "decider_chat", "identity")
    assert cal.T == {"choice": 1.0, "score": 1.0, "noul": 1.0}
