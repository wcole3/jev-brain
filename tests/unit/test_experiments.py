from scripts.experiments import compare, is_long, length_bucket, option_bucket, paired
from scripts.metrics import Scored


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
