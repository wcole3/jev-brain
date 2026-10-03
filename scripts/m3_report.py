"""Markdown for the M3 reports: scores with paired differences, order diagnostics, layout winners."""

from scripts.bench_report import provenance
from scripts.offline import fmt

BUCKETS = ["all", "2", "3-5", "6-26", "27+", "<512", "512-2k", "2k-8k", ">8k", "long", "rest"]
RULE = ("An arm wins on an accuracy CI low > 0 or an ECE CI high < 0, without the other metric getting worse"
        " beyond its CI; index-dev and eval must agree. The owner makes the final call.")

ORDERS_NOTE = ("Δ is arm − identity on the same questions, with a 95% paired-bootstrap CI. PriDe is scored and paired"
               " on the rows outside its 5% prior slice.")
LAYOUTS_NOTE = ("Every layout reads once per question (identity), on the questions all three answered. Δ is layout −"
                " decider_chat with a 95% paired-bootstrap CI; length buckets and the long slice use decider_chat's"
                " input_tokens.")


def tokens(x) -> str:
    return "n/a" if x is None else f"{x:.0f}"


def ci(diff) -> str:
    return "n/a" if diff is None else f"{diff[0]:+.3f} [{diff[1]:+.3f}, {diff[2]:+.3f}]"


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
            deltas = [ci(c[m]) if c else "baseline" for m in ("accuracy", "ece", "nll")]
            lines.append(f"| {bucket} | {arm} | {g['n']} | {fmt(g['accuracy'])} | {fmt(g['ece'])} | {fmt(g['nll'])}"
                         f" | {fmt(g['brier'])} | " + " | ".join(deltas) + " |")
    return lines


def recommendation(report: dict, cost: str) -> list[str]:
    picks = [f"- {split}: {data['recommendation']}" for split, data in report["splits"].items()]
    return ["## Recommendation", "", *picks, f"- **verdict: {report['recommendation']}**", f"- read cost: {cost}",
            "", RULE, ""]


def read_cost(report: dict) -> str:
    """The winning arm's reads per question, or identity's when the default stays."""
    arms = report["splits"]["index-dev"]["arms"]
    arm = report["recommendation"] if report["recommendation"] in arms else "identity"
    return f"{arm}: at most {arms[arm]['reads']} reads per question, {fmt(arms[arm]['mean_reads'])} on average on index-dev"


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
        f"PriDe prior (5% slice, cyclic:4 reads) for option counts: {prior}; other counts pass through unchanged.",
    ]


def histograms(data: dict) -> list[str]:
    lines = ["| arm | options | series | count by caller position |", "|---|---|---|---|"]
    for arm, by_bucket in data["histograms"].items():
        for bucket in ordered(by_bucket):
            for series, counts in by_bucket[bucket].items():
                lines.append(f"| {arm} | {bucket} | {series} | {' '.join(map(str, counts))} |")
    return lines


def orders_split(split: str, data: dict) -> list[str]:
    arms, vs = data["arms"], data["vs_identity"]
    costs = [f"| {arm} | {a['reads']} | {fmt(a['mean_reads'])} |" for arm, a in arms.items()]
    return [
        f"## {split}", "",
        ORDERS_NOTE, "",
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
    lines = [f"# {meta['profile']} M3 option orders: {meta['layout']}", "", provenance(meta),
             *recommendation(report, read_cost(report))]
    for split, data in report["splits"].items():
        lines += orders_split(split, data)
    return "\n".join(lines)


def winners(data: dict) -> list[str]:
    w = data["winners"]
    lines = [f"Overall winner: {w['overall']}.", "",
             f"| grouping | bucket | winner | accuracy | Δ accuracy vs {w['overall']} | auto-switch |",
             "|---|---|---|---|---|---|"]
    for grouping in ("length", "slice"):
        for bucket in ordered(w[grouping]):
            b = w[grouping][bucket]
            delta = ci(b["vs_overall"]["accuracy"]) if b["vs_overall"] else "same layout"
            switch = "yes" if b["auto_switch"] else "no"
            lines.append(f"| {grouping} | {bucket} | {b['winner']} | {fmt(b['accuracy'])} | {delta} | {switch} |")
    return lines


def layouts_split(split: str, data: dict) -> list[str]:
    layouts, vs = data["layouts"], data["vs_decider_chat"]
    sizes = [f"| {name} | {tokens(s['mean_input_tokens'])} |" for name, s in layouts.items()]
    return [
        f"## {split}", "",
        LAYOUTS_NOTE, "",
        "| layout | mean input tokens |", "|---|---|", *sizes, "",
        *arm_table("overall", "overall", layouts, vs), "",
        *arm_table("type", "type", layouts, vs), "",
        *arm_table("state length", "length", layouts, vs), "",
        *arm_table("slice", "slice", layouts, vs), "",
        "### Bucket winners (auto-switch needs a different winner with an accuracy CI clear of zero)", "",
        *winners(data), "",
    ]


def layouts_markdown(report: dict) -> str:
    sizes = report["splits"]["index-dev"]["layouts"]
    cost = "one read per question for every layout; mean input tokens on index-dev: " + ", ".join(
        f"{name} {tokens(s['mean_input_tokens'])}" for name, s in sizes.items())
    lines = [f"# {report['meta']['profile']} M3 layouts", "", provenance(report["meta"]),
             *recommendation(report, cost)]
    for split, data in report["splits"].items():
        lines += layouts_split(split, data)
    return "\n".join(lines)
