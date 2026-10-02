"""Fit calibration from collected logprobs: T per type (+ noul yes-offset when it earns its place on eval).

usage: uv run python scripts/calibrate.py --profile qwen3.6-27b [--layouts decider_chat,header] [--orders identity] [--dry-run]
Fits on data/splits/calib.json only (never Jev outputs, never Index rows); judges on eval.
"""

import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path

from gateway.calibration import STAMP_KEYS, Calibration
from gateway.config import ROOT, Settings
from gateway.decide import probabilities
from gateway.layouts import load_layouts
from gateway.orders import option_orders
from gateway.questions import render_question
from gateway.schema import Question as Q
from scripts import fit as fits
from scripts import metrics
from scripts.bench import git_revision
from scripts.bench_report import provenance
from scripts.collect import COLLECT, records
from scripts.metrics import Scored
from scripts.offline import gold_index
from scripts.splits import SPLITS, rows_for

MIN_QUESTIONS = 30  # fewer and the fitted T is mostly noise: keep 1.0
TYPES = ("choice", "score", "noul")


def questions_by_type(recs, rows, layout: str, orders: str):
    layouts, by_type, stamp = load_layouts(), {t: [] for t in TYPES}, None
    for rec in recs:
        if rec["layout"] != layout or rec["status"] != "ok":
            continue
        this = {k: rec["stamp"].get(k) for k in STAMP_KEYS}
        if stamp is None:
            stamp = this
        elif this != stamp:
            changed = [k for k in STAMP_KEYS if this[k] != stamp[k]]
            raise SystemExit(f"{layout}: records disagree on {', '.join(changed)}; recollect before fitting")
        row = rows[rec["id"]]
        for qid, reads in rec["questions"].items():
            q = render_question(Q(**row["questions"][qid]), layouts[layout])
            gold = gold_index(q, row["gold"].get(qid))
            if gold is None:
                continue
            wanted = option_orders(len(q.options), orders)
            chosen = [(r["logprobs"], r["perm"]) for r in reads if r["perm"] in wanted]
            by_type[q.type].append((chosen, gold))
    return by_type, stamp


def fit_layout(calib: dict) -> dict:
    out = {}
    for t in ("choice", "score"):
        out[t] = {"T": fits.fit_temperature(calib[t]) if len(calib[t]) >= MIN_QUESTIONS else 1.0}
    if len(calib["noul"]) >= MIN_QUESTIONS:
        T, b = fits.fit_noul(calib["noul"])
        out["noul"], out["noul_b0"] = {"T": T, "b": b}, {"T": fits.fit_temperature(calib["noul"])}
    else:
        out["noul"], out["noul_b0"] = {"T": 1.0, "b": 0.0}, {"T": 1.0}
    return out


def scored(questions, q_type: str, cal: Calibration) -> list[Scored]:
    return [Scored("s", "f", q_type, gold, probabilities(reads, q_type, cal)) for reads, gold in questions]


def ship_offset(eval_noul, with_b: tuple[float, float], without_b: float) -> tuple[bool, dict]:
    """The spec rule: ship b only for an accuracy or ECE gain without a loss in the other beyond its CI."""
    a = scored(eval_noul, "noul", Calibration({"choice": 1, "score": 1, "noul": without_b}))
    b = scored(eval_noul, "noul", Calibration({"choice": 1, "score": 1, "noul": with_b[0]}, with_b[1]))
    acc = fits.bootstrap_diff(a, b, metrics.accuracy)
    ece = fits.bootstrap_diff(a, b, metrics.ece)
    ship = (acc[1] > 0 and ece[1] <= 0) or (ece[2] < 0 and acc[2] >= 0)
    return ship, {"acc": acc, "ece": ece}


def history(path: Path) -> tuple[int, list[dict]]:
    """Last version and comment history of an existing v2 file; a v1, missing or unreadable file starts fresh."""
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return 0, []
    if data.get("format") != 2:
        return 0, []
    return int(data.get("version", 0)), list(data.get("comments", []))


def calibration_file(fit: dict, stamp: dict, orders: str, calib_n: dict, before_after: dict, decision: dict,
                     previous: tuple[int, list[dict]], comment: str, date: str) -> dict:
    split = SPLITS / "calib.json"
    version = previous[0] + 1
    return {
        "format": 2,
        "version": version,  # version, date and comments are informational; the gateway never reads them
        "date": date,
        "comments": [*previous[1], {"version": version, "date": date, "text": comment}],
        "stamp": stamp,
        "types": {"choice": fit["choice"], "score": fit["score"], "noul": fit["noul"]},
        "fit": {"split": str(split.relative_to(ROOT)) if split.is_absolute() else str(split),
                "split_sha256": hashlib.sha256(split.read_bytes()).hexdigest() if split.exists() else None,
                "orders": orders, "n": calib_n, **before_after, "b_decision": decision},
    }


def summarize(questions, q_type: str, cal: Calibration) -> dict:
    items = scored(questions, q_type, cal)
    return metrics.summary(items) if items else {"n": 0, "accuracy": None, "ece": None, "nll": None, "brier": None}


def at_edge(value: float, bounds: tuple[float, float], log: bool = False) -> bool:
    """True when a fitted value sits within 1e-3 of its search range (on the log scale for T): the optimum may lie beyond."""
    x = math.log(value) if log else value
    return min(x - bounds[0], bounds[1] - x) < 1e-3


def fmt(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_comment(path: Path, orders: str) -> str:
    """Says when a fit replaces a v1 file, so the history starts with where the old numbers came from."""
    try:
        old = json.loads(path.read_text())
    except (OSError, ValueError):
        old = None
    if isinstance(old, dict) and old.get("format") != 2 and "choice" in old:
        return f"first own fit; replaces v1 file (T={old['choice']})"
    return f"refit on calib (orders {orders})"


def layout_report(layout, fit, calib, held, before, after, stats, b_fitted, ship) -> list[str]:
    lines = [f"## {layout}", "", "| type | n calib/eval | T | b | eval NLL before → after | eval ECE before → after | eval acc |",
             "|---|---|---|---|---|---|---|"]
    for t in TYPES:
        T_text = f"{fit[t]['T']:.3f}" + (" (edge)" if at_edge(fit[t]["T"], fits.LOG_T, log=True) else "")
        b = fit["noul"]["b"]
        b_text = f"{b:+.3f}" + (" (edge)" if at_edge(b, fits.B_RANGE) else "") if t == "noul" else ""
        lines.append(f"| {t} | {len(calib[t])}/{len(held[t])} | {T_text} | {b_text} | {fmt(before[t]['nll'])} → "
                     f"{fmt(after[t]['nll'])} | {fmt(before[t]['ece'])} → {fmt(after[t]['ece'])} | {fmt(after[t]['accuracy'])} |")
    acc, ece = stats["acc"], stats["ece"]
    verdict = "shipped" if ship else "not shipped (b = 0)"
    lines += ["", (f"noul offset: fitted b = {b_fitted:+.3f}; eval accuracy change {acc[0]:+.4f} [{acc[1]:+.4f}, {acc[2]:+.4f}], "
                    f"ECE change {ece[0]:+.4f} [{ece[1]:+.4f}, {ece[2]:+.4f}] → {verdict}"), ""]
    return lines


def calibrate_layout(args, s, layout, recs, rows) -> list[str]:
    """Fit one layout on calib, judge b on eval, write its file (unless dry run) and return its report lines."""
    calib, stamp = questions_by_type(recs["calib"], rows["calib"], layout, args.orders)
    held, eval_stamp = questions_by_type(recs["eval"], rows["eval"], layout, args.orders)
    if stamp != eval_stamp:
        raise SystemExit(f"{layout}: calib and eval were collected under different stamps")
    fit = fit_layout(calib)
    if held["noul"]:
        ship, stats = ship_offset(held["noul"], (fit["noul"]["T"], fit["noul"]["b"]), fit["noul_b0"]["T"])
    else:
        ship, stats = False, {"acc": (0, 0, 0), "ece": (0, 0, 0)}
    b_fitted = fit["noul"]["b"]
    if not ship:
        fit["noul"] = {"T": fit["noul_b0"]["T"], "b": 0.0}
    cal = Calibration({t: fit[t]["T"] for t in TYPES}, fit["noul"]["b"])
    before = {t: summarize(held[t], t, Calibration({x: 1.0 for x in TYPES})) for t in TYPES}
    after = {t: summarize(held[t], t, cal) for t in TYPES}
    before_after = {m: {"before": {t: before[t][m] for t in TYPES}, "after": {t: after[t][m] for t in TYPES}}
                    for m in ("nll", "ece")}
    decision = {"ship": ship, "acc": list(stats["acc"]), "ece": list(stats["ece"]), "b_fitted": b_fitted}
    path = s.data_dir(layout) / "calibration.json"
    data = calibration_file(fit, stamp, args.orders, {t: len(calib[t]) for t in TYPES}, before_after, decision,
                            history(path), args.comment or default_comment(path, args.orders), now_iso())
    if not args.dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=1) + "\n")
    return layout_report(layout, fit, calib, held, before, after, stats, b_fitted, ship)


def main(argv=None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--layouts")
    p.add_argument("--orders", default="identity")
    p.add_argument("--comment", help="one line for this file's change history")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    s = Settings.from_profile(args.profile)
    rows = {n: {r["id"]: r for r in rows_for(n)} for n in ("calib", "eval")}
    recs = {n: list(records(COLLECT / args.profile / f"{n}.jsonl.gz")) for n in ("calib", "eval")}
    layouts = args.layouts.split(",") if args.layouts else sorted(load_layouts())
    stamp_utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")
    lines = [line for layout in layouts for line in calibrate_layout(args, s, layout, recs, rows)]
    meta = {"timestamp": stamp_utc, "repo commit": git_revision(), "profile": args.profile, "orders": args.orders,
            "calib split sha256": hashlib.sha256((SPLITS / "calib.json").read_bytes()).hexdigest(),
            "collect": f".cache/collect/{args.profile}/{{calib,eval}}.jsonl.gz", "written": not args.dry_run}
    out = ROOT / "docs" / "results" / args.profile / f"{stamp_utc}-calibrate"
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.md").write_text(f"# {args.profile} calibration\n\n{provenance(meta)}\n" + "\n".join(lines) + "\n")
    print(out / "summary.md")


if __name__ == "__main__":
    main()
