"""Download a profile's model weights into the host's Hugging Face cache.

usage: uv run python scripts/fetch_model.py --profile qwen3.6-27b
"""

import argparse

from huggingface_hub import snapshot_download

from gateway.config import Settings

# Exactly the files vLLM itself downloaded for every profile, so cached models stay valid.
FILES = ["*.json", "*.safetensors", "*.jinja", "*.txt"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    s = Settings.from_profile(parse_args(argv).profile)
    path = snapshot_download(s.hf_model, revision=s.hf_revision, allow_patterns=FILES)
    print(path)


if __name__ == "__main__":
    main()
