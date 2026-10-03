"""M3 reports: which option order and which prompt layout each profile should default to.

usage:
  uv run python scripts/m3.py orders --profile P [--layout L] [--dry-run]
  uv run python scripts/m3.py layouts --profile P [--dry-run]
Each arm's T is fitted on calib (no gate); arms are judged on index-dev and eval, and both must agree.
--dry-run prints the markdown and writes nothing.
"""

import argparse
import json
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

from transformers import AutoTokenizer

from gateway.calibration import Calibration
from gateway.config import ROOT, Settings
from gateway.layouts import load_layouts
from gateway.orders import option_orders
from gateway.prompts import encode_each
from gateway.questions import render_state
from scripts import host_info, metrics
from scripts.bench import git_revision
from scripts.collect import COLLECT, records
from scripts.evaluate import now, results_dir
from scripts.experiments import compare, fit_arm, is_long, length_bucket, option_bucket
from scripts.m3_report import layouts_markdown, orders_markdown
from scripts.offline import Arm, keyed
from scripts.order_stats import (
    disagreement_auroc,
    flip_rate,
    noul_lean,
    position_histogram,
    pride_keyed,
    pride_prior,
    reversed_keyed,
)
from scripts.splits import rows_for

ORDER_ARMS = ("identity", "identity+reversed", "cyclic:2", "cyclic:3", "cyclic:4")
READS = {"identity": 1, "identity+reversed": 2, "cyclic:2": 2, "cyclic:3": 3, "cyclic:4": 4, "pride": 1}
DEFAULT_ORDERS, DEFAULT_LAYOUT = "identity", "decider_chat"  # every profile's current default
SPLITS = ("index-dev", "eval")
BY_OPTIONS = {
    "overall": lambda key, item: "all",
    "type": lambda key, item: item.type,
    "options": lambda key, item: option_bucket(len(item.probs)),
}


def split_by(items: dict, group) -> dict[str, dict]:
    parts = defaultdict(dict)
    for key, item in items.items():
        parts[group(key, item)][key] = item
    return dict(sorted(parts.items()))


def per_group(items: dict, groups: dict, fn) -> dict[str, dict]:
    """fn over each bucket of each grouping: {grouping: {bucket: fn(items in it)}}."""
    return {name: {bucket: fn(part) for bucket, part in split_by(items, group).items()} for name, group in groups.items()}


def summary(items: dict) -> dict:
    return metrics.summary(list(items.values()))


def run_compare(job: tuple) -> dict:
    return compare(*job)


def job(a: dict, b: dict) -> tuple:
    """A comparison to run in a worker process, with b cut down to a's questions so less is pickled."""
    return a, {k: b[k] for k in a.keys() & b.keys()}


def compare_groups(base: dict, arms: dict, groups: dict, pmap=map) -> dict[str, dict]:
    """Each arm against base in every bucket; pmap spreads the bootstraps over processes."""
    parts = {name: split_by(base, group) for name, group in groups.items()}
    slots = [(arm, name, bucket) for arm in arms for name in parts for bucket in parts[name]]
    results = pmap(run_compare, [job(parts[name][bucket], arms[arm]) for arm, name, bucket in slots])
    out = {arm: {name: {} for name in parts} for arm in arms}
    for (arm, name, bucket), result in zip(slots, results, strict=True):
        out[arm][name][bucket] = result
    return out


def recommend(comps: dict[str, dict], default: str) -> str:
    """An arm beats the default on accuracy or ECE with a CI clear of zero, and loses neither beyond its CI."""
    def wins(c):
        acc, ece = c["accuracy"], c["ece"]
        better_acc = acc[1] > 0 and ece[1] <= 0
        better_ece = ece[2] < 0 and acc[2] >= 0
        return better_acc or better_ece
    winners = [arm for arm, c in comps.items() if arm != default and c and wins(c)]
    if not winners:
        return "keep the default"
    return max(winners, key=lambda arm: comps[arm]["accuracy"][0])


def overall_comparisons(vs: dict) -> dict[str, dict]:
    return {arm: c["overall"]["all"] for arm, c in vs.items() if c["overall"]["all"]["n"]}


def agree(by_split: dict[str, str]) -> str:
    picks = list(by_split.values())
    return picks[0] if len(set(picks)) == 1 else f"no change: splits disagree ({' vs '.join(picks)})"


def mean_reads(items: dict, arm: str) -> float | None:
    """Reads per question as served: PriDe reads once, cyclic:k reads min(k, options) orders."""
    orders = DEFAULT_ORDERS if arm == "pride" else arm
    return sum(len(option_orders(len(i.probs), orders)) for i in items.values()) / len(items) if items else None


def fit_orders(calib_recs: list[dict], calib_rows: dict, layout: str) -> dict[str, Calibration]:
    cals = {arm: fit_arm(calib_recs, calib_rows, layout, arm) for arm in ORDER_ARMS}
    return cals | {"pride": cals["identity"]}


def orders_data(calib_recs, calib_rows, recs, rows, layout: str, cals=None, pmap=map) -> dict:
    """Every order arm on one split: scores, paired differences from identity, and the order diagnostics."""
    layouts = load_layouts()
    cals = cals or fit_orders(calib_recs, calib_rows, layout)
    arms = {arm: keyed(recs, rows, Arm(layout, arm, cals[arm]), layouts) for arm in ORDER_ARMS}
    prior = pride_prior(calib_recs, calib_rows, layout, cals["identity"], layouts)  # deployable: no extra reads
    arms["pride"] = pride_keyed(recs, rows, layout, cals["identity"], prior, layouts)
    identity, averaged = arms["identity"], arms["identity+reversed"]
    reversed_ = reversed_keyed(recs, rows, layout, cals["identity"], layouts)
    vs = compare_groups(identity, arms, BY_OPTIONS, pmap)
    summaries = {arm: {"T": cals[arm].T, "reads": READS[arm], "mean_reads": mean_reads(items, arm),
                       **per_group(items, BY_OPTIONS, summary)} for arm, items in arms.items()}
    best = max((arm for arm in arms if arm != DEFAULT_ORDERS),
               key=lambda arm: summaries[arm]["overall"]["all"]["accuracy"])
    choices = {k: i for k, i in identity.items() if i.type != "noul"}  # a noul flip is the lean, reported apart
    return {
        "arms": summaries,
        "vs_identity": vs,
        "flips": per_group(choices, BY_OPTIONS, lambda part: flip_rate(part, reversed_)),
        "auroc": per_group(identity, BY_OPTIONS, lambda part: disagreement_auroc(part, reversed_, averaged)),
        "best": best,
        "histograms": {arm: position_histogram(list(arms[arm].values())) for arm in (DEFAULT_ORDERS, best)},
        "noul_lean": noul_lean(identity, reversed_),
        "pride_prior_options": sorted(prior),
        "recommendation": recommend(overall_comparisons(vs), DEFAULT_ORDERS),
    }


def load_tokenizer(profile: str):
    s = Settings.from_profile(profile)
    return AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision, local_files_only=True)  # HF cache only


def count_state_tokens(tok, rows: dict) -> dict[str, int]:
    """Each row's state as the prompt renders it, in tokens; one tokenizer call for all rows."""
    ids = list(rows)
    return dict(zip(ids, map(len, encode_each(tok, [render_state(rows[i]["state"]) for i in ids])), strict=True))


def layout_groups(tokens: dict[str, int]) -> dict:
    """Buckets by state length in tokens, the same for every layout."""
    return {
        "overall": lambda key, item: "all",
        "type": lambda key, item: item.type,
        "length": lambda key, item: length_bucket(tokens[key[0]]),
        "slice": lambda key, item: "long" if is_long(item.source, item.family, tokens[key[0]]) else "rest",
    }


def winners(arms: dict, summaries: dict, groups: dict, pmap=map) -> dict:
    """The most accurate layout overall and per bucket; a bucket auto-switches only on a CI clear of zero."""
    def best(name, bucket, prefer):  # a tie goes to prefer
        return max(arms, key=lambda layout: (summaries[layout][name][bucket]["accuracy"], layout == prefer))
    top = best("overall", "all", DEFAULT_LAYOUT)
    slots = [(name, bucket, best(name, bucket, top)) for name in ("length", "slice") for bucket in summaries[top][name]]
    differ = [slot for slot in slots if slot[2] != top]
    results = pmap(run_compare, [job(split_by(arms[top], groups[name])[bucket], arms[winner])
                                 for name, bucket, winner in differ])
    vs = dict(zip(differ, results, strict=True))
    out = {"overall": top, "length": {}, "slice": {}}
    for name, bucket, winner in slots:
        c = vs.get((name, bucket, winner))
        out[name][bucket] = {"winner": winner, "accuracy": summaries[winner][name][bucket]["accuracy"],
                             "vs_overall": c, "auto_switch": bool(c and c["accuracy"] and c["accuracy"][1] > 0)}
    return out


def fit_layouts(calib_recs: list[dict], calib_rows: dict) -> dict[str, Calibration]:
    return {name: fit_arm(calib_recs, calib_rows, name, DEFAULT_ORDERS) for name in sorted(load_layouts())}


def layouts_data(calib_recs, calib_rows, recs, rows, state_tokens: dict[str, int], cals=None, pmap=map) -> dict:
    """Each layout at identity with its own T, on the questions every layout answered."""
    layouts = load_layouts()
    cals = cals or fit_layouts(calib_recs, calib_rows)
    arms = {name: keyed(recs, rows, Arm(name, DEFAULT_ORDERS, cals[name]), layouts) for name in sorted(layouts)}
    shared = set.intersection(*(set(items) for items in arms.values()))
    arms = {name: {k: v for k, v in items.items() if k in shared} for name, items in arms.items()}
    groups = layout_groups(state_tokens)
    summaries = {name: {"T": cals[name].T, **per_group(items, groups, summary)} for name, items in arms.items()}
    others = {name: items for name, items in arms.items() if name != DEFAULT_LAYOUT}
    vs = compare_groups(arms[DEFAULT_LAYOUT], others, groups, pmap)
    return {
        "layouts": summaries,
        "vs_decider_chat": vs,
        "winners": winners(arms, summaries, groups, pmap),
        "recommendation": recommend(overall_comparisons(vs), DEFAULT_LAYOUT),
    }


def switches_on_both(splits: dict) -> list[str]:
    """Buckets that auto-switch to the same layout on every split, as "grouping bucket: layout"."""
    flagged = [{f"{name} {bucket}: {w['winner']}" for name in ("length", "slice")
                for bucket, w in data["winners"][name].items() if w["auto_switch"]} for data in splits.values()]
    return sorted(set.intersection(*flagged))


def load(profile: str, split: str) -> tuple[list[dict], dict, str]:
    path = COLLECT / profile / f"{split}.jsonl.gz"
    recs = list(records(path))
    if not recs:
        raise SystemExit(f"no records in {path}: collect {split} first")
    return recs, {r["id"]: r for r in rows_for(split)}, str(path.relative_to(ROOT))


def provenance(profile: str, paths: dict, cals: dict, **extra) -> dict:
    meta = {"timestamp": now(), "repo commit": git_revision(), "host": host_info.summary(), "profile": profile,
            **extra, **{f"collect {split}": path for split, path in paths.items()},
            "temperatures": "each arm's T is an ungated fit on the calib split (b = 0), not the shipped calibration.json"}
    return meta | {f"T {arm}": ", ".join(f"{t} {v:.3f}" for t, v in cal.T.items()) for arm, cal in cals.items()}


def orders_report(profile: str, layout: str, pmap=map) -> dict:
    calib_recs, calib_rows, calib_path = load(profile, "calib")
    cals = fit_orders(calib_recs, calib_rows, layout)
    splits, paths = {}, {"calib": calib_path}
    for split in SPLITS:
        recs, rows, paths[split] = load(profile, split)
        splits[split] = orders_data(calib_recs, calib_rows, recs, rows, layout, cals, pmap)
    return {"meta": provenance(profile, paths, cals, layout=layout), "splits": splits,
            "recommendation": agree({split: data["recommendation"] for split, data in splits.items()})}


def layouts_report(profile: str, pmap=map) -> dict:
    calib_recs, calib_rows, calib_path = load(profile, "calib")
    cals, tok = fit_layouts(calib_recs, calib_rows), load_tokenizer(profile)
    splits, paths = {}, {"calib": calib_path}
    for split in SPLITS:
        recs, rows, paths[split] = load(profile, split)
        splits[split] = layouts_data(calib_recs, calib_rows, recs, rows, count_state_tokens(tok, rows), cals, pmap)
    return {"meta": provenance(profile, paths, cals), "splits": splits,
            "recommendation": agree({split: data["recommendation"] for split, data in splits.items()}),
            "auto_switch_on_both": switches_on_both(splits)}


def write(report: dict, markdown: str, name: str, dry_run: bool) -> None:
    if dry_run:  # results are committed deliberately: a dry run leaves nothing behind
        print(markdown)
        return
    meta = report["meta"]
    out = results_dir(meta["profile"], f"{meta['timestamp']}-{name}")
    (out / "summary.md").write_text(markdown)
    (out / "report.json").write_text(json.dumps(report, indent=1) + "\n")
    print(out / "summary.md")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="M3 order and layout reports")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("orders", "layouts"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--profile", required=True)
        cmd.add_argument("--dry-run", action="store_true")
    sub.choices["orders"].add_argument("--layout", default=DEFAULT_LAYOUT, choices=sorted(load_layouts()))
    args = p.parse_args(argv)
    with ProcessPoolExecutor() as pool:  # the paired bootstraps dominate the run time
        if args.command == "orders":
            report = orders_report(args.profile, args.layout, pool.map)
            write(report, orders_markdown(report), f"m3-orders-{args.layout}", args.dry_run)
        else:
            report = layouts_report(args.profile, pool.map)
            write(report, layouts_markdown(report), "m3-layouts", args.dry_run)


if __name__ == "__main__":
    main()
