"""How many Index rows a decision cap refuses: proxy-token buckets for all rows, real token counts near the cap."""

from collections import defaultdict

from gateway.decide import build_batch
from gateway.schema import RequestError, SystemOneRequest

BUCKETS = (8192, 16384, 32768, 65536, 131072, 262144)
NAMES = ("<8k", "8k-16k", "16k-32k", "32k-64k", "64k-128k", "128k-256k", ">=256k")


def bucket(tokens: int | None) -> str:
    if tokens is None:
        return "unknown"
    return NAMES[sum(tokens >= b for b in BUCKETS)]


def bucket_counts(meta: list[dict]) -> dict[str, dict[int, int]]:
    counts: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for m in meta:
        counts[bucket(m["meta"]["proxy_tokens"])][m["meta"]["catalog_id"]] += 1
    return {k: dict(v) for k, v in counts.items()}


async def real_lengths(engine, rows: list[dict]) -> dict[str, int]:
    """Longest prompt per row in the profile's default layout; tokenizer only, no vLLM."""
    out = {}
    for row in rows:
        try:
            request = SystemOneRequest.model_validate({"state": row["state"], "questions": row["questions"]})
            _, _, batch = await build_batch(engine, request)
        except RequestError:
            continue  # refused for another reason (option count); not a length question
        out[row["id"]] = batch.longest
    return out
