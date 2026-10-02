import shlex

import pytest

from scripts.profile_env import exports


def test_exports_quote_values_and_apply_overrides(tmp_path, monkeypatch):
    (tmp_path / "p.env").write_text('# c\nA=1\nCHAT_TEMPLATE_KWARGS={"enable_thinking": true}\n')
    monkeypatch.setattr("scripts.profile_env.PROFILES", tmp_path)
    lines = exports("p", ["A=2", "NEW=x y"]).splitlines()
    assert lines == [
        "export A=2",
        "export CHAT_TEMPLATE_KWARGS='{\"enable_thinking\": true}'",
        "export NEW='x y'",
    ]
    assert shlex.split(lines[1])[1] == 'CHAT_TEMPLATE_KWARGS={"enable_thinking": true}'


def test_override_without_equals_exits(tmp_path, monkeypatch):
    (tmp_path / "p.env").write_text("A=1\n")
    monkeypatch.setattr("scripts.profile_env.PROFILES", tmp_path)
    with pytest.raises(SystemExit, match="K=V"):
        exports("p", ["oops"])
