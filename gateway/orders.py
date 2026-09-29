"""Show options in several orders and average the answers back to the caller's option positions."""


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
    raise ValueError(f"unknown option_orders {setting!r}: use identity, identity+reversed or cyclic:<k>")


def average_back(probs: list[list[float]], perms: list[list[int]]) -> list[float]:
    total = [0.0] * len(perms[0])
    for p, perm in zip(probs, perms, strict=True):
        for shown, caller in enumerate(perm):
            total[caller] += p[shown]
    return [x / len(perms) for x in total]
