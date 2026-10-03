"""Shared pieces of the M3 experiments: buckets, the long slice, per-arm temperatures, paired comparisons."""

from gateway.calibration import Calibration
from scripts import calibrate, metrics
from scripts import fit as fits

LONG_FAMILIES = {("jevbench", "invoices"), ("jevbench", "invoice_processing"), ("index", "ContractNLI"),
                 ("index", "NLI4CT"), ("index", "BRIGHT")}


def option_bucket(k: int) -> str:
    return "2" if k == 2 else "3-5" if k <= 5 else "6-26" if k <= 26 else "27+"


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


def paired(a: dict, b: dict, keep=None) -> tuple[list, list]:
    keys = sorted(k for k in a.keys() & b.keys() if keep is None or keep(k, a[k]))
    return [a[k] for k in keys], [b[k] for k in keys]


def compare(a: dict, b: dict, keep=None) -> dict:
    """metric(b) - metric(a) with 95% paired-bootstrap intervals, over the questions both arms answered."""
    xa, xb = paired(a, b, keep)
    out = {"n": len(xa)}
    for name, metric in (("accuracy", metrics.accuracy), ("ece", metrics.ece), ("nll", metrics.nll)):
        out[name] = fits.bootstrap_diff(xa, xb, metric) if xa else None
    return out
