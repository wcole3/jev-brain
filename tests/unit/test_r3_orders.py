import gzip
import json
import random

import pytest

from gateway.calibration import Calibration
from scripts import r3_orders
from scripts.collect import all_orders, records
from scripts.offline import Arm, evaluate
from scripts.order_policies import POLICIES

SHIPPED = Calibration({"choice": 2.0, "score": 1.0, "noul": 1.5}, source="p/header/calibration.json")
PICKED = ["identity", "always reversed/mean-prob", "top_p 0.7 reversed/mean-logprob", "aleria half/tn-prob"]


def row(prefix: str, i: int) -> dict:
    n = 2 + i % 4
    criteria = {chr(97 + k): None for k in range(n)}
    return {"id": f"{prefix}{i}", "source": "index", "family": "fg"[i % 2], "state": "s",
            "questions": {"c": {"type": "choice", "instructions": "pick", "criteria": criteria},
                          "y": {"type": "noul", "instructions": "is it?"}},
            "gold": {"c": chr(97 + i % n), "y": i % 3 == 0}}


def reads(rng: random.Random, n: int, liked: int) -> list[dict]:
    """The model likes one option and shown position 0, by amounts that vary per read."""
    return [{"perm": perm, "logprobs": [2.0 * (perm[j] == liked) + rng.random() * (j == 0) - rng.random()
                                        for j in range(n)]} for perm in all_orders(n)]


def collect(path, prefix: str, count: int = 30, seed: int = 0) -> dict:
    rng, rows = random.Random(seed), [row(prefix, i) for i in range(count)]
    with gzip.open(path, "wt") as f:
        for i, r in enumerate(rows):
            n = len(r["questions"]["c"]["criteria"])
            qs = {"c": reads(rng, n, rng.choice([i % n, 0])), "y": reads(rng, 2, i % 2)}
            f.write(json.dumps({"id": r["id"], "layout": "header", "status": "ok", "stamp": {}, "questions": qs}) + "\n")
        f.write(json.dumps({"id": "other", "layout": "decider_chat", "status": "ok", "stamp": {}, "questions": {}}) + "\n")
    return {r["id"]: r for r in rows}


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("r3")
    loaded = {}
    for split, seed in (("calib", 1), ("index-dev", 2), ("eval", 3)):
        rows = collect(tmp / f"{split}.jsonl.gz", split[0], seed=seed)
        loaded[split] = list(records(tmp / f"{split}.jsonl.gz")), rows
    policies = [p for p in POLICIES if p.name in PICKED]
    calib, splits = loaded.pop("calib"), loaded
    return r3_orders.report(calib, splits, SHIPPED, policies), splits


def test_report_on_fixture(run):
    report, splits = run
    T = report["fits"]["identity"]
    for split, (recs, rows) in splits.items():
        expect = evaluate(recs, rows, Arm("header", "identity", Calibration(T)))["overall"]
        got = report["splits"][split]["policies"]["identity"]
        assert got["overall"]["all"]["accuracy"] == expect["accuracy"] and got["overall"]["all"]["n"] == 60
        assert got["overall"]["all"]["nll"] == pytest.approx(expect["nll"])
        assert got["mean_reads"] == 1 and got["share_second"] == 0


def test_report_fits_each_type_and_compares_every_policy(run):
    report, _ = run
    assert set(report["fits"]) == set(PICKED) and set(report["fits"]["identity"]) == {"choice", "score", "noul"}
    assert set(report["fits"]["aleria half/tn-prob"]["choice"]) == {"alpha", "beta"}
    assert report["gate_T"] == SHIPPED.T
    data = report["splits"]["eval"]
    assert set(data["vs_identity"]) == set(PICKED) - {"identity"}
    assert set(data["vs_identity"]["always reversed/mean-prob"]["options"]) == {"2", "3-5"}
    always = data["policies"]["always reversed/mean-prob"]
    assert always["mean_reads"] == 2 and always["share_second"] == 1
    assert always["cost"]["options"]["2"] == {"mean_reads": 2, "share_second": 1}
    assert 0 < data["policies"]["top_p 0.7 reversed/mean-logprob"]["share_second"] <= 1


def test_approx_skill_is_the_chance_corrected_family_mean():
    from scripts.metrics import Scored
    items = [Scored("s", "f", "choice", 0, [0.9, 0.1]), Scored("s", "f", "choice", 0, [0.1, 0.9]),
             Scored("s", "g", "choice", 0, [0.5, 0.3, 0.2, 0.0]), Scored("s", "h", "choice", 1, [0.9, 0.1])]
    # f: acc 0.5 at chance 0.5 -> 0; g: acc 1 at chance 0.25 -> 1; h: acc 0 -> clipped to 0
    assert r3_orders.approx_skill(items) == pytest.approx(1 / 3)


def test_write_puts_both_files_in_the_results_dir(run, tmp_path):
    report, _ = run
    report = report | {"meta": {"timestamp": "T", "profile": "p", "layout": "header"}}
    out = r3_orders.write(report, tmp_path)
    summary = json.loads((out / "summary.json").read_text())
    assert summary["fits"]["identity"]["choice"] == report["fits"]["identity"]["choice"]
    md = (out / "summary.md").read_text()
    assert md.startswith("# p R3 option-order policies: text (header)")
    assert "| aleria half/tn-prob |" in md and "## index-dev" in md and "approx skill" in md
