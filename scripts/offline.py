"""Experiment arms from collected logprobs: pick the orders, apply temperatures, average, score against gold."""

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field

from gateway.decide import blend
from gateway.layouts import load_layouts
from gateway.orders import option_orders
from gateway.questions import Rendered, render_question
from gateway.schema import Question
from scripts import metrics
from scripts.metrics import Scored

UNCALIBRATED = {"choice": 1.0, "score": 1.0, "noul": 1.0}


@dataclass(frozen=True)
class Arm:
    layout: str = "decider_chat"
    orders: str = "identity"
    temperatures: dict[str, float] = field(default_factory=lambda: dict(UNCALIBRATED))


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
        out.append(Scored(row["source"], row["family"], q.type, gold, blend(chosen, arm.temperatures[q.type])))
    return out


def grouped(items: list[Scored], key) -> dict[str, dict]:
    groups: dict[str, list[Scored]] = defaultdict(list)
    for i in items:
        groups[key(i)].append(i)
    return {k: metrics.summary(v) for k, v in sorted(groups.items())}


def evaluate(recs: Iterable[dict], rows_by_id: dict[str, dict], arm: Arm) -> dict:
    layouts, items, status = load_layouts(), [], Counter()
    for rec in recs:
        if rec["layout"] != arm.layout:
            continue
        status[rec["status"]] += 1
        items += scored(rec, rows_by_id[rec["id"]], arm, layouts) if rec["status"] == "ok" else []
    return {
        "arm": {"layout": arm.layout, "orders": arm.orders, "temperatures": arm.temperatures},
        "overall": metrics.summary(items),
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
    """Accuracy here is over answered, gold-labelled questions; refusals are counted separately under Status."""
    b = report["noul_bias"]
    lines = [
        f"Arm: {report['arm']}",
        "",
        "Status: " + ", ".join(f"{k} {v}" for k, v in sorted(report["status"].items())),
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
