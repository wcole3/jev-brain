import pytest

from gateway.config import Settings
from scripts import fetch_model


def test_parse_args_requires_profile():
    with pytest.raises(SystemExit):
        fetch_model.parse_args([])


def test_main_downloads_profile_model(monkeypatch, capsys):
    calls = []

    def fake_download(repo, **kwargs):
        calls.append((repo, kwargs))
        return "/cache/snapshot"

    monkeypatch.setattr(fetch_model, "snapshot_download", fake_download)
    fetch_model.main(["--profile", "qwen3.6-27b"])
    s = Settings.from_profile("qwen3.6-27b")
    assert calls == [(s.hf_model, {"revision": s.hf_revision, "allow_patterns": fetch_model.FILES})]
    assert capsys.readouterr().out.strip() == "/cache/snapshot"
