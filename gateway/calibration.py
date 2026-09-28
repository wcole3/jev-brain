"""Softmax temperatures per question type (fitted in phase 2; 1.0 means uncalibrated)."""
import json
import logging
import math
from pathlib import Path

log = logging.getLogger(__name__)
TYPES = ("choice", "score", "noul")


def load_temperatures(path: Path) -> dict[str, float]:
    if not path.exists():
        log.warning("%s missing: temperature 1.0 (uncalibrated)", path)
        return {t: 1.0 for t in TYPES}
    data = json.loads(path.read_text())
    return {t: float(data.get(t, 1.0)) for t in TYPES}


def softmax(logprobs: list[float], temperature: float) -> list[float]:
    top = max(logprobs)
    weights = [math.exp((x - top) / temperature) for x in logprobs]
    total = sum(weights)
    return [w / total for w in weights]
