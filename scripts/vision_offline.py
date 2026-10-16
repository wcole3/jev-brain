"""Offline arms: re-score collected vision letter logprobs under one calibration method and order subset, on CPU.

usage: uv run python scripts/vision_offline.py --collect FILE --arm A [--orders identity] [--fit-on DEV] --out DIR
Fitted arms are 2-fold cross-fitted by group: a row is scored with parameters fitted on the other fold.
Nothing is fitted on holdout rows: on a holdout collect, fitted arms fit on a dev collect (--fit-on).
"""

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path

from gateway.calibration import Calibration, load_calibration, orders_warning
from gateway.config import Settings
from gateway.decide import blend, probabilities
from gateway.orders import option_orders
from scripts import vision_splits
from scripts.collect import records
from scripts.fit import fit_temperature

ARMS = ("text", "fit-T", "fit-T-bench", "pride")
MIN_FIT = 30  # a fit on fewer questions uses the text T (a fallback); a PriDe prior needs as many reads
SAME_CONFIG = ("profile", "layout", "orders", "env")  # a --fit-on collect must match the scored one on these
Reads = list[tuple[list[float], list[int]]]


@dataclass(frozen=True)
class Item:
    rec: dict
    reads: Reads
    fold: str  # "0" or "1", or "dev" when every row is scored with a fit on a dev collect


def fold(group: str) -> int:
    return int(hashlib.sha256(("fold:" + group).encode()).hexdigest(), 16) % 2


def chosen_reads(rec: dict, orders: str) -> Reads:
    """The collected reads an order setting would have made live; refuses a setting that was not collected."""
    by_perm = {tuple(r["perm"]): r["logprobs"] for r in rec["reads"]}
    wanted = option_orders(len(rec["names"]), orders)
    missing = [p for p in wanted if tuple(p) not in by_perm]
    if missing:
        raise ValueError(f"{rec['id']}: orders {orders!r} need perms {missing}, which were not collected")
    return [(by_perm[tuple(p)], p) for p in wanted]


def require_choice(rec: dict) -> None:
    """Every vision row is a choice question (string option names), so T is the choice T."""
    if rec.get("type", "choice") != "choice" or not all(isinstance(n, str) for n in rec["names"]):
        raise ValueError(f"{rec['id']}: not a choice question (names {rec['names']}); vision arms score choices only")


def usable(recs: list[dict]) -> tuple[list[dict], dict[str, int]]:
    """Ok records with a gold answer, and how many of the rest per status (ok without gold is "no_gold")."""
    keep, skipped = [], Counter()
    for r in recs:
        if r["status"] != "ok":
            skipped[r["status"]] += 1
        elif r["gold"] is None:
            skipped["no_gold"] += 1
        else:
            keep.append(r)
    return keep, dict(skipped)


def items_of(recs: list[dict], orders: str) -> tuple[list[Item], dict[str, int]]:
    keep, skipped = usable(recs)
    for r in keep:
        require_choice(r)
    return [Item(r, chosen_reads(r, orders), str(fold(r["group"]))) for r in keep], skipped


def fitted_T(items: list[Item], text_T: float) -> dict:
    if len(items) < MIN_FIT:
        return {"n": len(items), "T": text_T, "fallback": True}
    return {"n": len(items), "T": fit_temperature([(i.reads, i.rec["gold"]) for i in items]), "fallback": False}


def letter_prior(items: list[Item]) -> tuple[dict[str, list[float]], dict[str, int]]:
    """Per option count with enough reads: the mean of each read's logprobs centred to mean zero, by position.
    Also the read count per option count."""
    sums: dict[str, list[float]] = {}
    counts: Counter = Counter()
    for item in items:
        for lp, _ in item.reads:
            k, centre = str(len(lp)), sum(lp) / len(lp)
            acc = sums.setdefault(k, [0.0] * len(lp))
            for j, x in enumerate(lp):
                acc[j] += x - centre
            counts[k] += 1
    prior = {k: [s / counts[k] for s in acc] for k, acc in sums.items() if counts[k] >= MIN_FIT}
    return prior, dict(counts)


def debiased(item: Item, prior: dict[str, list[float]]) -> Item:
    p = prior.get(str(len(item.rec["names"])))
    if p is None:  # an option count the fitting rows saw too rarely
        return item
    return replace(item, reads=[([x - b for x, b in zip(lp, p, strict=True)], perm) for lp, perm in item.reads])


def fit_fold(arm: str, train: list[Item], scored: list[Item], text_T: float) -> dict:
    """The parameters the scored items get, fitted on the train items only."""
    if arm == "fit-T":
        return fitted_T(train, text_T)
    if arm == "fit-T-bench":
        by_bench = defaultdict(list)
        for i in train:
            by_bench[i.rec["benchmark"]].append(i)
        return {"benchmarks": {b: fitted_T(by_bench[b], text_T) for b in sorted({i.rec["benchmark"] for i in scored})}}
    if len(train) < MIN_FIT:  # pride: a tiny fold is scored exactly like the text arm
        return {"prior": {}, "prior_reads": {}} | fitted_T(train, text_T)
    prior, counts = letter_prior(train)
    return {"prior": prior, "prior_reads": counts} | fitted_T([debiased(i, prior) for i in train], text_T)


def fold_probs(arm: str, item: Item, params: dict) -> list[float]:
    if arm == "fit-T-bench":
        return blend(item.reads, params["benchmarks"][item.rec["benchmark"]]["T"])
    if arm == "pride":
        return blend(debiased(item, params["prior"]).reads, params["T"])
    return blend(item.reads, params["T"])


def fallbacks(arm: str, folds: dict[str, dict]) -> list[str]:
    name = {"0": "fold 0", "1": "fold 1", "dev": "dev"}
    if arm == "fit-T-bench":
        return [f"{name[k]} / {b}" for k, f in folds.items() for b, p in f["benchmarks"].items() if p["fallback"]]
    return [name[k] for k, f in folds.items() if f["fallback"]]


def fits(arm: str, items: list[Item], text_T: float) -> dict[str, dict]:
    """2-fold cross-fit: each fold's parameters come from the other fold."""
    in_fold = {k: [i for i in items if i.fold == k] for k in ("0", "1")}
    return {k: {"fitted_on": o} | fit_fold(arm, in_fold[o], in_fold[k], text_T) for k, o in (("0", "1"), ("1", "0"))}


def score(recs: list[dict], arm: str, orders: str, text_cal: Calibration,
          fit_on: list[dict] | None = None) -> tuple[list[dict], dict]:
    """Scored rows {id, benchmark, group, gold, probs, chance} and the arm's report (fitted values per fold).
    With fit_on (dev records), fitted arms fit on all of those and score every row: no folds."""
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}: use one of {ARMS}")
    option_orders(2, orders)  # refuses an unknown setting even when no row is scored
    items, skipped = items_of(recs, orders)
    text_T = text_cal.T["choice"]
    if arm == "text":
        folds, probs = None, [probabilities(i.reads, "choice", text_cal) for i in items]
    else:
        if fit_on is None:
            folds = fits(arm, items, text_T)
        else:
            items = [replace(i, fold="dev") for i in items]
            folds = {"dev": {"fitted_on": "dev"} | fit_fold(arm, items_of(fit_on, orders)[0], items, text_T)}
        probs = [fold_probs(arm, i, folds[i.fold]) for i in items]
    rows = [{"id": i.rec["id"], "benchmark": i.rec["benchmark"], "group": i.rec["group"], "gold": i.rec["gold"],
             "probs": p, "chance": 1 / len(i.rec["names"])} for i, p in zip(items, probs, strict=True)]
    report = {"arm": arm, "orders": orders, "folds": folds, "fallbacks": fallbacks(arm, folds) if folds else [],
              "skipped": skipped, "scored": len(rows)}
    return rows, report


def text_calibration(profile: str, layout: str) -> tuple[Calibration, Path]:
    """The profile's shipped calibration; offline reuse skips the stamp check, and arm.json says so."""
    path = Settings.from_profile(profile).calibration_path(layout)
    return load_calibration(path, expect=None), path


def only(values: set, what: str, path: Path):
    if len(values) != 1:
        raise SystemExit(f"{path}: expected one {what}, found {sorted(values)}")
    return next(iter(values))


def split_config(collect: Path) -> dict:
    """<split>.config.json beside the collect file: config.json belongs to whichever split came first."""
    path = collect.with_name(collect.name.removesuffix(".jsonl.gz") + ".config.json")
    if not path.exists():
        raise SystemExit(f"{path} missing: collect writes it next to {collect.name}")
    return json.loads(path.read_text())


def fit_source(args, config: dict) -> list[dict] | None:
    """Holdout rows are never fitted on: a fitted arm on a holdout collect fits on a matching dev collect."""
    holdout = config["split"] == "holdout"
    if args.fit_on is None:
        if holdout and args.arm != "text":
            raise SystemExit(f"{args.collect} is holdout: arm {args.arm} needs --fit-on DEV_COLLECT")
        return None
    if not holdout or args.arm == "text":
        raise SystemExit("--fit-on is only for fitted arms on a holdout collect; dev arms cross-fit")
    dev = split_config(args.fit_on)
    if dev["split"] != "dev":
        raise SystemExit(f"--fit-on {args.fit_on} is split {dev['split']!r}, not dev")
    diff = [k for k in SAME_CONFIG if dev.get(k) != config.get(k)]
    if diff:
        raise SystemExit(f"--fit-on {args.fit_on} differs from {args.collect} in {diff}")
    return list(records(args.fit_on))


def run(args) -> dict:
    recs = list(records(args.collect))
    if not recs:
        raise SystemExit(f"{args.collect}: no records")
    config = split_config(args.collect)
    fit_on = fit_source(args, config)
    profile = only({r["stamp"]["profile"] for r in recs}, "profile", args.collect)
    layout = only({r["layout"] for r in recs}, "layout", args.collect)
    cal, cal_path = text_calibration(profile, layout)
    if warning := orders_warning(cal, args.orders):
        print(f"warning: {warning}", file=sys.stderr)
    try:
        rows, report = score(recs, args.arm, args.orders, cal, fit_on)
    except ValueError as e:
        raise SystemExit(str(e)) from e
    text = {"path": str(cal_path), "source": cal.source, "T": cal.T["choice"], "orders": cal.orders,
            "stamp_checked": False}
    fit = str(args.fit_on) if args.fit_on else None
    arm = report | {"collect": str(args.collect), "collect_config": config, "fit_on": fit, "text_calibration": text,
                    "commit": vision_splits.commit()}
    args.out.mkdir(parents=True, exist_ok=True)
    with gzip.open(args.out / "scored.jsonl.gz", "wt", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    (args.out / "arm.json").write_text(json.dumps(arm, indent=1) + "\n")
    print(f"{args.arm} {args.orders}: scored {len(rows)}, skipped {report['skipped']}, "
          f"fallbacks {report['fallbacks']} -> {args.out}")
    return arm


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--collect", type=Path, required=True)
    p.add_argument("--arm", required=True, choices=ARMS)
    p.add_argument("--orders", default="identity")
    p.add_argument("--fit-on", type=Path, help="dev collect that fitted arms fit on when --collect is holdout")
    p.add_argument("--out", type=Path, required=True)
    return p.parse_args(argv)


def main(argv=None) -> dict:
    return run(parse_args(argv))


if __name__ == "__main__":
    main()
