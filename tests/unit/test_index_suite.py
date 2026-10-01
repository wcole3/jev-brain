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
