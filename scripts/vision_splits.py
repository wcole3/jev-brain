"""Dev / holdout / latency splits of the public vision suite, cut by image group and committed.

usage: uv run python scripts/vision_splits.py write
"""

import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from gateway.config import ROOT

SUITE = ROOT / ".cache/decision-index-vision/work/vision/vision-rows.jsonl"
SPLITS = ROOT / "data/splits"
HOLDOUT_LOG = ROOT / "docs/results/vision-experiments/holdout-log.md"
SEED = 20261016
DEV_CAP, HOLDOUT_CAP, SHARE = 136, 218, 0.4
LATENCY_ROWS, WARMUP = 320, 20
MAX_HOLDOUT_LABELS = 5  # distinct experiments on the holdout before it warns
MAX_PER_GROUP = 10  # one big group (a 70-row FUNSD document) must not dominate a benchmark's split
LOG_HEADER = "| UTC | tool | label | commit |\n|---|---|---|---|\n"
CELL = re.compile(r"(?<!\\)\|")  # a cell border: a pipe not escaped as \|
STAMP = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ")
RULE = ("Image groups per benchmark by seeded hash, each capped at 10 rows chosen by sha256(seed:row_id); "
        "dev min(136, 40%), holdout min(218, 40%), the rest of each group and of each benchmark reserve.")


def digest(seed: int, key: str) -> str:
    return hashlib.sha256(f"{seed}:{key}".encode()).hexdigest()


def groups(rows: list[dict]) -> dict[str, str]:
    """Row id -> smallest id among rows linked by any shared image path."""
    parent = {r["id"]: r["id"] for r in rows}

    def find(i: str) -> str:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    owner: dict[str, str] = {}
    for r in rows:
        for image in r["images"]:
            a, b = find(r["id"]), find(owner.setdefault(image, r["id"]))
            parent[max(a, b)] = min(a, b)
    return {i: find(i) for i in parent}


def fill(order: list[list[str]], target: int) -> tuple[list[str], list[list[str]]]:
    """Take whole groups in order until target rows are met; return them and the rest."""
    taken: list[str] = []
    for n, members in enumerate(order):
        if len(taken) >= target:
            return taken, order[n:]
        taken += members
    return taken, []


def quotas(sizes: dict[str, int], total: int) -> dict[str, int]:
    """Largest-remainder split of total across the keys, proportional to sizes."""
    whole = sum(sizes.values())
    base = {k: total * v // whole for k, v in sizes.items()}
    by_remainder = sorted(sizes, key=lambda k: (-(total * sizes[k] % whole), k))
    for k in by_remainder[: total - sum(base.values())]:
        base[k] += 1
    return base


def latency_ids(dev: list[str], bench: dict[str, str], seed: int) -> list[str]:
    ordered = sorted(dev, key=lambda i: digest(seed, i))
    per: dict[str, list[str]] = defaultdict(list)
    for i in ordered:
        per[bench[i]].append(i)
    quota = quotas({b: len(v) for b, v in per.items()}, LATENCY_ROWS)
    picked = {i for b, v in per.items() for i in v[: quota[b]]}
    return [i for i in ordered if i in picked]


def capped(members: list[str], seed: int) -> list[str]:
    """A group's rows in the split: at most MAX_PER_GROUP, the first by seeded hash; the rest stay reserve."""
    return sorted(sorted(members, key=lambda i: digest(seed, i))[:MAX_PER_GROUP])


def cut(rows: list[dict], seed: int = SEED) -> dict[str, list[str]]:
    key_of = groups(rows)
    bench = {r["id"]: r["benchmark"] for r in rows}
    members: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for i, key in key_of.items():
        members[bench[i]][key].append(i)
    dev: list[str] = []
    holdout: list[str] = []
    for b in sorted(members):
        n = sum(len(m) for m in members[b].values())
        order = [capped(members[b][k], seed) for k in sorted(members[b], key=lambda k: digest(seed, k))]
        got, order = fill(order, min(DEV_CAP, int(SHARE * n)))
        dev += got
        got, _ = fill(order, min(HOLDOUT_CAP, int(SHARE * n)))
        holdout += got
    return {"dev": sorted(dev), "holdout": sorted(holdout), "latency": latency_ids(dev, bench, seed)}


def suite_hash() -> str:
    if not SUITE.exists():
        raise SystemExit(f"{SUITE}: the vision suite file is missing; split manifests are checked against it")
    return hashlib.sha256(SUITE.read_bytes()).hexdigest()


def read_suite() -> list[dict]:
    return [json.loads(line) for line in SUITE.read_text().splitlines() if line]


def commit() -> str:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()

    return git("rev-parse", "--short", "HEAD") + ("-dirty" if git("status", "--porcelain") else "")


def logged_labels(log_path: Path) -> set[str]:
    """The distinct labels in the holdout log: rereading one experiment is one use. Only dated rows count."""
    rows = [CELL.split(line.strip()) for line in log_path.read_text().splitlines()]
    return {r[3].strip().replace("\\|", "|") for r in rows if len(r) == 6 and STAMP.fullmatch(r[1].strip())}


def log_holdout_use(tool: str, label: str, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text(LOG_HEADER)
    labels = logged_labels(log_path) | {label}
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    cell = label.replace("|", "\\|")
    with log_path.open("a") as f:
        f.write(f"| {now} | {tool} | {cell} | {commit()} |\n")
    if len(labels) > MAX_HOLDOUT_LABELS:
        print(f"warning: holdout read under {len(labels)} labels (log: {log_path}); stop tuning on it", file=sys.stderr)


def read_manifest(name: str) -> dict:
    """A split manifest. Refuses one cut from a suite file other than the one on disk."""
    manifest = json.loads((SPLITS / f"{name}.json").read_text())
    have = suite_hash()
    if manifest["meta"]["suite_sha256"] != have:
        raise SystemExit(f"{name}: cut from suite {manifest['meta']['suite_sha256']}, file is {have}; rerun write")
    return manifest


def load_split(
    name: str, *, holdout: bool = False, tool: str = "", label: str = "", log_path: Path | None = None
) -> list[dict]:
    """Suite rows for a manifest, in manifest order. Refuses a stale suite and unflagged holdout reads."""
    if name == "vision-holdout":
        if not holdout:
            raise SystemExit("vision-holdout is the untouched test set: pass holdout=True (--holdout) to read it")
        log_holdout_use(tool, label, log_path or HOLDOUT_LOG)
    manifest = read_manifest(name)
    by_id = {r["id"]: r for r in read_suite()}
    return [by_id[i] for i in manifest["ids"]]


def write() -> None:
    rows = read_suite()
    bench = {r["id"]: r["benchmark"] for r in rows}
    parts = cut(rows)
    SPLITS.mkdir(parents=True, exist_ok=True)
    for name, ids in parts.items():
        counts = defaultdict(int)
        for i in ids:
            counts[bench[i]] += 1
        meta = {"suite_sha256": suite_hash(), "seed": SEED, "rule": RULE, "counts": dict(sorted(counts.items()))}
        if name == "latency":
            meta["warmup"] = WARMUP
        (SPLITS / f"vision-{name}.json").write_text(json.dumps({"meta": meta, "ids": ids}, indent=0) + "\n")
        print(name, len(ids), meta["counts"])


if __name__ == "__main__":
    if sys.argv[1:] != ["write"]:
        raise SystemExit(__doc__)
    write()
