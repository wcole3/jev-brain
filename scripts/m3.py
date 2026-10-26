"""M3 reports: which option order and which prompt layout each profile should default to.

usage:
  uv run python scripts/m3.py orders --profile P [--layout L] [--dry-run]
  uv run python scripts/m3.py layouts --profile P [--dry-run]
Each arm's T is fitted on calib (no gate); arms are judged on index-dev and eval, and both must agree.
--dry-run prints the markdown and writes nothing.
"""

import argparse
import json
from concurrent.futures import ProcessPoolExecutor

from gateway.calibration import Calibration, load_calibration, orders_warning, to_json
from gateway.config import ROOT, Settings
from gateway.layouts import load_layouts
from gateway.orders import option_orders
from scripts import host_info
from scripts.bench import git_revision
from scripts.collect import COLLECT, records
from scripts.evaluate import collect_stamp, now, results_dir
from scripts.experiments import BY_OPTIONS, SHIPPED, compare_groups, fit_arm, per_group, qualifying, summary, verdict
from scripts.m3_layouts import count_state_tokens, fit_layouts, layouts_study, load_tokenizer
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
READS = {"identity": 1, "identity+reversed": 2, "cyclic:2": 2, "cyclic:3": 3, "cyclic:4": 4}
NOT_CANDIDATES = ("pride", SHIPPED)  # pride has no OPTION_ORDERS value; the shipped row is a reference
SPLITS = ("index-dev", "eval")


def served_orders(arm: str, default: str) -> str:
    """The OPTION_ORDERS an arm reads with: PriDe divides a prior out of identity reads."""
    return {"pride": "identity", SHIPPED: default}.get(arm, arm)


def mean_reads(items: dict, orders: str) -> float | None:
    """Reads per question as served: cyclic:k reads min(k, options) orders."""
    return sum(len(option_orders(len(i.probs), orders)) for i in items.values()) / len(items) if items else None


def fit_orders(calib_recs: list[dict], calib_rows: dict, layout: str) -> dict[str, Calibration]:
    cals = {arm: fit_arm(calib_recs, calib_rows, layout, arm) for arm in ORDER_ARMS}
    return cals | {"pride": cals["identity"]}


def orders_data(calib_recs, calib_rows, recs, rows, layout: str, default: str, shipped: Calibration,
                cals=None, pmap=map) -> dict:
    """Every order arm on one split: scores, paired differences from the default, and the order diagnostics."""
    layouts = load_layouts()
    cals = (cals or fit_orders(calib_recs, calib_rows, layout)) | {SHIPPED: shipped}
    arms = {arm: keyed(recs, rows, Arm(layout, arm, cals[arm]), layouts) for arm in ORDER_ARMS}
    prior = pride_prior(calib_recs, calib_rows, layout, cals["identity"], layouts)  # deployable: no extra reads
    arms["pride"] = pride_keyed(recs, rows, layout, cals["identity"], prior, layouts)
    arms[SHIPPED] = keyed(recs, rows, Arm(layout, default, shipped), layouts)
    identity, averaged = arms["identity"], arms["identity+reversed"]
    reversed_ = reversed_keyed(recs, rows, layout, cals["identity"], layouts)
    vs = compare_groups(arms[default], {arm: items for arm, items in arms.items() if arm != default}, BY_OPTIONS, pmap)
    summaries = {arm: {"T": cals[arm].T, "reads": READS[served_orders(arm, default)],
                       "mean_reads": mean_reads(items, served_orders(arm, default)),
                       **per_group(items, BY_OPTIONS, summary)} for arm, items in arms.items()}
    best = max((arm for arm in arms if arm not in (default, SHIPPED)),
               key=lambda arm: summaries[arm]["overall"]["all"]["accuracy"])
    choices = {k: i for k, i in identity.items() if i.type != "noul"}  # a noul flip is the lean, reported apart
    return {
        "default": default,
        "arms": summaries,
        "vs_default": vs,
        "qualifying": qualifying(vs, [arm for arm in vs if arm not in NOT_CANDIDATES]),
        "flips": per_group(choices, BY_OPTIONS, lambda part: flip_rate(part, reversed_)),
        "auroc": per_group(identity, BY_OPTIONS, lambda part: disagreement_auroc(part, reversed_, averaged)),
        "best": best,
        "histograms": {arm: position_histogram(list(arms[arm].values())) for arm in (default, best)},
        "noul_lean": noul_lean(identity, reversed_),
        "pride_prior_options": sorted(prior),
    }


def orders_verdict(splits: dict[str, dict]) -> str:
    """Cheapest by mean reads per question over the splits."""
    return verdict(splits, cost=lambda arm: sum(d["arms"][arm]["mean_reads"] for d in splits.values()) / len(splits))


def load(profile: str, split: str) -> tuple[list[dict], dict, str]:
    path = COLLECT / profile / f"{split}.jsonl.gz"
    recs = list(records(path))
    if not recs:
        raise SystemExit(f"no records in {path}: collect {split} first")
    return recs, {r["id"]: r for r in rows_for(split)}, str(path.relative_to(ROOT))


def shipped_calibration(s: Settings, layout: str, recs: list[dict]) -> Calibration:
    """The layout's calibration file as the gateway loads it, refused when stale (as evaluate.py offline)."""
    return load_calibration(s.calibration_path(layout), collect_stamp(recs, layout))


def provenance(s: Settings, paths: dict, cals: dict, shipped: Calibration, **extra) -> dict:
    meta = {"timestamp": now(), "repo commit": git_revision(), "host": host_info.summary(), "profile": s.profile,
            "defaults": f"PROMPT_LAYOUT {s.prompt_layout}, OPTION_ORDERS {s.option_orders} (profiles/{s.profile}.env)",
            **extra, **{f"collect {split}": path for split, path in paths.items()},
            "temperatures": "each arm's T is an ungated fit on the calib split (b = 0), not the shipped calibration file",
            SHIPPED: (f"{shipped.source}: T " + ", ".join(f"{t} {v:.3f}" for t, v in shipped.T.items())
                      + f", b {shipped.b:.3f}" + (f" ({w})" if (w := orders_warning(shipped, s.option_orders)) else ""))}
    return meta | {f"T {arm}": ", ".join(f"{t} {v:.3f}" for t, v in cal.T.items()) for arm, cal in cals.items()}


def orders_report(profile: str, layout: str | None = None, pmap=map) -> dict:
    s = Settings.from_profile(profile)
    layout, default = layout or s.prompt_layout, s.option_orders
    if default not in ORDER_ARMS:
        raise SystemExit(f"OPTION_ORDERS {default} in profiles/{profile}.env is not an M3 arm ({', '.join(ORDER_ARMS)})")
    calib_recs, calib_rows, calib_path = load(profile, "calib")
    cals = fit_orders(calib_recs, calib_rows, layout)
    splits, paths = {}, {"calib": calib_path}
    for split in SPLITS:
        recs, rows, paths[split] = load(profile, split)
        shipped = shipped_calibration(s, layout, recs)
        splits[split] = orders_data(calib_recs, calib_rows, recs, rows, layout, default, shipped, cals, pmap)
    return {"meta": provenance(s, paths, cals, shipped, layout=layout), "splits": splits,
            "recommendation": orders_verdict(splits)}


def layouts_report(profile: str, pmap=map) -> dict:
    s = Settings.from_profile(profile)
    calib_recs, calib_rows, calib_path = load(profile, "calib")
    cals, tok = fit_layouts(calib_recs, calib_rows, s.option_orders), load_tokenizer(profile)
    inputs, shipped, paths = {}, {}, {"calib": calib_path}
    for split in SPLITS:
        recs, rows, paths[split] = load(profile, split)
        inputs[split] = recs, rows, count_state_tokens(tok, rows)
        shipped[split] = shipped_calibration(s, s.prompt_layout, recs)
    study = layouts_study(calib_recs, calib_rows, inputs, s.prompt_layout, s.option_orders, shipped, cals, pmap)
    meta = provenance(s, paths, cals, shipped[SPLITS[-1]], orders=s.option_orders)
    return {"meta": meta, **study}


def write(report: dict, markdown: str, name: str, dry_run: bool) -> None:
    if dry_run:  # results are committed deliberately: a dry run leaves nothing behind
        print(markdown)
        return
    meta = report["meta"]
    out = results_dir(meta["profile"], f"{meta['timestamp']}-{name}", archive=True)
    (out / "summary.md").write_text(markdown)
    (out / "report.json").write_text(json.dumps(report, indent=1, default=to_json) + "\n")
    print(out / "summary.md")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="M3 order and layout reports")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("orders", "layouts"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--profile", required=True)
        cmd.add_argument("--dry-run", action="store_true")
    sub.choices["orders"].add_argument("--layout", choices=sorted(load_layouts()), help="default: PROMPT_LAYOUT")
    args = p.parse_args(argv)
    with ProcessPoolExecutor() as pool:  # the paired bootstraps dominate the run time
        if args.command == "orders":
            report = orders_report(args.profile, args.layout, pool.map)
            write(report, orders_markdown(report), f"m3-orders-{report['meta']['layout']}", args.dry_run)
        else:
            report = layouts_report(args.profile, pool.map)
            write(report, layouts_markdown(report), "m3-layouts", args.dry_run)


if __name__ == "__main__":
    main()
