import dataclasses
import gzip
import json

import pytest

from gateway.calibration import STAMP_KEYS, load_calibration
from scripts import fit_image_t
from scripts.fit import fit_temperature

STAMP = {"tokenizer_sha256": "t", "layout_sha256": "l", "hf_revision": "r", "prefix_pad": "off", "prefix_block": 0}
MM = {"max_soft_tokens": 560}  # what profiles/gemma-4-31b.env sets
ROWS_SHA = "a" * 64


def record(n: int, mm: dict = MM) -> dict:
    """Overconfident reads: the top letter is right two times in three, at logprob gaps of 6."""
    gold = 0 if n % 3 else 1
    lp = [0.0, -6.0, -6.0]
    return {"id": f"r{n}", "benchmark": "b", "group": f"g{n}", "layout": "header", "names": ["A", "B", "C"],
            "gold": gold, "status": "ok", "stamp": STAMP | {"profile": "gemma-4-31b", "mm_processor_kwargs": mm, "commit": "c"},
            "reads": [{"perm": [0, 1, 2], "logprobs": lp}, {"perm": [2, 1, 0], "logprobs": lp[::-1]}]}


@pytest.fixture
def setup(tmp_path, monkeypatch):
    folder = tmp_path / "collect"
    folder.mkdir()
    collect = folder / "calib.jsonl.gz"
    recs = [record(n) for n in range(60)] + [record(60) | {"status": "unsupported"}, record(61) | {"gold": None}]
    with gzip.open(collect, "wt") as f:
        f.writelines(json.dumps(r) + "\n" for r in recs)
    config = {"profile": "gemma-4-31b", "label": "x", "layout": "header", "orders": "identity+reversed", "env": {},
              "split": "calib", "rows": ".cache/vision-calib/rows.jsonl", "rows_sha256": ROWS_SHA}
    (folder / "calib.config.json").write_text(json.dumps(config))
    manifest = tmp_path / "vision-calib.json"
    manifest.write_text(json.dumps({"meta": {"rows_sha256": ROWS_SHA}}))
    cal = tmp_path / "data" / "gemma-4-31b" / "header" / "calibration.json"
    cal.parent.mkdir(parents=True)
    comment = {"version": 1, "date": "2026-10-09T00:00:00Z", "text": "first fit"}
    cal.write_text(json.dumps({"format": 2, "version": 1, "date": comment["date"], "comments": [comment],
                               "stamp": STAMP, "types": {"choice": {"T": 1.0}, "score": {"T": 1.0},
                                                         "noul": {"T": 1.0, "b": 0.0}}, "fit": {}}))
    monkeypatch.setattr(fit_image_t, "MANIFEST", manifest)
    real = fit_image_t.profile_settings
    monkeypatch.setattr(fit_image_t, "profile_settings",
                        lambda p: dataclasses.replace(real(p), data_root=tmp_path / "data"))
    return collect, config, cal


def run(collect, *extra):
    return fit_image_t.main(["--collect", str(collect), "--profile", "gemma-4-31b", *extra])


def test_fit_image_t_refuses_a_suite_collect(setup):
    collect, config, cal = setup
    before = cal.read_text()
    suite = {k: v for k, v in config.items() if k not in ("rows", "rows_sha256")} | {"split": "dev"}
    (collect.parent / "calib.config.json").write_text(json.dumps(suite))
    with pytest.raises(SystemExit, match="not a --rows collect"):
        run(collect, "--write")
    (collect.parent / "calib.config.json").write_text(json.dumps(config | {"rows_sha256": "b" * 64}))
    with pytest.raises(SystemExit, match="rows_sha256 .* vision-calib"):
        run(collect, "--write")
    assert cal.read_text() == before


def test_fit_image_t_refuses_another_layout_or_profile(setup):
    collect, _, cal = setup
    with pytest.raises(SystemExit, match="profile"):
        fit_image_t.main(["--collect", str(collect), "--profile", "q"])
    data = json.loads(cal.read_text())
    cal.write_text(json.dumps(data | {"stamp": STAMP | {"layout_sha256": "other"}}))
    with pytest.raises(SystemExit, match="layout_sha256"):
        run(collect, "--write")


def test_fit_image_t_without_write_writes_nothing(setup, capsys):
    collect, _, cal = setup
    before = cal.read_text()
    out = run(collect)
    assert cal.read_text() == before
    assert out["rows"] == 60 and out["T"] > 1.0
    assert out["nll"]["after"] < out["nll"]["before"]
    printed = capsys.readouterr().out
    assert f"T_image {out['T']:.3f}" in printed and "NLL" in printed and "ECE" in printed


def test_fit_image_t_writes_block_and_comment(setup):
    collect, _, cal = setup
    out = run(collect, "--write")
    data = json.loads(cal.read_text())
    assert data["version"] == 2 and len(data["comments"]) == 2
    assert data["comments"][-1]["version"] == 2 and "T_image" in data["comments"][-1]["text"]
    image = data["image"]
    assert image["stamp"] == {k: STAMP[k] for k in STAMP_KEYS} | {"mm_processor_kwargs": MM}
    assert image["fit"]["source"] == "vision-calib" and image["fit"]["rows"] == 60
    assert image["fit"]["orders"] == "identity"  # the profile's OPTION_ORDERS, not the collect's
    assert image["fit"]["edge"] is False
    reads = [([0.0, -6.0, -6.0], [0, 1, 2])]
    assert image["T"] == out["T"] == pytest.approx(fit_temperature([(reads, 0 if n % 3 else 1) for n in range(60)]))
    cal_loaded = load_calibration(cal, STAMP | {"mm_processor_kwargs": MM})
    assert cal_loaded.T_image == image["T"]
    run(collect, "--write")  # a refit replaces the block and adds a comment
    again = json.loads(cal.read_text())
    assert again["version"] == 3 and len(again["comments"]) == 3 and again["image"]["T"] == image["T"]


def test_fit_image_t_refuses_a_collect_without_the_served_orders(setup):
    collect, _, cal = setup
    before = cal.read_text()
    reversed_only = [record(n) for n in range(60)]
    for r in reversed_only:
        r["reads"] = r["reads"][1:]
    with gzip.open(collect, "wt") as f:
        f.writelines(json.dumps(r) + "\n" for r in reversed_only)
    with pytest.raises(SystemExit, match="serves orders 'identity'.*not collected"):
        run(collect, "--write")
    assert cal.read_text() == before


def test_fit_image_t_flags_a_T_at_the_search_bound(setup, capsys):
    collect, _, cal = setup
    with gzip.open(collect, "wt") as f:  # always wrong: the NLL keeps falling as T grows
        f.writelines(json.dumps(record(n) | {"gold": 1}) + "\n" for n in range(60))
    out = run(collect, "--write")
    assert out["edge"] is True and "(edge)" in capsys.readouterr().out
    assert json.loads(cal.read_text())["image"]["fit"]["edge"] is True


def write_dev(folder, recs, **over):
    folder.mkdir()
    dev = folder / "dev.jsonl.gz"
    with gzip.open(dev, "wt") as f:
        f.writelines(json.dumps(r) + "\n" for r in recs)
    config = {"profile": "gemma-4-31b", "label": "x", "layout": "header", "orders": "identity+reversed", "env": {},
              "split": "dev"} | over
    (folder / "dev.config.json").write_text(json.dumps(config))
    return dev


def test_fit_image_t_dev_scores_text_T_and_T_image_without_writing_data(setup, tmp_path, capsys):
    collect, _, cal = setup
    before = cal.read_text()
    dev = write_dev(tmp_path / "dev", [record(n) | {"id": f"d{n}"} for n in range(90)])
    out = run(collect, "--dev", str(dev), "--out", str(tmp_path / "out"))
    assert cal.read_text() == before and sorted(p.name for p in cal.parent.iterdir()) == ["calibration.json"]
    d = out["dev"]
    assert d["rows"] == 90 and d["orders"] == "identity"
    for arm in ("text", "image"):
        assert set(d[arm]) >= {"ece", "nll", "accuracy"}
    assert d["text"]["T"] == 1.0 and d["image"]["T"] == out["T"]
    assert d["image"]["accuracy"] == d["text"]["accuracy"] == pytest.approx(2 / 3, abs=0.01)
    assert d["image"]["nll"] < d["text"]["nll"] and d["image"]["ece"] < d["text"]["ece"]
    assert json.loads((tmp_path / "out" / "dev.json").read_text()) == d
    printed = capsys.readouterr().out
    assert "dev" in printed and f"{d['image']['ece']:.4f}" in printed


def test_fit_image_t_dev_without_out_only_prints(setup, tmp_path, monkeypatch):
    collect, _, _ = setup
    dev = write_dev(tmp_path / "dev", [record(n) for n in range(40)])
    monkeypatch.chdir(tmp_path)
    run(collect, "--dev", str(dev))
    assert not (tmp_path / "dev.json").exists()


@pytest.mark.parametrize("over, recs, match", [
    ({"split": "holdout"}, None, "split 'holdout', not dev"),
    ({"profile": "q"}, None, "profile"),
    ({"layout_file": "prompts/experiments/x.toml"}, None, "layout"),
    ({}, [record(n, {"max_soft_tokens": 1120}) for n in range(40)], "other stamps.*mm_processor_kwargs"),
])
def test_fit_image_t_dev_refuses_another_split_profile_layout_or_stamp(setup, tmp_path, over, recs, match):
    collect, _, _ = setup
    dev = write_dev(tmp_path / "dev", recs or [record(n) for n in range(40)], **over)
    with pytest.raises(SystemExit, match=match):
        run(collect, "--dev", str(dev))


def test_fit_image_t_dev_refuses_a_collect_without_the_served_orders(setup, tmp_path):
    collect, _, _ = setup
    recs = [record(n) for n in range(40)]
    for r in recs:
        r["reads"] = r["reads"][1:]
    dev = write_dev(tmp_path / "dev", recs)
    with pytest.raises(SystemExit, match="dev.jsonl.gz.*serves orders 'identity'"):
        run(collect, "--dev", str(dev))


def test_fit_image_t_refuses_image_settings_the_profile_does_not_run(setup):
    collect, _, cal = setup
    before = cal.read_text()
    with gzip.open(collect, "wt") as f:
        f.writelines(json.dumps(record(n, {"max_soft_tokens": 1120})) + "\n" for n in range(60))
    with pytest.raises(SystemExit, match="max_soft_tokens.: 1120.*max_soft_tokens.: 560"):
        run(collect, "--write")
    assert cal.read_text() == before
