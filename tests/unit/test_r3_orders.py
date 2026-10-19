import gzip
import json
import random

import pytest

from gateway.calibration import Calibration
from gateway.layouts import PROMPTS_DIR, load_layouts
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


def fixed(n: int) -> list[dict]:
    """Every read picks shown position 0, whatever the order."""
    return [{"perm": perm, "logprobs": [float(j == 0) for j in range(n)]} for perm in all_orders(n)]


def collect(path, prefix: str, count: int = 30, seed: int = 0, stamp: dict | None = None,
            other: str = "") -> dict:
    """header records hold the reads; with other, those reads go to that layout and header reads are fixed."""
    rng, rows = random.Random(seed), [row(prefix, i) for i in range(count)]
    with gzip.open(path, "wt") as f:
        for i, r in enumerate(rows):
            n = len(r["questions"]["c"]["criteria"])
            qs = {"c": reads(rng, n, rng.choice([i % n, 0])), "y": reads(rng, 2, i % 2)}
            if other:
                f.write(json.dumps({"id": r["id"], "layout": other, "status": "ok", "stamp": {}, "questions": qs}) + "\n")
                qs = {"c": fixed(n), "y": fixed(2)}
            f.write(json.dumps({"id": r["id"], "layout": "header", "status": "ok", "stamp": stamp or {},
                                "questions": qs}) + "\n")
        if not other:
            f.write(json.dumps({"id": "other", "layout": "decider_chat", "status": "ok", "stamp": {},
                                "questions": {}}) + "\n")
    return {r["id"]: r for r in rows}


def picked(names=PICKED) -> list:
    return [p for p in POLICIES if p.name in names]


@pytest.fixture(scope="module")
def data(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("r3")
    loaded = {}
    for split, seed in (("calib", 1), ("index-dev", 2), ("eval", 3)):
        rows = collect(tmp / f"{split}.jsonl.gz", split[0], seed=seed)
        loaded[split] = list(records(tmp / f"{split}.jsonl.gz")), rows
    return loaded.pop("calib"), loaded


@pytest.fixture(scope="module")
def run(data):
    calib, splits = data
    return r3_orders.report(calib, splits, SHIPPED.T, picked()), splits


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


def test_report_on_another_layout(tmp_path):
    loaded = {}
    for split, seed in (("calib", 1), ("eval", 3)):
        rows = collect(tmp_path / f"{split}.jsonl.gz", split[0], seed=seed, other="decider_chat")
        loaded[split] = list(records(tmp_path / f"{split}.jsonl.gz")), rows
    report = r3_orders.report(loaded["calib"], {"eval": loaded["eval"]}, SHIPPED.T, picked(PICKED[:2]),
                              layout=load_layouts()["decider_chat"])
    recs, rows = loaded["eval"]
    T = Calibration(report["fits"]["identity"])
    expect = evaluate(recs, rows, Arm("decider_chat", "identity", T))["overall"]["accuracy"]
    got = report["splits"]["eval"]["policies"]["identity"]["overall"]["all"]["accuracy"]
    assert got == expect != evaluate(recs, rows, Arm("header", "identity", T))["overall"]["accuracy"]


def test_own_gate_is_the_identity_fit(data):
    calib, splits = data
    report = r3_orders.report(calib, {"eval": splits["eval"]}, None, picked(PICKED[:2]))
    assert report["gate_T"] == r3_orders.identity_T(r3_orders.items(*calib, load_layouts()["header"]))
    assert report["gate_T"] == report["fits"]["identity"] != SHIPPED.T


def test_files_mode_keeps_manifest_rows_only(tmp_path):
    rows = collect(tmp_path / "c.jsonl.gz", "c")
    recs = list(records(tmp_path / "c.jsonl.gz"))
    keep = {rid: rows[rid] for rid in list(rows)[:10]}
    got = r3_orders.items(recs, keep, load_layouts()["header"])
    assert len(recs) == 31 and {rid for rid, _ in got} == set(keep)


def files(tmp_path, monkeypatch, dev_stamp: dict) -> tuple:
    rows = {"calib-600": collect(tmp_path / "calib.jsonl.gz", "c", seed=1, stamp={"hf_revision": "a"}),
            "index-dev-2k": collect(tmp_path / "dev.jsonl.gz", "d", seed=2, stamp=dev_stamp)}
    monkeypatch.setattr(r3_orders, "rows_for", lambda split: list(rows[split].values())[:20])
    return tmp_path / "calib.jsonl.gz", tmp_path / "dev.jsonl.gz"


def test_files_mode_refuses_mixed_stamps(tmp_path, monkeypatch):
    calib, dev = files(tmp_path, monkeypatch, {"hf_revision": "b"})
    with pytest.raises(SystemExit, match=f"{calib}.*{dev}"):
        r3_orders.run_files("p", load_layouts()["header"], calib, dev)


def test_files_mode_gates_at_its_own_identity_fit(tmp_path, monkeypatch):
    calib, dev = files(tmp_path, monkeypatch, {"hf_revision": "a"})
    monkeypatch.setattr(r3_orders, "POLICIES", picked(PICKED[:2]))
    out = r3_orders.run_files("p", load_layouts()["header"], calib, dev)
    assert list(out["splits"]) == ["index-dev-2k"] and out["gate_T"] == out["fits"]["identity"]
    assert out["splits"]["index-dev-2k"]["policies"]["identity"]["overall"]["all"]["n"] == 40  # 20 manifest rows
    assert out["meta"]["layout"] == "header" and out["meta"]["gates"] == "own identity T on calib-600"


def test_out_names(tmp_path, monkeypatch):
    def stub(profile, layout, *paths, pmap=map):
        meta = {"timestamp": "T", "profile": profile, "layout": getattr(layout, "name", layout)}
        return {"meta": meta, "fits": {}, "splits": {}}
    monkeypatch.setattr(r3_orders, "run", stub)
    monkeypatch.setattr(r3_orders, "run_files", stub)
    monkeypatch.setattr(r3_orders, "ROOT", tmp_path)
    blurb = str(PROMPTS_DIR / "experiments" / "blurb-header.toml")
    for flags, end in ((["--layout", "decider_chat"], "-r4-orders-text-decider_chat-p"),
                       (["--calib", "c", "--dev", "d", "--layout-file", blurb], "-r4-orders-text-blurb-header-2k-p"),
                       ([], "-r3-orders-text-p")):
        r3_orders.main(["--profile", "p", *flags])
        assert len(list((tmp_path / "docs" / "results" / "archive").glob(f"*{end}"))) == 1


@pytest.mark.parametrize("flags", [["--calib", "c"], ["--layout-file", "x.toml"],
                                   ["--layout", "header", "--layout-file", "x.toml", "--calib", "c", "--dev", "d"]])
def test_flags_go_together(flags):
    with pytest.raises(SystemExit):
        r3_orders.main(["--profile", "p", *flags])
