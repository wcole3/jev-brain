import json

import pytest

from gateway.calibration import Calibration
from gateway.config import Settings
from scripts import calibrate, calibrate_report
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
    by_split = {"calib": {"nll": {}, "ece": {}}, "eval": {"nll": {"after": {"choice": 0.5}}, "ece": {}}}
    data = calibrate.calibration_file(FIT, STAMP, "identity", {"choice": 1}, by_split,
                                      {"b_decision": {"ship": False}, "t_decision": {}}, previous, comment, date)
    path.write_text(json.dumps(data))
    return data


def test_calibration_file_is_v2_and_loadable(tmp_path):
    from gateway.calibration import load_calibration

    path = tmp_path / "calibration.json"
    write(path, (0, []), "first fit", "2026-10-02T00:00:00Z")
    cal = load_calibration(path, STAMP)
    assert cal.T == {"choice": 1.2, "score": 1.4, "noul": 0.9} and cal.b == 0.0 and cal.orders == "identity"


def test_fit_block_keeps_eval_metrics_apart_from_the_calib_split(tmp_path):
    fit = write(tmp_path / "calibration.json", (0, []), "first fit", "2026-10-02T00:00:00Z")["fit"]
    assert fit["split"] == "data/splits/calib.json" and fit["eval"]["nll"]["after"] == {"choice": 0.5}
    assert "nll" not in fit and "ece" not in fit


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
    at_edge = calibrate_report.at_edge
    assert at_edge(20.0, fits.LOG_T, log=True) and at_edge(0.05, fits.LOG_T, log=True)
    assert at_edge(-10.0, fits.B_RANGE) and not at_edge(1.9, fits.LOG_T, log=True)


def test_uncollected_orders_are_refused_clearly():
    recs, rows = [rec(0, [0.0, -1.0], [0, 1])], {"r0": row(0, "choice", "a")}
    with pytest.raises(ValueError, match="needs 2 orders"):
        calibrate.questions_by_type(recs, rows, LAYOUT, "identity+reversed")


def test_layout_without_ok_records_is_refused():
    recs, rows = [rec(0, [0.0, -1.0], [0, 1], layout="header")], {"r0": row(0, "choice", "a")}
    with pytest.raises(SystemExit, match="decider_chat: no ok records in eval"):
        calibrate.split_questions(recs, rows, LAYOUT, "identity", "eval")


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
    fitted = {t: {"source": "fitted"} for t in calibrate.TYPES}
    monkeypatch.setattr(calibrate, "gate_temperatures", lambda fit, held: fitted)
    calib = {"choice": [], "score": [], "noul": qs}
    r = calibrate.fit_and_judge(LAYOUT, calib, calib)
    b0 = calibrate.fit_layout(calib)["noul_b0"]["T"]
    assert r.fit["noul"] == {"T": b0, "b": 0.0} and r.b_fitted > 0.3
    raw = calibrate.summarize(qs, "noul", Calibration({"choice": 1, "score": 1, "noul": 1.0}))
    assert r.before["eval"]["noul"]["nll"] == raw["nll"] and r.after["eval"]["noul"]["nll"] != raw["nll"]


def calibrated_choice(n=200):
    """Two options, logit gap 1 (p = 0.73 at T = 1), right 73% of the time: T = 1 is already calibrated."""
    return [([([0.0, -1.0], [0, 1])], 0 if i % 100 < 73 else 1) for i in range(n)]


def underconfident_choice(n=200):
    """Same logit gap, right 90% of the time: a T below 1 sharpens it and cuts ECE."""
    return [([([0.0, -1.0], [0, 1])], 0 if i % 100 < 90 else 1) for i in range(n)]


def gate_fit(choice_T, pooled_T, noul=(1.0, 0.0)):
    return {"choice": {"T": choice_T}, "score": {"T": 1.0}, "noul": {"T": noul[0], "b": noul[1]},
            "pooled": {"T": pooled_T}}


def test_gate_falls_back_to_pooled_when_the_fitted_T_worsens_eval_ece():
    held = {"choice": underconfident_choice(), "score": [], "noul": []}
    gate = calibrate.gate_temperatures(gate_fit(20.0, 0.5), held)
    assert gate["choice"]["source"] == "pooled" and gate["choice"]["shipped_T"] == 0.5
    assert gate["choice"]["fitted_T"] == 20.0 and gate["choice"]["ece"][1] > 0
    assert gate["score"] == {"fitted_T": 1.0, "pooled_T": 0.5, "shipped_T": 1.0, "source": "fitted",
                             "ece": [0.0, 0.0, 0.0], "ece_pooled": [0.0, 0.0, 0.0]}


def test_gate_records_the_pooled_T_for_every_type_even_when_fitted_ships():
    held = {"choice": calibrated_choice(), "score": [], "noul": []}
    gate = calibrate.gate_temperatures(gate_fit(1.0, 1.05), held)
    assert gate["choice"]["source"] == "fitted"
    assert all(g["pooled_T"] == 1.05 and len(g["ece_pooled"]) == 3 for g in gate.values())


def test_gate_uses_temperature_one_when_pooled_fails_too():
    held = {"choice": calibrated_choice(), "score": [], "noul": []}
    gate = calibrate.gate_temperatures(gate_fit(20.0, 15.0), held)
    assert gate["choice"]["source"] == "none" and gate["choice"]["shipped_T"] == 1.0
    assert gate["choice"]["ece_pooled"][1] > 0


def test_gated_noul_drops_its_offset_and_the_decision_is_recorded(monkeypatch):
    noul = [([([0.0, -1.0], [0, 1])], 0 if i % 100 < 73 else 1) for i in range(200)]
    held = {"choice": [], "score": [], "noul": noul}
    fit = gate_fit(1.0, 15.0, (20.0, 0.5)) | {"noul_b0": {"T": 20.0}}
    monkeypatch.setattr(calibrate, "fit_layout", lambda calib: fit)
    monkeypatch.setattr(calibrate, "ship_offset", lambda *a: (True, {"acc": (0, 0, 0), "ece": (0, 0, 0)}))
    r = calibrate.fit_and_judge(LAYOUT, held, held)
    assert r.fit["noul"] == {"T": 1.0, "b": 0.0} and r.ship is False
    assert r.gate["noul"]["source"] == "none" and r.gate["noul"]["fitted_T"] == 20.0
    assert r.after["eval"]["noul"]["nll"] == r.before["eval"]["noul"]["nll"]


def test_gate_outcome_names_what_each_type_ships(monkeypatch):
    noul = [([([0.0, -1.0], [0, 1])], 0 if i % 100 < 73 else 1) for i in range(200)]
    held = {"choice": [], "score": [], "noul": noul}
    fit = gate_fit(1.2, 15.0, (20.0, 0.5)) | {"noul_b0": {"T": 20.0}}
    monkeypatch.setattr(calibrate, "fit_layout", lambda calib: fit)
    monkeypatch.setattr(calibrate, "ship_offset", lambda *a: (True, {"acc": (0, 0, 0), "ece": (0, 0, 0)}))
    r = calibrate.fit_and_judge(LAYOUT, held, held)
    assert calibrate.gate_outcome(r) == ("choice: fitted T 1.200, score: fitted T 1.000, noul: none T 1.000,"
                                         " b not shipped")
    assert "pooled T (one T for every type, b = 0; the gate's fallback): 15.000" in calibrate.layout_report(r)


def test_calibrate_writes_the_file_the_gateway_reads_for_that_block(tmp_path, monkeypatch):
    from types import SimpleNamespace

    s = Settings.from_env({"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s",
                           "MAX_MODEL_LEN": "1024", "PREFIX_BLOCK": "784", "DATA_ROOT": str(tmp_path)})
    (tmp_path / "p" / LAYOUT).mkdir(parents=True)
    (tmp_path / "p" / LAYOUT / "calibration-784.json").write_text("{}")
    monkeypatch.setattr(calibrate, "history", lambda path: (0, []))
    r = SimpleNamespace(fit={}, ship=False, stats={"acc": (0, 0), "ece": (0, 0)}, b_fitted=0.0, gate={})
    monkeypatch.setattr(calibrate, "split_questions", lambda *a: ({t: [] for t in calibrate.TYPES}, STAMP))
    monkeypatch.setattr(calibrate, "fit_and_judge", lambda *a: r)
    monkeypatch.setattr(calibrate, "moves", lambda *a: {})
    monkeypatch.setattr(calibrate, "gate_outcome", lambda r: "gate")
    monkeypatch.setattr(calibrate, "layout_report", lambda r: [])
    monkeypatch.setattr(calibrate, "calibration_file", lambda *a: {"format": 2})
    args = SimpleNamespace(orders="identity", comment="c", dry_run=False)
    calibrate.calibrate_layout(args, s, LAYOUT, {"calib": [], "eval": []}, {"calib": {}, "eval": {}})
    assert (tmp_path / "p" / LAYOUT / "calibration-784.json").read_text().startswith('{\n "format"')
    assert not (tmp_path / "p" / LAYOUT / "calibration.json").exists()


def test_dry_run_writes_nothing_and_prints_the_report(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(calibrate, "RESULTS", tmp_path)
    monkeypatch.setattr(calibrate, "rows_for", lambda name: [])
    monkeypatch.setattr(calibrate, "records", lambda path: [])
    monkeypatch.setattr(calibrate, "calibrate_layout", lambda args, s, layout, recs, rows: [f"## {layout}"])
    calibrate.main(["--profile", "qwen3.6-27b", "--layouts", LAYOUT, "--dry-run"])
    assert list(tmp_path.iterdir()) == [] and f"## {LAYOUT}" in capsys.readouterr().out


def noul_gate(b0_T, pooled_T):
    held = {"choice": [], "score": [], "noul": underconfident_choice()}
    return calibrate.gate_temperatures(gate_fit(1.0, pooled_T, (20.0, 0.5)) | {"noul_b0": {"T": b0_T}}, held)


def test_gate_noul_tries_the_b0_temperature_before_pooled():
    g = noul_gate(0.5, 0.5)["noul"]
    assert g["source"] == "b0" and g["shipped_T"] == 0.5 and g["ece"][1] > 0 and len(g["ece_b0"]) == 3


def test_gate_noul_falls_to_pooled_when_b0_fails_too():
    g = noul_gate(20.0, 0.5)["noul"]
    assert g["source"] == "pooled" and g["shipped_T"] == 0.5 and g["ece_b0"][1] > 0


def test_gate_noul_without_b_makes_no_b0_attempt():
    held = {"choice": [], "score": [], "noul": underconfident_choice()}
    g = calibrate.gate_temperatures(gate_fit(1.0, 0.5, (20.0, 0.0)), held)["noul"]
    assert g["source"] == "pooled" and "ece_b0" not in g


def test_b0_source_writes_b_as_zero(monkeypatch):
    held = {"choice": [], "score": [], "noul": underconfident_choice()}
    fit = gate_fit(1.0, 15.0, (20.0, 0.5)) | {"noul_b0": {"T": 0.5}}
    monkeypatch.setattr(calibrate, "fit_layout", lambda calib: fit)
    monkeypatch.setattr(calibrate, "ship_offset", lambda *a: (True, {"acc": (0, 0, 0), "ece": (0, 0, 0)}))
    r = calibrate.fit_and_judge(LAYOUT, held, held)
    assert r.gate["noul"]["source"] == "b0" and r.fit["noul"] == {"T": 0.5, "b": 0.0} and r.ship is False
    assert "b = 0 " in calibrate_report.gate_text(r.gate["noul"])


def test_gate_ships_pooled_when_both_pass_and_pooled_has_the_lower_ece():
    held = {"choice": calibrated_choice(), "score": [], "noul": []}
    g = calibrate.gate_temperatures(gate_fit(1.1, 1.0), held)["choice"]
    assert g["source"] == "pooled" and g["shipped_T"] == 1.0 and g["ece"][1] <= 0


def test_gate_ships_fitted_when_both_pass_and_fitted_has_the_lower_ece():
    held = {"choice": calibrated_choice(), "score": [], "noul": []}
    g = calibrate.gate_temperatures(gate_fit(1.0, 1.1), held)["choice"]
    assert g["source"] == "fitted" and g["shipped_T"] == 1.0


def test_gate_keeps_a_passing_noul_b_even_when_pooled_has_the_lower_ece():
    held = {"choice": [], "score": [], "noul": calibrated_choice()}
    fit = gate_fit(1.0, 1.0, (1.0, 0.1)) | {"noul_b0": {"T": 1.0}}
    g = calibrate.gate_temperatures(fit, held)["noul"]
    assert g["source"] == "fitted" and g["ece_pooled"][0] < g["ece"][0]


def test_gate_ships_the_lowest_real_candidate_even_when_all_are_worse_than_no_calibration():
    held = {"choice": calibrated_choice(), "score": [], "noul": []}
    g = calibrate.gate_temperatures(gate_fit(1.0, 1.0), held)["choice"]
    assert g["source"] == "fitted"  # ties go to the earlier candidate
    g = calibrate.gate_temperatures(gate_fit(1.05, 1.1), held)["choice"]
    worse = calibrate.ece_change(held["choice"], "choice", 1.05)
    assert worse[0] > 0 and worse[1] <= 0  # positive point change but passes the CI test
    assert g["source"] == "fitted" and g["shipped_T"] == 1.05


def test_gate_ships_a_candidate_with_a_negative_point_change():
    held = {"choice": underconfident_choice(), "score": [], "noul": []}
    g = calibrate.gate_temperatures(gate_fit(0.5, 15.0), held)["choice"]
    assert g["ece"][0] < 0 and g["source"] == "fitted" and g["shipped_T"] == 0.5


def refit_with_image(tmp_path, monkeypatch, new_stamp):
    """A first fit plus an image block stamped STAMP, then a text refit whose records carry new_stamp."""
    from types import SimpleNamespace

    s = Settings.from_env({"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s",
                           "MAX_MODEL_LEN": "1024", "DATA_ROOT": str(tmp_path)})
    path = s.calibration_path(LAYOUT)
    path.parent.mkdir(parents=True)
    first = write(path, (0, []), "first fit", "2026-10-02T00:00:00Z")
    image = {"T": 2.5, "stamp": STAMP | {"mm_processor_kwargs": {}}, "fit": {"source": "vision-calib", "rows": 40}}
    path.write_text(json.dumps(first | {"image": image}))
    r = SimpleNamespace(fit=FIT, ship=False, stats={"acc": (0, 0), "ece": (0, 0)}, b_fitted=0.0, gate={})
    monkeypatch.setattr(calibrate, "split_questions", lambda *a: ({t: [] for t in calibrate.TYPES}, new_stamp))
    monkeypatch.setattr(calibrate, "fit_and_judge", lambda *a: r)
    monkeypatch.setattr(calibrate, "moves", lambda *a: {})
    monkeypatch.setattr(calibrate, "gate_outcome", lambda r: "gate")
    monkeypatch.setattr(calibrate, "layout_report", lambda r: [])
    args = SimpleNamespace(orders="identity", comment="refit", dry_run=False)
    calibrate.calibrate_layout(args, s, LAYOUT, {"calib": [], "eval": []}, {"calib": {}, "eval": {}})
    return image, json.loads(path.read_text())


def test_text_refit_keeps_the_image_block_and_says_so(tmp_path, monkeypatch):
    image, data = refit_with_image(tmp_path, monkeypatch, STAMP)
    assert data["image"] == image and data["version"] == 2
    assert [c["text"] for c in data["comments"]] == ["first fit", "refit; gate; image block kept (T_image 2.500)"]


def test_text_refit_under_a_new_stamp_drops_the_image_block(tmp_path, monkeypatch, capsys):
    _, data = refit_with_image(tmp_path, monkeypatch, STAMP | {"hf_revision": "new"})
    assert "image" not in data and data["comments"][-1]["text"] == "refit; gate"
    assert "image block dropped" in capsys.readouterr().out
