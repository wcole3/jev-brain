"""Decision Index 0.2.1 board entries we compare against (snapshot 2026-09-27, docs/3-leaderboard.md)."""

BOARD = {
    "jev": {"name": "Jev (hosted API, latency over HTTPS)", "index": 57.9, "ece": 0.074, "median_ms": 524.1},
    "decider-chat-qwen3.6-27b": {"name": "Decider chat · Qwen3.6-27B", "index": 51.35, "ece": 0.0209, "median_ms": 83.6},
    "decider-chat-gemma4-31b": {"name": "Decider chat · Gemma-4-31B", "index": 57.33, "ece": 0.0471, "median_ms": 108.5},
    "simple-jev-qwen3.8-27b": {"name": "simple-jev · Qwen3.8-27B", "index": 55.7, "ece": 0.113, "median_ms": 373.0},
    "reflex-27b": {"name": "reflex 27B", "index": 52.2, "ece": 0.024, "median_ms": 108.0},
    "jevfire-uncapped": {"name": "Jevfire (Qwen3.8-27B-FP8)", "index": 49.4, "ece": 0.0521, "median_ms": 89.6},
}
MATCHES = {
    "qwen3.6-27b": ["decider-chat-qwen3.6-27b"],
    "gemma-4-31b": ["decider-chat-gemma4-31b"],
    "qwen3.8-27b": ["simple-jev-qwen3.8-27b", "reflex-27b", "jevfire-uncapped"],
}
PARITY = {"qwen3.6-27b": ("decider-chat-qwen3.6-27b", 1.5)}  # same prompt token for token as decider


def fmt(x, digits: int) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def comparison(profile: str, ours: dict, complete: bool = True) -> list[str]:
    """Ours next to the matching entries and Jev. ECE and latency are measured differently; see the notes."""
    lines = ["| entry | Index | ECE | median ms | coverage |", "|---|---|---|---|---|"]
    lines.append(f"| **ours: {profile}** | {fmt(ours['index'], 2)} | {fmt(ours['ece'], 3)} "
                 f"| {fmt(ours['median_ms'], 1)} | {fmt(ours['coverage'], 3)} |")
    for key in [*MATCHES[profile], "jev"]:
        e = BOARD[key]
        lines.append(f"| {e['name']} | {e['index']:.2f} | {e['ece']:.3f} | {e['median_ms']:.1f} | board |")
    if profile in PARITY:
        key, tolerance = PARITY[profile]
        gap = ours["index"] - BOARD[key]["index"]
        verdict = "pass" if abs(gap) <= tolerance else "MISS: file a ticket before M2"
        if not complete:
            verdict = f"not judged (run incomplete: {ours['completed']} rows)"
        lines += ["", f"Parity gate vs {BOARD[key]['name']}: {gap:+.2f} (±{tolerance}) → {verdict}"]
    return lines
