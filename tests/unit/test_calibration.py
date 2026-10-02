import json
import math

import pytest

from gateway.calibration import UNCALIBRATED, Calibration, load_calibration, softmax

STAMP = {"tokenizer_sha256": "t", "layout_sha256": "l", "hf_revision": "r", "prefix_pad": "off", "prefix_block": 0}


def v2(tmp_path, **over):
    data = {"format": 2, "version": 1, "date": "2026-10-02T00:00:00Z", "comments": [], "stamp": dict(STAMP),
            "types": {"choice": {"T": 1.5}, "score": {"T": 2.0}, "noul": {"T": 0.8, "b": 0.3}}, "fit": {}}
    data.update(over)
    path = tmp_path / "calibration.json"
    path.write_text(json.dumps(data))
    return path


def test_softmax_with_temperature():
    assert softmax([0.0, math.log(3)], 1.0) == pytest.approx([0.25, 0.75])
    assert softmax([0.0, 2.0], 2.0) == pytest.approx(softmax([0.0, 1.0], 1.0))


def test_missing_file_means_uncalibrated(tmp_path):
    assert load_calibration(tmp_path / "calibration.json", STAMP) == UNCALIBRATED


def test_v2_file_loads_temperatures_and_offset(tmp_path):
    cal = load_calibration(v2(tmp_path), STAMP)
    assert cal.T == {"choice": 1.5, "score": 2.0, "noul": 0.8} and cal.b == 0.3 and cal.source.endswith(".json")


def test_v1_or_unstamped_file_is_refused(tmp_path):
    path = tmp_path / "calibration.json"
    path.write_text(json.dumps({"choice": 1.943, "score": 1.943, "noul": 1.943}))
    with pytest.raises(RuntimeError, match="not a v2"):
        load_calibration(path, STAMP)


def test_stale_stamp_is_refused_naming_the_field(tmp_path):
    with pytest.raises(RuntimeError, match="hf_revision changed"):
        load_calibration(v2(tmp_path), STAMP | {"hf_revision": "new"})


def test_no_expectation_skips_the_stamp_check(tmp_path):
    assert load_calibration(v2(tmp_path), None).b == 0.3


def test_as_dict_round_trips_through_json():
    cal = Calibration({"choice": 1.0, "score": 1.0, "noul": 2.0}, 0.5, "x")
    assert json.loads(json.dumps(cal.as_dict())) == cal.as_dict()
