import json
import math

import pytest

from gateway.calibration import (
    STAMP_KEYS,
    UNCALIBRATED,
    Calibration,
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


IMAGE_EXPECT = STAMP | {"mm_processor_kwargs": {"max_pixels": 1638400}}


def image_block(**over):
    return {"T": 2.5, "stamp": dict(IMAGE_EXPECT), "fit": {"source": "vision-calib", "rows": 40}} | over


def test_image_block_is_optional_and_loaded(tmp_path):
    text_only = load_calibration(v2(tmp_path / "a"), IMAGE_EXPECT)
    assert text_only.T_image is None and "T_image" not in text_only.as_dict()
    cal = load_calibration(v2(tmp_path / "b", image=image_block()), IMAGE_EXPECT)
    assert cal.T_image == 2.5 and cal.T == text_only.T and cal.b == text_only.b
    shown = cal.as_dict()
    assert shown["T_image"] == 2.5 and shown["image"]["stamp"] == IMAGE_EXPECT
    assert shown["image"]["fit"]["source"] == "vision-calib"
    assert json.loads(json.dumps(shown)) == shown


@pytest.mark.parametrize("key, value", [("mm_processor_kwargs", {"max_pixels": 819200}), ("hf_revision", "new")])
def test_stale_image_stamp_is_refused(tmp_path, key, value):
    path = v2(tmp_path, image=image_block(stamp=IMAGE_EXPECT | {key: value}))
    with pytest.raises(RuntimeError, match=f"image.stamp.{key} changed .* recollect vision-calib .*"
                                           "fit_image_t.py --write, or remove the image block"):
        load_calibration(path, IMAGE_EXPECT)
    assert load_calibration(path, None).T_image == 2.5  # no expectation: unchecked, like the text stamp


@pytest.mark.parametrize("block, field", [({"T": 0.0}, "image.T"), ({"stamp": "x"}, "image.stamp")])
def test_malformed_image_block_is_refused(tmp_path, block, field):
    with pytest.raises(RuntimeError, match=field):
        load_calibration(v2(tmp_path, image=image_block(**block)), IMAGE_EXPECT)


def test_an_image_block_that_is_not_an_object_is_refused(tmp_path):
    with pytest.raises(RuntimeError, match="image.stamp must be a non-empty object"):
        load_calibration(v2(tmp_path, image="x"), IMAGE_EXPECT)


def test_a_text_only_expect_checks_the_image_stamp_text_keys_only(tmp_path):
    other_budget = v2(tmp_path / "a", image=image_block(stamp=IMAGE_EXPECT | {"mm_processor_kwargs": {"x": 1}}))
    assert load_calibration(other_budget, STAMP).T_image == 2.5  # text tools never use T_image
    stale = v2(tmp_path / "b", image=image_block(stamp=IMAGE_EXPECT | {"hf_revision": "new"}))
    with pytest.raises(RuntimeError, match="image.stamp.hf_revision changed"):
        load_calibration(stale, STAMP)


def test_as_dict_with_T_image_but_no_block():
    shown = Calibration({"choice": 1.0, "score": 1.0, "noul": 1.0}, T_image=2.0).as_dict()
    assert shown["T_image"] == 2.0 and shown["image"] == {"stamp": None, "fit": None}
