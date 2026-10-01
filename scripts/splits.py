"""Which rows each phase-2 step uses, written once to data/splits/ and committed so every fit is reproducible.

usage: uv run python scripts/splits.py   (needs the Index export from scripts/index_suite.py export)
"""

import hashlib
import json
import random
from collections import defaultdict

from gateway.config import ROOT
from scripts.bench_data import JEVBENCH_SHA
from scripts.decision_rows import (
    DECISIONBENCH_SHA,
    decisionbench,
    index_meta,
    index_rows,
    jevbench,
    state_key,
)
from scripts.index_suite import EDITION, HARNESS_SHA

SPLITS = ROOT / "data" / "splits"
SEED = "phase2-v1"
CAP_PER_TASK = 300
LATENCY_SEED = 20260926  # latency-v1's published seed
SIMPLEBENCH = 34  # outside latency-v1's scope


def unit(key: str) -> float:
    return int(hashlib.sha256(f"{SEED}:{key}".encode()).hexdigest()[:12], 16) / 16**12


def cap_per_family(rows: list[dict], cap: int) -> list[dict]:
    by_family: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_family[r["family"]].append(r)
    return [r for members in by_family.values() for r in sorted(members, key=lambda r: unit(r["id"]))[:cap]]


def split_extras(rows: list[dict], index_keys: set[str]) -> dict[str, list[str]]:
    """Dedupe by state, then alternate calib/eval in hash order inside each (source, family, type) stratum."""
    unique: dict[str, dict] = {}
    for r in sorted(rows, key=lambda r: r["id"]):
        unique.setdefault(state_key(r["state"]), r)
    strata: dict[tuple, list[dict]] = defaultdict(list)
    for r in unique.values():
        strata[(r["source"], r["family"], next(iter(r["questions"].values()))["type"])].append(r)
    out: dict[str, list[str]] = {"calib": [], "eval": []}
    for key in sorted(strata):
        for i, r in enumerate(sorted(strata[key], key=lambda r: unit(r["id"]))):
            forced = r["meta"].get("reasoning") or state_key(r["state"]) in index_keys
            out["eval" if forced or i % 2 else "calib"].append(r["id"])
    return out


def systematic(n_items: int, n: int, rng: random.Random) -> list[int]:
    """n evenly spaced indices with a random start: proportional to every stretch of the sorted list."""
    step = n_items / n
    start = rng.random() * step
    return [int(start + i * step) for i in range(n)]


def index_dev(meta: list[dict], n_rows: int = 8000, seed: int = 0) -> list[str]:
    """Whole linked groups, systematic over (benchmark, payload length)."""
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for m in meta:
        groups[(m["meta"]["catalog_id"], m["meta"]["group_id"])].append(m)
    ordered = sorted(groups.values(), key=lambda g: (g[0]["meta"]["catalog_id"], g[0]["meta"]["payload_chars"], g[0]["id"]))
    n_groups = max(1, round(n_rows * len(ordered) / len(meta)))
    return [m["id"] for i in systematic(len(ordered), n_groups, random.Random(seed)) for m in ordered[i]]


def latency_sample(meta: list[dict], timed: int = 750, warmup: int = 10, seed: int = LATENCY_SEED) -> dict:
    """latency-v1's design on our rows: systematic over (benchmark, payload length), SimpleBench out."""
    scope = sorted(
        (m for m in meta if m["meta"]["catalog_id"] != SIMPLEBENCH),
        key=lambda m: (m["meta"]["catalog_id"], m["meta"]["payload_chars"], m["id"]),
    )
    chosen = set(systematic(len(scope), timed, random.Random(seed)))
    rest = [m for i, m in enumerate(scope) if i not in chosen]
    warm = systematic(len(rest), warmup, random.Random(seed + 1))
    return {"warmup": [rest[i]["id"] for i in warm], "timed": [scope[i]["id"] for i in sorted(chosen)]}


def write(name: str, data: dict) -> None:
    SPLITS.mkdir(parents=True, exist_ok=True)
    (SPLITS / f"{name}.json").write_text(json.dumps(data, indent=0) + "\n")


def load_split(name: str) -> dict:
    return json.loads((SPLITS / f"{name}.json").read_text())


def extras() -> list[dict]:
    return jevbench() + cap_per_family(decisionbench(), CAP_PER_TASK)


def rows_for(name: str) -> list[dict]:
    split = load_split(name)
    if name in ("calib", "eval"):
        wanted = set(split["ids"])
        return [r for r in extras() if r["id"] in wanted]
    ids = split["warmup"] + split["timed"] if name == "latency-v1" else split["ids"]
    by_id = {r["id"]: r for r in index_rows(set(ids))}
    return [by_id[i] for i in ids]


def main() -> None:
    meta = index_meta()
    sources = {"jevbench": JEVBENCH_SHA, "decisionbench": DECISIONBENCH_SHA, "harness": HARNESS_SHA, "edition": EDITION}
    parts = split_extras(extras(), {m["state_key"] for m in meta})
    for name in ("calib", "eval"):
        write(name, {"meta": sources | {"seed": SEED, "cap_per_task": CAP_PER_TASK}, "ids": parts[name]})
    write("index-dev", {"meta": sources | {"rows_target": 8000}, "ids": index_dev(meta)})
    write("latency-v1", {"meta": sources | {"seed": LATENCY_SEED, "design": "latency-v1, our rows"}, **latency_sample(meta)})
    print({name: len(v) for name, v in parts.items()})


if __name__ == "__main__":
    main()
