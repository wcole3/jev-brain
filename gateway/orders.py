"""Show options in several orders and average the answers back to the caller's option positions."""

FORMS = (
    "identity, identity+reversed, cyclic:<k>, min_n:<k>+reversed (k >= 2), top_p:<tau>+reversed"
    " or reread_p:<tau> (0 < tau <= 1)"
)


def _gated(setting: str) -> tuple[str, float] | None:
    """(kind, value) for min_n:<k>+reversed, top_p:<tau>+reversed and reread_p:<tau>; None for other settings."""
    kind, _, rest = setting.partition(":")
    if kind not in ("min_n", "top_p", "reread_p"):
        return None
    value, plus, suffix = rest.partition("+")
    try:
        number = int(value) if kind == "min_n" else float(value)
    except ValueError:
        raise ValueError(f"bad option_orders {setting!r}: use {FORMS}") from None
    in_range = number >= 2 if kind == "min_n" else 0 < number <= 1
    if plus + suffix != ("" if kind == "reread_p" else "+reversed") or not in_range:
        raise ValueError(f"bad option_orders {setting!r}: use {FORMS}")
    return kind, number


def gate(setting: str) -> float | None:
    """The top_p or reread_p threshold tau, or None when the setting has no probability gate."""
    gated = _gated(setting)
    return gated[1] if gated and gated[0] in ("top_p", "reread_p") else None


def rereads(setting: str) -> bool:
    """reread_p: an unsure question is read again with the shared block read twice (decide.reread_pass)."""
    return setting.startswith("reread_p:")


def live_rows(option_counts: list[int], setting: str) -> int:
    """Rows the first pass reads: one per order of each question."""
    return sum(len(option_orders(n, setting)) for n in option_counts)


def option_orders(n: int, setting: str) -> list[list[int]]:
    """Permutations of range(n); perm[j] is the caller's option shown at position j."""
    identity = list(range(n))
    if setting == "identity":
        return [identity]
    if setting == "identity+reversed":
        return [identity, identity[::-1]]
    if setting.startswith("cyclic:"):
        k = int(setting.removeprefix("cyclic:"))
        if k < 1:
            raise ValueError("cyclic:<k> needs k >= 1")
        k = min(k, n)  # more shifts than options is pointless and stalls the loop
        shifts = sorted({round(i * n / k) % n for i in range(k)})
        return [identity[s:] + identity[:s] for s in shifts]
    gated = _gated(setting)
    if gated:
        kind, value = gated
        return [identity, identity[::-1]] if kind == "min_n" and n >= value else [identity]
    raise ValueError(f"unknown option_orders {setting!r}: use {FORMS}")


def average_back(probs: list[list[float]], perms: list[list[int]]) -> list[float]:
    total = [0.0] * len(perms[0])
    for p, perm in zip(probs, perms, strict=True):
        for shown, caller in enumerate(perm):
            total[caller] += p[shown]
    return [x / len(perms) for x in total]
