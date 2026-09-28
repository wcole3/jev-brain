import json
import math

import pytest

from gateway.calibration import load_temperatures, softmax


def test_softmax_with_temperature():
    assert softmax([0.0, math.log(3)], 1.0) == pytest.approx([0.25, 0.75])
    assert softmax([0.0, 2.0], 2.0) == pytest.approx(softmax([0.0, 1.0], 1.0))


def test_missing_file_means_uncalibrated(tmp_path):
    assert load_temperatures(tmp_path / "calibration.json") == {"choice": 1.0, "score": 1.0, "noul": 1.0}


def test_partial_file_fills_defaults(tmp_path):
    f = tmp_path / "calibration.json"
    f.write_text(json.dumps({"choice": 1.5, "source": "test"}))
    assert load_temperatures(f) == {"choice": 1.5, "score": 1.0, "noul": 1.0}
