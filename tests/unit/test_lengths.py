import json

from scripts import evaluate, lengths
from scripts.evaluate import parse_args
from tests.helpers import QUICKSTART, STATE


def test_buckets():
    assert lengths.bucket(100) == "<8k"
    assert lengths.bucket(40000) == "32k-64k"
    assert lengths.bucket(300000) == ">=256k"
    assert lengths.bucket(None) == "unknown"


def test_bucket_counts_by_catalog():
    meta = [{"meta": {"catalog_id": 1, "proxy_tokens": 100}}, {"meta": {"catalog_id": 1, "proxy_tokens": 40000}},
            {"meta": {"catalog_id": 2, "proxy_tokens": 50}}]
    assert lengths.bucket_counts(meta) == {"<8k": {1: 1, 2: 1}, "32k-64k": {1: 1}}


async def test_real_lengths_measure_the_longest_row(engine):
    rows = [{"id": "r1", "state": STATE, "questions": QUICKSTART}]
    out = await lengths.real_lengths(engine, rows)
    assert out["r1"] > 20


def test_lengths_cli_parses():
    assert parse_args(["lengths", "--profile", "p"]).near == 0.5
    assert parse_args(["lengths", "--profile", "p", "--baseline", "runs/x"]).baseline == "runs/x"


def test_baseline_length_refusals_are_read_exactly(tmp_path):
    rows = [
        {"run_id": "a", "status": "unsupported", "error": "prompt is longer than the maximum context length"},
        {"run_id": "b", "status": "unsupported", "error": "too many options per choice"},
        {"run_id": "c", "status": "error", "error": "maximum context length"},
        {"run_id": "d", "status": "ok"},
    ]
    (tmp_path / "merged").mkdir()
    (tmp_path / "merged" / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert evaluate.context_refusals(tmp_path) == {"a"}


def test_long_rows_are_measured_over_cap_plus_baseline_refusals():
    longest = {"x": 40000, "y": 1000, "z": 32768}
    assert evaluate.over_cap(longest, 32768, {"y", "w"}) == ["w", "x", "y", "z"]
