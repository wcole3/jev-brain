"""Order diagnostics: flips, position histograms, disagreement as an error signal, noul lean, and PriDe."""

import hashlib
from collections import defaultdict

from gateway.calibration import Calibration, softmax
from gateway.decide import probabilities
from scripts import offline
from scripts.experiments import option_bucket
from scripts.metrics import Scored


def flip_rate(identity: dict, reversed_: dict) -> float:
    keys = [k for k in identity.keys() & reversed_.keys() if identity[k].type != "noul"]
    return sum(identity[k].pred != reversed_[k].pred for k in keys) / len(keys) if keys else 0.0


BUCKET_WIDTH = {"2": 2, "3-5": 5, "6-26": 26, "27+": 27}  # positions kept per bucket; 27+ truncates


def position_histogram(items: list[Scored]) -> dict[str, dict[str, list[int]]]:
    out = {}
    for i in items:
        if i.type == "noul":
            continue
        bucket = option_bucket(len(i.probs))
        width = BUCKET_WIDTH[bucket]
        h = out.setdefault(bucket, {"chosen": [0] * width, "gold": [0] * width})
        for name, pos in (("chosen", i.pred), ("gold", i.gold)):
            if pos < width:
                h[name][pos] += 1
    return out


def tvd(p: list[float], q: list[float]) -> float:
    return sum(abs(a - b) for a, b in zip(p, q, strict=True)) / 2


def disagreement_auroc(identity: dict, reversed_: dict, averaged: dict) -> float | None:
    """Chance that a wrong answer shows more identity-vs-reversed disagreement than a right one (ties half)."""
    keys = identity.keys() & reversed_.keys() & averaged.keys()
    gap = {k: tvd(identity[k].probs, reversed_[k].probs) for k in keys}
    wrong = [gap[k] for k in keys if not averaged[k].correct]
    right = [gap[k] for k in keys if averaged[k].correct]
    if not wrong or not right:
        return None
    wins = sum((w > r) + 0.5 * (w == r) for w in wrong for r in right)
    return wins / (len(wrong) * len(right))


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def noul_lean(identity: dict, reversed_: dict) -> dict:
    """p(yes) moving with the order is a position lean; staying put is a lean to the word."""
    keys = [k for k in identity.keys() & reversed_.keys() if identity[k].type == "noul"]
    return {
        "n": len(keys),
        "p_yes_identity": mean([identity[k].probs[1] for k in keys]),
        "p_yes_reversed": mean([reversed_[k].probs[1] for k in keys]),
        "gold_yes": mean([identity[k].gold for k in keys]),
    }


def in_prior_slice(row_id: str) -> bool:
    return int(hashlib.sha256(row_id.encode()).hexdigest(), 16) % 20 == 0


def pride_prior(recs, rows_by_id, layout: str, cal: Calibration, layouts,
                min_questions: int = 20) -> dict[int, list[float]]:
    """Mean probability at each shown position over the cyclic:4 reads of the 5% slice, per option count."""
    sums, counts = {}, defaultdict(int)
    for rec in recs:
        if not in_prior_slice(rec["id"]):
            continue
        for _, t, chosen, _ in offline.questions(rec, rows_by_id[rec["id"]], layout, "cyclic:4", layouts):
            if t == "noul":
                continue
            k = len(chosen[0][0])
            by_shown = [softmax(lp, cal.T[t]) for lp, _ in chosen]
            avg = [sum(p[j] for p in by_shown) / len(chosen) for j in range(k)]
            sums[k] = avg if k not in sums else [a + b for a, b in zip(sums[k], avg, strict=True)]
            counts[k] += 1
    return {k: [x / counts[k] for x in v] for k, v in sums.items() if counts[k] >= min_questions}


def pride_keyed(recs, rows_by_id, layout: str, cal: Calibration, prior: dict, layouts) -> dict:
    """Identity reads of the rows outside the slice, with the position prior divided out (noul unchanged)."""
    out = {}
    for rec in recs:
        if in_prior_slice(rec["id"]):
            continue
        row = rows_by_id[rec["id"]]
        for qid, t, chosen, gold in offline.questions(rec, row, layout, "identity", layouts):
            p = probabilities(chosen, t, cal)
            if t != "noul" and len(p) in prior:
                p = [x / max(prior[len(p)][j], 1e-9) for j, x in enumerate(p)]
                p = [x / sum(p) for x in p]
            out[(rec["id"], qid)] = Scored(row["source"], row["family"], t, gold, p)
    return out


def reversed_keyed(recs, rows_by_id, layout: str, cal: Calibration, layouts) -> dict:
    """The reversed read alone, back in caller order: the partner of identity for flips and disagreement."""
    out = {}
    for rec in recs:
        row = rows_by_id[rec["id"]]
        for qid, t, chosen, gold in offline.questions(rec, row, layout, "identity+reversed", layouts):
            rev = [c for c in chosen if c[1] != sorted(c[1])] or chosen  # one option: both orders coincide
            out[(rec["id"], qid)] = Scored(row["source"], row["family"], t, gold, probabilities(rev, t, cal))
    return out
