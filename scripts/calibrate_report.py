"""The calibrate report: one markdown table per layout, with the T gate and the noul offset decision."""

import math
from dataclasses import dataclass

from gateway.calibration import TYPES
from scripts import fit as fits
from scripts.offline import fmt


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
    gate: dict  # {type: T decision}, see calibrate.gate_temperatures


def at_edge(value: float, bounds: tuple[float, float], log: bool = False) -> bool:
    """True when a fitted value sits within 1e-3 of its search range (log scale for T): the optimum may lie beyond."""
    x = math.log(value) if log else value
    return min(x - bounds[0], bounds[1] - x) < 1e-3


def mark(text: str, edge: bool) -> str:
    return text + (" (edge)" if edge else "")


def ci(x: list[float]) -> str:
    return f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"


def gate_text(g: dict) -> str:
    return f"fitted {ci(g['ece'])}; pooled {ci(g['ece_pooled'])} → {g['source']}"


def type_row(r: LayoutResult, t: str) -> str:
    g = r.gate[t]
    T_text = mark(f"{g['fitted_T']:.3f}", at_edge(g["fitted_T"], fits.LOG_T, log=True))
    if g["source"] != "fitted":
        T_text = f"{g['shipped_T']:.3f} ({g['source']}; fitted {T_text})"
    b = r.fit["noul"]["b"]
    b_text = mark(f"{b:+.3f}", at_edge(b, fits.B_RANGE)) if t == "noul" else ""
    moves = [f"{fmt(r.before[s][t][m])} → {fmt(r.after[s][t][m])}" for m in ("nll", "ece") for s in ("calib", "eval")]
    cells = [t, f"{r.n[t][0]}/{r.n[t][1]}", T_text, gate_text(g), b_text, *moves, fmt(r.after["eval"][t]["accuracy"])]
    return "| " + " | ".join(cells) + " |"


def layout_report(r: LayoutResult) -> list[str]:
    head = ("| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) "
            "| NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |")
    lines = [f"## {r.layout}", "", head, "|---|---|---|---|---|---|---|---|---|---|"]
    lines += [type_row(r, t) for t in TYPES]
    acc, ece = r.stats["acc"], r.stats["ece"]
    verdict = "shipped" if r.ship else "not shipped (b = 0)"
    b_text = mark(f"{r.b_fitted:+.3f}", at_edge(r.b_fitted, fits.B_RANGE))
    pooled = r.fit["pooled"]["T"]
    lines += ["", f"pooled T (one T for every type, b = 0; the gate's fallback): {pooled:.3f}", "",
              (f"noul offset: fitted b = {b_text}; eval accuracy change {acc[0]:+.4f} [{acc[1]:+.4f}, {acc[2]:+.4f}],"
               f" ECE change {ece[0]:+.4f} [{ece[1]:+.4f}, {ece[2]:+.4f}] → {verdict}"), ""]
    return lines
