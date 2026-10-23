"""hle-focus: every HLE row plus a few whole groups from each other Index benchmark, in data/splits/hle-focus.json.

usage: uv run python scripts/hle_focus.py   (needs the Index export from scripts/index_suite.py export; CPU only)
"""

import hashlib
from collections import Counter, defaultdict

from scripts.decision_rows import index_meta
from scripts.splits import load_split, pins, write

SEED = "hle-focus"
HLE = 45
MIN_HLE_SHARE = 0.70
RULE = "all HLE rows; other benchmarks: whole index-dev groups in seeded hash order until q rows, largest q with HLE >= 70%"
# index-0.3.json in the Decision Index harness (areas[].benchmarks), minus HLE
PUBLIC_INDEX = {1, 2, 3, 4, 5, 9, 11, 12, 20, 21, 22, 23, 25, 28, 29, 30, 31, 32, 33, 36, 37, 38, 39, 40, 41, 42,
                43, 44, 50, 56, 57, 58, 59, 61, 62, 64}


def group_key(catalog_id: int, group_id) -> str:
    return hashlib.sha256(f"{SEED}:{catalog_id}:{group_id}".encode()).hexdigest()


def ordered_groups(meta: list[dict]) -> dict[int, list[list[str]]]:
    """Per benchmark, its linked groups (lists of ids) in seeded hash order."""
    groups: dict[tuple, list[str]] = defaultdict(list)
    for m in meta:
        groups[(m["meta"]["catalog_id"], m["meta"]["group_id"])].append(m["id"])
    out: dict[int, list[list[str]]] = defaultdict(list)
    for (cid, gid), ids in sorted(groups.items(), key=lambda kv: group_key(*kv[0])):
        out[cid].append(sorted(ids))
    return out


def pick_groups(groups: list[list[str]], q: int) -> list[str]:
    """Whole groups, in order, until at least q rows."""
    ids: list[str] = []
    for g in groups:
        if len(ids) >= q:
            break
        ids += g
    return ids


def others(meta: list[dict], dev_ids: list[str]) -> dict[int, list[list[str]]]:
    dev = set(dev_ids)
    pool = [m for m in meta if m["id"] in dev and m["meta"]["catalog_id"] in PUBLIC_INDEX]
    return ordered_groups(pool)


def hle_share(hle: int, picked: dict[int, list[str]]) -> float:
    return hle / (hle + sum(len(v) for v in picked.values()))


def largest_q(hle: int, groups: dict[int, list[list[str]]]) -> int:
    """Binary search: more q never means fewer rows, so the HLE share only falls."""
    def share(q: int) -> float:
        return hle_share(hle, {c: pick_groups(g, q) for c, g in groups.items()})

    if share(1) < MIN_HLE_SHARE:
        raise SystemExit(f"HLE share is {share(1):.3f} at q=1: the first groups are too big for {MIN_HLE_SHARE}")
    lo, hi = 1, max(sum(map(len, g)) for g in groups.values())
    while lo < hi:
        mid = (lo + hi + 1) // 2
        lo, hi = (mid, hi) if share(mid) >= MIN_HLE_SHARE else (lo, mid - 1)
    return lo


def hle_focus(meta: list[dict], dev_ids: list[str]) -> tuple[int, list[str]]:
    hle = sorted(m["id"] for m in meta if m["meta"]["catalog_id"] == HLE)
    groups = others(meta, dev_ids)
    q = largest_q(len(hle), groups)
    return q, sorted(hle + [i for g in groups.values() for i in pick_groups(g, q)])


def main() -> None:
    meta = index_meta()
    q, ids = hle_focus(meta, load_split("index-dev")["ids"])
    cid = {m["id"]: m["meta"]["catalog_id"] for m in meta}
    per_benchmark = dict(sorted(Counter(cid[i] for i in ids).items()))
    hle = per_benchmark[HLE]
    info = {"rule": RULE, "seed": SEED, "q": q, "rows": len(ids), "hle_rows": hle,
            "hle_share": round(hle / len(ids), 4), "per_benchmark": per_benchmark}
    write("hle-focus", {"meta": pins() | info, "ids": ids})
    print({k: v for k, v in info.items() if k != "rule"})


if __name__ == "__main__":
    main()
