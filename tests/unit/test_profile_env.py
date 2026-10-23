import shlex

import pytest

from gateway.config import Settings, read_env_file
from scripts.profile_env import PROFILES, exports


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


DEFAULTS = [
    ("gemma-4-31b", "top_p:0.9+reversed", "identity"),
    ("gemma-4-31b-fp8", "top_p:0.9+reversed", "identity"),
    ("gemma-4-12b", "identity", ""),
    ("gemma-4-12b-qat", "identity", ""),
    ("qwen3.8-27b", "min_n:4+reversed", ""),
    ("qwen3.8-27b-fp8", "min_n:4+reversed", ""),
    ("qwen3.8-27b-nvfp4", "min_n:4+reversed", ""),
    ("qwen3.6-27b", "identity", ""),
    ("qwen3.6-27b-fp8", "identity", ""),
]


@pytest.mark.parametrize(("profile", "orders", "orders_images"), DEFAULTS)
def test_profiles_serve_the_ds045_defaults(profile, orders, orders_images):
    s = Settings.from_profile(profile)
    assert (s.prompt_layout, s.option_orders, s.option_orders_images) == ("blurb_header_reread", orders, orders_images)


@pytest.mark.parametrize("profile", sorted(p.stem for p in PROFILES.glob("*.env")))
def test_vision_profiles_raise_max_logprobs(profile):
    env = read_env_file(PROFILES / f"{profile}.env")
    if env.get("SYSTEMONE_IMAGES") == "1":
        assert "--max-logprobs 128" in env["EXTRA_ARGS"]
        assert '"image":4' in env["EXTRA_ARGS"]
