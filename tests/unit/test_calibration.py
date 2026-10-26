import json
import math

import pytest

from gateway.calibration import (
    STAMP_KEYS,
    UNCALIBRATED,
    Calibration,
    Curve,
    load_calibration,
    orders_warning,
    softmax,
    stamp_for,
)
from scripts.collect import stamp as collect_stamp

STAMP = {"tokenizer_sha256": "t", "layout_sha256": "l", "hf_revision": "r", "prefix_pad": "off", "prefix_block": 0}


def v2(tmp_path, **over):
    data = {"format": 2, "version": 1, "date": "2026-10-02T00:00:00Z", "comments": [], "stamp": dict(STAMP),
            "types": {"choice": {"T": 1.5}, "score": {"T": 2.0}, "noul": {"T": 0.8, "b": 0.3}},
            "fit": {"orders": "identity"}}
    data.update(over)
    path = tmp_path / "qwen" / "decider_chat" / "calibration.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(data))
    return path


def test_softmax_with_temperature():
    assert softmax([0.0, math.log(3)], 1.0) == pytest.approx([0.25, 0.75])
    assert softmax([0.0, 2.0], 2.0) == pytest.approx(softmax([0.0, 1.0], 1.0))


def test_missing_file_means_uncalibrated(tmp_path):
    assert load_calibration(tmp_path / "calibration.json", STAMP) == UNCALIBRATED


def test_v2_file_loads_temperatures_and_offset(tmp_path):
    cal = load_calibration(v2(tmp_path), STAMP)
    assert cal.T == {"choice": 1.5, "score": 2.0, "noul": 0.8} and cal.b == 0.3
    assert cal.source == "qwen/decider_chat/calibration.json" and cal.orders == "identity"


def test_v1_or_unstamped_file_is_refused(tmp_path):
    path = tmp_path / "calibration.json"
    path.write_text(json.dumps({"choice": 1.943, "score": 1.943, "noul": 1.943}))
    with pytest.raises(RuntimeError, match="not a v2"):
        load_calibration(path, STAMP)


def test_stale_stamp_is_refused_naming_the_field_and_the_way_out(tmp_path):
    with pytest.raises(RuntimeError, match="hf_revision changed .* move the stale file aside .* recollect"):
        load_calibration(v2(tmp_path), STAMP | {"hf_revision": "new"})


@pytest.mark.parametrize("over, field", [
    ({"stamp": "abc"}, "not a v2"),
    ({"types": {"choice": {"T": 0.0}, "score": {"T": 1.0}, "noul": {"T": 1.0}}}, "types.choice.T"),
    ({"types": {"choice": {"T": 1.0}, "score": {"T": -2.0}, "noul": {"T": 1.0}}}, "types.score.T"),
    ({"types": {"choice": {"T": 1.0}, "score": {"T": 1.0}, "noul": {"T": "1"}}}, "types.noul.T"),
    ({"types": {"choice": {"T": 1.0}, "score": {"T": 1.0}, "noul": {"T": 1.0, "b": math.inf}}}, "types.noul.b"),
    ({"types": {"choice": {"T": {"b": -1.0}}, "score": {"T": 1.0}, "noul": {"T": 1.0}}}, "types.choice.T.a"),
    ({"types": {"choice": {"T": {"a": 7.0, "b": "x"}}, "score": {"T": 1.0}, "noul": {"T": 1.0}}}, "types.choice.T.b"),
    ({"types": {"choice": {"T": {"a": 7.0, "b": -1.0, "floor": 0}}, "score": {"T": 1.0}, "noul": {"T": 1.0}}},
     "types.choice.T.floor"),
])
def test_malformed_values_are_refused_naming_the_field(tmp_path, over, field):
    with pytest.raises(RuntimeError, match=field):
        load_calibration(v2(tmp_path, **over), STAMP)


def test_orders_warning_only_when_a_fit_meets_other_orders():
    fitted = Calibration({"choice": 1.0, "score": 1.0, "noul": 1.0}, source="x", orders="identity")
    assert orders_warning(fitted, "identity") is None and orders_warning(UNCALIBRATED, "cyclic:3") is None
    assert "'identity', used here with 'identity+reversed'" in orders_warning(fitted, "identity+reversed")


def test_no_expectation_skips_the_stamp_check(tmp_path):
    assert load_calibration(v2(tmp_path), None).b == 0.3


def test_as_dict_round_trips_through_json():
    cal = Calibration({"choice": 1.0, "score": 1.0, "noul": 2.0}, 0.5, "x")
    assert json.loads(json.dumps(cal.as_dict())) == cal.as_dict()


def test_collect_stamp_carries_stamp_for_exactly(engine):
    stamp = stamp_for(engine.tokenizer, engine.layouts["decider_chat"], engine.settings)
    assert set(stamp) == set(STAMP_KEYS)
    collected = collect_stamp(engine, "decider_chat")
    assert {k: collected[k] for k in STAMP_KEYS} == stamp


CURVED = {"choice": {"T": {"a": 6.85, "b": -0.8, "floor": 0.05}}, "score": {"T": 2.0}, "noul": {"T": 0.8, "b": 0.3}}


def test_a_type_can_hold_a_curve_beside_constant_types(tmp_path):
    cal = load_calibration(v2(tmp_path, types=CURVED), STAMP)
    assert cal.T == {"choice": Curve(6.85, -0.8), "score": 2.0, "noul": 0.8} and cal.b == 0.3
    assert cal.temperature("choice", 2) == pytest.approx(6.85 - 0.8 * math.log(2))
    assert cal.temperature("score", 7) == 2.0 and cal.temperature("noul", 2) == 0.8


def test_a_curve_without_floor_takes_the_default_floor(tmp_path):
    types = CURVED | {"choice": {"T": {"a": 6.85, "b": -0.8}}}
    assert load_calibration(v2(tmp_path, types=types), STAMP).T["choice"] == Curve(6.85, -0.8, 0.05)


def test_curve_follows_ln_n_down_to_its_floor():
    curve = Curve(4.0, -1.0, floor=0.5)
    assert curve(1) == 4.0 and curve(4) == pytest.approx(4.0 - math.log(4))
    assert curve(10**6) == 0.5
    assert f"{curve:.2f}" == "4.00 -1.00 ln n"


def test_as_dict_writes_a_curve_as_the_file_holds_it():
    cal = Calibration({"choice": Curve(6.85, -0.8), "score": 1.0, "noul": 2.0}, 0.5, "x")
    assert cal.as_dict()["T"]["choice"] == {"a": 6.85, "b": -0.8, "floor": 0.05}
    assert json.loads(json.dumps(cal.as_dict())) == cal.as_dict()
