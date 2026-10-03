"""Markdown for the M3 reports: scores with paired differences, order diagnostics, layout winners."""

from scripts.bench_report import provenance
from scripts.experiments import SHIPPED
from scripts.offline import fmt

BUCKETS = ["all", "2", "3-5", "6-26", "27+", "<512", "512-2k", "2k-8k", ">8k", "long", "rest"]
RULE = ("An arm qualifies on a split on an accuracy CI low > 0 or an ECE CI high < 0 over the default, without the"
        " other metric getting worse beyond its CI. The verdict is an arm that qualifies on both index-dev and eval:"
        " the cheapest by mean reads per question, then the larger mean Δ accuracy. Each arm is tested at 95%, so one"
        " of several can clear by chance; needing both splits guards against that. pride and the shipped-calibration"
        " row are never candidates. The owner makes the final call.")
LATENCY = "latency measured live on the latency sample (latency.py)"
PRIDE = "needs gateway support (no OPTION_ORDERS value)"


def ci(diff, places: int = 3) -> str:
    return "n/a" if diff is None else "{:+.{p}f} [{:+.{p}f}, {:+.{p}f}]".format(*diff, p=places)


def ordered(buckets) -> list[str]:
    return sorted(buckets, key=lambda b: (BUCKETS.index(b) if b in BUCKETS else len(BUCKETS), b))


def arm_table(title: str, grouping: str, summaries: dict, vs: dict) -> list[str]:
    """One row per bucket and arm: its scores, then its paired difference from the baseline (b - a)."""
    lines = [f"| {title} | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    buckets = ordered({b for s in summaries.values() for b in s[grouping]})
    for bucket in buckets:
        for arm, s in summaries.items():
            g = s[grouping].get(bucket)
            if g is None:
                continue
            c = vs.get(arm, {}).get(grouping, {}).get(bucket)
            deltas = [ci(c[m], places) if c else "baseline" for m, places in (("accuracy", 3), ("ece", 4), ("nll", 4))]
            lines.append(f"| {bucket} | {arm} | {g['n']} | {fmt(g['accuracy'])} | {fmt(g['ece'])} | {fmt(g['nll'])}"
                         f" | {fmt(g['brier'])} | " + " | ".join(deltas) + " |")
    return lines


def overall_deltas(report: dict, arm: str) -> str:
    """arm − default overall on each split."""
    return "; ".join(f"{split} Δ accuracy {ci(c['accuracy'])}, Δ ECE {ci(c['ece'], 4)}"
                     for split, data in report["splits"].items() if (c := data["vs_default"][arm]["overall"]["all"]))


def recommendation(report: dict, cost: str, describe, extra=()) -> list[str]:
    """Each split's qualifying arms (described by describe(data, arm)), the verdict, then the non-candidate rows."""
    picks = [f"- {split} qualifies: " + (", ".join(f"{arm} ({describe(data, arm)})" for arm in data["qualifying"])
                                          or "none") for split, data in report["splits"].items()]
    default = next(iter(report["splits"].values()))["default"]
    return ["## Recommendation", "", f"Default: {default}, each arm at its own calib-fitted T (b = 0).", "", *picks,
            f"- **verdict: {report['recommendation']}**", f"- read cost: {cost}", *extra,
            f"- {SHIPPED}: {overall_deltas(report, SHIPPED)}", "", RULE, ""]


def gain(data: dict, arm: str) -> str:
    return f"Δ accuracy {data['vs_default'][arm]['overall']['all']['accuracy'][0]:+.3f}"


def order_cost(data: dict, arm: str) -> str:
    return f"{gain(data, arm)}, {fmt(data['arms'][arm]['mean_reads'])} mean reads"


def read_cost(report: dict) -> str:
    """The verdict's reads per question, or the default's when it stays."""
    data = report["splits"]["index-dev"]
    arm = report["recommendation"] if report["recommendation"] in data["arms"] else data["default"]
    a = data["arms"][arm]
    return f"{arm}: at most {a['reads']} reads per question, {fmt(a['mean_reads'])} on average on index-dev; {LATENCY}"


def diagnostics(data: dict) -> list[str]:
    lines = ["| grouping | bucket | flip rate | AUROC |", "|---|---|---|---|"]
    for grouping in data["auroc"]:
        for bucket in ordered(data["auroc"][grouping]):
            flips = data["flips"][grouping].get(bucket)
            lines.append(f"| {grouping} | {bucket} | {fmt(flips)} | {fmt(data['auroc'][grouping][bucket])} |")
    lean, prior = data["noul_lean"], ", ".join(map(str, data["pride_prior_options"])) or "none"
    return [
        *lines, "",
        ("flip rate: identity vs reversed top answer (noul left out). AUROC: identity-vs-reversed TVD as a predictor"
         " of identity+reversed errors (0.5 = no signal)."),
        "",
        (f"Noul lean: n {lean['n']}, p(yes) identity {fmt(lean['p_yes_identity'])}, reversed"
         f" {fmt(lean['p_yes_reversed'])}, gold yes {fmt(lean['gold_yes'])}. p(yes) that moves with the order is a"
         " lean to a position; p(yes) that stays put is a lean to the word."),
        "",
        (f"PriDe prior from the calib split (deployable without extra reads): the arithmetic mean of cyclic:4"
         f" probabilities at identity's T (the paper averages log-probabilities), for option counts {prior}; other"
         " counts pass through unchanged."),
    ]


def histograms(data: dict) -> list[str]:
    lines = ["| arm | options | series | count by caller position |", "|---|---|---|---|"]
    for arm, by_bucket in data["histograms"].items():
        for bucket in ordered(by_bucket):
            for series, counts in by_bucket[bucket].items():
                lines.append(f"| {arm} | {bucket} | {series} | {' '.join(map(str, counts))} |")
    return lines


def orders_split(split: str, data: dict) -> list[str]:
    arms, vs = data["arms"], data["vs_default"]
    costs = [f"| {arm} | {a['reads']} | {fmt(a['mean_reads'])} |" for arm, a in arms.items()]
    return [
        f"## {split}", "",
        f"Δ is arm − {data['default']} on the same questions, with a 95% paired-bootstrap CI.", "",
        "| arm | reads (max) | mean reads |", "|---|---|---|", *costs, "",
        *arm_table("overall", "overall", arms, vs), "",
        *arm_table("type", "type", arms, vs), "",
        *arm_table("options", "options", arms, vs), "",
        "### Order diagnostics", "", *diagnostics(data), "",
        f"### Position histograms: identity and the most accurate other arm ({data['best']})", "",
        *histograms(data), "",
    ]


def orders_markdown(report: dict) -> str:
    meta = report["meta"]
    pride = f"- pride (diagnostic, {PRIDE}): {overall_deltas(report, 'pride')}"
    lines = [f"# {meta['profile']} M3 option orders: {meta['layout']}", "", provenance(meta),
             *recommendation(report, read_cost(report), order_cost, [pride])]
    for split, data in report["splits"].items():
        lines += orders_split(split, data)
    return "\n".join(lines)


def winners(data: dict) -> list[str]:
    w = data["winners"]
    lines = [f"Baseline: {w['baseline']} (the verdict's layout, or the default when it stays), on both splits.", "",
             f"| grouping | bucket | winner | accuracy | Δ accuracy vs {w['baseline']} | auto-switch |",
             "|---|---|---|---|---|---|"]
    for grouping in ("length", "slice"):
        for bucket in ordered(w[grouping]):
            b = w[grouping][bucket]
            delta = ci(b["vs_baseline"]["accuracy"]) if b["vs_baseline"] else "same layout"
            switch = "yes" if b["auto_switch"] else "no"
            lines.append(f"| {grouping} | {bucket} | {b['winner']} | {fmt(b['accuracy'])} | {delta} | {switch} |")
    return lines


def layouts_split(split: str, data: dict, orders: str) -> list[str]:
    layouts, vs, answered = data["layouts"], data["vs_default"], data["answered"]
    counts = ", ".join(f"{name} {n}" for name, n in answered.items() if name not in ("any", "all"))
    return [
        f"## {split}", "",
        (f"Every layout reads with {orders}, on the questions all of them answered. Δ is layout − {data['default']}"
         " with a 95% paired-bootstrap CI. State length is the rendered state in the profile's tokens."), "",
        f"Questions answered: {counts}, of {answered['any']} answered by any; compared on {answered['all']}.", "",
        *arm_table("overall", "overall", layouts, vs), "",
        *arm_table("type", "type", layouts, vs), "",
        *arm_table("state length", "length", layouts, vs), "",
        *arm_table("slice", "slice", layouts, vs), "",
        "### Bucket winners (auto-switch needs a different winner with an accuracy CI clear of zero)", "",
        *winners(data), "",
    ]


def layouts_markdown(report: dict) -> str:
    switches, orders = ", ".join(report["auto_switch_on_both"]) or "none", report["meta"]["orders"]
    lines = [f"# {report['meta']['profile']} M3 layouts", "", provenance(report["meta"]),
             *recommendation(report, f"the same reads per question for each layout ({orders}); {LATENCY}", gain),
             f"Auto-switch on both splits: {switches}.", ""]
    for split, data in report["splits"].items():
        lines += layouts_split(split, data, orders)
    return "\n".join(lines)
