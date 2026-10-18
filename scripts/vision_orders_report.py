"""orders.md for vision_orders.py: each arm's cost and fit beside its vision_compare index, then what was skipped."""

from scripts.bench_report import provenance
from scripts.vision_compare import fmt, interval


def fit_text(v) -> str:
    return f"α {v['alpha']:.3f}, β {v['beta']:+.3f}" if isinstance(v, dict) else f"T {v:.3f}"


def fit_cell(name: str, arm: dict) -> str:
    if "folds" in arm:
        return "; ".join(f"fold {k}: {fit_text(f['param'])}" + (" (text, tiny fold)" if f["fallback"] else "")
                         for k, f in arm["folds"].items())
    fit = arm["text_fit"]
    return fit_text(fit["param"]) + ("" if fit["from"] == name else f" (from {fit['from']})")


def arm_rows(report: dict, compare: dict) -> list[str]:
    lines = [("| arm | mean reads | share paying | extra suffix tokens | mean input tokens | index | Δ index [95% CI]"
              " | ECE | NLL | fit (choice) |"), "|---" * 10 + "|"]
    for name, arm in report["arms"].items():
        c, p = compare["configs"][name], compare["paired"].get(name)
        delta = interval(p["delta_index"], p["ci"], ".2f") if p else "baseline"
        lines.append(f"| {name} | {arm['mean_reads']:.3f} | {arm['share_paying']:.3f} | "
                     f"{arm['mean_extra_suffix_tokens']:.1f} | {fmt(c['mean_input_tokens'], '.0f')} | "
                     f"{fmt(c['index'])} | {delta} | {fmt(c['ece'], '.4f')} | {fmt(c['nll'], '.4f')} | "
                     f"{fit_cell(name, arm)} |")
    return lines


def markdown(report: dict, compare: dict) -> str:
    meta = {k: v for k, v in report["meta"].items() if k != "notes"}
    lines = [f"# {meta['profile']} R3 option-order policies: image dev", "", provenance(meta), "## Notes", "",
             *(f"- {n}" for n in report["meta"]["notes"]), "",
             f"## Arms ({compare['rows']} rows, Δ vs {compare['baseline']})", "",
             ("Index, CIs, ECE and NLL come from vision_compare (summary.md beside this file): paired bootstrap over"
              " image groups. Extra suffix tokens: the suffixes of every read after the first. Reports; the owner"
              " picks."), "", *arm_rows(report, compare), "", "## Skipped", ""]
    skipped = report["skipped"]
    lines += [f"- {name}: {why}" for name, why in skipped.items()] if skipped else ["None."]
    return "\n".join(lines) + "\n"
