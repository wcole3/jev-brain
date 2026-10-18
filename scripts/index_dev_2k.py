"""Round-3 samples: index-dev-2k (every k-th Index dev group) and calib-600 (calib, per family), in data/splits/.

usage: uv run python scripts/index_dev_2k.py   (needs the Index export from scripts/index_suite.py export; CPU only)
"""

import hashlib
from collections import defaultdict

from scripts.decision_rows import index_meta
from scripts.host_compare import make_ids
from scripts.splits import load_split, pins, rows_for, write

RULE = "every k-th whole linked group, ordered by benchmark and payload length"
CALIB_SEED = "calib-600"


def index_dev_2k(meta: list[dict], dev_ids: list[str]) -> list[str]:
    return make_ids(meta, dev_ids, 2000)


def quotas(counts: dict[str, int], n: int) -> dict[str, int]:
    """n split proportionally to counts, by largest remainder (ties by name)."""
    total = sum(counts.values())
    out = {k: n * c // total for k, c in counts.items()}
    by_remainder = sorted(counts, key=lambda k: (-(n * counts[k] % total), k))
    for k in by_remainder[: n - sum(out.values())]:
        out[k] += 1
    return out


def calib_key(row_id: str) -> str:
    return hashlib.sha256(f"{CALIB_SEED}:{row_id}".encode()).hexdigest()


def calib_600(rows: list[dict], n: int = 600) -> list[str]:
    """Per family its share of n; within a family the lowest sha256(seed:id)."""
    by_family: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        by_family[r["family"]].append(r["id"])
    share = quotas({f: len(ids) for f, ids in by_family.items()}, n)
    return sorted(i for f, ids in by_family.items() for i in sorted(ids, key=calib_key)[: share[f]])


def main() -> None:
    ids = index_dev_2k(index_meta(), load_split("index-dev")["ids"])
    write("index-dev-2k", {"meta": pins() | {"from": "index-dev", "rule": RULE, "rows": len(ids)}, "ids": ids})
    write("calib-600", {"meta": pins() | {"seed": CALIB_SEED}, "ids": calib_600(rows_for("calib"))})
    print({"index-dev-2k": len(ids), "calib-600": 600})


if __name__ == "__main__":
    main()
