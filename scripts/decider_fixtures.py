"""Record decider's token ids for tests/parity/cases.json. Runs in its own venv (decider pins numpy<2):

  uv venv .cache/decider-venv
  uv pip install --python .cache/decider-venv --no-deps decider-ai==1.5.0
  uv pip install --python .cache/decider-venv transformers jinja2 "numpy<2" huggingface_hub
  .cache/decider-venv/bin/python scripts/decider_fixtures.py --profile qwen3.6-27b
"""
import argparse
import json
from pathlib import Path

from decider import systemone as S1
from decider.prompt import chat_template, label_table
from decider.prompt_fast import build_rows
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent


def read_profile(name: str) -> dict[str, str]:
    """Plain parse: this venv does not have the gateway package."""
    lines = (ROOT / "profiles" / f"{name}.env").read_text().splitlines()
    return dict(line.split("=", 1) for line in lines if line.strip() and not line.startswith("#"))


def decider_rows(tok, case: dict) -> list[list[int]]:
    """decider.serve.prepare(independent=True, isolated=False), without loading the model."""
    rqs = {k: S1.render_question(v) for k, v in case["questions"].items()}
    flat, _ = S1.plan_rows(rqs, isolated=False)
    rows = [[(r["question"], list(r["options"]))] for r in flat]
    items, _ = build_rows(tok, S1.render_state(case["state"]), rows, max_ctx_tokens=32768, chat=chat_template(tok))
    return [item["ids"] for item in items]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    name = parser.parse_args().profile
    env = read_profile(name)
    tok = AutoTokenizer.from_pretrained(env["HF_MODEL"], revision=env["HF_REVISION"])
    cases = json.loads((ROOT / "tests" / "parity" / "cases.json").read_text())
    out = {"decider": "1.5.0", "label_ids": label_table(tok)[1], "rows": [decider_rows(tok, c) for c in cases]}
    path = ROOT / "tests" / "parity" / "fixtures" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
