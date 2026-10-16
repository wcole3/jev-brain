import gzip
import hashlib
import json
import math
import random

import pytest

from gateway.calibration import Calibration
from gateway.decide import blend, probabilities
from scripts import vision_offline as vo
from scripts import vision_splits as vs
from scripts.collect import records


@pytest.fixture(autouse=True)
def holdout_log(tmp_path, monkeypatch):
    """Holdout looks in tests land in tmp, never in the committed log."""
    monkeypatch.setattr(vs, "HOLDOUT_LOG", tmp_path / "holdout-log.md")
    return tmp_path / "holdout-log.md"


TEXT = Calibration({"choice": 3.0, "score": 1.0, "noul": 1.0}, source="p/header/calibration.json")


def log_softmax(z: list[float]) -> list[float]:
    top = max(z)
    total = top + math.log(sum(math.exp(x - top) for x in z))
    return [x - total for x in z]


def rec(i: int, logprobs: list[list[float]], gold: int | None, *, benchmark="B", group=None,
        perms=None, status="ok") -> dict:
    n = len(logprobs[0])
    perms = perms or [list(range(n)), list(range(n))[::-1]][: len(logprobs)]
    reads = [{"perm": p, "logprobs": lp, "suffix_len": 7 + k} for k, (p, lp) in enumerate(zip(perms, logprobs, strict=True))]
    return {"id": f"r{i}", "benchmark": benchmark, "group": group or f"g{i}", "layout": "header", "status": status,
            "names": [f"o{j}" for j in range(n)], "gold": gold, "input_tokens": 10, "shared_len": 5,
            "padded": False, "unpadded_len": 5, "image_tokens": 100, "images_shared": False, "reads": reads,
            "stamp": {"profile": "gemma-4-31b", "layout": "header"}}


def planted(bases: int, seed: int, *, T: float = 1.0, bias: float = 0.0, copies: int = 10, benchmark="B") -> list[dict]:
    """Each base z in all 4 rotations (one group), gold j repeated ∝ softmax(z): the fit's optimum is exact.
    The model reads T·z (overconfident when T > 1) plus a bias on position 0."""
    rng, out = random.Random(seed), []
    for b in range(bases):
        z = [rng.gauss(0, 1.0) for _ in range(4)]
        for r in range(4):
            zr = z[r:] + z[:r]
            lp = [x + (bias if j == 0 else 0.0) for j, x in enumerate(log_softmax([T * x for x in zr]))]
            for gold, p in enumerate(math.exp(x) for x in log_softmax(zr)):
                out += [rec(len(out), [lp], gold, benchmark=benchmark, group=f"{benchmark}{b}")] * round(p * copies)
    return [r | {"id": f"{benchmark}:{i}"} for i, r in enumerate(out)]


def by_id(scored: list[dict]) -> dict[str, dict]:
    return {s["id"]: s for s in scored}


def test_text_arm_reproduces_gateway_probabilities():
    rng = random.Random(1)
    recs = [rec(i, [[rng.gauss(0, 3) for _ in range(5)] for _ in range(2)], rng.randrange(5)) for i in range(20)]
    scored, report = vo.score(recs, "text", "identity+reversed", TEXT)
    for r, s in zip(recs, scored, strict=True):
        reads = [(x["logprobs"], x["perm"]) for x in r["reads"]]
        assert s["probs"] == probabilities(reads, "choice", TEXT)
        assert s | {"probs": None} == {"id": r["id"], "benchmark": "B", "group": r["group"], "gold": r["gold"],
                                       "probs": None, "chance": 0.2, "input_tokens": 5 + 7 + 8 + 2 * 100}
    assert report["arm"] == "text" and report["folds"] is None and report["fallbacks"] == []


@pytest.mark.parametrize("arm", ["fit-T", "fit-T-bench", "pride"])
def test_cross_fit_never_scores_a_row_with_its_own_fold(arm):
    recs = planted(10, seed=2, T=2.0, bias=0.5)
    target = recs[0]
    own = vo.fold(target["group"])
    before = by_id(vo.score(recs, arm, "identity", TEXT)[0])[target["id"]]["probs"]

    def shaken(r: dict) -> dict:
        lp = r["reads"][0]["logprobs"]
        read = {"perm": [0, 1, 2, 3], "logprobs": [3 * x for x in lp[::-1]], "suffix_len": 7}
        return r | {"reads": [read], "gold": 3 - r["gold"]}

    same = [shaken(r) if vo.fold(r["group"]) == own and r is not target else r for r in recs]
    other = [shaken(r) if vo.fold(r["group"]) != own else r for r in recs]
    assert by_id(vo.score(same, arm, "identity", TEXT)[0])[target["id"]]["probs"] == before
    assert by_id(vo.score(other, arm, "identity", TEXT)[0])[target["id"]]["probs"] != before


def test_folds_hash_the_group_key():
    assert vo.fold("bench:7") == int(hashlib.sha256(b"fold:bench:7").hexdigest(), 16) % 2


def test_fit_T_recovers_a_planted_temperature():
    _, report = vo.score(planted(30, seed=3, T=2.0, copies=50), "fit-T", "identity", TEXT)
    for f in report["folds"].values():
        assert f["T"] == pytest.approx(2.0, abs=0.1) and not f["fallback"] and f["n"] >= 30
    assert report["fallbacks"] == []


def test_pride_removes_a_planted_letter_bias():
    _, report = vo.score(planted(30, seed=4, bias=1.0, copies=50), "pride", "identity", TEXT)
    for f in report["folds"].values():
        prior = f["prior"]["4"]
        assert prior[0] - sum(prior[1:]) / 3 == pytest.approx(1.0, abs=0.1)
        assert f["T"] == pytest.approx(1.0, abs=0.1)


def test_pride_k_unseen_in_the_fitting_fold_uses_no_prior():
    recs = planted(10, seed=5, bias=1.0)
    two = next(r for r in recs if vo.fold(r["group"]) == 0) | {"id": "two", "names": ["a", "b"], "gold": 0,
                                                                  "reads": [{"perm": [0, 1], "logprobs": [0.0, -1.0], "suffix_len": 7}]}
    scored, report = vo.score([*recs, two], "pride", "identity", TEXT)
    assert "2" not in report["folds"]["0"]["prior"]
    assert by_id(scored)["two"]["probs"] == blend([([0.0, -1.0], [0, 1])], report["folds"]["0"]["T"])


def test_tiny_fold_falls_back_to_text_T_and_says_so():
    recs = planted(1, seed=6, copies=5)
    text = by_id(vo.score(recs, "text", "identity", TEXT)[0])
    for arm in ("fit-T", "pride"):
        scored, report = vo.score(recs, arm, "identity", TEXT)
        assert all(f["fallback"] and f["T"] == 3.0 for f in report["folds"].values())
        assert sorted(report["fallbacks"]) == ["fold 0", "fold 1"]
        assert by_id(scored) == text
    big, tiny = planted(10, seed=7, T=2.0, benchmark="Big"), planted(3, seed=8, copies=2, benchmark="Tiny")
    _, report = vo.score(big + tiny, "fit-T-bench", "identity", TEXT)
    for f in report["folds"].values():
        assert f["benchmarks"]["Tiny"] == {"n": f["benchmarks"]["Tiny"]["n"], "T": 3.0, "fallback": True}
        assert not f["benchmarks"]["Big"]["fallback"]
    assert sorted(report["fallbacks"]) == ["fold 0 / Tiny", "fold 1 / Tiny"]


def test_orders_subset_uses_only_collected_perms():
    both = rec(1, [[0.0, -1.0, -2.0], [-3.0, 0.0, -1.0]], 0)
    scored, _ = vo.score([both], "text", "identity", TEXT)
    assert scored[0]["probs"] == probabilities([([0.0, -1.0, -2.0], [0, 1, 2])], "choice", TEXT)
    only = rec(2, [[0.0, -1.0, -2.0]], 0)
    with pytest.raises(ValueError, match="r2"):
        vo.score([both, only], "text", "identity+reversed", TEXT)
    with pytest.raises(ValueError, match="unknown option_orders"):
        vo.score([], "text", "sideways", TEXT)


@pytest.mark.parametrize("shared, orders, want", [
    (False, "identity", 5 + 7 + 100), (False, "identity+reversed", 5 + 7 + 8 + 200),
    (True, "identity", 5 + 7 + 100), (True, "identity+reversed", 5 + 7 + 8 + 100)])
def test_input_tokens_count_only_the_arm_reads(shared, orders, want):
    r = rec(0, [[0.0, -1.0, -2.0], [-2.0, -1.0, 0.0]], 0) | {"images_shared": shared}
    assert vo.score([r], "text", orders, TEXT)[0][0]["input_tokens"] == want


def test_old_records_without_token_fields_give_no_input_tokens():
    r = rec(0, [[0.0, -1.0]], 0)
    old = {k: v for k, v in r.items() if k not in ("unpadded_len", "image_tokens", "images_shared")}
    old["reads"] = [{"perm": x["perm"], "logprobs": x["logprobs"]} for x in r["reads"]]
    assert vo.score([old], "text", "identity", TEXT)[0][0]["input_tokens"] is None


def test_unscored_rows_are_counted_per_status():
    recs = [rec(0, [[0.0, -1.0]], 0), rec(1, [[0.0, -1.0]], None), rec(2, [[0.0, -1.0]], None, status="unsupported"),
            rec(3, [[0.0, -1.0]], None, status="invalid") | {"names": [], "reads": []}]
    scored, report = vo.score(recs, "text", "identity", TEXT)
    assert [s["id"] for s in scored] == ["r0"]
    assert report["skipped"] == {"no_gold": 1, "unsupported": 1, "invalid": 1}


CONFIG = {"profile": "gemma-4-31b", "label": "x", "layout": "header", "orders": "identity+reversed", "env": {}}


def write_collect(folder, split: str, recs: list[dict], **config) -> object:
    """A label folder as collect leaves it: <split>.jsonl.gz, <split>.config.json, and config.json from the first."""
    folder.mkdir(parents=True, exist_ok=True)
    config = CONFIG | {"split": split, "commit": "abc"} | config
    (folder / f"{split}.config.json").write_text(json.dumps(config))
    if not (folder / "config.json").exists():
        (folder / "config.json").write_text(json.dumps(config))
    path = folder / f"{split}.jsonl.gz"
    with gzip.open(path, "wt", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in recs)
    return path


def test_cli_writes_scored_rows_and_arm_report(tmp_path):
    write_collect(tmp_path / "x", "holdout", planted(1, seed=10, copies=5))  # first split: owns config.json
    recs = planted(2, seed=9, copies=5)
    collect = write_collect(tmp_path / "x", "dev", recs)
    out = tmp_path / "out"
    vo.main(["--collect", str(collect), "--arm", "fit-T", "--out", str(out)])
    scored = list(records(out / "scored.jsonl.gz"))
    arm = json.loads((out / "arm.json").read_text())
    assert [s["id"] for s in scored] == [r["id"] for r in recs]
    assert arm["arm"] == "fit-T" and arm["orders"] == "identity" and arm["fit_on"] is None
    assert arm["collect_config"] == CONFIG | {"split": "dev", "commit": "abc"}
    assert arm["collect"] == str(collect) and arm["commit"] and set(arm["folds"]) == {"0", "1"}
    text = arm["text_calibration"]
    assert text["source"] == "gemma-4-31b/header/calibration.json" and text["orders"] == "identity"
    assert text["stamp_checked"] is False


def test_holdout_fitted_arm_needs_fit_on(tmp_path):
    holdout = write_collect(tmp_path / "x", "holdout", planted(2, seed=11, copies=5))
    for arm in ("fit-T", "fit-T-bench", "pride"):
        with pytest.raises(SystemExit, match="--fit-on"):
            vo.main(["--collect", str(holdout), "--arm", arm, "--holdout", "--out", str(tmp_path / "out")])
    vo.main(["--collect", str(holdout), "--arm", "text", "--holdout", "--out", str(tmp_path / "out")])


def test_fit_on_scores_holdout_with_dev_fitted_values_only(tmp_path):
    dev, holdout = planted(10, seed=12, T=2.0), planted(5, seed=13, T=0.5, benchmark="H")
    flipped = [r | {"gold": (r["gold"] + 1) % 4} for r in holdout]
    rows, report = vo.score(holdout, "fit-T", "identity", TEXT, fit_on=dev)
    rows2, report2 = vo.score(flipped, "fit-T", "identity", TEXT, fit_on=dev)
    assert report["folds"] == report2["folds"] and set(report["folds"]) == {"dev"}
    assert report["folds"]["dev"]["n"] == len(dev)
    assert [r["probs"] for r in rows] == [r["probs"] for r in rows2] and len(rows) == len(holdout)
    assert report["folds"]["dev"]["T"] == vo.score(dev, "fit-T", "identity", TEXT, fit_on=dev)[1]["folds"]["dev"]["T"]
    dev_path = write_collect(tmp_path / "x", "dev", dev, orders="identity")
    holdout_path = write_collect(tmp_path / "x", "holdout", holdout, orders="identity")
    out = tmp_path / "out"
    arm = vo.main(["--collect", str(holdout_path), "--arm", "fit-T", "--fit-on", str(dev_path), "--holdout",
                   "--out", str(out)])
    assert arm["fit_on"] == str(dev_path) and arm["folds"] == report["folds"]


def test_fit_on_refused_on_a_dev_collect_and_from_another_config(tmp_path):
    dev = write_collect(tmp_path / "x", "dev", planted(2, seed=14, copies=5))
    with pytest.raises(SystemExit, match="holdout"):
        vo.main(["--collect", str(dev), "--arm", "fit-T", "--fit-on", str(dev), "--out", str(tmp_path / "o")])
    holdout = write_collect(tmp_path / "x", "holdout", planted(2, seed=15, copies=5))
    for key, value in (("profile", "qwen3.8-27b"), ("layout", "other"), ("orders", "identity"),
                       ("env", {"MM_PROCESSOR_KWARGS": "{\"max_pixels\": 1}"})):
        other = write_collect(tmp_path / key, "dev", planted(2, seed=14, copies=5), **{key: value})
        with pytest.raises(SystemExit, match=key):
            vo.main(["--collect", str(holdout), "--arm", "fit-T", "--fit-on", str(other), "--holdout",
                     "--out", str(tmp_path / "o")])
    not_dev = write_collect(tmp_path / "y", "latency", planted(2, seed=14, copies=5))
    with pytest.raises(SystemExit, match="dev"):
        vo.main(["--collect", str(holdout), "--arm", "fit-T", "--fit-on", str(not_dev), "--holdout",
                 "--out", str(tmp_path / "o")])


def test_non_choice_rows_are_refused_naming_the_row():
    noul = rec(5, [[0.0, -1.0]], 0) | {"names": [False, True]}
    with pytest.raises(ValueError, match="r5"):
        vo.score([noul], "text", "identity", TEXT)
    score_type = rec(6, [[0.0, -1.0]], 0) | {"type": "score"}
    with pytest.raises(ValueError, match="r6"):
        vo.score([score_type], "text", "identity", TEXT)


def test_pride_prior_needs_30_reads_per_option_count():
    recs = planted(10, seed=16, bias=1.0)
    twos = [rec(100 + i, [[0.0, -1.0]], 0, group=f"two{i}") for i in range(40)]
    _, report = vo.score(recs + twos, "pride", "identity", TEXT)
    for k, f in report["folds"].items():
        n2 = sum(vo.fold(r["group"]) != int(k) for r in twos)
        assert f["prior_reads"]["2"] == n2 and ("2" in f["prior"]) == (n2 >= 30)
        assert f["prior_reads"]["4"] >= 30 and "4" in f["prior"]
    assert any(f["prior_reads"]["2"] < 30 for f in report["folds"].values())


def test_text_calibration_orders_are_recorded_and_a_mismatch_warns(tmp_path, capsys):
    recs = [rec(i, [[0.0, -1.0, -2.0], [-2.0, -1.0, 0.0]], 0) for i in range(3)]
    collect = write_collect(tmp_path / "x", "dev", recs)
    vo.main(["--collect", str(collect), "--arm", "text", "--out", str(tmp_path / "a")])
    assert "fitted under option orders" not in capsys.readouterr().err
    arm = vo.main(["--collect", str(collect), "--arm", "text", "--orders", "identity+reversed",
                   "--out", str(tmp_path / "b")])
    assert arm["text_calibration"]["orders"] == "identity"
    assert "fitted under option orders 'identity'" in capsys.readouterr().err


def test_holdout_collect_needs_the_flag_and_is_logged(tmp_path, holdout_log):
    holdout = write_collect(tmp_path / "x", "holdout", planted(2, seed=17, copies=5))
    with pytest.raises(SystemExit, match="--holdout"):
        vo.main(["--collect", str(holdout), "--arm", "text", "--out", str(tmp_path / "o")])
    assert not holdout_log.exists() and not (tmp_path / "o").exists()
    vo.main(["--collect", str(holdout), "--arm", "text", "--holdout", "--out", str(tmp_path / "o")])
    (entry,) = holdout_log.read_text().splitlines()[2:]
    assert "| vision_offline | x text identity |" in entry


def test_refused_holdout_run_logs_nothing(tmp_path, holdout_log):
    holdout = write_collect(tmp_path / "x", "holdout", planted(2, seed=18, copies=5))
    with pytest.raises(SystemExit, match="--fit-on"):
        vo.main(["--collect", str(holdout), "--arm", "fit-T", "--holdout", "--out", str(tmp_path / "o")])
    assert not holdout_log.exists()


def test_dev_collect_logs_nothing(tmp_path, holdout_log):
    dev = write_collect(tmp_path / "x", "dev", planted(2, seed=19, copies=5))
    vo.main(["--collect", str(dev), "--arm", "text", "--out", str(tmp_path / "o")])
    assert not holdout_log.exists()


def restamped(recs: list[dict], **stamp) -> list[dict]:
    return [r | {"stamp": r["stamp"] | stamp} for r in recs]


def test_fit_on_refuses_a_dev_collect_with_other_stamps(tmp_path):
    holdout = write_collect(tmp_path / "h", "holdout", restamped(planted(2, seed=20, copies=5), commit="aaa"))
    other = restamped(planted(2, seed=21, copies=5), labels_sha256="other", layout_sha256="x", commit="bbb")
    dev = write_collect(tmp_path / "d", "dev", other)
    with pytest.raises(SystemExit) as e:
        vo.main(["--collect", str(holdout), "--arm", "fit-T", "--fit-on", str(dev), "--holdout",
                 "--out", str(tmp_path / "o")])
    assert "labels_sha256" in str(e.value) and "layout_sha256" in str(e.value) and "commit" not in str(e.value)
    same = write_collect(tmp_path / "s", "dev", restamped(planted(2, seed=21, copies=5), commit="bbb"))
    vo.main(["--collect", str(holdout), "--arm", "fit-T", "--fit-on", str(same), "--holdout",
             "--out", str(tmp_path / "o")])


def write_calibration(path, T: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    types = {t: {"T": T} for t in ("choice", "score", "noul")}
    path.write_text(json.dumps({"format": 2, "stamp": {}, "types": types}))


def test_text_calibration_follows_the_collect_env(tmp_path):
    data = tmp_path / "data"
    write_calibration(data / "gemma-4-31b" / "header" / "calibration.json", 2.0)
    write_calibration(data / "gemma-4-31b" / "header" / "calibration-800.json", 5.0)
    env = {"DATA_ROOT": str(data), "PREFIX_BLOCK": "800"}
    collect = write_collect(tmp_path / "x", "dev", planted(1, seed=22, copies=5), env=env)
    arm = vo.main(["--collect", str(collect), "--arm", "text", "--out", str(tmp_path / "o")])
    assert arm["text_calibration"]["T"] == 5.0 and arm["text_calibration"]["path"].endswith("calibration-800.json")


def test_arm_json_paths_are_absolute(tmp_path, monkeypatch):
    collect = write_collect(tmp_path / "x", "dev", planted(1, seed=23, copies=5))
    monkeypatch.chdir(tmp_path)
    arm = vo.main(["--collect", "x/dev.jsonl.gz", "--arm", "text", "--out", "o"])
    assert arm["collect"] == str(collect.resolve())
