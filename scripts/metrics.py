"""Scores for probability answers: accuracy, ECE, NLL, Brier, noul bias, and paired bootstrap intervals."""

import math
import random
from dataclasses import dataclass

EPS = 1e-12  # floor for log(p) so a confident miss costs a large but finite NLL


@dataclass(frozen=True)
class Scored:
    source: str
    family: str
    type: str  # choice | score | noul
    gold: int  # index of the gold option in the caller's order (noul: 0 = no, 1 = yes)
    probs: list[float]  # caller's order, sums to 1

    @property
    def pred(self) -> int:
        if self.type == "noul":
            return int(self.probs[1] >= 0.5)  # the gateway answers yes at p(yes) >= 0.5
        return max(range(len(self.probs)), key=self.probs.__getitem__)

    @property
    def correct(self) -> bool:
        return self.pred == self.gold

    @property
    def confidence(self) -> float:
        return self.probs[self.pred]


def ece_of(confidences: list[float], correct: list[bool], bins: int = 15) -> float:
    """Row-weighted mean |accuracy - confidence| over equal-width bins; confidence 1.0 goes in the top bin."""
    buckets: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for conf, ok in zip(confidences, correct, strict=True):
        buckets[min(int(conf * bins), bins - 1)].append((conf, ok))
    n = len(confidences)
    return sum(len(b) / n * abs(sum(c for c, _ in b) / len(b) - sum(o for _, o in b) / len(b)) for b in buckets if b)


def accuracy(items: list[Scored]) -> float:
    return sum(i.correct for i in items) / len(items)


def ece(items: list[Scored]) -> float:
    return ece_of([i.confidence for i in items], [i.correct for i in items])


def nll(items: list[Scored]) -> float:
    return sum(-math.log(max(i.probs[i.gold], EPS)) for i in items) / len(items)


def brier(items: list[Scored]) -> float:
    return sum(sum((p - (k == i.gold)) ** 2 for k, p in enumerate(i.probs)) for i in items) / len(items)


def noul_bias(items: list[Scored]) -> dict[str, int]:
    noul = [i for i in items if i.type == "noul"]
    return {
        "rows": len(noul),
        "said_yes": sum(i.pred == 1 for i in noul),
        "gold_yes": sum(i.gold == 1 for i in noul),
        "false_no": sum(i.gold == 1 and i.pred == 0 for i in noul),
        "false_yes": sum(i.gold == 0 and i.pred == 1 for i in noul),
    }


def summary(items: list[Scored]) -> dict:
    if not items:
        return {"n": 0, "accuracy": None, "ece": None, "nll": None, "brier": None}
    return {"n": len(items), "accuracy": accuracy(items), "ece": ece(items), "nll": nll(items), "brier": brier(items)}


def paired_bootstrap(a: list[float], b: list[float], resamples: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    """Mean of b - a over paired rows, with a 95% percentile interval from resampling the rows."""
    diffs = [y - x for x, y in zip(a, b, strict=True)]
    rng, n = random.Random(seed), len(diffs)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(resamples))
    return sum(diffs) / n, means[int(0.025 * resamples)], means[int(0.975 * resamples) - 1]
