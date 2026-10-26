"""Assemble a Decision Index board submission folder from a local run directory, checked against the suite.

usage: uv run python scripts/hub_export.py text|vision RUN_DIR --name NAME --out OUT [--no-rescore]
Writes OUT/runs/NAME/ (only the files the board reads) and the report OUT/NAME.export.txt; any failed check writes no folder.
"""

import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from gateway.config import ROOT
from scripts.index_suite import EXPORT

VISION_KIT = ROOT / ".cache" / "decision-index-vision"
ALLOWED = {"ok", "unsupported", "abstained"}  # anything else (error, pending) means the run is not finished
SUITES = {"text": EXPORT, "vision": VISION_KIT / "work" / "vision" / "vision-rows.jsonl"}
RESULTS = {"text": "merged/results.jsonl", "vision": "results.jsonl"}
SCORES = {"text": "merged/scores.json", "vision": "vision-scores.json"}
# Destination name in the run folder -> source under RUN_DIR (text adds shards/shard-N/ files).
FILES = {
    "text": {"benchmark-summary.json": "merged/benchmark-summary.json", "index.json": "merged/index.json",
             "scores.json": "merged/scores.json"},
    "vision": {"environment.json": "environment.json", "status.json": "status.json",
               "vision-scores.json": "vision-scores.json"},
}


def read_lines(path: Path) -> list[bytes]:
    with (gzip.open if path.suffix == ".gz" else open)(path, "rb") as f:
        return f.readlines()


def suite_evaluations(path: Path) -> dict[str, dict]:
    """run_id -> the hashes the harness stamped on that suite row."""
    return {e["run_id"]: e for e in (json.loads(x)["_evaluation"] for x in read_lines(path))}


def select(lines: list[bytes], suite: dict[str, dict], retries: bool) -> tuple[list[bytes], list[str], list[str], Counter]:
    """(kept lines, dropped notes, problems, status counts): one line per run_id, in first-seen order.

    With retries, an earlier line is dropped only if it is an error or a byte-identical repeat of the last line.
    """
    attempts: dict[str, list[tuple[int, bytes, dict]]] = {}
    kept, dropped, problems = [], [], []
    for n, line in enumerate(lines, 1):
        try:
            row = json.loads(line)
            attempts.setdefault(row["run_id"], []).append((n, line, row))
        except (ValueError, KeyError, TypeError):
            problems.append(f"line {n}: blank, not JSON or no run_id")
    for run_id, tries in attempts.items():
        *earlier, (n, line, row) = tries
        for m, old, old_row in earlier:
            if retries and old_row.get("status") == "error":
                dropped.append(f"line {m} {run_id}: superseded error (retried on line {n})")
            elif retries and old.strip() == line.strip():
                dropped.append(f"line {m} {run_id}: identical repeat of line {n}")
            else:
                problems.append(f"line {m} {run_id}: duplicate of line {n}, content differs" if old != line
                                else f"line {m} {run_id}: duplicate of line {n}")
        want = suite.get(run_id)
        if want is None:
            problems.append(f"line {n} {run_id}: not in the suite")
        elif any(row.get(k) != want[k] for k in ("payload_sha256", "image_sha256") if k in want):
            problems.append(f"line {n} {run_id}: payload/image sha256 differs from the suite row")
        if row.get("status") not in ALLOWED:
            problems.append(f"line {n} {run_id}: status {row.get('status')!r}")
        kept.append(line if line.endswith(b"\n") else line + b"\n")
    missing = suite.keys() - attempts.keys()
    if missing:
        problems.append(f"{len(missing)} suite run_ids missing, e.g. {min(missing)}")
    counts = Counter(t[-1][2].get("status") for t in attempts.values())
    return kept, dropped, problems, counts


def check_scores(scores: dict, n: int) -> list[str]:
    """The board needs a complete score file that covers the rows we ship."""
    problems = [] if scores.get("complete") is True else ['scores file does not say "complete": true']
    if scores.get("completed", n) != n:
        problems.append(f"scores file counts {scores['completed']} rows, results file has {n}")
    if scores.get("missing_rows", 0):
        problems.append(f"scores file has {scores['missing_rows']} missing rows")
    return problems


def sources(kind: str, run_dir: Path) -> dict[str, Path]:
    """Run-folder path -> source file; text also ships each shard's environment.json and status.json."""
    files = {dest: run_dir / src for dest, src in FILES[kind].items()}
    if kind == "text":
        for shard in sorted(run_dir.glob("shard-*/")):
            files.update({f"shards/{shard.name}/{name}": shard / name for name in ("environment.json", "status.json")})
    return files


def rescore(kept: list[bytes], kit_dir: Path, shipped: dict) -> list[str]:
    """Score the cleaned vision results with the kit; the shipped vision-scores.json must be identical."""
    kit_python = kit_dir / "venv" / "bin" / "python"
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "results.jsonl").write_bytes(b"".join(kept))
        cmd = [str(kit_python), "-m", "decision_index", "vision", "score", "--results", f"{tmp}/results.jsonl",
               "--dir", str(kit_dir / "work" / "vision"), "--out", tmp]
        subprocess.run(cmd, cwd=kit_dir / "src", check=True, capture_output=True)
        again = json.loads((Path(tmp) / "vision-scores.json").read_text())
    return [] if again == shipped else ["the kit's score of the cleaned results differs from vision-scores.json"]


def write_gz(path: Path, lines: list[bytes]) -> None:
    """mtime 0: the same lines always give the same bytes."""
    with open(path, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as gz:
        gz.writelines(lines)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def export(args, report: list[str]) -> list[str]:
    """Verify, then write the run folder. Returns the problems; the folder exists only when there are none."""
    run_dir, kind = args.run_dir, args.kind
    suite = suite_evaluations(SUITES[kind])
    lines = read_lines(run_dir / RESULTS[kind])
    kept, dropped, problems, counts = select(lines, suite, retries=kind == "vision")
    files = sources(kind, run_dir)
    problems += [f"missing {src}" for src in files.values() if not src.is_file()]
    if (run_dir / SCORES[kind]).is_file():
        problems += check_scores(json.loads((run_dir / SCORES[kind]).read_text()), len(kept))
    dest = args.out / "runs" / args.name
    if dest.exists():
        problems.append(f"{dest} already exists")
    if kind == "vision" and not problems and not args.no_rescore:
        problems += rescore(kept, args.kit_dir, json.loads((run_dir / SCORES[kind]).read_text()))
    report += [f"{kind} export of {run_dir}", f"suite {SUITES[kind]}: {len(suite)} run_ids",
               f"results: {len(lines)} lines read, {len(kept)} kept, {len(dropped)} dropped",
               f"statuses: {dict(counts)}"] + [f"dropped {d}" for d in dropped[:20]]
    if problems:
        return problems
    dest.mkdir(parents=True)
    write_gz(dest / "results.jsonl.gz", kept)
    for name, src in files.items():
        (dest / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest / name)
    assert read_lines(dest / "results.jsonl.gz") == kept
    report += [f"wrote {dest}", f"results.jsonl.gz sha256 {sha256((dest / 'results.jsonl.gz').read_bytes())}",
               f"results lines sha256 {sha256(b''.join(kept))}"]
    return []


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("kind", choices=["text", "vision"])
    p.add_argument("run_dir", type=Path)
    p.add_argument("--name", required=True, help="folder name under runs/")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--kit-dir", type=Path, default=VISION_KIT)
    p.add_argument("--no-rescore", action="store_true", help="vision: skip scoring the cleaned file with the kit")
    return p.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    report: list[str] = []
    problems = export(args, report)
    report += ([f"FAILED: {len(problems)} problems"] + [f"  {x}" for x in problems[:20]]) if problems else ["OK"]
    text = "\n".join(report) + "\n"
    (args.out / f"{args.name}.export.txt").write_text(text)
    print(text, end="")
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    main()
