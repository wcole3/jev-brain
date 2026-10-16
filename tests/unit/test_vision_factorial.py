import json
import random
from itertools import product
from pathlib import Path

import pytest

from scripts import vision_compare as vc
from scripts import vision_factorial as vf
from scripts import vision_splits as vs
from tests.unit.test_vision_compare import latency_dir, write_offline

N = 240
BENCHES = ("CV-Bench", "BLINK", "R-Bench-M")
FACTORS = {"budget": ["560", "280", "1120"], "placement": ["current", "first"], "wording": ["none", "worded"]}
REFERENCE = {"budget": "560", "placement": "current", "wording": "none"}
RNG = random.Random(7)
BASE = [RNG.random() < 0.6 and i % 20 != 0 for i in range(N)]  # rows i % 20 == 0 start wrong


def no_effect(levels: dict, i: int) -> bool:
    return BASE[i]


@pytest.fixture(autouse=True)
def manifests(tmp_path, monkeypatch):
    splits = tmp_path / "splits"
    splits.mkdir()
    (splits / "vision-dev.json").write_text(json.dumps({"meta": {"suite_sha256": "x"},
                                                        "ids": [f"r{i}" for i in range(N)]}))
    monkeypatch.setattr(vs, "SPLITS", splits)
    monkeypatch.setattr(vs, "suite_hash", lambda: "x")
    monkeypatch.setattr(vf, "RESAMPLES", 2000)


def row(i: int, ok: bool) -> dict:
    """Four options (chance 0.25), two rows per image group, benchmarks interleaved."""
    probs = [0.7, 0.1, 0.1, 0.1] if ok else [0.1, 0.7, 0.1, 0.1]
    return {"id": f"r{i}", "benchmark": BENCHES[i % 3], "group": f"g{i // 6}.{i % 3}", "gold": 0, "probs": probs,
            "chance": 0.25}


def grid(tmp_path: Path, outcome=no_effect, ids=range(N), cells=None) -> Path:
    """A GRID.json over one offline dir per cell; outcome(levels, i) says whether row i is correct."""
    entries = []
    for values in product(*FACTORS.values()):
        levels = dict(zip(FACTORS, values, strict=True))
        path = write_offline(tmp_path / "cells" / "-".join(values), [row(i, outcome(levels, i)) for i in ids])
        entries.append({"dir": str(path)} | levels)
    doc = {"factors": FACTORS, "reference": REFERENCE, "cells": entries if cells is None else cells(entries)}
    (tmp_path / "GRID.json").write_text(json.dumps(doc))
    return tmp_path / "GRID.json"


def run(tmp_path: Path, path: Path, *extra: str) -> dict:
    return vf.main(["--grid", str(path), "--out-label", "t", "--out-root", str(tmp_path / "o"), *extra])


def effect(summary: dict, **levels) -> dict:
    (found,) = [e for e in summary["main_effects"] + summary["interactions"] if e["levels"] == levels]
    return found


def cell_index(tmp_path: Path, *values: str) -> float:
    rows, _ = vc.load_offline(tmp_path / "cells" / "-".join(values))
    return vc.index(rows)[0]


def test_main_effect_recovers_a_planted_effect(tmp_path):
    path = grid(tmp_path, lambda lv, i: BASE[i] or (lv["budget"] == "1120" and i % 20 == 0))
    summary = run(tmp_path, path)
    others = list(product(FACTORS["placement"], FACTORS["wording"]))
    direct = sum(cell_index(tmp_path, "1120", *o) - cell_index(tmp_path, "560", *o) for o in others) / len(others)
    high = effect(summary, budget="1120")
    assert direct > 1.0
    assert high["delta"] == pytest.approx(direct, abs=1e-9)
    assert 0 < high["ci"][0] < high["delta"] < high["ci"][1]
    assert all(v["delta"] > 0 and v["ci"][0] > 0 for v in high["skill"].values())  # 5% flipped in every benchmark
    assert effect(summary, budget="280") | {"skill": None} == {"levels": {"budget": "280"}, "delta": 0.0,
                                                              "ci": [0.0, 0.0], "skill": None}
    (folder,) = (tmp_path / "o").iterdir()
    md = (folder / "summary.md").read_text()
    assert "| budget | 1120 |" in md and "## Two-way interactions" in md and "## Per-benchmark main effects" in md


def test_null_factor_has_zero_effect_and_ci_covering_zero(tmp_path):
    # placement=first swaps a right row for a wrong one in the same benchmark: no net change, but noise
    swap = {i: i + 9 for i in range(0, N - 9, 30)}

    def outcome(lv, i):
        if lv["placement"] != "first":
            return BASE[i]
        partner = swap.get(i, next((k for k, v in swap.items() if v == i), None))
        return BASE[partner] if partner is not None else BASE[i]

    summary = run(tmp_path, grid(tmp_path, outcome))
    first = effect(summary, placement="first")
    assert first["delta"] == pytest.approx(0.0, abs=1e-9)
    assert first["ci"][0] < 0 < first["ci"][1]


def test_interaction_is_zero_for_additive_effects_and_nonzero_when_planted(tmp_path):
    def additive(lv, i):
        return BASE[i] or (lv["budget"] == "1120" and i % 40 == 0) or (lv["wording"] == "worded" and i % 40 == 20)

    summary = run(tmp_path, grid(tmp_path, additive))
    assert effect(summary, wording="worded")["delta"] > 0
    for e in summary["interactions"]:
        assert e["delta"] == pytest.approx(0.0, abs=1e-9) and e["ci"] == pytest.approx([0.0, 0.0], abs=1e-9)

    def planted(lv, i):  # worded helps only at budget 1120
        return BASE[i] or (lv["budget"] == "1120" and lv["wording"] == "worded" and i % 20 == 0)

    out = tmp_path / "planted"
    summary = run(out, grid(out, planted))
    direct = sum(cell_index(out, "1120", p, "worded") - cell_index(out, "1120", p, "none")
                 - cell_index(out, "560", p, "worded") + cell_index(out, "560", p, "none")
                 for p in FACTORS["placement"]) / 2
    both = effect(summary, budget="1120", wording="worded")
    assert direct > 1.0 and both["delta"] == pytest.approx(direct, abs=1e-9) and both["ci"][0] > 0
    assert effect(summary, budget="280", wording="worded")["delta"] == pytest.approx(0.0, abs=1e-9)
    assert effect(summary, budget="1120", placement="first")["delta"] == pytest.approx(0.0, abs=1e-9)
    assert len(summary["interactions"]) == 5  # budget×placement 2, budget×wording 2, placement×wording 1


@pytest.mark.parametrize("cells, error", [
    (lambda e: [c for c in e if c["dir"].split("/")[-1] != "280-first-worded"],
     "1 missing cell.*budget=280 placement=first wording=worded"),
    (lambda e: e + [e[3]], "duplicate cell budget=560 placement=first wording=worded"),
    (lambda e: [e[0] | {"budget": "2240"}] + e[1:], "unknown budget level '2240'"),
    (lambda e: [{k: v for k, v in e[0].items() if k != "wording"}] + e[1:], "wording"),
])
def test_missing_or_duplicate_cell_is_refused_naming_it(tmp_path, cells, error):
    with pytest.raises(SystemExit, match=error):
        run(tmp_path, grid(tmp_path, cells=cells))
    assert not (tmp_path / "o").exists()


def test_unknown_reference_level_is_refused(tmp_path):
    path = grid(tmp_path)
    doc = json.loads(path.read_text())
    path.write_text(json.dumps(doc | {"reference": REFERENCE | {"placement": "last"}}))
    with pytest.raises(SystemExit, match="reference: unknown placement level 'last'"):
        run(tmp_path, path)


def test_cells_on_different_ids_are_refused(tmp_path):
    path = grid(tmp_path)
    short = tmp_path / "short"
    write_offline(short, [row(i, BASE[i]) for i in range(N - 1)])
    doc = json.loads(path.read_text())
    doc["cells"][5]["dir"] = str(short)
    path.write_text(json.dumps(doc))
    with pytest.raises(SystemExit, match="budget=280 placement=current wording=worded: ids differ") as e:
        run(tmp_path, path)
    assert "1 missing" in str(e.value) and "r239" in str(e.value)


def test_cells_scored_by_different_arms_are_refused(tmp_path):
    path = grid(tmp_path)
    arm = Path(json.loads(path.read_text())["cells"][2]["dir"]) / "arm.json"
    arm.write_text(json.dumps(json.loads(arm.read_text()) | {"arm": "fit-T"}))
    with pytest.raises(SystemExit, match="different arms"):
        run(tmp_path, path)


def test_latency_attaches_per_budget_level_under_compare_power_rules(tmp_path):
    path = grid(tmp_path)
    lat = latency_dir(tmp_path / "lat-1120", power_limit_w=510, power_limit_w_end=510)
    summary = run(tmp_path, path, "--latency", f"1120={lat}")
    timed = {c["name"]: c["latency"] for c in summary["cells"]}
    assert all((t is not None) == ("budget=1120" in n) for n, t in timed.items())
    assert timed["budget=1120 placement=first wording=none"]["p80"] == 1000.0 and summary["power_limit_w"] == 510
    other = latency_dir(tmp_path / "lat-560")
    with pytest.raises(SystemExit, match="power limit"):
        run(tmp_path / "again", path, "--latency", f"1120={lat}", "--latency", f"560={other}")
    with pytest.raises(SystemExit, match="not budget levels"):
        run(tmp_path / "again", path, "--latency", f"720={other}")
