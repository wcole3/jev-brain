import gzip
import json
import random
from pathlib import Path

import pytest

from scripts import vision_compare as vc
from scripts import vision_splits as vs

STORED = Path("docs/results/gemma-4-31b/2026-10-16T023752Z-vision")


def row(i, gold: int, probs: list[float], *, bench="CV-Bench", group=None) -> dict:
    return {"id": f"r{i}", "benchmark": bench, "group": group or f"g{i}", "gold": gold, "probs": probs,
            "chance": 1 / len(probs)}


def hit(i, ok: bool, **kw) -> dict:
    return row(i, 0, [0.8, 0.2] if ok else [0.3, 0.7], **kw)


def write_offline(path: Path, rows: list[dict]) -> Path:
    path.mkdir(parents=True)
    with gzip.open(path / "scored.jsonl.gz", "wt") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    (path / "arm.json").write_text(json.dumps({"arm": "text", "orders": "identity", "skipped": {}, "fallbacks": [],
                                               "collect_config": {"split": "dev"}}))
    return path


def write_live(path: Path, results: list[dict]) -> Path:
    path.mkdir(parents=True)
    with gzip.open(path / "results.jsonl.gz", "wt") as f:
        f.writelines(json.dumps(r) + "\n" for r in results)
    return path


def ok_result(rid: str, probs: dict, tokens=100) -> dict:
    answer = {"type": "choice", "choice": max(probs, key=probs.__getitem__), "probabilities": probs}
    return {"run_id": rid, "benchmark": "CV-Bench", "status": "ok",
            "response": {"answers": {"answer": answer}, "usage": {"input_tokens": tokens}}}


def fake_suite(tmp_path, monkeypatch, n: int) -> None:
    rows = [{"id": f"r{i}", "benchmark": "CV-Bench", "images": [f"img{i}.png"], "state": {},
             "questions": {"answer": {"type": "choice", "instructions": "q", "criteria": {"A": "x", "B": "y"}}},
             "expected": {"answer": "A"}} for i in range(n)]
    path = tmp_path / "vision-rows.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    monkeypatch.setattr(vs, "SUITE", path)


def summary_of(out_root: Path) -> dict:
    (folder,) = out_root.iterdir()
    assert (folder / "summary.md").exists()
    return json.loads((folder / "summary.json").read_text())


@pytest.mark.skipif(not vs.SUITE.exists() or not STORED.exists(), reason="vision suite or stored run absent")
def test_index_matches_the_kit_on_stored_results():
    rows, _ = vc.load_live(STORED, vc.suite_by_id())
    value, skills = vc.index(rows)
    kit = json.loads((STORED / "vision-scores.json").read_text())
    assert len(rows) == 12210
    assert value == pytest.approx(73.70, abs=0.005)
    assert value == pytest.approx(kit["public_vision_index"], abs=1e-9)
    assert skills == pytest.approx({b: v["skill"] for b, v in kit["benchmarks"].items()}, abs=1e-12)


def test_mcnemar_exact_on_known_counts():
    assert vc.mcnemar_p(10, 2) == pytest.approx(2 * 79 / 4096)
    assert vc.mcnemar_p(10, 2) == pytest.approx(0.0386, abs=1e-4)
    assert vc.mcnemar_p(2, 10) == vc.mcnemar_p(10, 2)
    assert vc.mcnemar_p(0, 0) == 1.0
    a = [hit(i, i < 10) for i in range(14)]
    b = [hit(i, 10 <= i < 12) for i in range(14)]
    out = vc.paired(a, b, resamples=200)
    assert (out["b"], out["c"]) == (10, 2)
    assert out["mcnemar_p"] == pytest.approx(0.0386, abs=1e-4)
    assert out["discordant_share"] == pytest.approx(12 / 14)
    assert out["agreement"] == pytest.approx(2 / 14)  # rows 12 and 13: same top answer, both wrong


def test_bootstrap_ci_resamples_groups_within_benchmarks():
    rng = random.Random(3)
    base = [(i, bench, rng.random() < 0.6, rng.random() < 0.7) for bench in ("CV-Bench", "BLINK") for i in range(40)]

    def configs(copies: int, own_groups: bool):
        a, b = [], []
        for i, bench, ok_a, ok_b in base:
            for k in range(copies):
                group = f"{bench}{i}.{k}" if own_groups else f"{bench}{i}"
                rid = f"{bench}{i}.{k}"
                a.append(hit(rid, ok_a, bench=bench, group=group))
                b.append(hit(rid, ok_b, bench=bench, group=group))
        return a, b

    once = vc.paired(*configs(1, False), resamples=2000)
    in_group = vc.paired(*configs(3, False), resamples=2000)
    own = vc.paired(*configs(3, True), resamples=2000)
    assert in_group["delta_index"] == pytest.approx(once["delta_index"])
    assert in_group["ci"] == pytest.approx(once["ci"])
    assert in_group["delta_skill"]["BLINK"]["ci"] == pytest.approx(once["delta_skill"]["BLINK"]["ci"])
    width = once["ci"][1] - once["ci"][0]
    assert own["ci"][1] - own["ci"][0] < 0.8 * width  # rows counted as independent would narrow it


def test_identical_configs_give_zero_delta_and_p_one():
    rng = random.Random(5)
    rows = [row(i, rng.randrange(3), [rng.random() for _ in range(3)], bench=rng.choice(["CV-Bench", "BLINK"]))
            for i in range(60)]
    rows = [r | {"probs": [p / sum(r["probs"]) for p in r["probs"]]} for r in rows]
    out = vc.paired(rows, list(reversed(rows)), resamples=500)
    assert out["delta_index"] == 0.0 and out["ci"] == [0.0, 0.0]
    assert out["mcnemar_p"] == 1.0 and out["discordant_share"] == 0.0 and out["agreement"] == 1.0
    assert out["delta_ece"] == 0.0 and out["delta_nll"] == 0.0
    assert all(v == {"delta": 0.0, "ci": [0.0, 0.0]} for v in out["delta_skill"].values())


def test_different_ids_are_refused_with_examples(tmp_path, capsys):
    base = write_offline(tmp_path / "base", [hit(i, True) for i in range(30)])
    other = write_offline(tmp_path / "other", [hit(i, True) for i in range(5, 45)])
    with pytest.raises(SystemExit) as e:
        vc.main(["--baseline", f"base={base}", f"other={other}", "--out-label", "t", "--out-root", str(tmp_path / "o")])
    msg = str(e.value)
    assert "other" in msg and "r0" in msg and "r35" in msg
    assert "5 missing" in msg and "15 extra" in msg
    assert "r39" in msg and "r40" not in msg  # at most 10 examples each way
    assert not (tmp_path / "o").exists()


def test_live_baseline_against_offline_hints_the_order(tmp_path, monkeypatch):
    fake_suite(tmp_path, monkeypatch, 8)
    live = write_live(tmp_path / "live", [ok_result(f"r{i}", {"A": 0.9, "B": 0.1}) for i in range(8)])
    arm = write_offline(tmp_path / "arm", [hit(i, True) for i in range(4)])
    with pytest.raises(SystemExit, match="put the offline arm first as --baseline"):
        vc.main(["--baseline", f"live={live}", f"arm={arm}", "--out-label", "t", "--out-root", str(tmp_path / "o")])


def test_errored_live_rows_count_as_wrong_and_are_reported(tmp_path, monkeypatch):
    fake_suite(tmp_path, monkeypatch, 8)
    base = write_offline(tmp_path / "base", [hit(i, True) for i in range(8)])
    results = [ok_result(f"r{i}", {"A": 0.9, "B": 0.1}) for i in range(5)]
    results += [{"run_id": "r5", "benchmark": "CV-Bench", "status": "error", "response": None}]
    results += [{"run_id": "r6", "benchmark": "CV-Bench", "status": "ok", "response": {"answers": {}}}]
    results += [{"run_id": "r7", "benchmark": "CV-Bench", "status": "error"}, ok_result("r7", {"A": 0.6, "B": 0.4})]
    results += [ok_result("r99", {"A": 1.0, "B": 0.0})]  # outside the baseline's ids: dropped
    live = write_live(tmp_path / "live", results)
    rows, about = vc.load_live(live, vc.suite_by_id(), keep={f"r{i}" for i in range(8)})
    by = {r["id"]: r for r in rows}
    assert by["r5"]["probs"] == [0.5, 0.5] and not vc.correct(by["r5"])  # uniform, gold A, still wrong
    assert not vc.correct(by["r6"]) and vc.correct(by["r7"])  # last row per run_id wins
    assert about["errored"] == 2 and "r99" not in by
    vc.main(["--baseline", f"base={base}", f"live={live}", "--out-label", "t", "--out-root", str(tmp_path / "o")])
    summary = summary_of(tmp_path / "o")
    assert summary["configs"]["live"]["errored"] == 2 and summary["configs"]["base"]["errored"] == 0
    assert summary["configs"]["live"]["accuracy"] == pytest.approx(6 / 8)
    assert summary["paired"]["live"]["b"] == 2 and summary["paired"]["live"]["c"] == 0
    assert summary["paired"]["live"]["agreement"] == pytest.approx(6 / 8)  # an errored row agrees with nothing
    assert summary["configs"]["live"]["mean_input_tokens"] == 100


def latency_dir(path: Path, **summary) -> Path:
    """A latency run folder shaped like vision_summary's summary.json plus Task 5's power limits."""
    path.mkdir()
    full = {"status": {"ok": 300}, "latency_ms": {"median": 900.0, "mean": 950.0, "p80": 1000.0},
            "calibration": {"ece": None, "accuracy": None, "n": 0}, "power_limit_w": 600, "power_limit_w_end": 600}
    (path / "summary.json").write_text(json.dumps({k: v for k, v in (full | summary).items() if v != "drop"}))
    return path


def test_mixed_power_limits_are_refused(tmp_path):
    base = write_offline(tmp_path / "base", [hit(i, True) for i in range(6)])
    other = write_offline(tmp_path / "other", [hit(i, i % 2 == 0) for i in range(6)])
    lat = {"base": latency_dir(tmp_path / "lat-base"),
           "other": latency_dir(tmp_path / "lat-other", power_limit_w=510, power_limit_w_end=510)}
    argv = ["--baseline", f"base={base}", f"other={other}", "--out-label", "t", "--out-root", str(tmp_path / "o")]
    with pytest.raises(SystemExit, match="power limit"):
        vc.main(argv + ["--latency", f"base={lat['base']}", "--latency", f"other={lat['other']}"])
    assert not (tmp_path / "o").exists()
    vc.main(argv + ["--latency", f"base={lat['base']}"])
    summary = summary_of(tmp_path / "o")
    assert summary["configs"]["base"]["latency"]["p80"] == 1000.0 and summary["configs"]["other"]["latency"] is None
    assert summary["power_limit_w"] == 600


@pytest.mark.parametrize("summary, error", [
    ({"latency_ms": None}, "no latency"),
    ({"latency_ms": "drop"}, "no latency"),
    ({"power_limit_w": "drop"}, "power_limit_w"),
    ({"power_limit_w_end": "drop"}, "power_limit_w"),
    ({"power_limit_w_end": 510}, "changed mid-run"),
])
def test_latency_dir_without_latency_or_steady_power_limit_is_refused(tmp_path, summary, error):
    lat = latency_dir(tmp_path / "lat", **summary)
    with pytest.raises(SystemExit, match=error) as e:
        vc.load_latency({"base": lat})
    assert str(lat) in str(e.value)


@pytest.mark.skipif(not STORED.exists(), reason="stored run absent")
def test_pre_task5_live_summary_is_refused_for_lacking_a_power_limit():
    with pytest.raises(SystemExit, match="power_limit_w"):
        vc.load_latency({"live": STORED})
