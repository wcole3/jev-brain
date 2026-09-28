from gateway.config import ROOT, Settings, read_env_file
from tests.helpers import PROFILES


def test_read_env_file_skips_comments_and_strips_quotes(tmp_path):
    f = tmp_path / "x.env"
    f.write_text("# comment\nA=1\n\nB='two words'\nC={\"enable_thinking\": true}\n")
    assert read_env_file(f) == {"A": "1", "B": "two words", "C": '{"enable_thinking": true}'}


def test_every_profile_loads_with_a_pinned_revision():
    for name in PROFILES:
        s = Settings.from_profile(name)
        assert s.profile == name
        assert len(s.hf_revision) == 40
        assert s.data_dir("decider_chat") == ROOT / "data" / name / "decider_chat"


def test_blank_optional_keys_fall_back_to_defaults():
    s = Settings.from_env(
        {
            "PROFILE": "p",
            "HF_MODEL": "m",
            "HF_REVISION": "r",
            "SERVED_MODEL": "s",
            "MAX_MODEL_LEN": "1024",
            "PROMPT_LAYOUT": "",
            "GATEWAY_API_KEY": "",
        }
    )
    assert s.prompt_layout == "decider_chat"
    assert s.option_orders == "identity"
    assert s.api_key is None
    assert s.warm_min_prefix_tokens == 512
