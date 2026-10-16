import hashlib
import json
from collections import Counter

import pytest

from scripts import vision_splits as vs


def rows_of(bench: str, n: int, shared: int = 0) -> list[dict]:
    """n rows, each with its own image; the first `shared` pairs share one image."""
    rows = [{"id": f"{bench}:{i}", "benchmark": bench, "images": [f"{bench}/{i}.jpg"]} for i in range(n)]
    for i in range(shared):
        rows[2 * i + 1]["images"] = list(rows[2 * i]["images"])
    return rows


def suite() -> list[dict]:
    return rows_of("big", 2465, shared=300) + rows_of("small", 244, shared=20) + rows_of("mid", 900)


def bench_of(rows):
    return {r["id"]: r["benchmark"] for r in rows}


def test_rows_sharing_an_image_are_one_group():
    rows = [
        {"id": "b", "images": ["x.jpg", "y.jpg"]},
        {"id": "c", "images": ["y.jpg"]},
        {"id": "a", "images": ["x.jpg"]},
        {"id": "d", "images": ["z.jpg"]},
    ]
    g = vs.groups(rows)
    assert g == {"a": "a", "b": "a", "c": "a", "d": "d"}


def test_groups_never_straddle_splits():
    rows = suite()
    g = vs.groups(rows)
    where = {i: name for name, ids in vs.cut(rows).items() if name != "latency" for i in ids}
    for key in set(g.values()):
        members = [i for i, k in g.items() if k == key and i in where]
        assert len({where[i] for i in members}) <= 1
        assert len(members) in (0, sum(1 for k in g.values() if k == key))


def test_counts_follow_min_136_and_40_percent():
    rows = suite()
    parts = vs.cut(rows)
    bench = bench_of(rows)
    g = vs.groups(rows)
    for name, big, small in (("dev", 136, 0.4), ("holdout", 218, 0.4)):
        got = Counter(bench[i] for i in parts[name])
        for b in ("big", "small", "mid"):
            n = sum(1 for r in rows if r["benchmark"] == b)
            target = min(big, int(small * n))
            largest = max(Counter(k for i, k in g.items() if bench[i] == b).values())
            assert target <= got[b] <= target + min(largest, vs.MAX_PER_GROUP)
    small_dev = sum(1 for i in parts["dev"] if bench[i] == "small")
    assert small_dev <= 98
    assert not set(parts["dev"]) & set(parts["holdout"])


def test_a_big_group_gives_at_most_10_rows_chosen_by_hash():
    rows = rows_of("kie", 161)
    for r in rows[:70]:  # one 70-row document group, like FUNSD in KIE
        r["images"] = ["kie/doc.jpg"]
    parts = vs.cut(rows, seed=3)
    big = {r["id"] for r in rows[:70]}
    used = {name: big & set(ids) for name, ids in parts.items() if name != "latency"}
    assert [len(v) for v in used.values()].count(0) == 1  # the group lives in one split only
    kept = next(v for v in used.values() if v)
    assert kept == set(sorted(big, key=lambda i: vs.digest(3, i))[: vs.MAX_PER_GROUP])
    for ids in parts.values():
        assert max(Counter(vs.groups(rows)[i] for i in ids).values()) <= vs.MAX_PER_GROUP


def test_same_seed_same_cut():
    rows = suite()
    assert vs.cut(rows, seed=1) == vs.cut(rows, seed=1)


def test_other_seed_other_cut():
    rows = suite()
    assert vs.cut(rows, seed=1)["dev"] != vs.cut(rows, seed=2)["dev"]


def test_latency_set_is_320_dev_rows_stratified():
    rows = suite()
    parts = vs.cut(rows)
    lat = parts["latency"]
    assert len(lat) == 320 and len(set(lat)) == 320
    assert set(lat) <= set(parts["dev"])
    bench = bench_of(rows)
    dev = Counter(bench[i] for i in parts["dev"])
    got = Counter(bench[i] for i in lat)
    for b in dev:
        assert abs(got[b] - 320 * dev[b] / len(parts["dev"])) < 1


def write_suite(tmp_path, monkeypatch, rows):
    path = tmp_path / "rows.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.setattr(vs, "SUITE", path)
    monkeypatch.setattr(vs, "SPLITS", tmp_path)
    return path


def write_manifest(tmp_path, name, ids, sha):
    (tmp_path / f"{name}.json").write_text(json.dumps({"meta": {"suite_sha256": sha}, "ids": ids}))


def test_holdout_refused_without_flag(tmp_path, monkeypatch):
    rows = rows_of("b", 3)
    path = write_suite(tmp_path, monkeypatch, rows)
    write_manifest(tmp_path, "vision-holdout", ["b:1"], hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(SystemExit, match="holdout"):
        vs.load_split("vision-holdout", log_path=tmp_path / "log.md")
    assert not (tmp_path / "log.md").exists()


def test_holdout_use_is_logged_and_warns_after_five(tmp_path, monkeypatch, capsys):
    rows = rows_of("b", 3)
    path = write_suite(tmp_path, monkeypatch, rows)
    write_manifest(tmp_path, "vision-holdout", ["b:1", "b:0"], hashlib.sha256(path.read_bytes()).hexdigest())
    log = tmp_path / "sub" / "log.md"
    for n in range(1, 7):
        got = vs.load_split("vision-holdout", holdout=True, tool="t", label=f"run{n}", log_path=log)
        assert [r["id"] for r in got] == ["b:1", "b:0"]
        warned = "warning" in capsys.readouterr().err.lower()
        assert warned == (n > 5)
    lines = log.read_text().splitlines()
    assert lines[0].startswith("| UTC") and len(lines) == 2 + 6
    assert "| t | run6 |" in lines[-1]


def test_stale_suite_hash_refused_naming_both_hashes(tmp_path, monkeypatch):
    path = write_suite(tmp_path, monkeypatch, rows_of("b", 3))
    write_manifest(tmp_path, "vision-dev", ["b:0"], "deadbeef")
    with pytest.raises(SystemExit) as e:
        vs.load_split("vision-dev")
    assert "deadbeef" in str(e.value) and hashlib.sha256(path.read_bytes()).hexdigest() in str(e.value)
