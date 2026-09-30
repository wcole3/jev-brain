"""The `spread` padding placement (DS-008): pad ids scattered evenly through the state, each at a word or line start."""

from bisect import bisect_left


def word_starts(tok, ids: list[int]) -> list[int]:
    """Inner positions i where ids[i] begins with whitespace or ids[i-1] ends a line, so a pad there splits no word."""
    unique = list(set(ids))
    text = dict(zip(unique, tok.batch_decode([[i] for i in unique]), strict=True))  # distinct ids only: fast on 30k
    return [i for i in range(1, len(ids)) if text[ids[i]][:1].isspace() or text[ids[i - 1]].endswith("\n")]


def nearest(starts: list[int], target: float) -> int:
    """Index of the start closest to target."""
    i = bisect_left(starts, target)
    if i == len(starts) or (i > 0 and target - starts[i - 1] <= starts[i] - target):
        return i - 1
    return i


def pad_points(n: int, pad: int, starts: list[int]) -> list[int]:
    """`pad` ascending insertion points evenly spaced over n ids, snapped to starts and distinct while starts last."""
    starts = starts or list(range(n + 1))  # no word starts: plain even spacing
    m = len(starts)
    if pad >= m:
        return [starts[k * m // pad] for k in range(pad)]
    points, j = [], -1
    for k in range(pad):
        # after the previous point, and leaving one start for each point still to come
        j = min(max(nearest(starts, (k + 0.5) * n / pad), j + 1), m - pad + k)
        points.append(starts[j])
    return points


def spread(tok, ids: list[int], pad: int, token: int) -> list[int]:
    """ids with `pad` copies of token inserted, spread evenly between words."""
    if not ids:
        return [token] * pad  # one run: the front, end and middle placements
    out, last = [], 0
    for point in pad_points(len(ids), pad, word_starts(tok, ids)):
        out += ids[last:point]
        out.append(token)
        last = point
    return out + ids[last:]
