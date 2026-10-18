import math
import random

import pytest

from gateway.calibration import softmax
from gateway.decide import blend
from scripts.order_policies import (
    IMAGE_POLICIES,
    POLICIES,
    Policy,
    combine,
    cost,
    extra_tokens,
    fit,
    fit_types,
    select,
    tn_temperature,
)


def reads_for(n: int, identity: list[float], perms: list[list[int]] | None = None) -> dict:
    """Every rotation and the reversal (or the given perms); each read follows the content, so all agree."""
    perms = perms or [list(range(n)), list(range(n))[::-1], *([(list(range(n)) * 2)[s:s + n] for s in range(1, n)])]
    return {tuple(p): identity if p == list(range(n)) else [identity[p[j]] for j in range(n)] for p in perms}


def logs(*probs: float) -> list[float]:
    return [math.log(p) for p in probs]


def test_gate_reads_second_only_when_unsure():
    policy = Policy("top_p 0.7", "reversed", "top_p", 0.7, "mean-prob")
    tops = [logs(0.95, 0.03, 0.02), logs(0.6, 0.3, 0.1), logs(0.4, 0.35, 0.25)]
    assert [cost(select(reads_for(3, lp), 3, policy, 1.0)) for lp in tops] == [1, 2, 2]
    assert select(reads_for(3, tops[1]), 3, policy, 1.0)[1][1] == [2, 1, 0]


def test_gate_reads_the_first_order_at_the_given_temperature():
    policy = Policy("top_p 0.7", "reversed", "top_p", 0.7, "mean-prob")
    sure = reads_for(3, logs(0.95, 0.03, 0.02))
    assert cost(select(sure, 3, policy, 1.0)) == 1 and cost(select(sure, 3, policy, 10.0)) == 2


def test_min_n():
    policy = Policy("min_n 4", "reversed", "min_n", 4, "mean-prob")
    assert cost(select(reads_for(2, logs(0.5, 0.5)), 2, policy, 1.0)) == 1
    assert cost(select(reads_for(5, logs(0.2, 0.2, 0.2, 0.2, 0.2)), 5, policy, 1.0)) == 2


def test_aleria_rule():
    policy = Policy("aleria", "half", "aleria", None, "mean-prob")
    agree = reads_for(4, logs(0.7, 0.1, 0.1, 0.1))
    assert [perm for _, perm in select(agree, 4, policy, 1.0)] == [[0, 1, 2, 3], [2, 3, 0, 1]]
    disagree = agree | {(2, 3, 0, 1): logs(0.7, 0.1, 0.1, 0.1)}  # half favours shown position 0: caller option 2
    got = [perm for _, perm in select(disagree, 4, policy, 1.0)]
    assert sorted(perm[0] for perm in got) == [0, 1, 2, 3] and got[:2] == [[0, 1, 2, 3], [2, 3, 0, 1]]
    assert cost(select(reads_for(2, logs(0.9, 0.1)), 2, policy, 1.0)) == 2  # n = 2 never reads more


def test_missing_perm_named():
    reads = reads_for(5, logs(0.2, 0.2, 0.2, 0.2, 0.2), [[0, 1, 2, 3, 4], [4, 3, 2, 1, 0]])
    with pytest.raises(ValueError, match=r"missing perm \[2, 3, 4, 0, 1\]"):
        select(reads, 5, Policy("always half", "half", "always", None, "mean-prob"), 1.0)


def test_cyclic_reads_the_m3_orders():
    reads = reads_for(4, logs(0.4, 0.3, 0.2, 0.1))
    got = select(reads, 4, Policy("cyclic:3", "reversed", "cyclic", 3, "mean-prob"), 1.0)
    assert [perm for _, perm in got] == [[0, 1, 2, 3], [1, 2, 3, 0], [3, 0, 1, 2]]


def test_mean_logprob_renormalises():
    chosen = [([-1.0, -2.0, -4.0], [0, 1, 2]), ([-3.0, -1.0, -2.0], [2, 1, 0])]
    got = combine(chosen, "mean-logprob", 2.0, None)
    assert sum(got) == pytest.approx(1.0)
    assert got == pytest.approx(softmax([(-1.0 - 2.0) / 2, (-2.0 - 1.0) / 2, (-4.0 - 3.0) / 2], 2.0))


def test_mean_prob_matches_blend():
    chosen = [([-1.0, -2.0, -4.0], [0, 1, 2]), ([-3.0, -1.0, -2.0], [2, 1, 0])]
    assert combine(chosen, "mean-prob", 1.7, None) == blend(chosen, 1.7)


def test_tn_prob_is_mean_prob_at_the_option_count_temperature():
    chosen = [([-1.0, -2.0, -4.0, -3.0], [0, 1, 2, 3])]
    assert tn_temperature(3.0, -1.0, 4) == pytest.approx(3.0 - math.log(4))
    assert tn_temperature(1.0, -1.0, 128) == 0.05
    assert combine(chosen, "tn-prob", 99.0, (3.0, -1.0)) == blend(chosen, 3.0 - math.log(4))


def synthetic(T_of_n, ns, count: int, seed: int = 0) -> list:
    """Questions whose gold is drawn from softmax(logits / T(n)): a fit should recover T(n)."""
    rng, out = random.Random(seed), []
    for i in range(count):
        n = ns[i % len(ns)]
        lp = [rng.gauss(0, 6) for _ in range(n)]
        gold = rng.choices(range(n), softmax(lp, T_of_n(n)))[0]
        out.append(([(lp, list(range(n)))], gold, n))
    return out


def test_fit_recovers_temperature():
    assert fit(synthetic(lambda n: 3.0, [4], 3000), "mean-prob") == pytest.approx(3.0, abs=0.2)


def test_fit_tn_recovers_the_line():
    alpha, beta = fit(synthetic(lambda n: 4.0 - 0.8 * math.log(n), [2, 16], 1500), "tn-prob")
    assert tn_temperature(alpha, beta, 2) == pytest.approx(4.0 - 0.8 * math.log(2), abs=0.4)
    assert tn_temperature(alpha, beta, 16) == pytest.approx(4.0 - 0.8 * math.log(16), abs=0.4)


def test_fit_types_fits_each_type_and_keeps_one_when_too_few():
    many = synthetic(lambda n: 3.0, [4], 300)
    got = fit_types({"choice": many, "score": many[:5], "noul": []}, "mean-prob")
    assert got["choice"] == pytest.approx(3.0, abs=0.6) and got["score"] == 1.0 and got["noul"] == 1.0
    assert fit_types({"choice": many[:5]}, "tn-prob") == {"choice": (1.0, 0.0)}


def test_cost_and_extra_suffix_tokens():
    chosen = [([0.0, 0.0], [0, 1]), ([0.0, 0.0], [1, 0])]
    assert cost(chosen) == 2 and extra_tokens(chosen, {(0, 1): 80, (1, 0): 90}) == 90
    assert extra_tokens(chosen[:1], {(0, 1): 80}) == 0


def test_policy_lists():
    names = [p.name for p in POLICIES]
    assert len(names) == len(set(names)) == 46 and names[0] == "identity"
    assert {p.second for p in POLICIES if p.gate in ("always", "top_p", "min_n")} == {"reversed"}
    assert {p.combine for p in POLICIES if p.gate == "aleria"} == {"mean-prob", "mean-logprob", "tn-prob"}
    assert {p.value for p in POLICIES if p.gate == "top_p"} == {0.5, 0.6, 0.7, 0.8, 0.9}
    assert {p.value for p in POLICIES if p.gate == "min_n"} == {3, 4, 5, 6, 8}
    halves = [p for p in IMAGE_POLICIES if p not in POLICIES]
    assert len(halves) == 33 and {p.second for p in halves} == {"half"}
