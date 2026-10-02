import json

import pytest

from gateway.calibration import Calibration
from scripts import calibrate
from scripts import fit as fits

LAYOUT = "decider_chat"
STAMP = {"tokenizer_sha256": "t", "layout_sha256": "l", "hf_revision": "r", "prefix_pad": "off", "prefix_block": 0}


def rec(i, lp, perm, qtype="choice", layout=LAYOUT, stamp=STAMP):
    return {"id": f"r{i}", "layout": layout, "status": "ok", "stamp": stamp,
            "questions": {"q": [{"perm": perm, "logprobs": lp}]}}


def row(i, qtype, gold):
    q = ({"type": "noul", "instructions": "is it?"} if qtype == "noul"
         else {"type": "choice", "instructions": "pick", "criteria": {"a": None, "b": None}})
    return {"id": f"r{i}", "source": "s", "family": "f", "state": "x", "questions": {"q": q}, "gold": {"q": gold}}


def test_questions_by_type_groups_and_reads_the_stamp():
    recs = [rec(0, [0.0, -1.0], [0, 1]), rec(1, [-1.0, 0.0], [0, 1])]
    rows = {"r0": row(0, "choice", "a"), "r1": row(1, "noul", True)}
    by_type, stamp = calibrate.questions_by_type(recs, rows, LAYOUT, "identity")
    assert len(by_type["choice"]) == 1 and len(by_type["noul"]) == 1 and stamp == STAMP
    assert by_type["noul"][0][1] == 1  # gold yes is caller index 1


def test_mixed_stamps_are_refused():
    recs = [rec(0, [0.0, -1.0], [0, 1]), rec(1, [0.0, -1.0], [0, 1], stamp=STAMP | {"hf_revision": "x"})]
    rows = {"r0": row(0, "choice", "a"), "r1": row(1, "choice", "a")}
    try:
        calibrate.questions_by_type(recs, rows, LAYOUT, "identity")
    except SystemExit as e:
        assert "hf_revision" in str(e)
    else:
        raise AssertionError("expected SystemExit")


def test_small_types_keep_temperature_one():
    fit = calibrate.fit_layout({"choice": [([([0.0, -1.0], [0, 1])], 0)] * 5, "score": [], "noul": []})
    assert fit["choice"]["T"] == 1.0 and fit["noul"] == {"T": 1.0, "b": 0.0}


def test_offset_not_shipped_without_a_gain():
    qs = [([([0.0, 0.5], [0, 1])], 1), ([([0.0, -0.5], [0, 1])], 0)] * 100  # already well separated
    ship, stats = calibrate.ship_offset(qs, with_b=(1.0, 0.0), without_b=1.0)
    assert ship is False and stats["acc"][0] == 0.0


FIT = {"choice": {"T": 1.2}, "score": {"T": 1.4}, "noul": {"T": 0.9, "b": 0.0}}


def write(path, previous, comment, date):
    data = calibrate.calibration_file(FIT, STAMP, "identity", {"choice": 1}, {"nll": {}, "ece": {}}, {"ship": False},
                                      previous, comment, date)
    path.write_text(json.dumps(data))
    return data


def test_calibration_file_is_v2_and_loadable(tmp_path):
    from gateway.calibration import load_calibration

    path = tmp_path / "calibration.json"
    write(path, (0, []), "first fit", "2026-10-02T00:00:00Z")
    cal = load_calibration(path, STAMP)
    assert cal.T == {"choice": 1.2, "score": 1.4, "noul": 0.9} and cal.b == 0.0


def test_refit_bumps_version_and_keeps_the_comment_history(tmp_path):
    path = tmp_path / "calibration.json"
    write(path, calibrate.history(path), "first fit", "2026-10-02T00:00:00Z")
    data = write(path, calibrate.history(path), "refit after layout change", "2026-10-03T00:00:00Z")
    assert data["format"] == 2 and data["version"] == 2 and data["date"] == "2026-10-03T00:00:00Z"
    assert [c["text"] for c in data["comments"]] == ["first fit", "refit after layout change"]
    assert [c["version"] for c in data["comments"]] == [1, 2]


def test_v1_or_missing_file_starts_history_at_zero(tmp_path):
    path = tmp_path / "calibration.json"
    assert calibrate.history(path) == (0, [])
    path.write_text(json.dumps({"choice": 1.943, "score": 1.943, "noul": 1.943}))
    assert calibrate.history(path) == (0, [])


def test_edge_flag_marks_values_at_the_search_edge():
    assert calibrate.at_edge(20.0, fits.LOG_T, log=True) and calibrate.at_edge(0.05, fits.LOG_T, log=True)
    assert calibrate.at_edge(-10.0, fits.B_RANGE) and not calibrate.at_edge(1.9, fits.LOG_T, log=True)


def test_uncollected_orders_are_refused_clearly():
    recs, rows = [rec(0, [0.0, -1.0], [0, 1])], {"r0": row(0, "choice", "a")}
    with pytest.raises(ValueError, match="needs 2 orders"):
        calibrate.questions_by_type(recs, rows, LAYOUT, "identity+reversed")


def test_layout_without_ok_records_is_refused():
    with pytest.raises(SystemExit, match="decider_chat: no ok records in eval"):
        calibrate.split_questions([rec(0, [0.0, -1.0], [0, 1], layout="header")], {"r0": row(0, "choice", "a")},
                                  LAYOUT, "identity", "eval")


def biased_noul(n=200):
    """Yes-biased reads: the gold is yes for 60%, yet the logit gap sits mostly below zero."""
    out = []
    for i in range(n):
        gap = -1.0 + 0.3 * (i % 5)  # -1.0 .. 0.2
        gold = int(i % 5 >= 2)
        out.append(([([0.0, gap], [0, 1])], gold))
    return out


def test_offset_ships_when_it_fixes_a_bias_and_not_when_reversed():
    qs = biased_noul()
    T, b = fits.fit_noul(qs)
    assert b > 0.3
    ship, stats = calibrate.ship_offset(qs, with_b=(T, b), without_b=T)
    assert ship is True and stats["acc"][0] > 0
    assert calibrate.ship_offset(qs, with_b=(T, -b), without_b=T)[0] is False


def test_unshipped_offset_falls_back_to_the_b0_temperature_and_before_is_raw(monkeypatch):
    qs = biased_noul()
    monkeypatch.setattr(calibrate, "ship_offset", lambda *a: (False, {"acc": (0, 0, 0), "ece": (0, 0, 0)}))
    calib = {"choice": [], "score": [], "noul": qs}
    r = calibrate.fit_and_judge(LAYOUT, calib, calib)
    b0 = calibrate.fit_layout(calib)["noul_b0"]["T"]
    assert r.fit["noul"] == {"T": b0, "b": 0.0} and r.b_fitted > 0.3
    raw = calibrate.summarize(qs, "noul", Calibration({"choice": 1, "score": 1, "noul": 1.0}))
    assert r.before["eval"]["noul"]["nll"] == raw["nll"] and r.after["eval"]["noul"]["nll"] != raw["nll"]
