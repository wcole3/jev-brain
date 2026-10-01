import json
import random
from itertools import pairwise

import pytest

from scripts import splits
from scripts.decision_rows import state_key


def row(i, source="jevbench", family="f", qtype="choice", state=None, ask="?", **meta):
    return {"id": f"{source}:{i}", "source": source, "family": family, "state": state or f"state {i}",
            "questions": {"q": {"type": qtype, "instructions": ask}}, "gold": {"q": "a"}, "meta": meta}


def test_split_is_deterministic_disjoint_and_balanced():
    rows = [row(i) for i in range(100)]
    a, b = splits.split_extras(rows, set()), splits.split_extras(list(reversed(rows)), set())
    assert a == b
    assert not set(a["calib"]) & set(a["eval"]) and len(a["calib"]) == len(a["eval"]) == 50


def test_index_overlap_and_reasoning_rows_go_to_eval():
    rows = [row(i) for i in range(10)] + [row(99, source="decisionbench", reasoning=True)]
    out = splits.split_extras(rows, {state_key("state 3")})
    assert "jevbench:3" in out["eval"] and "decisionbench:99" in out["eval"]


def test_duplicate_state_and_question_keep_one_row():
    out = splits.split_extras([row(1, state="same"), row(2, state="Same ")], set())
    assert len(out["calib"]) + len(out["eval"]) == 1


def test_other_questions_about_one_state_are_kept_in_the_same_split():
    rows = [row(i, state=f"doc {i // 3}", ask=f"question {i % 3}") for i in range(60)]
    out = splits.split_extras(rows, set())
    assert len(out["calib"]) + len(out["eval"]) == 60
    for part in out.values():
        docs = {int(i.split(":")[1]) // 3 for i in part}
        assert {f"jevbench:{3 * d + k}" for d in docs for k in range(3)} <= set(part)


def test_forced_rows_take_no_calib_eval_slot():
    rows = [row(i) for i in range(40)] + [row(100 + i, reasoning=True) for i in range(40)]
    out = splits.split_extras(rows, set())
    assert len([i for i in out["calib"] if int(i.split(":")[1]) < 40]) == 20


def test_one_reasoning_row_sends_its_whole_state_to_eval():
    rows = [row(i, state=f"doc {i // 2}", ask=f"q{i % 2}", reasoning=i % 4 == 1) for i in range(40)]
    out = splits.split_extras(rows, set())
    assert {f"jevbench:{i}" for i in range(40) if i % 4 < 2} <= set(out["eval"])


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


@pytest.fixture
def cut(tmp_path, monkeypatch):
    """Splits cut by main() into a temp folder from 20 fake extras and 800 fake Index rows."""
    rows = [row(i) for i in range(20)]
    monkeypatch.setattr(splits, "SPLITS", tmp_path)
    monkeypatch.setattr(splits, "extras", lambda: rows)
    monkeypatch.setattr(splits, "index_meta", lambda: [meta(i, 1) | {"state_key": f"k{i}"} for i in range(800)])
    splits.main()
    return rows


def test_index_dev_meta_records_its_seed(cut):
    assert splits.load_split("index-dev")["meta"]["seed"] == splits.INDEX_DEV_SEED


def test_rows_for_reads_back_the_cut(cut):
    assert len(splits.rows_for("calib")) + len(splits.rows_for("eval")) == 20


def test_rows_for_refuses_a_split_cut_from_other_pins(cut, tmp_path):
    split = splits.load_split("calib")
    split["meta"]["edition"] = "0.1.0"
    (tmp_path / "calib.json").write_text(json.dumps(split))
    with pytest.raises(SystemExit, match=r"calib\.json was cut from other \['edition'\]"):
        splits.rows_for("calib")


def test_rows_for_refuses_ids_it_cannot_find(cut, monkeypatch):
    name = "calib" if cut[0]["id"] in splits.load_split("calib")["ids"] else "eval"
    monkeypatch.setattr(splits, "extras", lambda: cut[1:])
    with pytest.raises(SystemExit, match=f"{name}: 1 listed ids are missing"):
        splits.rows_for(name)
