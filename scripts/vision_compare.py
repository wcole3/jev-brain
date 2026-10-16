"""Paired compare of offline arms (scored.jsonl.gz) and live kit runs (results.jsonl.gz) on the same rows; no picks.
usage: uv run python scripts/vision_compare.py --baseline NAME=DIR NAME=DIR ... [--latency NAME=DIR ...] --out-label L"""

import argparse
import gzip
import json
import math
import random
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

from gateway.config import ROOT
from scripts import vision_splits
from scripts.collect import records
from scripts.metrics import EPS, ece_of
from scripts.vision_summary import last_per_run

OUT_ROOT = ROOT / "docs/results/vision-experiments"
RESAMPLES, SEED, EXAMPLES = 10_000, 0, 10
LIVE_FIRST_HINT = "; the baseline is a live run (full suite): put the offline arm first as --baseline"
# Kit edition 0.3 weights (decision_index/vision/spec.py): 1.0 except these two; they reproduce its stored 73.70.
WEIGHTS = {"CV-Bench": 1.0, "BLINK": 1.0, "RealWorldQA": 1.0, "CharXiv": 1.0, "InfographicVQA": 1.0, "Mind2Web": 1.0,
           "Winoground": 1.0, "KIE (CORD+FUNSD)": 1.0, "Moderation (Hateful Memes)": 1.0, "R-Bench-M": 0.5,
           "MMMU-Pro vision": 0.25}


def top(probs: list[float]) -> int:
    return max(range(len(probs)), key=probs.__getitem__)


def answer(row: dict) -> int | None:
    """The top option, or None for an errored live row (no answer)."""
    return None if row.get("errored", False) else top(row["probs"])


def correct(row: dict) -> bool:
    return answer(row) == row["gold"]


def skill(n: int, chance: float, hits: int) -> float:
    """Kit skill from a benchmark's row count, summed chance and summed hits: (acc − chance) / (1 − chance)."""
    return (hits / n - chance / n) / (1 - chance / n)


def combine(skills: dict[str, float]) -> float:
    total = sum(WEIGHTS[b] for b in skills)
    return 100 * sum(WEIGHTS[b] * min(1.0, max(0.0, s)) for b, s in skills.items()) / total


def index(rows: list[dict]) -> tuple[float, dict[str, float]]:
    """The kit's index and per-benchmark skills."""
    sums: dict[str, list] = defaultdict(lambda: [0, 0.0, 0])
    for r in rows:
        s = sums[r["benchmark"]]
        s[0], s[1], s[2] = s[0] + 1, s[1] + r["chance"], s[2] + correct(r)
    skills = {b: skill(*s) for b, s in sums.items()}
    return combine(skills), skills


def ece(rows: list[dict]) -> float:
    return ece_of([max(r["probs"]) for r in rows], [correct(r) for r in rows])


def nll(rows: list[dict]) -> float:
    return sum(-math.log(max(r["probs"][r["gold"]], EPS)) for r in rows) / len(rows)


def mcnemar_p(b: int, c: int) -> float:
    """Exact two-sided McNemar: binomial(b + c, 1/2) tail at min(b, c), doubled, capped at 1."""
    n = b + c
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2**n)


def group_columns(a_rows: list[dict], b_by_id: dict[str, dict]) -> dict[str, list[tuple]]:
    """Per benchmark, per group (sorted): (rows, summed chance, hits in a, hits in b)."""
    sums: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(lambda: [0, 0.0, 0, 0]))
    for r in a_rows:
        g = sums[r["benchmark"]][r["group"]]
        g[0], g[1] = g[0] + 1, g[1] + r["chance"]
        g[2], g[3] = g[2] + correct(r), g[3] + correct(b_by_id[r["id"]])
    return {b: list(zip(*(gs[k] for k in sorted(gs)), strict=True)) for b, gs in sorted(sums.items())}


def bootstrap(columns: dict[str, list[tuple]], resamples: int, seed: int) -> tuple[list[float], dict[str, list[float]]]:
    """Index deltas and per-benchmark skill deltas over resamples of whole groups within each benchmark."""
    rng = random.Random(seed)
    deltas, by_bench = [], {b: [] for b in columns}
    for _ in range(resamples):
        skills_a, skills_b = {}, {}
        for b, (ns, chances, hits_a, hits_b) in columns.items():
            pick = rng.choices(range(len(ns)), k=len(ns))
            n, chance = sum(map(ns.__getitem__, pick)), sum(map(chances.__getitem__, pick))
            skills_a[b] = skill(n, chance, sum(map(hits_a.__getitem__, pick)))
            skills_b[b] = skill(n, chance, sum(map(hits_b.__getitem__, pick)))
            by_bench[b].append(skills_b[b] - skills_a[b])
        deltas.append(combine(skills_b) - combine(skills_a))
    return deltas, by_bench


def ci(values: list[float]) -> list[float]:
    """95% percentile interval, indexed like metrics.paired_bootstrap."""
    s = sorted(values)
    return [s[int(0.025 * len(s))], s[int(0.975 * len(s)) - 1]]


def paired(a_rows: list[dict], b_rows: list[dict], resamples: int = RESAMPLES, seed: int = SEED) -> dict:
    """Config b against baseline a on the same ids (Δ = b − a); groups and benchmarks come from a."""
    b_by_id = {r["id"]: r for r in b_rows}
    if b_by_id.keys() != {r["id"] for r in a_rows}:
        raise ValueError("paired configs must cover the same ids")
    aligned = [b_by_id[r["id"]] for r in a_rows]
    (index_a, skills_a), (index_b, skills_b) = index(a_rows), index(aligned)
    deltas, by_bench = bootstrap(group_columns(a_rows, b_by_id), resamples, seed)
    a_only = sum(correct(x) and not correct(y) for x, y in zip(a_rows, aligned, strict=True))
    b_only = sum(correct(y) and not correct(x) for x, y in zip(a_rows, aligned, strict=True))
    return {
        "n": len(a_rows), "delta_index": index_b - index_a, "ci": ci(deltas),
        "delta_skill": {b: {"delta": skills_b[b] - skills_a[b], "ci": ci(by_bench[b])} for b in sorted(skills_a)},
        "b": a_only, "c": b_only, "mcnemar_p": mcnemar_p(a_only, b_only),
        "discordant_share": (a_only + b_only) / len(a_rows),
        "agreement": sum(answer(x) == answer(y) for x, y in zip(a_rows, aligned, strict=True)) / len(a_rows),
        "delta_ece": ece(aligned) - ece(a_rows), "delta_nll": nll(aligned) - nll(a_rows),
    }


def read_gz(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def collect_tokens(arm: dict) -> dict[str, int]:
    """Input tokens per id from the collect file the arm was scored from; empty if that file is gone."""
    path = Path(arm.get("collect", ""))
    path = path if path.is_absolute() else ROOT / path
    return {r["id"]: r["input_tokens"] for r in records(path)} if path.is_file() else {}


def load_offline(path: Path) -> tuple[list[dict], dict]:
    arm = json.loads((path / "arm.json").read_text()) if (path / "arm.json").exists() else {}
    tokens = collect_tokens(arm)
    rows = [r | {"errored": False, "input_tokens": tokens.get(r["id"])} for r in read_gz(path / "scored.jsonl.gz")]
    keys = ("arm", "orders", "skipped", "fallbacks", "fit_on")
    about = {k: arm.get(k) for k in keys} | {"split": arm.get("collect_config", {}).get("split"), "errored": 0}
    return rows, about


def suite_by_id() -> dict[str, dict]:
    """Suite rows by id, each with its image group."""
    rows = vision_splits.read_suite()
    group = vision_splits.groups(rows)
    return {r["id"]: r | {"group": group[r["id"]]} for r in rows}


def live_row(result: dict, suite_row: dict) -> dict:
    """A kit result as a scored row; an errored row or one without probabilities is uniform and wrong."""
    names = list(suite_row["questions"]["answer"]["criteria"])
    response = result.get("response") or {}
    probs = response.get("answers", {}).get("answer", {}).get("probabilities")
    errored = result["status"] != "ok" or not probs
    return {"id": result["run_id"], "benchmark": suite_row["benchmark"], "group": suite_row["group"],
            "gold": names.index(suite_row["expected"]["answer"]), "chance": 1 / len(names), "errored": errored,
            "probs": [1 / len(names)] * len(names) if errored else [probs.get(k, 0.0) for k in names],
            "input_tokens": None if errored else response.get("usage", {}).get("input_tokens")}


def load_live(path: Path, suite: dict[str, dict], keep: set[str] | None = None) -> tuple[list[dict], dict]:
    """The kit's last row per run_id, restricted to keep (the baseline's ids) when given."""
    results = [r for r in last_per_run(read_gz(path / "results.jsonl.gz")) if keep is None or r["run_id"] in keep]
    rows = [live_row(r, suite[r["run_id"]]) for r in results]
    return rows, {"status": dict(Counter(r["status"] for r in results)), "errored": sum(r["errored"] for r in rows)}


def kind(path: Path) -> str:
    if (path / "scored.jsonl.gz").exists():
        return "offline"
    if (path / "results.jsonl.gz").exists():
        return "live"
    raise SystemExit(f"{path}: neither scored.jsonl.gz (offline arm) nor results.jsonl.gz (live run)")


def check_ids(name: str, want: set[str], have: set[str], hint: str = "") -> None:
    missing, extra = sorted(want - have), sorted(have - want)
    if missing or extra:
        raise SystemExit(f"{name}: ids differ from the baseline: {len(missing)} missing {missing[:EXAMPLES]}, "
                         f"{len(extra)} extra {extra[:EXAMPLES]}{hint}")


def load_configs(sources: dict[str, Path]) -> dict[str, dict]:
    """Every config's rows on the baseline's ids; live runs are cut to them, anything else must match exactly."""
    suite = suite_by_id() if any(kind(p) == "live" for p in sources.values()) else {}
    configs, want, base_kind = {}, None, kind(next(iter(sources.values())))
    for name, path in sources.items():  # the baseline is first
        rows, about = load_offline(path) if kind(path) == "offline" else load_live(path, suite, want)
        ids = {r["id"] for r in rows}
        if want is None:
            want = ids
        live_first = base_kind == "live" and kind(path) == "offline"
        check_ids(name, want, ids, LIVE_FIRST_HINT if live_first else "")
        configs[name] = {"path": str(path), "kind": kind(path), "rows": rows, "about": about}
    return configs


def latency_summary(path: Path) -> dict:
    """A latency run's summary.json; refuses one without latency or with no steady power limit."""
    s = json.loads((path / "summary.json").read_text())
    if not s.get("latency_ms"):
        raise SystemExit(f"{path}: summary.json has no latency (latency_ms)")
    if s.get("power_limit_w") is None or s.get("power_limit_w_end") is None:
        raise SystemExit(f"{path}: summary.json lacks power_limit_w / power_limit_w_end (a run from before Task 5?)")
    if s["power_limit_w"] != s["power_limit_w_end"]:
        raise SystemExit(f"{path}: power limit changed mid-run ({s['power_limit_w']} -> {s['power_limit_w_end']} W)")
    return s


def load_latency(dirs: dict[str, Path]) -> tuple[dict[str, dict], int | None]:
    """Latency by config name and the shared power limit; refuses summaries taken at different limits."""
    summaries = {name: latency_summary(d) for name, d in dirs.items()}
    limits = {s["power_limit_w"] for s in summaries.values()}
    if len(limits) > 1:
        raise SystemExit(f"latency summaries mix power limits {sorted(limits)} W: compare like with like")
    return {n: s["latency_ms"] for n, s in summaries.items()}, next(iter(limits), None)


def describe(config: dict, latency: dict | None) -> dict:
    rows = config["rows"]
    value, skills = index(rows)
    tokens = [r["input_tokens"] for r in rows if r["input_tokens"] is not None]
    return {"path": config["path"], "kind": config["kind"], "about": config["about"], "index": value,
            "skills": skills, "accuracy": sum(map(correct, rows)) / len(rows), "ece": ece(rows), "nll": nll(rows),
            "errored": config["about"]["errored"], "mean_input_tokens": sum(tokens) / len(tokens) if tokens else None,
            "latency": latency}


def fmt(x, spec: str = ".2f") -> str:
    return "—" if x is None else format(x, spec)


def interval(delta: float, bounds: list[float], spec: str) -> str:
    return f"{delta:+{spec}} [{bounds[0]:+{spec}}, {bounds[1]:+{spec}}]"


def markdown(s: dict) -> str:
    base, cfgs, pairs = s["baseline"], s["configs"], s["paired"]
    timed = any(c["latency"] for c in cfgs.values())
    lines = [f"# Vision compare: {s['label']}", "",
             (f"Baseline `{base}`, {s['rows']} rows, Δ = config − baseline. CIs are 95% paired bootstrap "
              f"({s['resamples']} resamples, seed {s['seed']}) over image groups within each benchmark."),
             "Errored live rows count as wrong. This table reports; the owner picks.", "", "## Frontier", ""]
    head = "| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |"
    lines += [head + (" p50 ms | p80 ms |" if timed else ""), "|---" * (8 + 2 * timed) + "|"]
    for name, c in cfgs.items():
        delta = interval(pairs[name]["delta_index"], pairs[name]["ci"], ".2f") if name in pairs else "baseline"
        cells = [name, c["kind"], fmt(c["index"]), delta, fmt(c["ece"], ".4f"), fmt(c["nll"], ".4f"),
                 fmt(c["mean_input_tokens"], ".0f"), str(c["errored"])]
        lat = c["latency"] or {}
        cells += [fmt(lat.get("median"), ".0f"), fmt(lat.get("p80"), ".0f")] if timed else []
        lines.append("| " + " | ".join(cells) + " |")
    if timed:
        lines += ["", f"Latency at power limit {fmt(s['power_limit_w'], '')} W."]
    lines += ["", "## Paired", "", "| config | agreement | d | b (base only) | c (config only) | McNemar p | ΔECE | ΔNLL |",
              "|---|---|---|---|---|---|---|---|"]
    lines += [f"| {n} | {p['agreement']:.4f} | {p['discordant_share']:.4f} | {p['b']} | {p['c']} | {p['mcnemar_p']:.4g} | "
              f"{p['delta_ece']:+.4f} | {p['delta_nll']:+.4f} |" for n, p in pairs.items()]
    lines += ["", "## Per-benchmark Δ skill", "", "| benchmark | rows | baseline skill | " + " | ".join(pairs) + " |",
              "|---" * (3 + len(pairs)) + "|"]
    for b, n in s["benchmarks"].items():
        deltas = [interval(p["delta_skill"][b]["delta"], p["delta_skill"][b]["ci"], ".3f") for p in pairs.values()]
        lines.append(f"| {b} | {n} | {cfgs[base]['skills'][b]:.3f} | " + " | ".join(deltas) + " |")
    return "\n".join(lines) + "\n"


def named(pairs: list[str], what: str) -> dict[str, Path]:
    out = {}
    for item in pairs:
        name, sep, path = item.partition("=")
        if not sep or not name or not path or name in out:
            raise SystemExit(f"{what} {item!r}: want NAME=DIR with a unique NAME")
        out[name] = Path(path)
    return out


def run(args) -> dict:
    sources = named([args.baseline, *args.configs], "config")
    base = next(iter(sources))
    lat_dirs = named(args.latency, "--latency")
    if unknown := sorted(set(lat_dirs) - set(sources)):
        raise SystemExit(f"--latency names {unknown} are not configs {list(sources)}")
    latency, power = load_latency(lat_dirs)
    configs = load_configs(sources)
    rows = configs[base]["rows"]
    summary = {
        "label": args.out_label, "created_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": vision_splits.commit(), "baseline": base, "rows": len(rows),
        "benchmarks": dict(sorted(Counter(r["benchmark"] for r in rows).items())), "weights": WEIGHTS,
        "resamples": RESAMPLES, "seed": SEED, "power_limit_w": power,
        "configs": {n: describe(c, latency.get(n)) for n, c in configs.items()},
        "paired": {n: paired(rows, c["rows"]) for n, c in configs.items() if n != base},
    }
    out = args.out_root / f"{datetime.now(UTC).strftime('%Y-%m-%dT%H%M%SZ')}-{args.out_label}"
    out.mkdir(parents=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    (out / "summary.md").write_text(markdown(summary))
    print(f"compare {list(sources)} on {len(rows)} rows -> {out}")
    return summary


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", required=True, help="NAME=DIR of the config every other one is paired against")
    p.add_argument("configs", nargs="*", help="NAME=DIR of each other config")
    p.add_argument("--latency", action="append", default=[], help="NAME=DIR holding a latency summary.json")
    p.add_argument("--out-label", required=True)
    p.add_argument("--out-root", type=Path, default=OUT_ROOT)
    return p.parse_args(argv)


def main(argv=None) -> dict:
    return run(parse_args(argv))


if __name__ == "__main__":
    main()
