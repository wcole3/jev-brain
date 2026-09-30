import os
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "docker" / "vllm-entrypoint.sh"


def served_args(tmp_path, **env):
    stub = tmp_path / "vllm"
    stub.write_text('#!/bin/sh\necho "$@"\n')
    stub.chmod(0o755)
    base = {
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "HF_MODEL": "org/m",
        "HF_REVISION": "rev",
        "SERVED_MODEL": "m",
        "MAX_MODEL_LEN": "1000",
        "REASONING_PARSER": "qwen3",
        "TOOL_PARSER": "x",
    }
    out = subprocess.run(["bash", str(SCRIPT)], env=base | env, capture_output=True, text=True, check=True)
    return out.stdout


def test_extra_args_are_word_split_onto_the_command(tmp_path):
    assert served_args(tmp_path, EXTRA_ARGS="--mamba-ssm-cache-dtype bfloat16").endswith(
        "--mamba-ssm-cache-dtype bfloat16\n"
    )


def test_empty_extra_args_add_nothing(tmp_path):
    assert "mamba" not in served_args(tmp_path, EXTRA_ARGS="")
