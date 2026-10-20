"""Round-3 option-order policies on text: each fitted on calib, scored on index-dev and eval against identity.

usage: uv run python scripts/r3_orders.py --profile P [--layout NAME] [--dry-run]
       uv run python scripts/r3_orders.py --profile P [--layout NAME | --layout-file TOML] --calib FILE --dev FILE
Default: the header records of .cache/collect/P/{calib,index-dev,eval}.jsonl.gz, gated at the shipped T, written to
docs/results/archive/<UTC>-r3-orders-text-P/summary.{md,json}; --layout NAME (a served layout) writes
<UTC>-r4-orders-text-NAME-P/. --calib/--dev: the layout's records of two collect files, on the calib-600 and
index-dev-2k rows, gated at their own identity T (an experiment layout has no shipped calibration), written to
<UTC>-r4-orders-text-NAME-2k-P/. Runs on CPU. --dry-run prints the markdown and writes nothing.
"""

import argparse
import json
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path

from gateway.calibration import TYPES
from gateway.config import ROOT, Settings
from gateway.layouts import Layout, load_layout, load_layouts
from gateway.schema import Question
from scripts import host_info
from scripts.bench import git_revision
from scripts.bench_report import provenance
from scripts.collect import records
from scripts.evaluate import collect_stamp, now
from scripts.experiment_layouts import repo_relative
from scripts.experiments import BY_OPTIONS, compare_groups, per_group, summary
from scripts.m3 import load, shipped_calibration
from scripts.m3_report import arm_table, ci, ordered
from scripts.metrics import Scored
from scripts.offline import fmt, gold_index, render_question
from scripts.order_policies import IDENTITY, POLICIES, Policy, combine, cost, fit_types, select
from scripts.splits import SPLITS as SPLITS_DIR
from scripts.splits import rows_for

LAYOUT = "header"
SPLITS = ("index-dev", "eval")
FILE_SPLITS = ("calib-600", "index-dev-2k")  # file mode: fit on the first, score the second
BASE = "identity"
NOTES = {"fits": "each policy's T, or tn-prob's alpha + beta ln n (floored at 0.05), per type on calib, b = 0",
         "orders": "second = reversed; aleria = identity + cyclic:2's half turn, then cyclic:4's other shifts",
         "approx skill": "per source/family (acc − mean 1/n) / (1 − mean 1/n), clipped at 0, unweighted mean",
         "cost": "reads per question and share paying a second read (text records hold no token counts)"}


@dataclass(frozen=True)
class Item:
    source: str
    family: str
    type: str
    gold: int
    n: int
    reads: dict[tuple[int, ...], list[float]]


def items(recs: list[dict], rows: dict, layout: Layout) -> dict[tuple[str, str], Item]:
    """Every gold-labelled question of the layout's ok records among rows, with all its collected reads by perm."""
    out = {}
    for rec in recs:
        if rec["status"] != "ok" or rec["layout"] != layout.name or rec["id"] not in rows:
            continue
        row = rows[rec["id"]]
        for qid, reads in rec["questions"].items():
            q = render_question(Question(**row["questions"][qid]), layout)
            gold = gold_index(q, row["gold"].get(qid))
            if gold is not None:
                by_perm = {tuple(r["perm"]): r["logprobs"] for r in reads}
                out[(rec["id"], qid)] = Item(row["source"], row["family"], q.type, gold, len(q.options), by_perm)
    return out


def chosen(questions: dict, policy: Policy, gate_T: dict) -> dict:
    out = {}
    for key, i in questions.items():
        try:
            out[key] = select(i.reads, i.n, policy, gate_T[i.type])
        except ValueError as e:
            raise ValueError(f"{key[0]}/{key[1]}: {policy.name}: {e}") from None
    return out


def by_type(questions: dict, picked: dict) -> dict[str, list]:
    out = {t: [] for t in TYPES}
    for key, i in questions.items():
        out[i.type].append((picked[key], i.gold, i.n))
    return out


def identity_T(calib_items: dict) -> dict[str, float]:
    """The identity policy's mean-prob T per type; identity never gates, so its gate T is a placeholder."""
    picked = chosen(calib_items, IDENTITY, dict.fromkeys(TYPES, 1.0))
    return fit_types(by_type(calib_items, picked), IDENTITY.combine)


def fit_job(job: tuple) -> dict:
    policy, calib = job
    return fit_types(calib, policy.combine)


def probs(c: list, rule: str, param) -> list[float]:
    return combine(c, rule, 0.0, param) if rule == "tn-prob" else combine(c, rule, param, None)


def approx_skill(scored: list[Scored]) -> float | None:
    """Per source/family (acc − mean 1/n) / (1 − mean 1/n), clipped at 0; the unweighted mean over families."""
    families = defaultdict(list)
    for i in scored:
        families[(i.source, i.family)].append(i)
    skills = []
    for part in families.values():
        chance = sum(1 / len(i.probs) for i in part) / len(part)
        skills.append(max(0.0, (sum(i.correct for i in part) / len(part) - chance) / (1 - chance)))
    return sum(skills) / len(skills) if skills else None


def costs(reads: dict):
    def fn(part: dict) -> dict:
        counts = [reads[k] for k in part]
        return {"mean_reads": sum(counts) / len(counts), "share_second": sum(c > 1 for c in counts) / len(counts)}
    return fn


def split_data(questions: dict, policies: list[Policy], fits: dict, gate_T: dict, pmap=map) -> dict:
    """Every policy on one split, with its paired differences from identity in each bucket."""
    scored, summaries = {}, {}
    for p in policies:
        picked = chosen(questions, p, gate_T)
        scored[p.name] = {k: Scored(i.source, i.family, i.type, i.gold, probs(picked[k], p.combine, fits[p.name][i.type]))
                          for k, i in questions.items()}
        by_group = per_group(scored[p.name], BY_OPTIONS, costs({k: cost(c) for k, c in picked.items()}))
        summaries[p.name] = {**by_group["overall"]["all"], "approx_skill": approx_skill(list(scored[p.name].values())),
                             "cost": by_group, **per_group(scored[p.name], BY_OPTIONS, summary)}
    vs = compare_groups(scored[BASE], {name: s for name, s in scored.items() if name != BASE}, BY_OPTIONS, pmap)
    return {"policies": summaries, "vs_identity": vs}


def as_json(param) -> float | dict:
    return {"alpha": param[0], "beta": param[1]} if isinstance(param, tuple) else param


def report(calib: tuple[list, dict], splits: dict[str, tuple[list, dict]], gate_T: dict[str, float] | None,
           policies: list[Policy] = POLICIES, pmap=map, layout: Layout | None = None) -> dict:
    """Fit each policy per type on calib (b = 0), gating at gate_T or else calib's identity T, then score each split."""
    layout = layout or load_layouts()[LAYOUT]
    calib_items = items(*calib, layout)
    gate_T = dict(gate_T) if gate_T is not None else identity_T(calib_items)
    jobs = [(p, by_type(calib_items, chosen(calib_items, p, gate_T))) for p in policies]
    fits = dict(zip([p.name for p in policies], pmap(fit_job, jobs), strict=True))
    return {
        "policies": [asdict(p) for p in policies],
        "gate_T": gate_T,
        "fits": {name: {t: as_json(v) for t, v in fit.items()} for name, fit in fits.items()},
        "splits": {split: split_data(items(*data, layout), policies, fits, gate_T, pmap)
                   for split, data in splits.items()},
    }


def run(profile: str, layout: str = LAYOUT, pmap=map) -> dict:
    """Stage 1: a served layout's full collects, gated at its shipped T."""
    s, start = Settings.from_profile(profile), time.monotonic()
    calib_recs, calib_rows, calib_path = load(profile, "calib")
    shipped, splits, paths = shipped_calibration(s, layout, calib_recs), {}, {"calib": calib_path}
    for split in SPLITS:
        recs, rows, paths[split] = load(profile, split)
        shipped_calibration(s, layout, recs)  # refuses a split collected under another stamp
        splits[split] = recs, rows
    out = report((calib_recs, calib_rows), splits, shipped.T, POLICIES, pmap, load_layouts()[layout])
    meta = {"timestamp": now(), "repo commit": git_revision(), "host": host_info.summary(), "profile": profile,
            "layout": layout, **{f"collect {split}": path for split, path in paths.items()},
            "gates": (f"first (identity) read at {shipped.source}: T " +
                      ", ".join(f"{t} {v:.3f}" for t, v in shipped.T.items()) + f" (b {shipped.b:.3f}, not used)"),
            **NOTES, "run time": f"{time.monotonic() - start:.0f} s"}
    return {"meta": meta, **out}


def run_files(profile: str, layout: Layout, calib: Path, dev: Path, pmap=map) -> dict:
    """Stage 3: the layout's records of two collect files on the calib-600 and index-dev-2k rows, own identity gate."""
    start, paths = time.monotonic(), dict(zip(FILE_SPLITS, (calib, dev), strict=True))
    recs = {split: [r for r in records(path) if r["layout"] == layout.name] for split, path in paths.items()}
    if empty := [str(paths[split]) for split, rs in recs.items() if not rs]:
        raise SystemExit(f"no {layout.name} records in {', '.join(empty)}")
    if collect_stamp(recs["calib-600"], layout.name) != collect_stamp(recs["index-dev-2k"], layout.name):
        raise SystemExit(f"{calib} and {dev} were collected under other stamps")
    data = {split: (rs, {r["id"]: r for r in rows_for(split)}) for split, rs in recs.items()}
    out = report(data["calib-600"], {"index-dev-2k": data["index-dev-2k"]}, None, POLICIES, pmap, layout)
    meta = {"timestamp": now(), "repo commit": git_revision(), "host": host_info.summary(), "profile": profile,
            "layout": layout.name, **{f"collect {split}": repo_relative(path) for split, path in paths.items()},
            **{f"rows {split}": repo_relative(SPLITS_DIR / f"{split}.json") for split in FILE_SPLITS},
            "gates": "own identity T on calib-600", **NOTES, "run time": f"{time.monotonic() - start:.0f} s"}
    return {"meta": meta, **out}


def param(v) -> str:
    return f"α {v['alpha']:.3f}, β {v['beta']:+.3f}" if isinstance(v, dict) else f"{v:.3f}"


def fits_table(report: dict) -> list[str]:
    lines = ["| policy | " + " | ".join(TYPES) + " |", "|---|" + "---|" * len(TYPES)]
    return lines + [f"| {name} | " + " | ".join(param(fit[t]) for t in TYPES) + " |"
                    for name, fit in report["fits"].items()]


def headline(data: dict) -> list[str]:
    lines = [("| policy | mean reads | share 2nd read | n | accuracy | ECE | NLL | approx skill | Δ accuracy | Δ ECE"
              " | Δ NLL |"), "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, s in data["policies"].items():
        a, c = s["overall"]["all"], data["vs_identity"].get(name, {}).get("overall", {}).get("all")
        deltas = [ci(c[m], places) if c else "baseline" for m, places in (("accuracy", 3), ("ece", 4), ("nll", 4))]
        lines.append(f"| {name} | {fmt(s['mean_reads'])} | {fmt(s['share_second'])} | {a['n']} | {fmt(a['accuracy'])}"
                     f" | {fmt(a['ece'])} | {fmt(a['nll'])} | {fmt(s['approx_skill'])} | " + " | ".join(deltas) + " |")
    return lines


def cost_table(data: dict) -> list[str]:
    buckets = ordered({b for s in data["policies"].values() for b in s["cost"]["options"]})
    lines = ["| policy | " + " | ".join(buckets) + " |", "|---|" + "---|" * len(buckets)]
    for name, s in data["policies"].items():
        cells = [s["cost"]["options"].get(b) for b in buckets]
        lines.append(f"| {name} | " + " | ".join(f"{fmt(c['mean_reads'])} / {fmt(c['share_second'])}" if c else "n/a"
                                                 for c in cells) + " |")
    return lines


def markdown(report: dict) -> str:
    meta = report["meta"]
    lines = [f"# {meta['profile']} R3 option-order policies: text ({meta['layout']})", "", provenance(meta),
             "## Fits (calib)", "", "T per type; tn-prob as T(n) = α + β ln n.", "", *fits_table(report), ""]
    for split, data in report["splits"].items():
        lines += [f"## {split}", "",
                  ("Δ is policy − identity on the same questions, with a 95% paired-bootstrap CI. approx skill:"
                   " chance-corrected accuracy per source/family, unweighted mean."), "",
                  *headline(data), "", "### Cost by options (mean reads / share paying a second read)", "",
                  *cost_table(data), "", *arm_table("type", "type", data["policies"], data["vs_identity"]), "",
                  *arm_table("options", "options", data["policies"], data["vs_identity"]), ""]
    return "\n".join(lines)


def write(report: dict, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.md").write_text(markdown(report))
    (out / "summary.json").write_text(json.dumps(report, indent=1) + "\n")
    return out


def out_name(args, layout: str) -> str:
    if args.calib:
        return f"r4-orders-text-{layout}-2k-{args.profile}"
    return f"r4-orders-text-{layout}-{args.profile}" if args.layout else f"r3-orders-text-{args.profile}"


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="R3 option-order policies on text")
    p.add_argument("--profile", required=True)
    which = p.add_mutually_exclusive_group()
    which.add_argument("--layout", choices=sorted(load_layouts()), help=f"a served layout (default {LAYOUT})")
    which.add_argument("--layout-file", type=Path, help="an experiment layout; needs --calib and --dev")
    p.add_argument("--calib", type=Path, help="a collect file holding the calib-600 rows (with --dev)")
    p.add_argument("--dev", type=Path, help="a collect file holding the index-dev-2k rows (with --calib)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    if (args.calib is None) != (args.dev is None) or (args.layout_file and not args.calib):
        p.error("--calib and --dev go together, and --layout-file needs them")
    layout = load_layout(args.layout_file) if args.layout_file else load_layouts()[args.layout or LAYOUT]
    with ProcessPoolExecutor() as pool:  # the fits and the paired bootstraps dominate the run time
        if args.calib:
            result = run_files(args.profile, layout, args.calib, args.dev, pmap=pool.map)
        else:
            result = run(args.profile, layout.name, pmap=pool.map)
    if args.dry_run:
        print(markdown(result))
        return
    out = ROOT / "docs" / "results" / "archive" / f"{result['meta']['timestamp']}-{out_name(args, layout.name)}"
    print(write(result, out) / "summary.md")


if __name__ == "__main__":
    main()
