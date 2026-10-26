import math
import random

import pytest

from gateway.calibration import Curve, softmax
from scripts.fit import bootstrap_diff, fit_curve, fit_noul, fit_temperature, golden_min, nll


def sample_choice(true_T, n=4000, k=4, seed=0):
    """Logits drawn at random; gold drawn from softmax(logits / true_T): the fit should recover true_T."""
    rng, qs = random.Random(seed), []
    for _ in range(n):
        lp = [rng.gauss(0, 2) for _ in range(k)]
        w = [math.exp(x / true_T) for x in lp]
        gold = rng.choices(range(k), weights=w)[0]
        qs.append(([(lp, list(range(k)))], gold))
    return qs


def sample_noul(true_T, true_b, n=6000, seed=1):
    rng, qs = random.Random(seed), []
    for _ in range(n):
        delta = rng.gauss(0, 3)
        p_yes = 1 / (1 + math.exp(-(delta / true_T + true_b)))
        qs.append(([([0.0, delta], [0, 1])], int(rng.random() < p_yes)))
    return qs


def test_golden_min_finds_a_parabola_minimum():
    assert golden_min(lambda x: (x - 1.3) ** 2, -5, 5) == pytest.approx(1.3, abs=1e-3)


def test_fit_temperature_recovers_the_true_temperature():
    assert fit_temperature(sample_choice(2.0)) == pytest.approx(2.0, rel=0.1)


def test_fit_noul_recovers_temperature_and_offset():
    T, b = fit_noul(sample_noul(1.5, 0.8))
    assert T == pytest.approx(1.5, rel=0.15) and b == pytest.approx(0.8, abs=0.15)


def test_fitted_nll_beats_t_equal_one():
    qs = sample_choice(3.0)
    assert nll(qs, fit_temperature(qs)) < nll(qs, 1.0)


def test_bootstrap_diff_sees_a_clear_difference():
    a, b = [0.0] * 300, [1.0] * 150 + [0.0] * 150
    mean, lo, hi = bootstrap_diff(a, b, lambda xs: sum(xs) / len(xs))
    assert mean == pytest.approx(0.5) and lo > 0.4 and hi < 0.6


def exact_curve_sample(curve: Curve, per_n: int = 400):
    """Per option count, one logit vector and golds in exactly the proportions softmax(lp / T(n)) gives."""
    qs = []
    for n, gap in ((2, 3.0), (4, 3.0), (8, 4.0), (16, 4.0)):
        lp = [0.0] + [-gap] * (n - 1)
        for gold, p in enumerate(softmax(lp, curve(n))):
            qs += [([(lp, list(range(n)))], gold)] * round(per_n * p)
    return qs


def test_curve_fit_recovers_a_known_curve():
    got = fit_curve(exact_curve_sample(Curve(4.0, -1.0)))
    assert got.a == pytest.approx(4.0, abs=0.05) and got.b == pytest.approx(-1.0, abs=0.05)


def test_curve_fit_of_a_flat_temperature_is_flat():
    got = fit_curve(exact_curve_sample(Curve(2.5, 0.0)))
    assert got.a == pytest.approx(2.5, abs=0.05) and got.b == pytest.approx(0.0, abs=0.05)
