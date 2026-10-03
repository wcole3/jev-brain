"""The M3 layout study: each prompt layout at the default orders with its own T, bucketed by state length."""

from gateway.calibration import Calibration
from gateway.config import Settings
from gateway.layouts import load_layouts
from gateway.prompts import encode_each
from gateway.questions import render_state
from scripts.experiments import (
    BY_TYPE,
    SHIPPED,
    compare_groups,
    fit_arm,
    is_long,
    job,
    length_bucket,
    per_group,
    qualifying,
    run_compare,
    split_by,
    summary,
    verdict,
)
from scripts.offline import Arm, keyed


def load_tokenizer(profile: str):
    from transformers import AutoTokenizer  # slow to import: only the layouts command needs it

    s = Settings.from_profile(profile)
    return AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision, local_files_only=True)  # HF cache only


def count_state_tokens(tok, rows: dict) -> dict[str, int]:
    """Each row's state as the prompt renders it, in tokens; one tokenizer call for all rows."""
    ids = list(rows)
    return dict(zip(ids, map(len, encode_each(tok, [render_state(rows[i]["state"]) for i in ids])), strict=True))


def layout_groups(tokens: dict[str, int]) -> dict:
    """Buckets by state length in tokens, the same for every layout."""
    return BY_TYPE | {
        "length": lambda key, item: length_bucket(tokens[key[0]]),
        "slice": lambda key, item: "long" if is_long(item.source, item.family, tokens[key[0]]) else "rest",
    }


def fit_layouts(calib_recs: list[dict], calib_rows: dict, orders: str) -> dict[str, Calibration]:
    return {name: fit_arm(calib_recs, calib_rows, name, orders) for name in sorted(load_layouts())}


def layout_arms(recs, rows, cals: dict, orders: str, default: str, shipped: Calibration) -> tuple[dict, dict]:
    """Each layout, and the default under its shipped calibration, on the questions every layout answered."""
    layouts = load_layouts()
    arms = {name: keyed(recs, rows, Arm(name, orders, cal), layouts) for name, cal in cals.items()}
    arms[SHIPPED] = keyed(recs, rows, Arm(default, orders, shipped), layouts)
    shared = set.intersection(*(set(items) for items in arms.values()))
    answered = {"any": len(set.union(*(set(items) for items in arms.values()))), "all": len(shared),
                **{name: len(items) for name, items in arms.items() if name != SHIPPED}}
    return {name: {k: v for k, v in items.items() if k in shared} for name, items in arms.items()}, answered


def winners(arms: dict, summaries: dict, groups: dict, baseline: str, pmap=map) -> dict:
    """The most accurate layout per bucket; a bucket auto-switches from baseline only on a CI clear of zero."""
    def best(name, bucket):  # a tie goes to the baseline
        return max(arms, key=lambda layout: (summaries[layout][name][bucket]["accuracy"], layout == baseline))
    slots = [(name, bucket, best(name, bucket)) for name in ("length", "slice") for bucket in summaries[baseline][name]]
    differ = [slot for slot in slots if slot[2] != baseline]
    results = pmap(run_compare, [job(split_by(arms[baseline], groups[name])[bucket], arms[winner])
                                 for name, bucket, winner in differ])
    vs = dict(zip(differ, results, strict=True))
    out = {"baseline": baseline, "length": {}, "slice": {}}
    for name, bucket, winner in slots:
        c = vs.get((name, bucket, winner))
        out[name][bucket] = {"winner": winner, "accuracy": summaries[winner][name][bucket]["accuracy"],
                             "vs_baseline": c, "auto_switch": bool(c and c["accuracy"] and c["accuracy"][1] > 0)}
    return out


def switches_on_both(splits: dict) -> list[str]:
    """Buckets that auto-switch to the same layout on every split, as "grouping bucket: layout"."""
    flagged = [{f"{name} {bucket}: {w['winner']}" for name in ("length", "slice")
                for bucket, w in data["winners"][name].items() if w["auto_switch"]} for data in splits.values()]
    return sorted(set.intersection(*flagged))


def layouts_study(calib_recs, calib_rows, splits: dict[str, tuple], default: str, orders: str,
                  shipped: dict[str, Calibration], cals=None, pmap=map) -> dict:
    """splits: {split: (recs, rows, state tokens)}. The verdict, then bucket winners against it on every split."""
    cals = cals or fit_layouts(calib_recs, calib_rows, orders)
    arms, groups, out = {}, {}, {}
    for split, (recs, rows, tokens) in splits.items():
        arms[split], answered = layout_arms(recs, rows, cals, orders, default, shipped[split])
        groups[split] = layout_groups(tokens)
        others = {name: items for name, items in arms[split].items() if name != default}
        vs = compare_groups(arms[split][default], others, groups[split], pmap)
        T = {name: cal.T for name, cal in cals.items()} | {SHIPPED: shipped[split].T}
        out[split] = {"default": default, "answered": answered, "vs_default": vs,
                      "layouts": {name: {"T": T[name], **per_group(items, groups[split], summary)}
                                  for name, items in arms[split].items()},
                      "qualifying": qualifying(vs, [name for name in cals if name != default])}
    pick = verdict(out, cost=lambda arm: 0)  # every layout reads the same orders
    baseline = pick if pick in cals else default
    for split, data in out.items():
        data["winners"] = winners({name: arms[split][name] for name in cals}, data["layouts"], groups[split],
                                  baseline, pmap)
    return {"splits": out, "recommendation": pick, "auto_switch_on_both": switches_on_both(out)}
