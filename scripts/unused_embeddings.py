"""Were Gemma's <unusedN> embedding rows ever trained? Norms and cosines vs ordinary rows, read from the weights (CPU)."""

import argparse
import json
import os
import struct
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from gateway.config import ROOT, Settings

UNUSED = 255
ORDINARY = 2000
SEED = 0


def bf16_rows(path: Path, tensor: str, rows: list[int]) -> np.ndarray:
    """Selected rows of a 2-D bf16 safetensors tensor as float32; reads only those bytes."""
    with open(path, "rb") as f:
        (n,) = struct.unpack("<Q", f.read(8))
        info = json.loads(f.read(n))[tensor]
        width = info["shape"][1]
        out = np.empty((len(rows), width), dtype=np.float32)
        for i, row in enumerate(rows):
            f.seek(8 + n + info["data_offsets"][0] + row * width * 2)
            out[i] = (np.frombuffer(f.read(width * 2), dtype="<u2").astype(np.uint32) << 16).view(np.float32)
    return out


def stats(rows: np.ndarray) -> dict:
    norms = np.linalg.norm(rows, axis=1)
    unit = rows / np.maximum(norms[:, None], 1e-12)
    n = len(rows)
    mean_cos = float((unit.sum(0) @ unit.sum(0) - n) / (n * (n - 1)))
    return {"rows": n, "norm_min": float(norms.min()), "norm_median": float(np.median(norms)),
            "norm_max": float(norms.max()), "mean_pairwise_cosine": mean_cos}


def snapshot(s: Settings) -> Path:
    from huggingface_hub.constants import HF_HUB_CACHE

    return Path(HF_HUB_CACHE) / f"models--{s.hf_model.replace('/', '--')}" / "snapshots" / s.hf_revision


def report(profile: str) -> dict:
    os.environ["HF_HUB_OFFLINE"] = "1"
    from transformers import AutoTokenizer

    s = Settings.from_profile(profile)
    snap = snapshot(s)
    tensor, shard = next((k, v) for k, v in json.loads((snap / "model.safetensors.index.json").read_text())["weight_map"].items() if k.endswith("embed_tokens.weight"))
    tok = AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
    unused = [tok.convert_tokens_to_ids(f"<unused{i}>") for i in range(UNUSED)]
    special = set(tok.all_special_ids) | set(unused)
    pool = [i for i in range(len(tok)) if i not in special]
    ordinary = sorted(np.random.default_rng(SEED).choice(pool, ORDINARY, replace=False).tolist())
    path = snap / shard
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()
    return {"source": {"model": s.hf_model, "revision": s.hf_revision, "shard": shard, "tensor": tensor, "commit": commit},
            "unused": stats(bf16_rows(path, tensor, unused)), "ordinary": stats(bf16_rows(path, tensor, ordinary))}


def markdown(r: dict) -> str:
    src = r["source"]
    source = (f"Source: {src['model']} @ {src['revision']}, shard {src['shard']}, tensor `{src['tensor']}`, "
              f"repo commit {src['commit']}. Ordinary rows: {ORDINARY} seeded (seed {SEED}).")
    lines = ["# Unused-token embeddings", "", source, "",
             "| group | rows | norm min | norm median | norm max | mean pairwise cosine |", "|---|---|---|---|---|---|"]
    for g in ("unused", "ordinary"):
        x = r[g]
        lines.append(f"| {g} | {x['rows']} | {x['norm_min']:.4g} | {x['norm_median']:.4g} | {x['norm_max']:.4g} | {x['mean_pairwise_cosine']:.4f} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    args = ap.parse_args()
    r = report(args.profile)
    out = ROOT / "docs/results/archive" / f"{datetime.now(UTC):%Y-%m-%dT%H%M%SZ}-r3-unused-embeddings"
    out.mkdir(parents=True)
    (out / "summary.json").write_text(json.dumps(r, indent=2) + "\n")
    (out / "summary.md").write_text(markdown(r))
    print(markdown(r), out)


if __name__ == "__main__":
    main()
