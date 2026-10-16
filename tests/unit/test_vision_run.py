import json

import pytest

from scripts import vision_run, vision_summary

ROWS = [
    {"run_id": "a", "status": "ok", "model_request_wall_ms": 100.0,
     "response": {"answers": {"answer": {"probabilities": {"A": 0.9, "B": 0.1}}}}},
    {"run_id": "b", "status": "ok", "model_request_wall_ms": 200.0,
     "response": {"answers": {"answer": {"probabilities": {"A": 0.2, "B": 0.8}}}}},
    {"run_id": "c", "status": "ok", "model_request_wall_ms": 300.0,
     "response": {"answers": {"answer": {"probabilities": {"A": 0.7, "B": 0.3}}}}},
    {"run_id": "d", "status": "error", "model_request_wall_ms": 9000.0},
]
EXPECTED = {"a": "A", "b": "A", "c": "A", "d": "A"}


def test_latency_counts_only_ok_rows():
    assert vision_summary.latency(ROWS) == {"median": 200.0, "mean": 200.0, "p80": 300.0}


def test_latency_without_ok_rows_is_none():
    assert vision_summary.latency(ROWS[3:]) is None


def test_calibration_scores_the_top_probability():
    # confidences .9 .8 .7 in 15 bins: bins 13, 12, 10; row b is wrong
    cal = vision_summary.calibration(ROWS, EXPECTED)
    assert cal["n"] == 3
    assert cal["accuracy"] == pytest.approx(2 / 3)
    assert cal["ece"] == pytest.approx((0.1 + 0.8 + 0.3) / 3)


def test_status_counts():
    assert vision_summary.status_counts(ROWS) == {"ok": 3, "error": 1}


def suite(sizes):
    return [{"id": f"{b}:{i}", "benchmark": b} for b, n in sizes.items() for i in range(n)]


def test_sample_is_stratified_by_benchmark():
    picked = vision_run.stratified_sample(suite({"A": 60, "B": 30, "C": 10}), 10)
    counts = {b: sum(r["benchmark"] == b for r in picked) for b in "ABC"}
    assert counts == {"A": 6, "B": 3, "C": 1}


def test_sample_is_stable_and_keeps_suite_order():
    rows = suite({"A": 60, "B": 30, "C": 10})
    first = vision_run.stratified_sample(rows, 10)
    assert first == vision_run.stratified_sample(rows, 10)
    assert first == [r for r in rows if r in first]


def test_sample_gives_leftover_seats_to_largest_remainders():
    picked = vision_run.stratified_sample(suite({"A": 5, "B": 5, "C": 5}), 4)
    assert len(picked) == 4 and len({r["benchmark"] for r in picked}) == 3


def test_sample_larger_than_suite_returns_everything():
    rows = suite({"A": 3})
    assert vision_run.stratified_sample(rows, 10) == rows


def test_sample_dir_holds_only_the_rows_and_links_image_dirs(tmp_path):
    suite = tmp_path / "suite"
    (suite / "full").mkdir(parents=True)
    rows = [{"id": "x:1", "images": ["full/a/1.jpg", "full/a/2.jpg"]}, {"id": "x:2", "images": ["extra/3.jpg"]}]
    out = vision_run.write_sample_dir(suite, rows, tmp_path / "run" / "sample")
    lines = (out / "vision-rows.jsonl").read_text().splitlines()
    assert [json.loads(line)["id"] for line in lines] == ["x:1", "x:2"]
    assert (out / "full").resolve() == (suite / "full").resolve()
    assert (out / "extra").is_symlink()
