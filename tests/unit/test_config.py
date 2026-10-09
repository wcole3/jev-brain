import json

import pytest
import yaml

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


def test_systemone_priority_defaults_to_zero_and_reads_env():
    base = {"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s", "MAX_MODEL_LEN": "1024"}
    assert Settings.from_env(base).systemone_priority == 0
    assert Settings.from_env(base | {"SYSTEMONE_PRIORITY": ""}).systemone_priority == 0
    assert Settings.from_env(base | {"SYSTEMONE_PRIORITY": "1"}).systemone_priority == 1


REQUIRED = {"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s"}


def test_systemone_cap_defaults_to_32k_below_a_larger_model_limit():
    assert Settings.from_env(REQUIRED | {"MAX_MODEL_LEN": "262144"}).systemone_max_len == 32768


def test_systemone_cap_never_defaults_above_the_model_limit():
    assert Settings.from_env(REQUIRED | {"MAX_MODEL_LEN": "16384"}).systemone_max_len == 16384


def test_systemone_cap_from_env():
    env = REQUIRED | {"MAX_MODEL_LEN": "262144", "SYSTEMONE_MAX_LEN": "8192"}
    assert Settings.from_env(env).systemone_max_len == 8192


def test_governor_env():
    base = {"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s", "MAX_MODEL_LEN": "1024"}
    s = Settings.from_env(base | {"GOVERNOR_DUTY": "0.25", "GOVERNOR_WAVE": "2"})
    assert (s.governor_duty, s.governor_wave) == (0.25, 2)
    for blank in ({}, {"GOVERNOR_DUTY": "", "GOVERNOR_WAVE": ""}):
        s = Settings.from_env(base | blank)
        assert (s.governor_duty, s.governor_wave) == (1.0, 4)


def test_governor_env_junk_names_the_variable():
    base = {"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s", "MAX_MODEL_LEN": "1024"}
    for key in ("GOVERNOR_DUTY", "GOVERNOR_WAVE"):
        with pytest.raises(ValueError, match=key):
            Settings.from_env(base | {key: "abc"})


def sized(tmp_path, block, *names):
    for n in names:
        (tmp_path / "p" / "L").mkdir(parents=True, exist_ok=True)
        (tmp_path / "p" / "L" / n).write_text("{}")
    s = Settings.from_env({"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s",
                           "MAX_MODEL_LEN": "1024", "PREFIX_BLOCK": str(block), "DATA_ROOT": str(tmp_path)})
    return s.calibration_path("L"), tmp_path / "p" / "L"


def test_calibration_path_prefers_the_file_of_the_exact_block_size(tmp_path):
    path, d = sized(tmp_path, 784, "calibration.json", "calibration-784.json", "calibration-800.json")
    assert path == d / "calibration-784.json"


def test_calibration_path_falls_back_to_the_plain_file(tmp_path):
    path, d = sized(tmp_path, 784, "calibration.json", "calibration-800.json")
    assert path == d / "calibration.json"
    assert sized(tmp_path, 0, "calibration.json")[0] == d / "calibration.json"


@pytest.mark.parametrize("block", [None, "784"])
@pytest.mark.parametrize("name", ["qwen3.6-27b", "qwen3.8-27b"])
def test_shipped_qwen_calibration_is_stamped_for_the_profiles_block(name, block):
    env = read_env_file(ROOT / "profiles" / f"{name}.env")
    s = Settings.from_env({**env, **({"PREFIX_BLOCK": block} if block else {})})
    for layout in ("decider_chat", "header", "question_first"):
        stamp = json.loads(s.calibration_path(layout).read_text())["stamp"]
        assert stamp["prefix_block"] == s.prefix_block


QUANTIZED_QWEN = ["qwen3.8-27b-fp8", "qwen3.8-27b-nvfp4", "qwen3.6-27b-fp8"]


@pytest.mark.parametrize("name", QUANTIZED_QWEN)
def test_quantized_mtp_profiles_force_bf16_kv(name):
    env = read_env_file(ROOT / "profiles" / f"{name}.env")
    assert '"method":"mtp"' in env["EXTRA_ARGS"]
    assert "--kv-cache-dtype bfloat16" in env["EXTRA_ARGS"]
    assert env["VLLM_USE_DEEP_GEMM"] == "0"


def test_compose_passes_deep_gemm_with_default():
    vllm_env = yaml.safe_load((ROOT / "compose.yaml").read_text())["services"]["vllm"]["environment"]
    assert vllm_env["VLLM_USE_DEEP_GEMM"] == "${VLLM_USE_DEEP_GEMM:-1}"


QUANTIZED_CALIBRATED = ["qwen3.8-27b-nvfp4"]


@pytest.mark.parametrize("name", QUANTIZED_CALIBRATED)
def test_quantized_qwen_calibration_is_stamped_for_800_blocks(name):
    s = Settings.from_profile(name)
    for layout in ("decider_chat", "header", "question_first"):
        stamp = json.loads(s.calibration_path(layout).read_text())["stamp"]
        assert (stamp["prefix_block"], stamp["hf_revision"]) == (800, s.hf_revision)
