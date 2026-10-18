"""Round-3 option-order policies: which collected orders a question reads, how they combine, and their fits.

Aleria's rotations are cyclic:4's shifts (n/4, n/2, 3n/4, rounded as option_orders rounds), and "half" is cyclic:2's
second order, so every policy reads only orders a text collect or an image cyclic:4 collect holds.
"""

import math
from dataclasses import dataclass

from gateway.calibration import softmax
from gateway.decide import blend
from gateway.orders import average_back, option_orders
from scripts.calibrate import MIN_QUESTIONS
from scripts.fit import LOG_T, golden_min
from scripts.metrics import EPS

Chosen = list[tuple[list[float], list[int]]]
COMBINES = ("mean-prob", "mean-logprob", "tn-prob")
TAUS = (0.5, 0.6, 0.7, 0.8, 0.9)
MIN_NS = (3, 4, 5, 6, 8)
T_FLOOR = 0.05
TN_AT = (2, 16)  # tn-prob is fitted as the line through T(2) and T(16), as round 2 R1 did


@dataclass(frozen=True)
class Policy:
    name: str
    second: str  # reversed | half: the order a gated family adds (cyclic ignores it)
    gate: str  # never | always | top_p | min_n | aleria | cyclic
    value: float | None  # τ for top_p, k for min_n and cyclic
    combine: str  # mean-prob | mean-logprob | tn-prob


def family(gate: str, value, second: str) -> str:
    return {"always": f"always {second}", "cyclic": f"cyclic:{value}", "top_p": f"top_p {value} {second}",
            "min_n": f"min_n {value} {second}", "aleria": f"aleria {second}"}[gate]


def policies(families: list[tuple[str, float | None, str]]) -> list[Policy]:
    return [Policy(f"{family(gate, value, second)}/{rule}", second, gate, value, rule)
            for gate, value, second in families for rule in COMBINES]


def gated(second: str) -> list[tuple[str, float | None, str]]:
    return [("always", None, second), *(("top_p", t, second) for t in TAUS), *(("min_n", k, second) for k in MIN_NS)]


IDENTITY = Policy("identity", "reversed", "never", None, "mean-prob")
POLICIES = [IDENTITY, *policies([gated("reversed")[0], *(("cyclic", k, "reversed") for k in (2, 3, 4)),
                                 *gated("reversed")[1:], ("aleria", None, "half")])]
IMAGE_POLICIES = POLICIES + policies(gated("half"))


def second_perm(n: int, second: str) -> list[int]:
    return list(range(n))[::-1] if second == "reversed" else option_orders(n, "cyclic:2")[-1]


def top(reads: dict, perm: list[int]) -> int:
    lp = lookup(reads, perm)
    return perm[max(range(len(lp)), key=lp.__getitem__)]


def perms(reads: dict, n: int, policy: Policy, first_T: float) -> list[list[int]]:
    """The orders this policy reads; the gates look at the identity read only (top_p at first_T)."""
    identity = list(range(n))
    if policy.gate == "cyclic":
        return option_orders(n, f"cyclic:{policy.value}")
    pair = [identity, second_perm(n, policy.second)]
    if policy.gate == "never":
        return [identity]
    if policy.gate == "always":
        return pair
    if policy.gate == "top_p":
        return pair if max(softmax(lookup(reads, identity), first_T)) < policy.value else [identity]
    if policy.gate == "min_n":
        return pair if n >= policy.value else [identity]
    if policy.gate == "aleria":
        if n < 3 or top(reads, identity) == top(reads, pair[1]):
            return pair
        return pair + [p for p in option_orders(n, "cyclic:4") if p not in pair]
    raise ValueError(f"unknown gate {policy.gate!r}")


def lookup(reads: dict, perm: list[int]) -> list[float]:
    if tuple(perm) not in reads:
        raise ValueError(f"missing perm {perm}")
    return reads[tuple(perm)]


def select(reads: dict[tuple[int, ...], list[float]], n: int, policy: Policy, first_T: float) -> Chosen:
    """(logprobs, perm) for each order the policy reads; refuses a policy that needs an uncollected order."""
    return [(lookup(reads, perm), perm) for perm in perms(reads, n, policy, first_T)]


def tn_temperature(alpha: float, beta: float, n: int) -> float:
    return max(T_FLOOR, alpha + beta * math.log(n))


def combine(chosen: Chosen, rule: str, T: float, tn: tuple[float, float] | None) -> list[float]:
    """Caller-order probabilities; tn-prob ignores T and uses T(n) from tn = (alpha, beta)."""
    if rule == "mean-prob":
        return blend(chosen, T)
    if rule == "mean-logprob":
        return softmax(average_back([lp for lp, _ in chosen], [perm for _, perm in chosen]), T)
    if rule == "tn-prob":
        return blend(chosen, tn_temperature(*tn, len(chosen[0][1])))
    raise ValueError(f"unknown combine rule {rule!r}")


def nll(questions: list, rule: str, T: float, tn: tuple[float, float] | None = None) -> float:
    return sum(-math.log(max(combine(c, rule, T, tn)[gold], EPS)) for c, gold, _ in questions) / len(questions)


def line(t2: float, t16: float) -> tuple[float, float]:
    """(alpha, beta) of T = alpha + beta ln n through T(2) = t2 and T(16) = t16."""
    beta = (t16 - t2) / (math.log(TN_AT[1]) - math.log(TN_AT[0]))
    return t2 - beta * math.log(TN_AT[0]), beta


def fit_tn(questions: list) -> tuple[float, float]:
    """Nested golden search on log T(2) (outer) and log T(16) (inner); one option count leaves T(16) free."""
    def inner(lt2: float) -> tuple[float, float]:
        lt16 = golden_min(lambda x: nll(questions, "tn-prob", 0.0, line(math.exp(lt2), math.exp(x))), *LOG_T)
        return line(math.exp(lt2), math.exp(lt16))
    return inner(golden_min(lambda lt2: nll(questions, "tn-prob", 0.0, inner(lt2)), *LOG_T))


def fit(questions: list[tuple[list, int, int]], rule: str) -> float | tuple[float, float]:
    """questions are (chosen, gold, n); T by golden search on log T, or (alpha, beta) for tn-prob."""
    if rule == "tn-prob":
        return fit_tn(questions)
    return math.exp(golden_min(lambda lt: nll(questions, rule, math.exp(lt)), *LOG_T))


def fit_types(by_type: dict[str, list], rule: str) -> dict[str, float | tuple[float, float]]:
    """fit per question type; fewer than MIN_QUESTIONS keeps T = 1 (tn: alpha 1, beta 0), as calibrate.py does."""
    keep = (1.0, 0.0) if rule == "tn-prob" else 1.0
    return {t: fit(qs, rule) if len(qs) >= MIN_QUESTIONS else keep for t, qs in by_type.items()}


def cost(chosen: Chosen) -> int:
    return len(chosen)


def extra_tokens(chosen: Chosen, suffix_len: dict[tuple[int, ...], int]) -> int:
    """Suffix tokens of the reads after the first: what a second order adds to an image request."""
    return sum(suffix_len[tuple(perm)] for _, perm in chosen[1:])
