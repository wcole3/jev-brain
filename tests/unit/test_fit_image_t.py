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
    assert image["fit"]["orders"] == "identity+reversed"
    reads = [([0.0, -6.0, -6.0], [0, 1, 2]), ([-6.0, -6.0, 0.0], [2, 1, 0])]
    assert image["T"] == out["T"] == pytest.approx(fit_temperature([(reads, 0 if n % 3 else 1) for n in range(60)]))
    cal_loaded = load_calibration(cal, STAMP | {"mm_processor_kwargs": MM})
    assert cal_loaded.T_image == image["T"]
    run(collect, "--write")  # a refit replaces the block and adds a comment
    again = json.loads(cal.read_text())
    assert again["version"] == 3 and len(again["comments"]) == 3 and again["image"]["T"] == image["T"]


def test_fit_image_t_refuses_image_settings_the_profile_does_not_run(setup):
    collect, _, cal = setup
    before = cal.read_text()
    with gzip.open(collect, "wt") as f:
        f.writelines(json.dumps(record(n, {"max_soft_tokens": 1120})) + "\n" for n in range(60))
    with pytest.raises(SystemExit, match="max_soft_tokens.: 1120.*max_soft_tokens.: 560"):
        run(collect, "--write")
    assert cal.read_text() == before
