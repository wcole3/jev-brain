import pytest

from scripts import index_suite


def test_setup_clones_the_pinned_commit_into_an_editable_venv():
    cmds = index_suite.setup_commands()
    assert ["git", "-C", str(index_suite.SRC), "checkout", index_suite.HARNESS_SHA] in cmds
    assert cmds[-1][-2:] == ["-e", f"{index_suite.SRC}[rebuild]"]


def test_rebuild_then_import_into_the_work_dir():
    rebuild, imported = index_suite.rebuild_commands()
    assert rebuild[-4:] == ["suite", "rebuild", "--work", str(index_suite.WORK / "work")]
    assert "--added-rows" in imported and str(index_suite.SUITE) in imported


def test_token_is_read_from_the_secret_file(tmp_path, monkeypatch):
    secret = tmp_path / ".hf-token"
    secret.write_text("hf_abc\n")
    monkeypatch.setattr(index_suite, "HF_TOKEN_FILE", secret)
    env = index_suite.harness_env()
    assert env["HF_TOKEN"] == "hf_abc" and env["HF_HUB_DISABLE_XET"] == "1"


def test_rebuild_refuses_without_a_token(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(index_suite, "HF_TOKEN_FILE", tmp_path / ".hf-token")
    with pytest.raises(SystemExit, match="secrets/.hf-token"):
        index_suite.require_hf_token()
    (tmp_path / ".hf-token").write_text("hf_secret\n")
    index_suite.require_hf_token()
    assert "hf_secret" not in capsys.readouterr().out


def test_pins_edition_0_3_suite_and_export():
    assert index_suite.HARNESS_SHA == "9eb2dbe2a358004c8782c66e40a83ac07b953fec"
    assert index_suite.SUITE.name == "suite-0.3"
    assert index_suite.EXPORT.name == "rows-0.3.jsonl.gz"


def test_import_passes_rebuilt_gsm8k_rows():
    imp = index_suite.rebuild_commands()[1]
    assert imp[imp.index("--edition") + 1] == "0.3"
    assert imp[imp.index("--gsm8k-rows") + 1].endswith("release-v3-rebuilt/gsm8k-rows.jsonl.gz")


def test_export_passes_the_pinned_edition():
    cmd = index_suite.export_command()
    assert cmd[-3:] == [str(index_suite.SUITE), str(index_suite.EXPORT), "0.3"]
