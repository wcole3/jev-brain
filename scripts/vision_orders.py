"""Round-3 option-order policies on image dev, scored with the text-fitted parameters, then paired by vision_compare.

usage: uv run python scripts/vision_orders.py --profile P --collect FILE [--collect FILE2] --text-fit SUMMARY
       --out DIR [--out-label LABEL]
Merges the collects' reads per row (same rows, same stamp except orders) and writes one arm dir per policy under DIR
(scored.jsonl.gz + arm.json, as vision_offline.py writes), plus a 2-fold group cross-fit reference of
`always <second>` per combine rule. Then vision_compare.py pairs every arm with identity into
docs/results/vision-experiments/<UTC>-LABEL/ (default r3-orders-P), beside orders.{md,json}: cost, fits and the
skipped policies.
SUMMARY is r3_orders.py's summary.json. Dev collects only; a policy needing an uncollected order is skipped, listed.
"""

import argparse
import gzip
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from gateway.orders import option_orders
from scripts import vision_compare, vision_splits
from scripts.calibrate import MIN_QUESTIONS
from scripts.collect import records
from scripts.evaluate import now
from scripts.order_policies import COMBINES, IMAGE_POLICIES, Chosen, Policy, extra_tokens, family, fit, select
from scripts.r3_orders import as_json, probs
from scripts.vision_offline import bare_stamp, fold, input_tokens, require_choice, split_config, usable
from scripts.vision_orders_report import markdown

SAME_CONFIG = ("profile", "layout", "layout_file", "env", "split")  # what every merged collect shares
BASE = "identity"
REFERENCE = "xfit "  # prefix of the cross-fit reference arms
BY_NAME = {p.name: p for p in IMAGE_POLICIES}


@dataclass(frozen=True)
class Item:
    rec: dict
    n: int
    reads: dict[tuple[int, ...], list[float]]
    suffix: dict[tuple[int, ...], int]
    fold: str


def merge(paths: list[Path]) -> tuple[list[dict], list[dict]]:
    """Each row once, with every collect's reads (the first collect's read of a shared perm), and the configs."""
    configs = [split_config(p) for p in paths]
    for path, config in zip(paths, configs, strict=True):
        if config["split"] != "dev":
            raise SystemExit(f"{path} is split {config['split']!r}: order reports read dev collects only")
    if diff := [k for k in SAME_CONFIG if len({json.dumps(c.get(k), sort_keys=True) for c in configs}) > 1]:
        raise SystemExit(f"collects {[str(p) for p in paths]} differ in config {diff}")
    by_id, stamps = [], []
    for path in paths:
        recs = list(records(path))
        if not recs:
            raise SystemExit(f"{path}: no records")
        by_id.append({r["id"]: r for r in recs})
        stamps.append({k: v for k, v in bare_stamp(recs, path).items() if k != "orders"})
    for path, stamp, rows in zip(paths[1:], stamps[1:], by_id[1:], strict=True):
        if diff := sorted(k for k in stamp.keys() | stamps[0].keys() if stamp.get(k) != stamps[0].get(k)):
            raise SystemExit(f"{path} was collected under other stamps than {paths[0]}: {diff}")
        if rows.keys() != by_id[0].keys():
            raise SystemExit(f"{path}: row ids differ from {paths[0]} ({len(by_id[0].keys() - rows.keys())} missing,"
                             f" {len(rows.keys() - by_id[0].keys())} extra)")
    return [union([rows[rid] for rows in by_id]) for rid in by_id[0]], configs


def union(recs: list[dict]) -> dict:
    reads = {}
    for r in recs:
        for read in r["reads"]:
            reads.setdefault(tuple(read["perm"]), read)
    status = next((r["status"] for r in recs if r["status"] != "ok"), "ok")
    return recs[0] | {"reads": list(reads.values()), "status": status}


def items_of(recs: list[dict]) -> tuple[list[Item], dict[str, int]]:
    keep, skipped = usable(recs)
    try:
        for r in keep:
            require_choice(r)
    except ValueError as e:
        raise SystemExit(str(e)) from e
    return [Item(r, len(r["names"]), {tuple(x["perm"]): x["logprobs"] for x in r["reads"]},
                 {tuple(x["perm"]): x["suffix_len"] for x in r["reads"]}, str(fold(r["group"]))) for r in keep], skipped


def picks(items: list[Item], policy: Policy, gate_T: float) -> list[Chosen]:
    out = []
    for i in items:
        try:
            out.append(select(i.reads, i.n, policy, gate_T))
        except ValueError as e:
            raise ValueError(f"{i.rec['id']}: {e}") from None
    return out


def why_skipped(items: list[Item], policy: Policy, gate_T: float, error: ValueError) -> str:
    """Whether a cyclic:4 collect would cover the policy: its perms added (as zeros) let every row select."""
    try:
        for i in items:
            extra = {tuple(p): [0.0] * i.n for p in option_orders(i.n, "cyclic:4")}
            select(extra | i.reads, i.n, policy, gate_T)
    except ValueError:
        return f"needs perms no planned collect holds ({error})"
    return f"needs cyclic:4 collect ({error})"


def text_fit(path: Path, profile: str, layout: str) -> dict:
    s = json.loads(path.read_text())
    if (s["meta"]["profile"], s["meta"]["layout"]) != (profile, layout):
        raise SystemExit(f"{path} fits {s['meta']['profile']} {s['meta']['layout']}, not {profile} {layout}")
    return s


def fit_of(fits: dict, policy: Policy) -> tuple[str, float | dict]:
    """The policy's text choice fit; a half policy without one uses the reversed policy's (ruling R3)."""
    name = policy.name
    if name not in fits:
        name = f"{family(policy.gate, policy.value, 'reversed')}/{policy.combine}"
    if name not in fits:
        raise SystemExit(f"text fit has no {policy.name!r} (nor {name!r})")
    return name, fits[name]["choice"]


def param(v):
    return (v["alpha"], v["beta"]) if isinstance(v, dict) else v


def costs(picked: list[Chosen], items: list[Item]) -> dict:
    n = len(picked)
    return {"mean_reads": sum(map(len, picked)) / n, "share_paying": sum(len(c) > 1 for c in picked) / n,
            "mean_extra_suffix_tokens": sum(extra_tokens(c, i.suffix) for c, i in zip(picked, items, strict=True)) / n}


def scored_rows(items: list[Item], picked: list[Chosen], probabilities: list[list[float]]) -> list[dict]:
    return [{"id": i.rec["id"], "benchmark": i.rec["benchmark"], "group": i.rec["group"], "gold": i.rec["gold"],
             "probs": p, "chance": 1 / i.n, "input_tokens": input_tokens(i.rec, c)}
            for i, c, p in zip(items, picked, probabilities, strict=True)]


def text_arm(items: list[Item], picked: list[Chosen], policy: Policy, fits: dict) -> tuple[list, dict]:
    source, v = fit_of(fits, policy)
    rows = scored_rows(items, picked, [probs(c, policy.combine, param(v)) for c in picked])
    return rows, {"text_fit": {"from": source, "param": v}, "fallbacks": []}


def reference_arm(items: list[Item], picked: list[Chosen], policy: Policy, fits: dict) -> tuple[list, dict]:
    """2-fold group cross-fit on image dev: each fold scored with the other fold's fit; a tiny fold keeps the text fit."""
    source, v = fit_of(fits, policy)
    folds = {}
    for k, other in (("0", "1"), ("1", "0")):
        train = [(c, i.rec["gold"], i.n) for c, i in zip(picked, items, strict=True) if i.fold == other]
        small = len(train) < MIN_QUESTIONS
        folds[k] = {"fitted_on": other, "n": len(train), "fallback": small,
                    "param": v if small else as_json(fit(train, policy.combine))}
    rows = scored_rows(items, picked, [probs(c, policy.combine, param(folds[i.fold]["param"]))
                                       for c, i in zip(picked, items, strict=True)])
    fallbacks = [f"fold {k}" for k, f in folds.items() if f["fallback"]]
    return rows, {"text_fit": {"from": source, "param": v}, "folds": folds, "fallbacks": fallbacks}


def arms(policies: list[Policy]):
    """(name, policy, scorer) for every policy, then the cross-fit references of `always <second>` per rule."""
    yield from ((p.name, p, text_arm) for p in policies)
    for second in ("reversed", "half"):
        for rule in COMBINES:
            p = BY_NAME[f"always {second}/{rule}"]
            yield REFERENCE + p.name, p, reference_arm


def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.]+", "-", name)


def write_arm(folder: Path, rows: list[dict], arm: dict) -> None:
    folder.mkdir(parents=True)
    with gzip.open(folder / "scored.jsonl.gz", "wt", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    (folder / "arm.json").write_text(json.dumps(arm, indent=1) + "\n")


def score_all(recs: list[dict], fit_summary: dict, policies: list[Policy], out: Path,
              common: dict) -> tuple[dict[str, Path], dict[str, dict], dict[str, str]]:
    """Writes every arm a collect can score; returns their dirs, their arm.json, and the skipped ones with why."""
    items, statuses = items_of(recs)
    gate_T = fit_summary["gate_T"]["choice"]
    written, about, skipped = {}, {}, {}
    for name, policy, scorer in arms(policies):
        try:
            picked = picks(items, policy, gate_T)
        except ValueError as e:
            skipped[name] = why_skipped(items, policy, gate_T, e)
            print(f"skip {name}: {skipped[name]}")
            continue
        rows, extra = scorer(items, picked, policy, fit_summary["fits"])
        arm = {"arm": name, "orders": name, "policy": asdict(policy), "gate_T": gate_T, "skipped": statuses,
               "fit_on": None, "scored": len(rows), **costs(picked, items), **extra, **common}
        write_arm(out / slug(name), rows, arm)
        written[name], about[name] = out / slug(name), arm
        print(f"{name}: scored {len(rows)}, mean reads {arm['mean_reads']:.3f} -> {out / slug(name)}")
    return written, about, skipped


def compare(written: dict[str, Path], label: str, out_root: Path) -> tuple[dict, Path]:
    """vision_compare.py with identity as the baseline; returns its summary and the results dir it made."""
    if BASE not in written:
        raise SystemExit(f"no {BASE} arm to pair against")
    before = set(out_root.glob(f"*-{label}"))
    argv = ["--baseline", f"{BASE}={written[BASE]}", *(f"{n}={p}" for n, p in written.items() if n != BASE),
            "--out-label", label, "--out-root", str(out_root)]
    summary = vision_compare.main(argv)
    (out,) = set(out_root.glob(f"*-{label}")) - before
    return summary, out


def notes(profile: str, stamp: dict) -> list[str]:
    out = [("Each arm uses its text fit on text calib (choice T, or tn-prob's α + β ln n); gates read the identity"
            " read at the shipped choice T."),
           "A half policy without a text fit of its own uses the reversed policy's (ruling R3).",
           "Orders: half = cyclic:2's second order; aleria adds cyclic:4's other shifts; shifts are round(i·n/k) (R6).",
           (f"{REFERENCE.strip()} arms: 2-fold group cross-fit on image dev (vision_offline.fold), a reference only;"
            " a fold under 30 questions keeps the text fit.")]
    if stamp.get("prefix_pad", "off") != "off":
        out.append(f"{profile} pads its prefix (prefix_pad {stamp['prefix_pad']}): reads were padded for one order,"
                   " so two-order arms are not exactly live-equivalent (docs/background/vision-experiments.md §3).")
    return out


def run(args, policies: list[Policy]) -> dict:
    if args.out.exists() and any(args.out.iterdir()):
        raise SystemExit(f"{args.out} is not empty: arms from another run would mix in")
    recs, configs = merge(args.collect)
    if configs[0]["profile"] != args.profile:
        raise SystemExit(f"collects are {configs[0]['profile']}, not --profile {args.profile}")
    fit_summary = text_fit(args.text_fit, args.profile, configs[0]["layout"])
    common = {"collect": [str(p.resolve()) for p in args.collect], "text_fit_path": str(args.text_fit.resolve()),
              "collect_config": configs[0] | {"orders": " + ".join(c["orders"] for c in configs),
                                              "label": " + ".join(c["label"] for c in configs)},
              "commit": vision_splits.commit()}
    written, about, skipped = score_all(recs, fit_summary, policies, args.out, common)
    summary, out = compare(written, args.out_label or f"r3-orders-{args.profile}", args.out_root)
    report = {"meta": {"timestamp": now(), "commit": common["commit"], "profile": args.profile,
                       "collects": common["collect"], "text fit": common["text_fit_path"], "arms dir": str(args.out),
                       "gate T (choice)": fit_summary["gate_T"]["choice"],
                       "notes": notes(args.profile, recs[0]["stamp"])},
              "arms": {n: {k: a[k] for k in ("mean_reads", "share_paying", "mean_extra_suffix_tokens", "text_fit")}
                       | ({"folds": a["folds"]} if "folds" in a else {}) for n, a in about.items()},
              "skipped": skipped}
    (out / "orders.json").write_text(json.dumps(report, indent=1) + "\n")
    (out / "orders.md").write_text(markdown(report, summary))
    print(f"orders report -> {out / 'orders.md'}")
    return {"out": out, "arms": list(written), "skipped": skipped}


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="R3 option-order policies on image dev")
    p.add_argument("--profile", required=True)
    p.add_argument("--collect", type=Path, action="append", required=True, help="a dev collect; repeat to merge")
    p.add_argument("--text-fit", type=Path, required=True, help="r3_orders.py summary.json of this profile")
    p.add_argument("--out", type=Path, required=True, help="where the arm dirs go")
    p.add_argument("--out-root", type=Path, default=vision_compare.OUT_ROOT)
    p.add_argument("--out-label", help="the results dir's label (default r3-orders-<profile>)")
    return p.parse_args(argv)


def main(argv=None, policies: list[Policy] = IMAGE_POLICIES) -> dict:
    return run(parse_args(argv), policies)


if __name__ == "__main__":
    main()
