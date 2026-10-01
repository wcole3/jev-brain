import random
from itertools import pairwise

from scripts import splits
from scripts.decision_rows import state_key


def row(i, source="jevbench", family="f", qtype="choice", state=None, **meta):
    return {"id": f"{source}:{i}", "source": source, "family": family, "state": state or f"state {i}",
            "questions": {"q": {"type": qtype}}, "gold": {"q": "a"}, "meta": meta}


def test_split_is_deterministic_disjoint_and_balanced():
    rows = [row(i) for i in range(100)]
    a, b = splits.split_extras(rows, set()), splits.split_extras(list(reversed(rows)), set())
    assert a == b
    assert not set(a["calib"]) & set(a["eval"]) and len(a["calib"]) == len(a["eval"]) == 50


def test_index_overlap_and_reasoning_rows_go_to_eval():
    rows = [row(i) for i in range(10)] + [row(99, source="decisionbench", reasoning=True)]
    out = splits.split_extras(rows, {state_key("state 3")})
    assert "jevbench:3" in out["eval"] and "decisionbench:99" in out["eval"]


def test_duplicate_states_keep_one_row():
    out = splits.split_extras([row(1, state="same"), row(2, state="Same ")], set())
    assert len(out["calib"]) + len(out["eval"]) == 1


def test_cap_per_family_keeps_the_lowest_hashes():
    rows = [row(i, family="big") for i in range(10)] + [row(50, family="small")]
    kept = splits.cap_per_family(rows, 3)
    assert len([r for r in kept if r["family"] == "big"]) == 3 and any(r["family"] == "small" for r in kept)


def test_systematic_spreads_evenly():
    idx = splits.systematic(1000, 10, random.Random(0))
    assert len(idx) == 10 and all(80 <= b - a <= 120 for a, b in pairwise(idx))


def meta(i, catalog, group=None, chars=100):
    return {"id": f"r{i}", "meta": {"catalog_id": catalog, "group_id": group or f"g{i}", "payload_chars": chars}}


def test_index_dev_keeps_linked_groups_whole():
    rows = [meta(i, 1, group=f"g{i // 2}") for i in range(200)]
    ids = set(splits.index_dev(rows, n_rows=20))
    for g in range(100):
        assert ({f"r{2 * g}", f"r{2 * g + 1}"} <= ids) or not ({f"r{2 * g}", f"r{2 * g + 1}"} & ids)


def test_latency_sample_skips_simplebench_and_is_disjoint():
    rows = [meta(i, 34 if i < 50 else 1 + i % 5, chars=i) for i in range(2000)]
    s = splits.latency_sample(rows)
    assert len(s["timed"]) == 750 and len(s["warmup"]) == 10
    assert not set(s["timed"]) & set(s["warmup"])
    assert all(int(i[1:]) >= 50 for i in s["timed"] + s["warmup"])
    assert splits.latency_sample(rows) == s
