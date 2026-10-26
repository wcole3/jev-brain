"""Pure fits for calibration: golden-section search on NLL, and a paired bootstrap of any metric difference."""

import math
import random

from gateway.calibration import Curve, softmax
from gateway.decide import combine
from gateway.orders import average_back

Question = tuple[list[tuple[list[float], list[int]]], int]
LOG_T = (math.log(0.05), math.log(20.0))
B_RANGE = (-10.0, 10.0)
LOG_A = (math.log(0.05), math.log(100.0))  # a curve's intercept: T at n = 1
SLOPE = (-8.0, 8.0)  # a curve's slope per ln n
RATIO = (math.sqrt(5) - 1) / 2


def golden_min(f, lo: float, hi: float, tol: float = 1e-4) -> float:
    a, b = lo, hi
    c, d = b - RATIO * (b - a), a + RATIO * (b - a)
    fc, fd = f(c), f(d)
    while b - a > tol:
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - RATIO * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + RATIO * (b - a)
            fd = f(d)
    return (a + b) / 2


def nll(questions: list[Question], T: float, b: float = 0.0, noul: bool = False) -> float:
    offset = b if noul else 0.0
    return sum(-math.log(max(combine(reads, T, offset)[gold], 1e-12)) for reads, gold in questions) / len(questions)


def fit_temperature(questions: list[Question]) -> float:
    return math.exp(golden_min(lambda lt: nll(questions, math.exp(lt)), *LOG_T))


def fit_noul(questions: list[Question]) -> tuple[float, float]:
    """Coordinate descent: log T with b fixed, then b with T fixed, until the NLL stops moving."""
    T, b, last = 1.0, 0.0, math.inf
    for _ in range(8):
        T = math.exp(golden_min(lambda lt, b=b: nll(questions, math.exp(lt), b, noul=True), *LOG_T))
        b = golden_min(lambda x, T=T: nll(questions, T, x, noul=True), *B_RANGE)
        now = nll(questions, T, b, noul=True)
        if last - now < 1e-7:
            break
        last = now
    return T, b


def mean_logprobs(questions: list[Question]) -> list[tuple[list[float], int]]:
    """Each question's reads averaged back to caller order, once: a curve fit softmaxes them many times."""
    return [(average_back([lp for lp, _ in reads], [perm for _, perm in reads]), gold) for reads, gold in questions]


def curve_nll(means: list[tuple[list[float], int]], curve: Curve) -> float:
    return sum(-math.log(max(softmax(lp, curve(len(lp)))[gold], 1e-12)) for lp, gold in means) / len(means)


def fit_curve(questions: list[Question]) -> Curve:
    """T(n) = max(floor, a + b ln n) by NLL: golden search on b, each b with its best log a."""
    means = mean_logprobs(questions)

    def best_a(b: float) -> float:
        return math.exp(golden_min(lambda la: curve_nll(means, Curve(math.exp(la), b)), *LOG_A))

    b = golden_min(lambda b: curve_nll(means, Curve(best_a(b), b)), *SLOPE, tol=1e-3)
    return Curve(best_a(b), b)


def bootstrap_diff(a: list, b: list, metric, resamples: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    """metric(b) - metric(a) with a 95% interval from resampling the paired items."""
    rng, n = random.Random(seed), len(a)
    diffs = []
    for _ in range(resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(metric([b[i] for i in idx]) - metric([a[i] for i in idx]))
    diffs.sort()
    return metric(b) - metric(a), diffs[int(0.025 * resamples)], diffs[int(0.975 * resamples) - 1]
