"""Render bench records as markdown: latency tables, the JevBench board columns, provenance."""

from scripts.metrics import ece_of

JEV_USD_PER_M_INPUT = 0.042


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


def qwk(gold: list[int], pred: list[int]) -> float | None:
    """Quadratic-weighted kappa over levels 0..max; None when chance disagreement is zero."""
    n = max(gold + pred) + 1
    scale = (n - 1) ** 2 or 1
    rows, cols = [0] * n, [0] * n
    observed = 0.0
    for g, p in zip(gold, pred):
        rows[g] += 1
        cols[p] += 1
        observed += (g - p) ** 2 / scale
    expected = sum(rows[i] * cols[j] * (i - j) ** 2 / scale for i in range(n) for j in range(n)) / max(len(gold), 1)
    return 1 - observed / expected if expected > 0 else None


def is_int(text) -> bool:
    return isinstance(text, str) and text.lstrip("-").isdigit()


def percent(rows: list[dict]) -> str:
    return f"{100 * sum(r['correct'] for r in rows) / len(rows):.1f}" if rows else "n/a"


def of_type(rows: list[dict], kind: str) -> list[dict]:
    return [r for r in rows if r["type"] == kind]


def jevbench_section(bench: list[dict]) -> list[str]:
    """One table row; errored rows count as wrong, as upstream does."""
    ordinal = [r for r in bench if r["eval_metric"] == "ordinal"]
    scored = [r for r in ordinal if is_int(r["pred"])]
    gold, pred = [int(r["gold"]) for r in scored], [int(r["pred"]) for r in scored]
    kappa = qwk(gold, pred) if scored else None
    mae = sum(abs(g - p) for g, p in zip(gold, pred)) / max(len(ordinal), 1)
    ms = [r["ms"] for r in bench if "error" not in r]
    p50, p95 = (f"{percentile(ms, 0.5):.0f}", f"{percentile(ms, 0.95):.0f}") if ms else ("n/a", "n/a")
    kappa_text = "n/a" if kappa is None else f"{kappa:.3f}"
    return [
        "| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |",
        "|---|---|---|---|---|---|---|---|---|",
        (
            f"| {len(bench)} | {len(bench) - len(ms)} | {percent(bench)} | {percent(of_type(bench, 'choice'))} "
            f"| {percent(of_type(bench, 'noul'))} | {kappa_text} | {mae:.3f} | {p50} | {p95} |"
        ),
    ]


def ece(rows: list[dict], bins: int = 15) -> float:
    """Expected calibration error: confidence is the probability of the predicted answer."""
    return ece_of([max(r["probabilities"].values()) for r in rows], [r["correct"] for r in rows], bins)


def brier(rows: list[dict]) -> float:
    """Mean squared distance from the one-hot gold; a gold key missing from the answer counts as p = 0."""
    total = 0.0
    for r in rows:
        p = r["probabilities"]
        total += sum((x - (k == r["gold"])) ** 2 for k, x in p.items()) + (r["gold"] not in p)
    return total / len(rows)


def calibration_section(bench: list[dict]) -> list[str]:
    """ECE, Brier and the noul yes/no bias; empty for runs recorded without probabilities."""
    rows = [r for r in bench if "error" not in r and "probabilities" in r]
    if not rows:
        return []
    noul = of_type(rows, "noul")
    said_yes = sum(r["pred"] == "yes" for r in noul)
    gold_yes = sum(r["gold"] == "yes" for r in noul)
    false_no = sum(r["gold"] == "yes" and r["pred"] == "no" for r in noul)
    false_yes = sum(r["gold"] == "no" and r["pred"] == "yes" for r in noul)

    def share(n: int) -> str:
        return f"{100 * n / len(noul):.1f}" if noul else "n/a"

    return [
        "| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |",
        "|---|---|---|---|---|---|",
        f"| {ece(rows):.3f} | {brier(rows):.3f} | {share(said_yes)} | {share(gold_yes)} | {false_no} | {false_yes} |",
    ]


def vllm_section(records: list, usage: dict[str, int]) -> list[str]:
    """One row per phase: Jev-style usage beside what vLLM prefilled (prompt minus prefix-cache hits)."""
    lines = [
        (
            "| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens "
            "| KV peak % | KV mean % | waiting peak | preemptions |"
        ),
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        prompt, cached = r["prompt_tokens"], r["cached_prompt_tokens"]
        cached_text = f"{100 * cached / prompt:.1f}" if prompt else "n/a"
        lines.append(
            f"| {r['phase']} | {usage.get(r['phase'], 0)} | {prompt} | {prompt - cached} | {cached_text} "
            f"| {r['generation_tokens']} | {100 * r['kv_peak']:.1f} | {100 * r['kv_mean']:.1f} "
            f"| {r['waiting_peak']:.0f} | {r['preemptions']} |"
        )
    return lines


def chat_section(chat: list[dict]) -> list[str]:
    """Chat TTFT and decode rate; runs before DS-004 counted streamed chunks, not usage tokens."""
    key, unit = ("tokens_per_s", "tokens/s") if "tokens_per_s" in chat[0] else ("chunks_per_s", "chunks/s")
    lines = [f"| chat prompt | load | TTFT ms | {unit} |", "|---|---|---|---|"]
    return lines + [f"| {r['prompt']} | {r['load']} | {r['ttft_ms']:.0f} | {r[key]:.1f} |" for r in chat]


def jev_cost_line(total_tokens: int) -> str:
    cost = total_tokens * JEV_USD_PER_M_INPUT / 1e6
    return f"Jev usage: {total_tokens} input tokens, about ${cost:.2f} at ${JEV_USD_PER_M_INPUT} per million."


def summary(records: list, jev: bool = False) -> str:
    ok = [r for r in records if "error" not in r]  # error records carry no ms/workers/ttft to tabulate
    lines: list[str] = []
    groups: dict[tuple, list] = {}
    for r in ok:
        if r["test"] in ("cold", "warm"):
            groups.setdefault((r["test"], r["state_tokens"], r["questions"], r["options"]), []).append(r["ms"])
    if groups:
        lines += ["| test | state tokens | questions | options | p50 ms | p95 ms |", "|---|---|---|---|---|---|"]
        for key, ms in groups.items():
            lines.append(f"| {' | '.join(map(str, key))} | {percentile(ms, 0.5):.0f} | {percentile(ms, 0.95):.0f} |")
    load = [r for r in ok if r["test"] == "throughput"]
    if load:
        lines += ["", "| workers | requests/s |", "|---|---|"]
        lines += [f"| {r['workers']} | {r['requests_per_s']:.1f} |" for r in load]
    bench = [r for r in records if r["test"] == "jevbench"]
    if bench:
        lines += ["", *jevbench_section(bench)]
        if calibration := calibration_section(bench):
            lines += ["", *calibration]
    chat = [r for r in ok if r["test"] == "chat"]
    if chat:
        lines += ["", *chat_section(chat)]
    usage: dict[str, int] = {}  # phase -> summed usage.input_tokens
    for r in ok:
        if "input_tokens" in r:
            usage[r["phase"]] = usage.get(r["phase"], 0) + r["input_tokens"]
    watched = [r for r in ok if r["test"] == "vllm"]
    if watched:
        lines += ["", *vllm_section(watched, usage)]
    if jev:
        lines += ["", jev_cost_line(sum(usage.values()))]
    errors = [r for r in records if "error" in r]
    if errors:
        counts: dict[str, int] = {}
        for r in errors:
            counts[r["test"]] = counts.get(r["test"], 0) + 1
        lines += ["", "Errors: " + ", ".join(f"{test} {n}" for test, n in sorted(counts.items()))]
    return "\n".join(lines).lstrip("\n") + "\n"


def provenance(meta: dict) -> str:
    return "\n".join(["## Provenance", "", *(f"- {key}: {value}" for key, value in meta.items())]) + "\n"
