from scripts import lengths
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
