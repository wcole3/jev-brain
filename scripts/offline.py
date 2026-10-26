"""Experiment arms from collected logprobs: pick the orders, apply the calibration, average, score against gold."""

from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from gateway.calibration import STAMP_KEYS, UNCALIBRATED, Calibration, load_calibration, softmax
from gateway.config import Settings
from gateway.decide import probabilities
from gateway.layouts import load_layouts
from gateway.orders import gate as order_gate
from gateway.orders import option_orders, rereads
from gateway.questions import Rendered, render_question
from gateway.schema import Question
from scripts import metrics
from scripts.metrics import Scored


@dataclass(frozen=True)
class Arm:
    layout: str = "decider_chat"
    orders: str = "identity"
    calibration: Calibration = UNCALIBRATED
    gate: Calibration | None = None  # the identity fit a top_p setting reads its temperature from


def gold_index(q: Rendered, gold) -> int | None:
    if gold is None:
        return None
    if q.type == "noul":
        return int(bool(gold))
    if q.type == "choice":
        return q.names.index(gold) if gold in q.names else None
    return int(gold) if 0 <= int(gold) < len(q.names) else None


def chosen_reads(q: Rendered, reads: list[dict], orders: str, gate_T: float | None = None) -> list[tuple[list[float], list[int]]]:
    """The collected reads an order setting would have made live, as (logprobs, perm) pairs."""
    if rereads(orders):
        raise ValueError(f"arm {orders} reads the block once, then twice: collect records neither pass")
    wanted = option_orders(len(q.options), orders)
    if (tau := order_gate(orders)) is not None:
        if gate_T is None:
            raise ValueError(f"arm {orders} needs the identity temperature (gate_T)")
        identity = next((r["logprobs"] for r in reads if r["perm"] == wanted[0]), None)
        if identity is not None and max(softmax(identity, gate_T)) < tau:
            wanted = [wanted[0], wanted[0][::-1]]
    chosen = [(r["logprobs"], r["perm"]) for r in reads if r["perm"] in wanted]
    if len(chosen) != len(wanted):
        raise ValueError(f"arm {orders} needs {len(wanted)} orders, collected {len(chosen)}")
    return chosen


def collect_stamp(recs: list[dict], layout: str) -> dict | None:
    """The stamp the layout's records were collected under, for checking a calibration file against."""
    seen = next((r["stamp"] for r in recs if r["layout"] == layout), None)
    return {k: seen.get(k) for k in STAMP_KEYS} if seen else None


def identity_gate(s: Settings, layout: str, orders: str, expect: dict | None) -> Calibration | None:
    """The identity fit a gated setting reads its temperature from; None when the setting has no gate."""
    if order_gate(orders) is None:
        return None
    path = s.calibration_path(layout, "identity")
    cal = load_calibration(path, expect) if path.exists() else None
    if cal is None or cal.orders != "identity":
        raise SystemExit(f"{orders} gates on an identity fit: run calibrate.py --orders identity for {layout} first")
    return cal


def questions(record: dict, row: dict, layout: str, orders: str, layouts: dict,
              gate: Calibration | None = None) -> Iterator[tuple[str, str, list, int]]:
    """(qid, type, chosen reads, gold) for each gold-labelled question of an ok record of this layout."""
    if record["status"] != "ok" or record["layout"] != layout:
        return
    for qid, reads in record["questions"].items():
        q = render_question(Question(**row["questions"][qid]), layouts[layout])
        gold = gold_index(q, row["gold"].get(qid))
        if gold is None:
            continue
        try:
            chosen = chosen_reads(q, reads, orders, gate.temperature(q.type, len(q.options)) if gate else None)
        except ValueError as e:
            raise ValueError(f"{record['id']}/{qid}: {e}") from None
        yield qid, q.type, chosen, gold


def scored_one(row: dict, t: str, gold: int, chosen: list, cal: Calibration) -> Scored:
    return Scored(row["source"], row["family"], t, gold, probabilities(chosen, t, cal))


def scored(record: dict, row: dict, arm: Arm, layouts: dict) -> list[Scored]:
    """One Scored per gold-labelled question, as the gateway would answer it under this arm."""
    return [scored_one(row, t, gold, chosen, arm.calibration)
            for _, t, chosen, gold in questions(record, row, arm.layout, arm.orders, layouts, arm.gate)]


def keyed(recs: Iterable[dict], rows_by_id: dict[str, dict], arm: Arm,
          layouts: dict) -> dict[tuple[str, str], Scored]:
    """Scored answers by (row id, question id), so two arms can be paired on the same questions."""
    out = {}
    for rec in recs:
        row = rows_by_id[rec["id"]]
        for qid, t, chosen, gold in questions(rec, row, arm.layout, arm.orders, layouts, arm.gate):
            out[(rec["id"], qid)] = scored_one(row, t, gold, chosen, arm.calibration)
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
