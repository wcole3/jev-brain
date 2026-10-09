"""The pinned Decision Index harness in its own venv: install, rebuild the suite, export the scoreable rows.

usage: uv run python scripts/index_suite.py setup|rebuild|export
"""

import os
import subprocess
import sys

from gateway.config import ROOT

HARNESS_REPO = "https://github.com/apolinario/decision-index"
HARNESS_SHA = "9eb2dbe2a358004c8782c66e40a83ac07b953fec"
EDITION = "0.3"
WORK = ROOT / ".cache" / "decision-index"
SRC = WORK / "src"  # a clone: `suite import` reads hub/ relative to the repository
VENV = ROOT / ".cache" / "decision-index-venv"
PYTHON = VENV / "bin" / "python"
SUITE = WORK / "suite-0.3"
EXPORT = WORK / f"rows-{EDITION}.jsonl.gz"
REBUILT = WORK / "work" / "artifacts" / "benchmark-suite" / "release-v2-rebuilt"
REBUILT_V3 = WORK / "work" / "artifacts" / "benchmark-suite" / "release-v3-rebuilt"
HF_TOKEN_FILE = ROOT / "secrets" / ".hf-token"


def setup_commands() -> list[list[str]]:
    return [
        ["git", "clone", HARNESS_REPO, str(SRC)],
        ["git", "-C", str(SRC), "checkout", HARNESS_SHA],
        ["uv", "venv", "--python", "3.12", str(VENV)],
        ["uv", "pip", "install", "--python", str(PYTHON), "-e", f"{SRC}[rebuild]"],
    ]


def rebuild_commands() -> list[list[str]]:
    harness = [str(PYTHON), "-m", "decision_index"]
    return [
        harness + ["suite", "rebuild", "--work", str(WORK / "work")],
        harness + [
            "suite", "import", "--edition", EDITION, "--dir", str(SUITE),
            "--rows", str(REBUILT / "selected-rows.jsonl.gz"), "--added-rows", str(REBUILT / "added-rows.jsonl.gz"),
            "--gsm8k-rows", str(REBUILT_V3 / "gsm8k-rows.jsonl.gz"),
        ],
    ]


def export_command() -> list[str]:
    return [str(PYTHON), str(ROOT / "scripts" / "harness_export.py"), str(SUITE), str(EXPORT), EDITION]


def harness_env() -> dict[str, str]:
    """The HF token comes from secrets/ (HLE is gated); it is never printed or logged."""
    env = dict(os.environ, HF_HUB_DISABLE_XET="1")
    if HF_TOKEN_FILE.exists():
        env["HF_TOKEN"] = HF_TOKEN_FILE.read_text().strip()
    return env


def require_hf_token() -> None:
    """The rebuild downloads HLE, which is gated: stop now rather than hours in. The token is never printed."""
    if not HF_TOKEN_FILE.exists() or not HF_TOKEN_FILE.read_text().strip():
        raise SystemExit("secrets/.hf-token is missing or empty: the rebuild needs a Hugging Face token (HLE is gated)")


def run(commands: list[list[str]]) -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    for command in commands:
        subprocess.run(command, cwd=SRC if SRC.exists() else WORK, env=harness_env(), check=True)


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    steps = {"setup": setup_commands, "rebuild": rebuild_commands, "export": lambda: [export_command()]}
    if step not in steps:
        raise SystemExit(__doc__)
    if step == "rebuild":
        require_hf_token()
    run(steps[step]())
