"""Calibration per profile and layout: a temperature per question type and a yes-offset for noul (phase 2)."""

import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path

from gateway.labels import tokenizer_sha256

log = logging.getLogger(__name__)
TYPES = ("choice", "score", "noul")
STAMP_KEYS = ("tokenizer_sha256", "layout_sha256", "hf_revision", "prefix_pad", "prefix_block")
IMAGE_STAMP_KEYS = (*STAMP_KEYS, "mm_processor_kwargs")  # the image budget moves image logprobs
STALE = "move the stale file aside (T = 1 meanwhile), recollect calib and eval, then rerun scripts/calibrate.py"
IMAGE_STALE = "recollect vision-calib and rerun scripts/fit_image_t.py --write, or remove the image block"


@dataclass(frozen=True)
class Calibration:
    T: dict[str, float]
    b: float = 0.0  # noul: added to the "yes" logit after dividing by T
    source: str = "uncalibrated"
    orders: str | None = None  # the option orders it was fitted under; None when not fitted
    T_image: float | None = None  # choice questions in image requests; None: they use T["choice"]
    image: dict | None = None  # the image block's stamp and fit, shown on /health

    def as_dict(self) -> dict:
        out = {"T": dict(self.T), "b": self.b, "source": self.source, "orders": self.orders}
        if self.T_image is None:
            return out
        return out | {"T_image": self.T_image, "image": {k: (self.image or {}).get(k) for k in ("stamp", "fit")}}


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


def check_image_stamp(path: Path, stamp, expect: dict | None) -> None:
    """The text keys always; mm_processor_kwargs only when expect has it (text tools never use T_image)."""
    if not isinstance(stamp, dict) or not stamp:
        raise RuntimeError(f"{path}: image.stamp must be a non-empty object; {IMAGE_STALE}")
    keys = () if expect is None else IMAGE_STAMP_KEYS if "mm_processor_kwargs" in expect else STAMP_KEYS
    for key in keys:
        if stamp.get(key) != expect[key]:
            raise RuntimeError(f"{path}: image.stamp.{key} changed ({stamp.get(key)} != {expect[key]}); {IMAGE_STALE}")


def image_block(path: Path, data: dict, expect: dict | None) -> tuple[float | None, dict | None]:
    """The optional image temperature; its stamp adds mm_processor_kwargs to the text stamp."""
    block = data.get("image")
    if block is None:
        return None, None
    check_image_stamp(path, block.get("stamp") if isinstance(block, dict) else None, expect)
    return finite_number(path, "image.T", block.get("T"), positive=True), block


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
    T_image, image = image_block(path, data, expect)
    types = data["types"]
    T = {t: finite_number(path, f"types.{t}.T", types[t]["T"], positive=True) for t in TYPES}
    b = finite_number(path, "types.noul.b", types["noul"].get("b", 0.0))
    # source is relative to the data root (<profile>/<layout>/calibration.json), so host and container agree
    source = path.relative_to(path.parents[2]).as_posix()
    return Calibration(T, b, source, data.get("fit", {}).get("orders"), T_image, image)
