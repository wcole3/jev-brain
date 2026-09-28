"""Write data/<profile>/<layout>/labels.json for every prompt layout.

usage: uv run python scripts/build_labels.py --profile qwen3.6-27b
"""

import argparse

from transformers import AutoTokenizer

from gateway.config import Settings
from gateway.labels import build_labels, save_labels
from gateway.layouts import load_layouts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    s = Settings.from_profile(parser.parse_args().profile)
    tok = AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
    for name, layout in load_layouts().items():
        table = build_labels(tok, layout) | {"model": s.hf_model, "revision": s.hf_revision}
        path = s.data_dir(name) / "labels.json"
        save_labels(path, table)
        print(f"wrote {path} ({len(table['ids'])} labels)")


if __name__ == "__main__":
    main()
