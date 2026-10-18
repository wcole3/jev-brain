import gzip
import json
import random

import pytest

from gateway.orders import option_orders
from scripts import vision_compare as vc
from scripts import vision_orders as vor
from scripts import vision_splits as vs
from scripts.collect import records
from scripts.order_policies import IMAGE_POLICIES, POLICIES

STAMP = {"profile": "gemma-4-31b", "layout_sha256": "aa", "labels_sha256": "bb", "commit": "c1"}
CONFIG = {"profile": "gemma-4-31b", "label": "baseline", "layout": "header", "orders": "identity+reversed",
          "env": {}, "split": "dev", "commit": "c1"}
PICKED = ["identity", "always reversed/mean-prob", "min_n 3 reversed/mean-prob", "always half/tn-prob"]


@pytest.fixture(autouse=True)
def manifests(tmp_path, monkeypatch):
    """A vision-dev manifest over the fixture ids in tmp, and the holdout log in tmp."""
    splits = tmp_path / "splits"
    splits.mkdir()
    ids = [f"r{i}" for i in range(200)]
    (splits / "vision-dev.json").write_text(json.dumps({"meta": {"suite_sha256": "x"}, "ids": ids}))
    monkeypatch.setattr(vs, "SPLITS", splits)
    monkeypatch.setattr(vs, "HOLDOUT_LOG", tmp_path / "holdout-log.md")
    monkeypatch.setattr(vs, "suite_hash", lambda: "x")


def rec(i: int, n: int, perms: list[list[int]], *, rng=None, suffix=60, second_suffix=None, **stamp) -> dict:
    rng = rng or random.Random(i)
    reads = [{"perm": p, "logprobs": [rng.gauss(0, 2) for _ in range(n)],
              "suffix_len": suffix if k == 0 or second_suffix is None else second_suffix}
             for k, p in enumerate(perms)]
    return {"id": f"r{i}", "benchmark": "CV-Bench" if i % 2 else "BLINK", "group": f"g{i // 2}", "layout": "header",
            "names": [chr(65 + j) for j in range(n)], "gold": i % n, "input_tokens": 700, "shared_len": 30,
            "padded": False, "unpadded_len": 30, "image_tokens": 500, "images_shared": True, "reads": reads,
            "stamp": STAMP | stamp, "status": "ok"}


def write_collect(folder, recs: list[dict], **config):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "dev.config.json").write_text(json.dumps(CONFIG | config))
    path = folder / "dev.jsonl.gz"
    with gzip.open(path, "wt", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in recs)
    return path


def baseline(tmp_path, count: int = 12, **kw):
    recs = [rec(i, 2 + i % 3, option_orders(2 + i % 3, "identity+reversed"), **kw) for i in range(count)]
    return write_collect(tmp_path / "baseline", recs)


def cyclic4(tmp_path, count: int = 12):
    recs = [rec(i, 2 + i % 3, option_orders(2 + i % 3, "cyclic:4"), rng=random.Random(100 + i), commit="c2")
            for i in range(count)]
    return write_collect(tmp_path / "cyc", recs, label="r3-cyclic4", orders="cyclic:4", commit="c2")


def text_fit(tmp_path, profile="gemma-4-31b"):
    fits = {p.name: {"choice": {"alpha": 2.5, "beta": 0.1} if p.combine == "tn-prob" else 2.0 + k / 100,
                     "score": 1.0, "noul": 1.0} for k, p in enumerate(POLICIES)}
    path = tmp_path / "text-summary.json"
    path.write_text(json.dumps({"meta": {"profile": profile, "layout": "header"},
                                "gate_T": {"choice": 1.5, "score": 1.0, "noul": 1.0}, "fits": fits}))
    return path


def test_merge_collects_unions_reads(tmp_path):
    recs, configs = vor.merge([baseline(tmp_path), cyclic4(tmp_path)])
    four = [r for r in recs if len(r["names"]) == 4]
    assert four and all(len(r["reads"]) == 5 for r in four)  # identity, reversed and shifts 1, 2, 3
    assert all(len({tuple(x["perm"]) for x in r["reads"]}) == len(r["reads"]) for r in recs)
    assert [c["orders"] for c in configs] == ["identity+reversed", "cyclic:4"]


def test_merge_refuses_other_stamp(tmp_path):
    other = [rec(i, 2, [[0, 1]], layout_sha256="zz") for i in range(12)]
    with pytest.raises(SystemExit, match="layout_sha256"):
        vor.merge([baseline(tmp_path), write_collect(tmp_path / "other", other, label="o")])


def test_merge_refuses_other_rows_and_holdout(tmp_path):
    fewer = write_collect(tmp_path / "few", [rec(i, 2, [[0, 1]]) for i in range(5)], label="few")
    with pytest.raises(SystemExit, match="row ids"):
        vor.merge([baseline(tmp_path), fewer])
    held = write_collect(tmp_path / "held", [rec(i, 2, [[0, 1]]) for i in range(5)], split="holdout")
    with pytest.raises(SystemExit, match="holdout"):
        vor.merge([held])


def run(tmp_path, collects: list, policies=PICKED):
    picked = [p for p in IMAGE_POLICIES if p.name in policies]
    argv = ["--profile", "gemma-4-31b", "--text-fit", str(text_fit(tmp_path)), "--out", str(tmp_path / "arms"),
            "--out-root", str(tmp_path / "results")]
    for c in collects:
        argv += ["--collect", str(c)]
    return vor.main(argv, picked)


def test_arm_dirs_readable_by_compare(tmp_path):
    result = run(tmp_path, [baseline(tmp_path), cyclic4(tmp_path)])
    dirs = sorted(p for p in (tmp_path / "arms").iterdir())
    assert len(dirs) == len(PICKED) + 6  # one cross-fit reference per combine rule and second order
    for d in dirs:
        rows, about = vc.load_offline(d)
        assert len(rows) == 12 and about["split"] == "dev" and about["arm"]
    out = result["out"]
    assert out.parent == tmp_path / "results" and out.name.endswith("-r3-orders-gemma-4-31b")
    compare = json.loads((out / "summary.json").read_text())
    assert compare["baseline"] == "identity" and set(compare["paired"]) == set(result["arms"]) - {"identity"}
    assert (out / "orders.md").exists() and json.loads((out / "orders.json").read_text())["skipped"] == {}


def test_extra_suffix_tokens(tmp_path):
    recs = [rec(i, 2 + 2 * (i % 2), option_orders(2 + 2 * (i % 2), "identity+reversed"), second_suffix=90)
            for i in range(12)]
    run(tmp_path, [write_collect(tmp_path / "b", recs)], ["identity", "min_n 3 reversed/mean-prob"])
    gated = json.loads((tmp_path / "arms" / vor.slug("min_n 3 reversed/mean-prob") / "arm.json").read_text())
    assert gated["mean_reads"] == 1.5 and gated["share_paying"] == 0.5
    assert gated["mean_extra_suffix_tokens"] == 45.0  # half the rows (n = 4) pay the second read's 90 tokens
    scored = {r["id"]: r for r in records(tmp_path / "arms" / vor.slug("min_n 3 reversed/mean-prob") / "scored.jsonl.gz")}
    assert scored["r1"]["input_tokens"] == 30 + 60 + 90 + 500 and scored["r0"]["input_tokens"] == 30 + 60 + 500
    identity = json.loads((tmp_path / "arms" / "identity" / "arm.json").read_text())
    assert identity["mean_extra_suffix_tokens"] == 0 and identity["share_paying"] == 0


def test_policy_needing_an_uncollected_perm_is_skipped(tmp_path, capsys):
    result = run(tmp_path, [baseline(tmp_path)])
    halves = {"always half/tn-prob", *(f"xfit always half/{rule}" for rule in ("mean-prob", "mean-logprob", "tn-prob"))}
    assert set(result["skipped"]) == halves
    assert result["skipped"]["always half/tn-prob"].startswith("needs cyclic:4 collect")
    assert "needs cyclic:4 collect" in capsys.readouterr().out
    assert not (tmp_path / "arms" / vor.slug("always half/tn-prob")).exists()
    assert len(list((tmp_path / "arms").iterdir())) == 3 + 3  # reversed references only


def test_half_policy_uses_the_reversed_text_fit(tmp_path):
    run(tmp_path, [baseline(tmp_path), cyclic4(tmp_path)])
    arm = json.loads((tmp_path / "arms" / vor.slug("always half/tn-prob") / "arm.json").read_text())
    assert arm["text_fit"] == {"from": "always reversed/tn-prob", "param": {"alpha": 2.5, "beta": 0.1}}
    own = json.loads((tmp_path / "arms" / vor.slug("always reversed/mean-prob") / "arm.json").read_text())
    assert own["text_fit"]["from"] == "always reversed/mean-prob" and own["gate_T"] == 1.5


def test_cross_fit_scores_each_fold_with_the_other(tmp_path):
    recs = [rec(i, 3, option_orders(3, "identity+reversed")) for i in range(160)]
    run(tmp_path, [write_collect(tmp_path / "b", recs)], ["identity"])
    arm = json.loads((tmp_path / "arms" / vor.slug("xfit always reversed/mean-prob") / "arm.json").read_text())
    folds = arm["folds"]
    assert {k: f["fitted_on"] for k, f in folds.items()} == {"0": "1", "1": "0"}
    assert all(not f["fallback"] and f["n"] >= 30 for f in folds.values())
    assert folds["0"]["param"] != folds["1"]["param"]
    small = [rec(i, 3, option_orders(3, "identity+reversed")) for i in range(12)]
    run(tmp_path / "s", [write_collect(tmp_path / "s" / "b", small)], ["identity"])
    tiny = json.loads((tmp_path / "s" / "arms" / vor.slug("xfit always reversed/mean-prob") / "arm.json").read_text())
    assert all(f["fallback"] for f in tiny["folds"].values()) and tiny["fallbacks"] == ["fold 0", "fold 1"]


def test_text_fit_of_another_profile_is_refused(tmp_path):
    argv = ["--profile", "gemma-4-31b", "--collect", str(baseline(tmp_path)), "--out", str(tmp_path / "a"),
            "--text-fit", str(text_fit(tmp_path, profile="qwen3.8-27b"))]
    with pytest.raises(SystemExit, match="qwen3.8-27b"):
        vor.main(argv)
