"""Main effects and two-way interactions of a vision grid of offline arms on dev; reports, the owner picks.
usage: uv run python scripts/vision_factorial.py --grid GRID.json --out-label L [--latency LEVEL=DIR ...]
GRID.json: {"factors": {F: [level, ...]}, "reference": {F: level}, "cells": [{"dir": DIR, F: level, ...}]}, with
string levels, one cell per combination and DIRs relative to the working directory. --latency LEVEL is a budget level."""

import argparse
import json
import math
from collections import Counter
from datetime import UTC, datetime
from itertools import combinations, product
from pathlib import Path

from scripts import vision_compare as vc
from scripts import vision_splits

IDS, BUDGET = "vision-dev", "budget"
RESAMPLES, SEED = vc.RESAMPLES, vc.SEED


def cell_name(levels: dict[str, str]) -> str:
    return " ".join(f"{f}={v}" for f, v in levels.items())


def check_levels(what: str, levels: dict, factors: dict[str, list[str]]) -> None:
    if set(levels) != set(factors):
        raise SystemExit(f"{what}: names factors {sorted(levels)}, the grid has {sorted(factors)}")
    for f, v in levels.items():
        if v not in factors[f]:
            raise SystemExit(f"{what}: unknown {f} level {v!r}; the grid has {factors[f]}")


def read_grid(path: Path) -> tuple[dict[str, list[str]], dict[str, str], list[dict], list[Path]]:
    """Factors, reference, and each cell's levels and dir with the reference cell first; refuses an unknown
    level, a duplicate cell and a missing one."""
    grid = json.loads(path.read_text())
    factors, reference = grid["factors"], grid["reference"]
    for f, levels in factors.items():
        if len(levels) < 2 or len(set(levels)) < len(levels) or not all(isinstance(v, str) for v in levels):
            raise SystemExit(f"factor {f}: want two or more distinct string levels, got {levels}")
    check_levels("reference", reference, factors)
    dirs: dict[tuple, Path] = {}
    for cell in grid["cells"]:
        if "dir" not in cell:
            raise SystemExit(f"cell {cell}: no dir")
        levels = {k: v for k, v in cell.items() if k != "dir"}
        check_levels(f"cell {cell.get('dir')}", levels, factors)
        key = tuple(levels[f] for f in factors)
        if key in dirs:
            raise SystemExit(f"duplicate cell {cell_name(dict(zip(factors, key)))}: {dirs[key]} and {cell['dir']}")
        dirs[key] = Path(cell["dir"])
    if missing := [cell_name(dict(zip(factors, k))) for k in product(*factors.values()) if k not in dirs]:
        raise SystemExit(f"{len(missing)} missing cell(s): " + "; ".join(missing))
    first = tuple(reference[f] for f in factors)
    keys = [first] + [k for k in dirs if k != first]
    return factors, reference, [dict(zip(factors, k)) for k in keys], [dirs[k] for k in keys]


def load_cells(names: list[str], dirs: list[Path]) -> list[dict]:
    """Offline arms on the same dev ids, scored by one arm and order setting (compare's checks)."""
    for name, path in zip(names, dirs, strict=True):
        if vc.kind(path) != "offline":
            raise SystemExit(f"cell {name}: {path} is a live run; factorial cells are offline scored dirs")
    configs = vc.load_configs(dict(zip(names, dirs, strict=True)), IDS)
    arms = Counter((c["about"]["arm"], c["about"]["orders"]) for c in configs.values())
    if len(arms) > 1:
        raise SystemExit(f"cells scored by different arms or orders {dict(arms)}: rescore them alike")
    return list(configs.values())


def weights(cells: list[dict], factors: dict[str, list[str]], reference: dict[str, str], picks: dict) -> list[float]:
    """Per cell, its weight in the mean over the other factors of the main effect (one pick) or two-way
    interaction (two picks): + at the pick, − at the reference, multiplied across the picked factors."""
    others = math.prod(len(levels) for f, levels in factors.items() if f not in picks)
    return [math.prod((c[f] == v) - (c[f] == reference[f]) for f, v in picks.items()) / others for c in cells]


def dot(ws: list[float], values: list[float]) -> float:
    return sum(w * x for w, x in zip(ws, values, strict=True))


def resampled(rows: list[list[dict]], ws: list[list[float]], mains: int, benches: list[str], resamples: int,
              seed: int) -> tuple[list[list[float]], list[dict[str, list[float]]]]:
    """Each effect's index draws and each main effect's per-benchmark skill draws; every resample draws one set
    of groups within each benchmark and applies it to every cell."""
    draws, skill_draws = [[] for _ in ws], [{b: [] for b in benches} for _ in range(mains)]
    columns = vc.group_columns(rows[0], *({r["id"]: r for r in cell_rows} for cell_rows in rows[1:]))
    for skills in vc.resampled_skills(columns, resamples, seed):
        values = [vc.combine(s) for s in skills]
        for out, w in zip(draws, ws, strict=True):
            out.append(dot(w, values))
        for out, w in zip(skill_draws, ws[:mains], strict=True):
            for b in benches:
                out[b].append(dot(w, [s[b] for s in skills]))
    return draws, skill_draws


def effects(cells: list[dict], rows: list[list[dict]], factors: dict, reference: dict,
            resamples: int, seed: int) -> tuple[list[dict], list[dict]]:
    """Main effects (with per-benchmark unclipped skill effects) and two-way interactions on the index, each
    with a 95% CI from the shared resamples."""
    others = {f: [v for v in levels if v != reference[f]] for f, levels in factors.items()}
    mains = [{f: v} for f, levels in others.items() for v in levels]
    pairs = [{f: v, g: w} for f, g in combinations(factors, 2) for v in others[f] for w in others[g]]
    ws = [weights(cells, factors, reference, p) for p in mains + pairs]
    points = [vc.index(r) for r in rows]
    benches = sorted(points[0][1])
    draws, skill_draws = resampled(rows, ws, len(mains), benches, resamples, seed)
    index_points = [p[0] for p in points]
    result = [{"levels": p, "delta": dot(w, index_points), "ci": vc.ci(d)}
              for p, w, d in zip(mains + pairs, ws, draws, strict=True)]
    for main, w, by_bench in zip(result, ws, skill_draws, strict=False):  # main effects come first
        main["skill"] = {b: {"delta": dot(w, [p[1][b] for p in points]), "ci": vc.ci(by_bench[b])} for b in benches}
    return result[:len(mains)], result[len(mains):]


def latency_by_level(args, factors: dict[str, list[str]]) -> tuple[dict[str, dict], int | None]:
    dirs = vc.named(args.latency, "--latency")
    if unknown := sorted(set(dirs) - set(factors.get(BUDGET, []))):
        raise SystemExit(f"--latency levels {unknown} are not budget levels {factors.get(BUDGET)}")
    return vc.load_latency(dirs)


def interval(e: dict, spec: str) -> str:
    return vc.interval(e["delta"], e["ci"], spec)


def markdown(s: dict) -> str:
    factors, mains = s["factors"], s["main_effects"]
    timed = any(c["latency"] for c in s["cells"])
    lines = [f"# Vision factorial: {s['label']}", "",
             (f"{len(s['cells'])} cells on {s['rows']} rows of `{s['ids']}`; effects are index points against the "
              f"reference `{cell_name(s['reference'])}`. CIs are 95% paired bootstrap ({s['resamples']} resamples, "
              f"seed {s['seed']}) over image groups within each benchmark, one resample shared by every cell."),
             "This table reports; the owner picks.", "", "## Main effects", "",
             "Mean over the other factors' cells of index(level) − index(reference level).", "",
             "| factor | level | Δ index [95% CI] |", "|---|---|---|"]
    lines += [f"| {f} | {v} | {interval(e, '.2f')} |" for e in mains for f, v in e["levels"].items()]
    lines += ["", "## Two-way interactions", "",
              "Mean over the other factor of [index(v, w) − index(v, ref)] − [index(ref, w) − index(ref, ref)].", "",
              "| factors | levels | interaction [95% CI] |", "|---|---|---|"]
    lines += [f"| {' × '.join(e['levels'])} | {' × '.join(e['levels'].values())} | {interval(e, '.2f')} |"
              for e in s["interactions"]]
    lines += ["", "## Per-benchmark main effects", "", "Unclipped skill, Δ [95% CI].", "",
              "| benchmark | rows | " + " | ".join(cell_name(e["levels"]) for e in mains) + " |",
              "|---" * (2 + len(mains)) + "|"]
    for b, n in s["benchmarks"].items():
        lines.append(f"| {b} | {n} | " + " | ".join(interval(e["skill"][b], ".3f") for e in mains) + " |")
    head = "| " + " | ".join(factors) + " | index | ECE | NLL | mean input tokens |"
    lines += ["", "## Cells", "", head + (" p50 ms | p80 ms |" if timed else ""),
              "|---" * (len(factors) + 4 + 2 * timed) + "|"]
    for c in s["cells"]:
        values = [*c["levels"].values(), vc.fmt(c["index"]), vc.fmt(c["ece"], ".4f"), vc.fmt(c["nll"], ".4f"),
                  vc.fmt(c["mean_input_tokens"], ".0f")]
        lat = c["latency"] or {}
        values += [vc.fmt(lat.get("median"), ".0f"), vc.fmt(lat.get("p80"), ".0f")] if timed else []
        lines.append("| " + " | ".join(values) + " |")
    if timed:
        lines += ["", f"Latency per budget level, at power limit {vc.fmt(s['power_limit_w'], '')} W."]
    return "\n".join(lines) + "\n"


def run(args) -> dict:
    factors, reference, cells, dirs = read_grid(args.grid)
    latency, power = latency_by_level(args, factors)
    names = [cell_name(c) for c in cells]
    configs = load_cells(names, dirs)
    rows = [c["rows"] for c in configs]
    mains, pairs = effects(cells, rows, factors, reference, RESAMPLES, SEED)
    summary = {
        "label": args.out_label, "created_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": vision_splits.commit(), "grid": str(args.grid), "ids": IDS, "rows": len(rows[0]),
        "benchmarks": dict(sorted(Counter(r["benchmark"] for r in rows[0]).items())), "weights": vc.WEIGHTS,
        "resamples": RESAMPLES, "seed": SEED, "power_limit_w": power, "factors": factors, "reference": reference,
        "main_effects": mains, "interactions": pairs,
        "cells": [{"name": n, "levels": c} | vc.describe(config, latency.get(c.get(BUDGET)))
                  for n, c, config in zip(names, cells, configs, strict=True)],
    }
    out = args.out_root / f"{datetime.now(UTC).strftime('%Y-%m-%dT%H%M%SZ')}-{args.out_label}"
    out.mkdir(parents=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    (out / "summary.md").write_text(markdown(summary))
    print(f"factorial of {len(cells)} cells on {len(rows[0])} rows -> {out}")
    return summary


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--grid", type=Path, required=True, help="GRID.json: factors, reference and one dir per cell")
    p.add_argument("--latency", action="append", default=[], help="LEVEL=DIR: a budget level's latency summary.json")
    p.add_argument("--out-label", required=True)
    p.add_argument("--out-root", type=Path, default=vc.OUT_ROOT)
    return p.parse_args(argv)


def main(argv=None) -> dict:
    return run(parse_args(argv))


if __name__ == "__main__":
    main()
