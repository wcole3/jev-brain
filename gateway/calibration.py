"""Calibration per profile and layout: a temperature per question type and a yes-offset for noul (phase 2)."""

import json
import logging
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from gateway.labels import tokenizer_sha256

log = logging.getLogger(__name__)
TYPES = ("choice", "score", "noul")
STAMP_KEYS = ("tokenizer_sha256", "layout_sha256", "hf_revision", "prefix_pad", "prefix_block")
STALE = "move the stale file aside (T = 1 meanwhile), recollect calib and eval, then rerun scripts/calibrate.py"


FLOOR = 0.05  # a curve never goes below this T, however many options


@dataclass(frozen=True)
class Curve:
    """T(n) = max(floor, a + b ln n): a temperature that depends on the question's option count n."""

    a: float
    b: float
    floor: float = FLOOR

    def __call__(self, n: int) -> float:
        return max(self.floor, self.a + self.b * math.log(n))

    def __format__(self, spec: str) -> str:
        return f"{self.a:{spec}} {self.b:+{spec}} ln n"


Temperature = float | Curve


def temperature(T: Temperature, n: int) -> float:
    return T(n) if isinstance(T, Curve) else T


def to_json(value):
    """json.dumps default: a Curve is written as {"a", "b", "floor"}, as the calibration file holds it."""
    if isinstance(value, Curve):
        return asdict(value)
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


@dataclass(frozen=True)
class Calibration:
    T: dict[str, Temperature]
    b: float = 0.0  # noul: added to the "yes" logit after dividing by T
    source: str = "uncalibrated"
    orders: str | None = None  # the option orders it was fitted under; None when not fitted

    def temperature(self, q_type: str, n: int) -> float:
        """The T for a question of this type with n options."""
        return temperature(self.T[q_type], n)

    def as_dict(self) -> dict:
        T = {t: asdict(v) if isinstance(v, Curve) else v for t, v in self.T.items()}
        return {"T": T, "b": self.b, "source": self.source, "orders": self.orders}


UNCALIBRATED = Calibration({t: 1.0 for t in TYPES})


def softmax(logprobs: list[float], temperature: float) -> list[float]:
    top = max(logprobs)
    weights = [math.exp((x - top) / temperature) for x in logprobs]
    total = sum(weights)
    return [w / total for w in weights]


def stamp_for(tok, layout, settings) -> dict:
    """What a fit depends on: the prompt tokens (tokenizer, layout, padding) and the weights."""
    return {
        "tokenizer_sha256": tokenizer_sha256(tok),
        "layout_sha256": layout.sha256,
        "hf_revision": settings.hf_revision,
        "prefix_pad": settings.prefix_pad,
        "prefix_block": settings.prefix_block,
    }


def orders_warning(cal: Calibration, orders: str) -> str | None:
    """A fit holds for one option-order setting; say so when another one will use it."""
    if cal.orders is None or cal.orders == orders:
        return None
    return f"{cal.source} was fitted under option orders {cal.orders!r}, used here with {orders!r}"


def finite_number(path: Path, name: str, value, positive: bool = False) -> float:
    x = float(value) if isinstance(value, int | float) else math.nan
    if not math.isfinite(x) or (positive and x <= 0):
        raise RuntimeError(f"{path}: {name} must be a finite number{' > 0' if positive else ''}, got {value!r}")
    return x


def temperature_from(path: Path, name: str, value) -> Temperature:
    """A number, or a curve {"a", "b", "floor"?} whose floor keeps T > 0."""
    if not isinstance(value, dict):
        return finite_number(path, name, value, positive=True)
    a, b = (finite_number(path, f"{name}.{k}", value.get(k)) for k in ("a", "b"))
    return Curve(a, b, finite_number(path, f"{name}.floor", value.get("floor", FLOOR), positive=True))


def load_calibration(path: Path, expect: dict | None) -> Calibration:
    """Refuse v1, unstamped, stale or malformed files; with no file, run uncalibrated."""
    if not path.exists():
        log.warning("%s missing: uncalibrated (T = 1, no yes-offset)", path)
        return UNCALIBRATED
    data = json.loads(path.read_text())
    if data.get("format") != 2 or not isinstance(data.get("stamp"), dict):  # version/date/comments: informational
        raise RuntimeError(f"{path}: not a v2 calibration file; rerun scripts/calibrate.py")
    for key in STAMP_KEYS if expect is not None else ():
        file = data["stamp"].get(key)
        if file != expect[key]:
            raise RuntimeError(f"{path}: {key} changed ({file} != {expect[key]}); {STALE}")
    types = data["types"]
    T = {t: temperature_from(path, f"types.{t}.T", types[t]["T"]) for t in TYPES}
    b = finite_number(path, "types.noul.b", types["noul"].get("b", 0.0))
    # source is relative to the data root (<profile>/<layout>/calibration.json), so host and container agree
    source = path.relative_to(path.parents[2]).as_posix()
    return Calibration(T, b, source, data.get("fit", {}).get("orders"))
