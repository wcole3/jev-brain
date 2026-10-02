"""Experiment arms from collected logprobs: pick the orders, apply the calibration, average, score against gold."""

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from gateway.calibration import UNCALIBRATED, Calibration
from gateway.decide import probabilities
from gateway.layouts import load_layouts
from gateway.orders import option_orders
from gateway.questions import Rendered, render_question
from gateway.schema import Question
from scripts import metrics
from scripts.metrics import Scored


@dataclass(frozen=True)
class Arm:
    layout: str = "decider_chat"
    orders: str = "identity"
    calibration: Calibration = UNCALIBRATED


def gold_index(q: Rendered, gold) -> int | None:
    if gold is None:
        return None
    if q.type == "noul":
        return int(bool(gold))
    if q.type == "choice":
        return q.names.index(gold) if gold in q.names else None
    return int(gold) if 0 <= int(gold) < len(q.names) else None


def scored(record: dict, row: dict, arm: Arm, layouts: dict) -> list[Scored]:
    """One Scored per gold-labelled question, as the gateway would answer it under this arm."""
    if record["status"] != "ok" or record["layout"] != arm.layout:
        return []
    out = []
    for qid, reads in record["questions"].items():
        q = render_question(Question(**row["questions"][qid]), layouts[arm.layout])
        gold = gold_index(q, row["gold"].get(qid))
        if gold is None:
            continue
        wanted = option_orders(len(q.options), arm.orders)
        chosen = [(r["logprobs"], r["perm"]) for r in reads if r["perm"] in wanted]
        if len(chosen) != len(wanted):
            raise ValueError(f"arm {arm.orders} needs {len(wanted)} orders for {record['id']}/{qid}, collected {len(chosen)}")
        out.append(Scored(row["source"], row["family"], q.type, gold, probabilities(chosen, q.type, arm.calibration)))
    return out


def grouped(items: list[Scored], key) -> dict[str, dict]:
    groups: dict[str, list[Scored]] = defaultdict(list)
    for i in items:
        groups[key(i)].append(i)
    return {k: metrics.summary(v) for k, v in sorted(groups.items())}


def all_rows(items: list[Scored], refused: int) -> dict:
    """Accuracy with every gold-labelled question of a refused record counted as wrong (the spec's rule)."""
    n = len(items) + refused
    return {"n": n, "refused": refused, "accuracy": sum(i.correct for i in items) / n if n else None}


def evaluate(recs: Iterable[dict], rows_by_id: dict[str, dict], arm: Arm) -> dict:
    layouts, items, status, refused = load_layouts(), [], Counter(), 0
    for rec in recs:
        if rec["layout"] != arm.layout:
            continue
        status[rec["status"]] += 1
        row = rows_by_id[rec["id"]]
        if rec["status"] == "ok":
            items += scored(rec, row, arm, layouts)
        else:
            refused += sum(gold is not None for gold in row["gold"].values())
    return {
        "arm": {"layout": arm.layout, "orders": arm.orders, "calibration": arm.calibration.as_dict()},
        "overall": metrics.summary(items),
        "all_rows": all_rows(items, refused),
        "by_type": grouped(items, lambda i: i.type),
        "by_source": grouped(items, lambda i: i.source),
        "by_family": grouped(items, lambda i: f"{i.source}/{i.family}"),
        "noul_bias": metrics.noul_bias(items),
        "status": dict(status),
    }


def fmt(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def table(title: str, groups: dict[str, dict]) -> list[str]:
    lines = [f"| {title} | n | accuracy | ECE | NLL | Brier |", "|---|---|---|---|---|---|"]
    lines += [f"| {k} | {g['n']} | {fmt(g['accuracy'])} | {fmt(g['ece'])} | {fmt(g['nll'])} | {fmt(g['brier'])} |"
              for k, g in groups.items()]
    return lines


def markdown(report: dict) -> str:
    """Tables are over answered, gold-labelled questions; the all-rows line also counts refused ones as wrong."""
    b, every = report["noul_bias"], report["all_rows"]
    lines = [
        f"Arm: {report['arm']}",
        "",
        "Status: " + ", ".join(f"{k} {v}" for k, v in sorted(report["status"].items())),
        "",
        (f"All rows (refused questions count as wrong): n {every['n']}, refused {every['refused']},"
         f" accuracy {fmt(every['accuracy'])}"),
        "",
        *table("all", {"all": report["overall"]}),
        "",
        *table("type", report["by_type"]),
        "",
        *table("source", report["by_source"]),
        "",
        (
            f"Noul: {b['rows']} rows, said yes {b['said_yes']}, gold yes {b['gold_yes']}, "
            f"false no {b['false_no']}, false yes {b['false_yes']}"
        ),
        "",
        *table("family", report["by_family"]),
    ]
    return "\n".join(lines) + "\n"
