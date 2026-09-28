"""Probabilities → Jev answers, with TypeSafe's confidence formulas (system-one-adapter confidence_metrics)."""

from gateway.questions import Rendered

DECIMALS = 4


def choice_confidence(p: list[float]) -> float:
    """(p_max − 1/K) / (1 − 1/K): 0 for a uniform guess, 1 when certain."""
    k = len(p)
    return 1.0 if k == 1 else max(0.0, (max(p) - 1 / k) / (1 - 1 / k))


def score_confidence(p: list[float]) -> float:
    """1 − expected distance from the most likely level, relative to a uniform guess."""
    n = len(p)
    if n == 1:
        return 1.0
    mode = max(range(n), key=p.__getitem__)
    spread = sum(x * abs(i - mode) for i, x in enumerate(p))
    uniform = sum(abs(i - (n - 1) / 2) for i in range(n)) / n
    return max(0.0, 1.0 - spread / uniform)


def answer(q: Rendered, p: list[float]) -> dict:
    """p is in the caller's option order and sums to 1."""
    if q.type == "noul":
        return {"type": "noul", "noul": round(p[1], DECIMALS)}
    if q.type == "choice":
        best = max(range(len(p)), key=p.__getitem__)
        return {
            "type": "choice",
            "choice": q.names[best],
            "confidence": round(choice_confidence(p), DECIMALS),
            "probabilities": {name: round(x, DECIMALS) for name, x in zip(q.names, p)},
        }
    return {
        "type": "score",
        "score": round(sum(i * x for i, x in enumerate(p)), DECIMALS),
        "confidence": round(score_confidence(p), DECIMALS),
        "legend": {str(i): d for i, d in enumerate(q.legend)},
        "probabilities": {str(i): round(x, DECIMALS) for i, x in enumerate(p)},
    }
