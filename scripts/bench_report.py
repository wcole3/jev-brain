"""Render bench records as markdown: latency tables, the JevBench board columns, provenance."""


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


def summary(records: list) -> str:
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
    chat = [r for r in ok if r["test"] == "chat"]
    if chat:
        lines += ["", "| chat prompt | load | TTFT ms | chunks/s |", "|---|---|---|---|"]
        lines += [f"| {r['prompt']} | {r['load']} | {r['ttft_ms']:.0f} | {r['chunks_per_s']:.1f} |" for r in chat]
    errors = [r for r in records if "error" in r]
    if errors:
        counts: dict[str, int] = {}
        for r in errors:
            counts[r["test"]] = counts.get(r["test"], 0) + 1
        lines += ["", "Errors: " + ", ".join(f"{test} {n}" for test, n in sorted(counts.items()))]
    return "\n".join(lines).lstrip("\n") + "\n"


def provenance(meta: dict) -> str:
    return "\n".join(["## Provenance", "", *(f"- {key}: {value}" for key, value in meta.items())]) + "\n"
