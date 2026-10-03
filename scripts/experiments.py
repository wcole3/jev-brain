"""Shared pieces of the M3 experiments: buckets, the long slice, per-arm temperatures, paired comparisons, the verdict."""

import math
import random
from collections import defaultdict

from gateway.calibration import Calibration
from scripts import calibrate, metrics
from scripts.metrics import Scored

KEEP = "keep the default"
SHIPPED = "shipped calibration (reference)"  # the default arm as served today: a reference row, never a candidate
LONG_FAMILIES = {("jevbench", "invoices"), ("jevbench", "invoice_processing"), ("index", "ContractNLI"),
                 ("index", "NLI4CT"), ("index", "BRIGHT")}


def option_bucket(k: int) -> str:
    return "2" if k == 2 else "3-5" if k <= 5 else "6-26" if k <= 26 else "27+"


BY_TYPE = {
    "overall": lambda key, item: "all",
    "type": lambda key, item: item.type,
}
BY_OPTIONS = BY_TYPE | {"options": lambda key, item: option_bucket(len(item.probs))}


def length_bucket(tokens: int) -> str:
    return "<512" if tokens < 512 else "512-2k" if tokens < 2048 else "2k-8k" if tokens < 8192 else ">8k"


def is_long(source: str, family: str, tokens: int) -> bool:
    return (source, family) in LONG_FAMILIES or (source == "decisionbench" and tokens > 2000)


def fit_arm(calib_recs: list[dict], calib_rows: dict, layout: str, orders: str) -> Calibration:
    """This arm's own T per type, fitted on calib like calibrate.py (b = 0, no gate), so arms compare fairly."""
    by_type, _ = calibrate.questions_by_type(calib_recs, calib_rows, layout, orders)
    fit = calibrate.fit_layout(by_type)
    return Calibration({"choice": fit["choice"]["T"], "score": fit["score"]["T"], "noul": fit["noul_b0"]["T"]},
                       source=f"calib fit {layout} {orders}", orders=orders)


def paired(a: dict, b: dict) -> tuple[list, list]:
    keys = sorted(a.keys() & b.keys())
    return [a[k] for k in keys], [b[k] for k in keys]


def columns(items: list[Scored]) -> tuple[list, list, list]:
    """What accuracy, ECE and NLL read from each question, worked out once instead of once per resample."""
    return ([i.correct for i in items], [i.confidence for i in items],
            [-math.log(max(i.probs[i.gold], metrics.EPS)) for i in items])


def scores(cols: tuple[list, list, list], idx) -> tuple[float, float, float]:
    """Accuracy, ECE and NLL of the questions at idx, summed as metrics.py sums them, so the numbers match exactly."""
    correct, confidence, loss = ([col[i] for i in idx] for col in cols)
    return sum(correct) / len(idx), metrics.ece_of(confidence, correct), sum(loss) / len(idx)


def bootstrap(xa: list[Scored], xb: list[Scored], resamples: int = 2000, seed: int = 0) -> dict:
    """Must equal fit.bootstrap_diff per metric (tested): its calls share seed 0, so one draw serves all three."""
    ca, cb, rng, n = columns(xa), columns(xb), random.Random(seed), len(xa)
    diffs = []
    for _ in range(resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append([y - x for x, y in zip(scores(ca, idx), scores(cb, idx), strict=True)])
    point = [y - x for x, y in zip(scores(ca, range(n)), scores(cb, range(n)), strict=True)]
    out = {}
    for m, name in enumerate(("accuracy", "ece", "nll")):
        ranked = sorted(d[m] for d in diffs)
        out[name] = (point[m], ranked[int(0.025 * resamples)], ranked[int(0.975 * resamples) - 1])
    return out


def compare(a: dict, b: dict) -> dict:
    """metric(b) - metric(a) with 95% paired-bootstrap intervals, over the questions both arms answered."""
    xa, xb = paired(a, b)
    if not xa:
        return {"n": 0, "accuracy": None, "ece": None, "nll": None}
    return {"n": len(xa), **bootstrap(xa, xb)}


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
    return a, {k: b[k] for k in sorted(a.keys() & b.keys())}


def compare_groups(base: dict, arms: dict, groups: dict, pmap=map) -> dict[str, dict]:
    """Each arm against base in every bucket; pmap spreads the bootstraps over processes."""
    parts = {name: split_by(base, group) for name, group in groups.items()}
    slots = [(arm, name, bucket) for arm in arms for name in parts for bucket in parts[name]]
    results = pmap(run_compare, [job(parts[name][bucket], arms[arm]) for arm, name, bucket in slots])
    out = {arm: {name: {} for name in parts} for arm in arms}
    for (arm, name, bucket), result in zip(slots, results, strict=True):
        out[arm][name][bucket] = result
    return out


def wins(c: dict) -> bool:
    """Better on accuracy or ECE with a CI clear of zero, and worse on neither beyond its CI."""
    acc, ece = c["accuracy"], c["ece"]
    return (acc[1] > 0 and ece[1] <= 0) or (ece[2] < 0 and acc[2] >= 0)


def qualifying(vs_default: dict, candidates) -> list[str]:
    """The candidate arms that beat the default overall on this split."""
    return [arm for arm in sorted(candidates) if (c := vs_default[arm]["overall"]["all"])["n"] and wins(c)]


def verdict(splits: dict[str, dict], cost) -> str:
    """An arm that qualifies on every split: the cheapest by cost(arm), then the larger mean Δ accuracy."""
    both = set.intersection(*(set(data["qualifying"]) for data in splits.values()))

    def gain(arm):
        return sum(d["vs_default"][arm]["overall"]["all"]["accuracy"][0] for d in splits.values()) / len(splits)
    return min(sorted(both), key=lambda arm: (cost(arm), -gain(arm))) if both else KEEP
