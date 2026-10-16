"""Score the Decision Index Vision suite through the gateway with the kit's own runner.

usage: uv run python scripts/vision_run.py --profile P --gateway URL [--sample N] [--workers 8] [--run-dir DIR]
An existing run dir resumes. Results land in docs/results/<profile>/<UTC>-vision[-sample]/.
"""

import argparse
import json
import os
import random
import subprocess
from collections import defaultdict
from pathlib import Path

import httpx

from gateway.config import ROOT
from scripts.evaluate import gateway_headers, now, results_dir
from scripts.vision_summary import read_jsonl, write_folder

SEED = 24
DEFAULT_KIT = ROOT / ".cache" / "decision-index-vision"


def stratified_sample(rows: list[dict], n: int, seed: int = SEED) -> list[dict]:
    """n rows split across benchmarks in proportion to size (largest remainders), in suite order."""
    if n >= len(rows):
        return rows
    groups = defaultdict(list)
    for row in rows:
        groups[row["benchmark"]].append(row)
    quota = {b: n * len(g) // len(rows) for b, g in groups.items()}
    by_remainder = sorted(groups, key=lambda b: (-(n * len(groups[b]) % len(rows)), b))
    for b in by_remainder[: n - sum(quota.values())]:
        quota[b] += 1
    rng = random.Random(seed)
    picked = {id(r) for b in sorted(groups) for r in rng.sample(groups[b], quota[b])}
    return [r for r in rows if id(r) in picked]


def write_sample_dir(suite_dir: Path, rows: list[dict], out: Path) -> Path:
    """A suite dir holding only these rows; the kit has no --rows, so images are symlinked in."""
    out.mkdir(parents=True, exist_ok=True)
    (out / "vision-rows.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows))
    for top in sorted({Path(img).parts[0] for r in rows for img in r["images"]}):
        link = out / top
        if not link.is_symlink():
            link.symlink_to(suite_dir / top)
    return out


def check_health(gateway: str, profile: str) -> dict:
    health = httpx.get(f"{gateway}/health", headers=gateway_headers(), timeout=30).json()
    if health["profile"] != profile:
        raise SystemExit(f"gateway serves {health['profile']!r}, not {profile!r}")
    if not health.get("systemone_images"):
        raise SystemExit(f"{profile} does not accept images (SYSTEMONE_IMAGES is not 1)")
    return health


def kit_env() -> dict:
    env = dict(os.environ)
    if "GATEWAY_API_KEY" in os.environ:
        env["DECISION_INDEX_API_KEY"] = os.environ["GATEWAY_API_KEY"]
    return env


def run_command(args, health: dict, run_dir: Path, suite: Path) -> list[str]:
    cmd = [args.kit_python, "-m", "decision_index", "vision", "run", "--dir", str(suite), "--no-verify",
           "--engine", "decide", "--option", f"base_url={args.gateway}", "--option", "path=/v1/systemone",
           "--option", "protocol=decisions", "--option", f"model={health['served_model']}",
           "--workers", str(args.workers), "--compact", "--out", str(run_dir)]
    return cmd


def score_command(args, run_dir: Path, suite: Path) -> list[str]:
    return [args.kit_python, "-m", "decision_index", "vision", "score", "--results", str(run_dir / "results.jsonl"),
            "--dir", str(suite), "--out", str(run_dir)]


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--gateway", required=True)
    p.add_argument("--sample", type=int, help="seeded sample stratified by benchmark")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--kit-dir", type=Path, default=DEFAULT_KIT)
    p.add_argument("--kit-python")
    p.add_argument("--run-dir", type=Path, help="resumes when it exists (default .cache/vision-runs/<profile>/<UTC>)")
    args = p.parse_args(argv)
    kit_venv = args.kit_dir / "venv" / "bin" / "python"
    args.kit_python = args.kit_python or str(kit_venv if kit_venv.exists() else "python3")
    args.suite_dir = (args.kit_dir / "work" / "vision").resolve()
    args.kit_src = (args.kit_dir / "src").resolve()
    args.run_dir = (args.run_dir or ROOT / ".cache" / "vision-runs" / args.profile / now()).resolve()
    return args


def main(args) -> None:
    health = check_health(args.gateway, args.profile)
    args.run_dir.mkdir(parents=True, exist_ok=True)
    suite = args.suite_dir
    if args.sample:
        sample = stratified_sample(read_jsonl(args.suite_dir / "vision-rows.jsonl"), args.sample)
        suite = write_sample_dir(args.suite_dir, sample, args.run_dir / "sample-suite")
    for cmd in (run_command(args, health, args.run_dir, suite), score_command(args, args.run_dir, suite)):
        subprocess.run(cmd, cwd=args.kit_src, env=kit_env(), check=True)
    name = f"{now()}-vision" + ("-sample" if args.sample else "")
    out = results_dir(args.profile, name)
    (out / "health.json").write_text(json.dumps(health, indent=2) + "\n")
    summary = write_folder(args.run_dir, suite, out, f"Vision suite, {args.profile} via gateway")
    print(out, json.dumps(summary))


if __name__ == "__main__":
    main(parse_args())
