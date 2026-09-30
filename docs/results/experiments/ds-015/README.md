# DS-015: Gemma reused its shared prefix only partly

gemma-4-31b, bf16, vLLM 0.30.0, 2026-09-30. Background:
[prompt-sharing.md §7](../../../background/prompt-sharing.md) and
[model-architectures.md](../../../background/model-architectures.md).

## Outcome

**Adopted:** vLLM `--prefix-cache-retention-interval 32` (via `EXTRA_ARGS` in the gemma
profile) and **no warm-up call** (`WARM_UP=off`). Padding stays off for Gemma.

| Gemma, 16 clients | Before | After |
|---|---|---|
| Computed ÷ usage | 1.71 | **1.00** |
| Throughput | 0.5 req/s | **0.8 req/s** |
| Cold p50, 2,048-token state × 16 questions × 26 options | 1,660 ms | **1,377 ms** (full run) |
| JevBench | 87.2% | 87.0% (9 of 1,682 answers changed, within noise; see below) |

Full run: [gemma-4-31b/2026-09-30T143638Z](../../gemma-4-31b/2026-09-30T143638Z/summary.md).

## Why Gemma missed

Source reading (vLLM v0.30.0; raw notes in the git-ignored `.firecrawl/ds015/`):

- Gemma 4's 50 sliding-window layers (window 1,024) and 10 full-attention layers share one
  block pool: 16-token blocks for sliding window, 32 for full attention; hits are aligned to 32.
- A later request can reuse a sliding-window prefix only if the 64 blocks (1,024 tokens)
  ending at the hit point are cached **and hashed**.
- With the default `prefix_cache_retention_interval = 0`, sliding-window blocks are hashed
  only around a request's **own last position** (plus a junction pinned after a miss).
- So a row-1 warm-up caches its window at row 1's end, ~480 tokens past the shared prefix, and
  the first sibling misses the whole state. The state was prefilled about twice per request.

Measured directly, with rows sent straight to vLLM (`probe.py` in `.cache/ds015/`):

| Sequence (2,066-token shared prefix) | Cached per sibling row |
|---|---|
| Row 1 alone, then row 2 alone | 0 |
| …then rows 3–16 together | 2,066 |
| All 16 rows together, no warm-up | 1,808 |
| Shared prefix alone, then row 2 | 2,048 |

## Runs (`--quick`)

| Setup | Computed ÷ usage ×16 | Cached ×16 | Req/s ×1 / ×16 | Cold p50 2048×16×26 |
|---|---|---|---|---|
| Row warm-up, default vLLM (before) | 1.71 | 75% | 0.6 / 0.5 | 1,660 ms |
| Prefix-only warm-up | 1.55 | 78% | 0.8 / 0.5 | 1,305 ms |
| Retention 32 + prefix warm-up | 1.36 | 81% | 0.8 / 0.6 | 1,320 ms |
| Retention 32 + row warm-up | 1.38 | 79% | 0.7 / 0.6 | 1,388 ms |
| **Retention 32, no warm-up** | **1.00** | 85% | 0.8 / 0.8 | 1,286 ms |

With retention 32, vLLM hashes sliding-window blocks all along each prompt and registers them
when allocated, so rows sent together already share the prefix; a warm-up call only adds a
serial round trip. Padding cannot help Gemma: its hits are already 32-token aligned.

## Fidelity check

The full run changed 9 JevBench answers (0.5%), a few with a large baseline gap, which is
normally a bug signal. Tested directly:

- The same prompt computed fresh and then served from cache gave the same answer (probability
  differences ≤ 0.08).
- On a freshly restarted vLLM with the **default** cache (no retention flag), the flipped rows
  already gave the "new" answers (e.g. banking77:37 → `card_delivery_estimate` 0.94), and some
  moved between two identical asks (invoice 1168: `yes` 0.50, then `no` 0.73).

So the flips come from Gemma being very unstable on a handful of near-saturated rows, not from
the retention flag. See [determinism.md](../../../background/determinism.md).
