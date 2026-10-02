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


@dataclass(frozen=True)
class Calibration:
    T: dict[str, float]
    b: float = 0.0  # noul: added to the "yes" logit after dividing by T
    source: str = "uncalibrated"

    def as_dict(self) -> dict:
        return {"T": dict(self.T), "b": self.b, "source": self.source}


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


def load_calibration(path: Path, expect: dict | None) -> Calibration:
    """Refuse v1, unstamped or stale files; with no file, run uncalibrated."""
    if not path.exists():
        log.warning("%s missing: uncalibrated (T = 1, no yes-offset)", path)
        return UNCALIBRATED
    data = json.loads(path.read_text())
    if data.get("format") != 2 or "stamp" not in data:  # version/date/comments are informational only
        raise RuntimeError(f"{path}: not a v2 calibration file; rerun scripts/calibrate.py")
    for key in STAMP_KEYS if expect is not None else ():
        file = data["stamp"].get(key)
        if file != expect[key]:
            raise RuntimeError(f"{path}: {key} changed ({file} != {expect[key]}); rerun scripts/calibrate.py")
    types = data["types"]
    return Calibration({t: float(types[t]["T"]) for t in TYPES}, float(types["noul"].get("b", 0.0)), str(path))
