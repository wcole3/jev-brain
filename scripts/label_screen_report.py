"""summary.md for label_screen.py: the pipeline check, and a screen's text and image reports."""

from gateway.calibration import TYPES
from scripts.bench_report import provenance
from scripts.m3_report import arm_table, histograms, ordered
from scripts.offline import fmt
from scripts.vision_compare import interval

SUBSETS = ("all = every question both arms answered; pure = the questions the set run showed with its own labels"
           " (fallback questions use today's letters).")


def check_markdown(report: dict) -> str:
    lines = [f"# {report['meta']['profile']} R3 label pipeline check", "", provenance(report["meta"]),
             "| split | rows | questions | agree | status mismatches | one-sided questions | agreement |",
             "|---|---|---|---|---|---|---|"]
    lines += [f"| {split} | {s['rows']} | {s['questions']} | {s['agree']} | {s['status_mismatches']} | {s['one_sided']}"
              f" | {fmt(s['agreement'])} |" for split, s in report["splits"].items()]
    return "\n".join([*lines, "", f"**{'passed' if report['passed'] else 'FAILED'}**"]) + "\n"


def by_bucket(title: str, columns: dict[str, dict]) -> list[str]:
    """One row per grouping and bucket, one column per series (each {grouping: {bucket: value}})."""
    names, first = list(columns), next(iter(columns.values()))
    lines = [f"| grouping | bucket | {' | '.join(names)} |", "|---|---|" + "---|" * len(names)]
    for grouping in first:
        for bucket in ordered(first[grouping]):
            cells = [fmt(columns[n][grouping].get(bucket)) for n in names]
            lines.append(f"| {grouping} | {bucket} | " + " | ".join(cells) + " |")
    return [f"### {title}", "", *lines, ""]


def diagnostics(data: dict) -> list[str]:
    return [*by_bucket("Flip rate: identity vs reversed top answer (noul left out)", data["flips"]),
            "### Predicted vs gold shown position (identity read, noul left out)", "", *histograms(data), ""]


def head(report: dict, what: str) -> list[str]:
    meta, pure = report["meta"], "pure" in report["subsets"]
    title = f"# {meta['profile']} {meta.get('title', 'R3 label screen')}: {meta['set']} vs {control(meta)}, {what}"
    fallback = by_bucket("Fallback share (all questions, set run)", {"share": report["fallback_share"]}) if pure else []
    return [title, "", provenance(meta), *([SUBSETS] if pure else []), "Reports only; the owner picks.", "", *fallback]


def control(meta: dict) -> str:
    return meta.get("control", "letters")


def text_markdown(report: dict) -> str:
    meta = report["meta"]
    lines = [*head(report, "text index-dev-2k"), "## Fits (calib-600)", "",
             "| arm | calib questions | index-dev-2k questions | " + " | ".join(TYPES) + " |",
             "|---|---|---|" + "---|" * len(TYPES)]
    q = report["questions"]
    lines += [f"| {arm} | {q['calib'][arm]} | {q['dev'][arm]} | " + " | ".join(fmt(fit[t]) for t in TYPES) + " |"
              for arm, fit in report["fits"].items()]
    for name, data in report["subsets"].items():
        lines += ["", f"## {name} ({data['n']} questions)", "",
                  f"Δ is {meta['set']} − {control(meta)} on the same questions, with a 95% paired-bootstrap CI.", ""]
        for grouping in ("overall", "type", "options"):
            lines += [*arm_table(grouping, grouping, data["arms"], data["vs_base"]), ""]
        lines += diagnostics(data)
    return "\n".join(lines) + "\n"


def image_rows(compare: dict) -> list[str]:
    lines = ["| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |", "|---" * 9 + "|"]
    for arm, c in compare["configs"].items():
        p = compare["paired"].get(arm)
        deltas = ([interval(p["delta_index"], p["ci"], ".2f"), f"{p['delta_ece']:+.4f}", f"{p['delta_nll']:+.4f}",
                   f"{p['agreement']:.4f}"] if p else ["baseline", "", "", ""])
        lines.append(f"| {arm} | {c['index']:.2f} | {deltas[0]} | {c['accuracy']:.3f} | {c['ece']:.4f} | {deltas[1]}"
                     f" | {c['nll']:.4f} | {deltas[2]} | {deltas[3]} |")
    return lines


def image_markdown(report: dict) -> str:
    lines = [*head(report, "image dev"), "## T (choice, from each arm's text calib-600 fit)", "",
             *(f"- {arm}: {fmt(T)}" for arm, T in report["T"].items())]
    for name, data in report["subsets"].items():
        lines += ["", f"## {name} ({data['n']} rows)", ""]
        if "compare" not in data:
            lines += ["No rows.", ""]
            continue
        lines += [f"vision_compare: `{data['compare']['dir']}/` (paired bootstrap over image groups).", "",
                  *image_rows(data["compare"]), "", *diagnostics(data)]
    return "\n".join(lines) + "\n"
