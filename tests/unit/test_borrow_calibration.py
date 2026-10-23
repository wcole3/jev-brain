import dataclasses
import json

import pytest

from gateway.calibration import load_calibration
from gateway.config import Settings
from scripts import borrow_calibration

LAYOUT = "blurb_header_reread"
BASE, QUANT = "qwen3.8-27b", "qwen3.8-27b-fp8"
STAMPS = {
    BASE: {"tokenizer_sha256": "t", "layout_sha256": "l", "hf_revision": "base-rev", "prefix_pad": "front", "prefix_block": 800},
    QUANT: {"tokenizer_sha256": "t", "layout_sha256": "l", "hf_revision": "quant-rev", "prefix_pad": "front", "prefix_block": 800},
}
FIT = {"format": 2, "version": 3, "date": "2026-10-20T00:00:00Z", "comments": [{"version": 3, "date": "d", "text": "fit"}],
       "types": {"choice": {"T": 3.9}, "score": {"T": 5.2}, "noul": {"T": 6.7, "b": 0.4}}, "fit": {"orders": "identity"}}


@pytest.fixture
def run(tmp_path, monkeypatch):
    """Run the script on a tmp data root with fake stamps (no tokenizer download)."""
    real = Settings.from_profile
    monkeypatch.setattr(Settings, "from_profile", lambda name: dataclasses.replace(real(name), data_root=tmp_path))
    monkeypatch.setattr(borrow_calibration, "stamp_of", lambda profile, s, layout: STAMPS[profile])
    return lambda *extra: borrow_calibration.main(["--profile", QUANT, "--layout", LAYOUT, *extra])


def put(tmp_path, profile, name, data):
    path = tmp_path / profile / LAYOUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return path


def test_borrowed_file_has_quant_stamp_provenance_and_the_base_fit(run, tmp_path, capsys):
    put(tmp_path, BASE, "calibration.json", FIT | {"stamp": STAMPS[BASE]})
    put(tmp_path, BASE, "calibration-identity.json", FIT | {"stamp": STAMPS[BASE]})
    run()
    out = tmp_path / QUANT / LAYOUT
    data = json.loads((out / "calibration.json").read_text())
    assert data["stamp"] == STAMPS[QUANT] and data["types"] == FIT["types"] and data["fit"] == FIT["fit"]
    assert data["borrowed"]["profile"] == BASE and data["borrowed"]["stamp"] == STAMPS[BASE]
    assert data["borrowed"]["file"] == "calibration.json" and data["comments"][-1]["text"].startswith("borrowed from")
    assert (out / "calibration-identity.json").exists()
    assert str(out / "calibration.json") in capsys.readouterr().out


def test_gateway_accepts_the_borrowed_file_for_the_quant_only(run, tmp_path):
    put(tmp_path, BASE, "calibration.json", FIT | {"stamp": STAMPS[BASE]})
    run()
    path = tmp_path / QUANT / LAYOUT / "calibration.json"
    cal = load_calibration(path, STAMPS[QUANT])
    assert cal.T == {"choice": 3.9, "score": 5.2, "noul": 6.7} and cal.b == 0.4
    with pytest.raises(RuntimeError, match="hf_revision changed"):
        load_calibration(path, STAMPS[BASE])


def test_dry_run_writes_nothing(run, tmp_path, capsys):
    put(tmp_path, BASE, "calibration.json", FIT | {"stamp": STAMPS[BASE]})
    run("--dry-run")
    assert not (tmp_path / QUANT).exists() and "would write" in capsys.readouterr().out


def test_stale_base_is_refused(run, tmp_path):
    put(tmp_path, BASE, "calibration.json", FIT | {"stamp": STAMPS[BASE] | {"layout_sha256": "old"}})
    with pytest.raises(SystemExit, match="stale"):
        run()
    assert not (tmp_path / QUANT).exists()


def test_missing_base_is_refused(run):
    with pytest.raises(SystemExit, match="no calibration"):
        run()


def test_quants_own_fit_is_not_overwritten(run, tmp_path):
    put(tmp_path, BASE, "calibration.json", FIT | {"stamp": STAMPS[BASE]})
    own = put(tmp_path, QUANT, "calibration.json", FIT | {"stamp": STAMPS[QUANT]})
    with pytest.raises(SystemExit, match="own fit"):
        run()
    assert "borrowed" not in json.loads(own.read_text())


def test_a_profile_outside_quantized_needs_from(run):
    with pytest.raises(SystemExit, match="--from"):
        borrow_calibration.main(["--profile", BASE, "--layout", LAYOUT])
