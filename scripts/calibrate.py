"""Fit calibration from collected logprobs: T per type (+ noul yes-offset when it earns its place on eval).

usage: uv run python scripts/calibrate.py --profile qwen3.6-27b [--layouts decider_chat,header] [--orders identity] [--dry-run]
Fits on data/splits/calib.json only (never Jev outputs, never Index rows); judges on eval.
"""

import argparse
import datetime
import functools
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

from gateway.calibration import STAMP_KEYS, Calibration
from gateway.config import ROOT, Settings
from gateway.decide import probabilities
from gateway.layouts import load_layouts
from scripts import fit as fits
from scripts import metrics, offline
from scripts.bench import git_revision
from scripts.bench_report import provenance
from scripts.collect import COLLECT, records
from scripts.metrics import Scored
from scripts.splits import SPLITS, rows_for

MIN_QUESTIONS = 30  # fewer and the fitted T is mostly noise: keep 1.0
TYPES = ("choice", "score", "noul")
SPLIT = SPLITS / "calib.json"


@functools.cache
def split_sha256() -> str:
    return hashlib.sha256(SPLIT.read_bytes()).hexdigest()


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
        for q_type, chosen, gold in offline.questions(rec, rows[rec["id"]], layout, orders, layouts):
            by_type[q_type].append((chosen, gold))
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
    pooled = [q for t in TYPES for q in calib[t]]  # one T for every type, the gate's fallback (b = 0)
    out["pooled"] = {"T": fits.fit_temperature(pooled) if len(pooled) >= MIN_QUESTIONS else 1.0}
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


def ece_change(questions, q_type: str, T: float, b: float = 0.0) -> list[float]:
    """Eval ECE at (T, b) minus ECE at T = 1, b = 0: [mean, CI low, CI high] from the paired bootstrap."""
    if not questions:
        return [0.0, 0.0, 0.0]
    raw = scored(questions, q_type, Calibration({t: 1.0 for t in TYPES}))
    cal = scored(questions, q_type, Calibration({t: T for t in TYPES}, b))
    return list(fits.bootstrap_diff(raw, cal, metrics.ece))


def gate_temperatures(fit: dict, held: dict) -> dict:
    """Per type: ship the fitted T unless eval ECE worsens beyond its CI; else the pooled T; else 1.0."""
    gate = {}
    for t in TYPES:
        fitted, b = fit[t]["T"], fit["noul"]["b"] if t == "noul" else 0.0
        decision = {"fitted_T": fitted, "shipped_T": fitted, "source": "fitted", "ece": ece_change(held[t], t, fitted, b)}
        if decision["ece"][1] > 0:
            pooled = fit["pooled"]["T"]
            decision["ece_pooled"] = ece_change(held[t], t, pooled)
            ok = decision["ece_pooled"][1] <= 0
            decision["shipped_T"], decision["source"] = (pooled, "pooled") if ok else (1.0, "none")
        gate[t] = decision
    return gate


def history(path: Path) -> tuple[int, list[dict]]:
    """Last version and comment history of an existing v2 file; a v1, missing or unreadable file starts fresh."""
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return 0, []
    if data.get("format") != 2:
        return 0, []
    return int(data.get("version", 0)), list(data.get("comments", []))


def calibration_file(fit: dict, stamp: dict, orders: str, calib_n: dict, before_after: dict, decisions: dict,
                     previous: tuple[int, list[dict]], comment: str, date: str) -> dict:
    split = SPLIT
    version = previous[0] + 1
    return {
        "format": 2,
        "version": version,  # version, date and comments are informational; the gateway never reads them
        "date": date,
        "comments": [*previous[1], {"version": version, "date": date, "text": comment}],
        "stamp": stamp,
        "types": {"choice": fit["choice"], "score": fit["score"], "noul": fit["noul"]},
        "fit": {"split": str(split.relative_to(ROOT)) if split.is_absolute() else str(split),
                "split_sha256": split_sha256() if split.exists() else None,
                "orders": orders, "n": calib_n, **before_after, **decisions},
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


@dataclass
class LayoutResult:
    layout: str
    fit: dict
    n: dict  # {type: (calib, eval)}
    before: dict  # {"calib" | "eval": {type: summary}} at T = 1, b = 0
    after: dict  # the same under the shipped calibration
    stats: dict
    b_fitted: float
    ship: bool
    gate: dict  # {type: T decision}, see gate_temperatures


def mark(text: str, edge: bool) -> str:
    return text + (" (edge)" if edge else "")


def ci(x: list[float]) -> str:
    return f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"


def gate_text(g: dict) -> str:
    text = f"fitted {ci(g['ece'])}"
    return text + (f"; pooled {ci(g['ece_pooled'])}" if "ece_pooled" in g else "") + f" → {g['source']}"


def layout_report(r: LayoutResult) -> list[str]:
    head = ("| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) "
            "| NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |")
    lines = [f"## {r.layout}", "", head, "|---|---|---|---|---|---|---|---|---|---|"]
    for t in TYPES:
        g = r.gate[t]
        T_text = mark(f"{g['fitted_T']:.3f}", at_edge(g["fitted_T"], fits.LOG_T, log=True))
        if g["source"] != "fitted":
            T_text = f"{g['shipped_T']:.3f} ({g['source']}; fitted {T_text})"
        b = r.fit["noul"]["b"]
        b_text = mark(f"{b:+.3f}", at_edge(b, fits.B_RANGE)) if t == "noul" else ""
        moves = [f"{fmt(r.before[s][t][m])} → {fmt(r.after[s][t][m])}" for m in ("nll", "ece") for s in ("calib", "eval")]
        lines.append(f"| {t} | {r.n[t][0]}/{r.n[t][1]} | {T_text} | {gate_text(g)} | {b_text} | {' | '.join(moves)} "
                     f"| {fmt(r.after['eval'][t]['accuracy'])} |")
    acc, ece = r.stats["acc"], r.stats["ece"]
    verdict = "shipped" if r.ship else "not shipped (b = 0)"
    b_text = mark(f"{r.b_fitted:+.3f}", at_edge(r.b_fitted, fits.B_RANGE))
    lines += ["", (f"noul offset: fitted b = {b_text}; eval accuracy change {acc[0]:+.4f} [{acc[1]:+.4f}, {acc[2]:+.4f}], "
                    f"ECE change {ece[0]:+.4f} [{ece[1]:+.4f}, {ece[2]:+.4f}] → {verdict}"), ""]
    return lines


def split_questions(recs, rows, layout: str, orders: str, name: str):
    by_type, stamp = questions_by_type(recs, rows, layout, orders)
    if stamp is None:
        raise SystemExit(f"{layout}: no ok records in {name}")
    return by_type, stamp


def fit_and_judge(layout: str, calib: dict, held: dict) -> LayoutResult:
    """Fit on calib, decide b on eval, and measure before (T = 1, b = 0) and after on both splits."""
    fit = fit_layout(calib)
    if held["noul"]:
        ship, stats = ship_offset(held["noul"], (fit["noul"]["T"], fit["noul"]["b"]), fit["noul_b0"]["T"])
    else:
        ship, stats = False, {"acc": (0, 0, 0), "ece": (0, 0, 0)}
    b_fitted = fit["noul"]["b"]
    if not ship:
        fit["noul"] = {"T": fit["noul_b0"]["T"], "b": 0.0}
    gate = gate_temperatures(fit, held)
    for t in TYPES:
        if gate[t]["source"] != "fitted":
            fit[t] = {"T": gate[t]["shipped_T"], "b": 0.0} if t == "noul" else {"T": gate[t]["shipped_T"]}
    ship = ship and gate["noul"]["source"] == "fitted"
    cal = Calibration({t: fit[t]["T"] for t in TYPES}, fit["noul"]["b"])
    raw, splits = Calibration({t: 1.0 for t in TYPES}), {"calib": calib, "eval": held}
    before = {n: {t: summarize(qs[t], t, raw) for t in TYPES} for n, qs in splits.items()}
    after = {n: {t: summarize(qs[t], t, cal) for t in TYPES} for n, qs in splits.items()}
    n = {t: (len(calib[t]), len(held[t])) for t in TYPES}
    return LayoutResult(layout, fit, n, before, after, stats, b_fitted, ship, gate)


def calibrate_layout(args, s, layout, recs, rows) -> list[str]:
    """Fit one layout, write its file (unless dry run) and return its report lines."""
    calib, stamp = split_questions(recs["calib"], rows["calib"], layout, args.orders, "calib")
    held, eval_stamp = split_questions(recs["eval"], rows["eval"], layout, args.orders, "eval")
    if stamp != eval_stamp:
        raise SystemExit(f"{layout}: calib and eval were collected under different stamps")
    r = fit_and_judge(layout, calib, held)
    before_after = {m: {"before": {t: r.before["eval"][t][m] for t in TYPES}, "after": {t: r.after["eval"][t][m] for t in TYPES}}
                    for m in ("nll", "ece")}
    b_decision = {"ship": r.ship, "acc": list(r.stats["acc"]), "ece": list(r.stats["ece"]), "b_fitted": r.b_fitted}
    path = s.data_dir(layout) / "calibration.json"
    data = calibration_file(r.fit, stamp, args.orders, {t: len(calib[t]) for t in TYPES}, before_after,
                            {"b_decision": b_decision, "t_decision": r.gate},
                            history(path), args.comment or default_comment(path, args.orders), now_iso())
    if not args.dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=1) + "\n")
    return layout_report(r)


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
    revision = git_revision()  # before any file is written, so our own output doesn't read as "dirty"
    lines = [line for layout in layouts for line in calibrate_layout(args, s, layout, recs, rows)]
    meta = {"timestamp": stamp_utc, "repo commit": revision, "profile": args.profile, "orders": args.orders,
            "calib split sha256": split_sha256(),
            "collect": (COLLECT / args.profile).relative_to(ROOT) / "{calib,eval}.jsonl.gz", "written": not args.dry_run}
    out = ROOT / "docs" / "results" / args.profile / f"{stamp_utc}-calibrate"
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.md").write_text(f"# {args.profile} calibration\n\n{provenance(meta)}\n" + "\n".join(lines) + "\n")
    print(out / "summary.md")


if __name__ == "__main__":
    main()
