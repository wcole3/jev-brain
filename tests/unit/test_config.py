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
            "VLLM_API_KEY": "",
            "PREFIX_PAD": "",
            "PREFIX_BLOCK": "",
            "PREFIX_PAD_ALWAYS": "",
            "WARM_MIN_PREFIX_TOKENS": "",
        }
    )
    assert s.prompt_layout == "decider_chat"
    assert s.option_orders == "identity"
    assert s.api_key is None
    assert s.vllm_api_key is None
    assert s.warm_min_prefix_tokens == 512
    assert (s.prefix_pad, s.prefix_block, s.prefix_pad_always) == ("off", 0, False)


def test_keys_come_from_the_environment():
    base = {"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s", "MAX_MODEL_LEN": "1024"}
    s = Settings.from_env(base | {"GATEWAY_API_KEY": "g", "VLLM_API_KEY": "v"})
    assert (s.api_key, s.vllm_api_key) == ("g", "v")


def test_keys_stay_out_of_repr():
    base = {"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s", "MAX_MODEL_LEN": "1024"}
    s = Settings.from_env(base | {"GATEWAY_API_KEY": "gw-secret", "VLLM_API_KEY": "vllm-secret"})
    assert "secret" not in repr(s)


def test_prefix_padding_comes_from_the_environment():
    base = {"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s", "MAX_MODEL_LEN": "1024"}
    env = {"PREFIX_PAD": "middle", "PREFIX_BLOCK": "784", "PREFIX_PAD_ALWAYS": "1", "WARM_MIN_PREFIX_TOKENS": "784"}
    s = Settings.from_env(base | env)
    assert (s.prefix_pad, s.prefix_block, s.prefix_pad_always, s.warm_min_prefix_tokens) == ("middle", 784, True, 784)
    assert not Settings.from_env(base | {"PREFIX_PAD_ALWAYS": "0"}).prefix_pad_always


REQUIRED = {"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s"}


def test_systemone_cap_defaults_to_32k_below_a_larger_model_limit():
    assert Settings.from_env(REQUIRED | {"MAX_MODEL_LEN": "262144"}).systemone_max_len == 32768


def test_systemone_cap_never_defaults_above_the_model_limit():
    assert Settings.from_env(REQUIRED | {"MAX_MODEL_LEN": "16384"}).systemone_max_len == 16384


def test_systemone_cap_from_env():
    env = REQUIRED | {"MAX_MODEL_LEN": "262144", "SYSTEMONE_MAX_LEN": "8192"}
    assert Settings.from_env(env).systemone_max_len == 8192
