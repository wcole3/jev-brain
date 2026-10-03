# Prompt sharing on qwen3.6-27b

Based on the `--quick` bench run of 2026-09-29
([summary](../results/archive/qwen3.6-27b/2026-09-29T210957Z-quick/summary.md)), plus a replay of the same requests
to check the explanation.

## Short answer

- **Sharing works, but only in 784-token steps.** A request whose state is 2,064 tokens
  long reuses 1,568 of them (two whole blocks). Each of the other 15 question rows
  recomputes the remaining 496. Overall, vLLM computes **2.4×** the tokens it would
  need if the state were reused in full.
- **That waste directly limits throughput.** The GPU is saturated with prefill at about
  6,000 computed tokens per second, whether 1 or 16 clients are sending. So requests per
  second = 6,000 ÷ computed tokens per request, and today that is 0.42.
- **KV memory is not the limit.** At most 12% of the KV cache is ever in use and nothing
  is preempted. Requests wait for compute, not memory.
- **Two DS-008 fixes both reach ~1.05× in simulation:** finer cache blocks, or padding
  the shared state to a block boundary. That is about 2.5× throughput on this request
  shape (an estimate).

## 1. How one systemone request becomes vLLM work

The gateway turns each question into its own prompt, a "row". Every row starts with the
same shared part (chat header plus `Context:` and the state), then adds its own question,
options and answer slot:

```
row 1   [ shared: chat header + state, 2,064 tokens ][ own question + 26 options: 477 ]
row 2   [ shared: chat header + state, 2,064 tokens ][ own score question: 61 ]
row 3   [ shared: chat header + state, 2,064 tokens ][ own noul question: 34 ]
...     16 rows in total, one per question
```

A real 2,048-token-state, 16-question, 26-option request from the bench:

| | Tokens |
|---|---|
| Shared part | 2,064 |
| All 16 own parts together | 3,341 |
| Every row in full (what vLLM counts as "prompt tokens") | 36,365 |
| Shared part once + own parts (Jev-style `usage.input_tokens`) | 5,405 |

`usage.input_tokens` is the least work possible: the state once, each question once.

- **Getting the shared part cached:** the gateway sends row 1 alone first when the shared
  part is 512 tokens or more (`WARM_MIN_PREFIX_TOKENS`).
- **Reusing it:** the other 15 rows then go together, so vLLM can take the shared part
  from its prefix cache instead of computing it again.

## 2. Why only 1,568 of the 2,064 shared tokens are reused

Qwen3.6 is a hybrid model: 48 of its 64 layers are recurrent (Gated DeltaNet,
Mamba-style), and only 16 are attention.

- **Why blocks:** a recurrent layer keeps a running state instead of per-token keys and
  values, and vLLM can only save that state at chunk ends. In its "align" mode it saves
  one every **784 tokens**, so a cache hit must end on a multiple of 784.
- **What that means here:** 2,064 = 2 × 784 + 496. Rows 2–16 reuse 1,568 tokens and
  recompute the last 496 shared tokens before reaching their own question.

```
shared part   |------ block 1: 784 ------|------ block 2: 784 ------|--- 496, never a full block ---|
row 1         computed in full; fills blocks 1 and 2 of the cache
rows 2..16    [ cached ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ][ recomputed 496 ][ own part ]
```

The same request again:

| | Tokens | |
|---|---|---|
| Prompt tokens (every row in full) | 36,365 | 6.7× usage |
| Served from the prefix cache | 23,520 | 15 rows × 1,568 |
| Computed | 12,845 | **2.4× usage** |
| … of which shared state recomputed | 7,440 | 15 rows × 496, **58% of all computed tokens** |
| … of which necessary work | 5,405 | = usage |

With perfect reuse, computed tokens would equal usage exactly.

## 3. What the run measured

| Phase | What it sends | Usage | vLLM prompt | Cached | Computed | **Computed ÷ usage** | KV peak | Queue peak |
|---|---|---|---|---|---|---|---|---|
| cold | Mix of 256/2,048-token states, 1/16 questions, 2/26 options, each unique | 56,233 | 266,008 | 51.3% | 129,592 | **2.30** | 9.2% | 2 |
| warm | One 2,048×16×26 request, sent 3 times | 16,185 | 108,615 | 75.1% | 27,079 | **1.67** | 12.2% | 2 |
| throughput x1 | 2,048×16×26, 1 client | 27,031 | 181,921 | 60.3% | 72,161 | **2.67** | 8.9% | 2 |
| throughput x4 | same, 4 clients | 37,844 | 254,699 | 60.3% | 101,035 | **2.67** | 10.2% | 47 |
| throughput x16 | same, 16 clients | 86,508 | 582,288 | 60.3% | 231,056 | **2.67** | 10.2% | 213 |
| jevbench | 50 single-question rows | 10,129 | 10,129 | 0% | 10,129 | **1.00** | ~0% | 0 |

How to read each phase:

- **cold:** a mix.
  - 1-question requests have nothing to share.
  - 256-token states can't share either: the shared part is shorter than one 784-token
    block, and it is also below the 512-token warm-up threshold, so all rows go together.
  - Only the 2,048-token multi-question requests save anything.
- **warm:** the same request three times. The second and third copies also reuse whole
  blocks of their own identical rows, so the ratio falls to 1.67. This is cross-request
  reuse; real traffic rarely repeats a request exactly.
- **throughput:** 2.67×, slightly worse than the 2.38× of a single request replayed
  alone. With several requests in flight, some block hits are lost. This matches vLLM
  issue #52897, where chunk boundaries fragment under load.
- **jevbench:** one question per request, so there is nothing to share, and computed
  equals usage. This is the control row.

## 4. Checking the explanation: a replay

I rebuilt the cold and warm requests the bench sent (same random seed, same gateway
code) and counted what a 784-token block cache would reuse. The rules:
- only whole blocks are reused;
- the rows sent together can't reuse each other;
- at least the last token is always computed.

| Phase | Predicted prompt | Measured prompt | Predicted cached | Measured cached |
|---|---|---|---|---|
| cold | 266,026 | 266,008 | 141,120 | 136,416 |
| warm | 108,615 | 108,615 | 83,104 | 81,536 |

- **Prompt tokens:** match to within 18 tokens (the random nonce text differs in length).
- **Cached tokens:** vLLM reused 2–6 fewer blocks than the ideal; the same load effect
  as above.

The 784-token block rule explains the measurements.

## 5. What it costs

| Phase | Computed tokens/s | Requests/s |
|---|---|---|
| throughput x1 | 5,758 | 0.40 |
| throughput x4 | 6,093 | 0.42 |
| throughput x16 | 6,066 | 0.42 |

- **The GPU is already saturated with one client.** Adding clients only lengthens the
  queue (213 waiting at x16, ~13 running) without adding throughput.
- **The arithmetic closes:** 6,066 tokens/s ÷ 14,441 computed tokens per request =
  0.42 requests/s, exactly what was measured.
- **KV is not the constraint:** 665 blocks × 784 tokens are available, at most 12.2%
  was used, and there were no preemptions.
- **So computed tokens per request is the number that sets throughput.** Cutting it from
  ~14.4k to ~5.7k would give roughly 1 request/s on this shape, about 2.5× today. For
  latency, today's 2,467 ms cold p50 for this shape should roughly halve, since most of
  the batch step's work is the recomputed state. Both are estimates from this model, not
  measurements.

## 6. Fixes to test (DS-008), simulated

Replaying the same 2,048×16×26 request under each option:

| Option | Changes the prompt? | Computed ÷ usage | Cold mix ÷ usage | Open questions |
|---|---|---|---|---|
| Today: 784-token blocks | – | 2.38 | 2.22 | |
| `--mamba-block-size 256` (hypothetical) | No | 1.05 | 1.45 | **Not available in vLLM 0.30** (see below) |
| `--mamba-block-size 128` (hypothetical) | No | 1.05 | 1.45 | Same |
| Pad the shared part to a multiple of 784 | Yes (+288 tokens here) | 1.05 | 1.17 | Answers may shift, so it needs a fidelity check and its own fitted temperature |

Notes:

- **Why finer blocks aren't an option today.** In vLLM 0.30's source
  (`platforms/interface.py`, `_align_hybrid_block_size`), the attention block grows until one
  attention page holds one recurrent-state page: 784 tokens here. In align mode (the
  default with prefix caching) it then overwrites `mamba_block_size` with that block size,
  so `--mamba-block-size` has no effect. DS-008 confirms this on the GPU; the rows above
  show what a future vLLM with finer blocks could gain. More in
  [model-architectures.md](model-architectures.md).
- **Finer blocks leave small states unshared.** The cold mix stays at 1.45 because
  256-token states still go without a warm-up row (below the 512-token threshold). With
  finer blocks it would be worth lowering `WARM_MIN_PREFIX_TOKENS`. The cost is one extra
  round trip per request.
- **Padding only pays with several questions.** For a 1-question request the pad is pure
  extra work. Pad only when (rows − 1) × (tokens saved per row) exceeds the pad length.
- **Adopting either fix** needs the fidelity checks already planned in
  [ds007-scheduling.md §6a](../appendix/ds007-scheduling.md). This table is now the cost
  side: aim for computed ÷ usage of ~1.0–1.1 in the throughput phases.

**Outcome (DS-008, 2026-09-30):** front padding is adopted on both Qwen profiles. Measured:
computed ÷ usage 2.67 → 1.05, 0.5 → 1.1 req/s, cold p50 2,389 → 982 ms, with 1.4% of JevBench
answers changed in a worst-case test. `--mamba-block-size` was confirmed to be ignored. Full results:
[experiments/ds-008](../results/archive/experiments/ds-008/README.md).

### What front, middle and end padding look like

The pad is a run of the model's single newline token, inserted as token ids so it can't
merge with its neighbours. It always goes somewhere in the **shared part**, so every row
still starts with the same (now longer) prefix. The placement decides *where* in that part.

Below is row 1 of a real two-question request, decoded from the ids `build_rows` makes
for qwen3.6 ([`prompts.py`](../../gateway/prompts.py), `pad_site`). To keep it readable, the
block here is 32 tokens instead of 784. The shared part is 23 tokens, so every placement
adds **9 pad tokens** to reach 32, shown as `«9 newlines»`. Everything after the shared part
(question, options, answer slot) is unchanged and is where row 2 starts to differ.

**No padding (23 shared tokens):**

```
<|im_start|>user
Context:
Hi, my Stripe integration keeps failing and I'm losing sales. Please help ASAP.

Question: Which team should handle this
Options:
(A) billing: Payment or subscription issues
(B) technical: Bugs or integration problems<|im_end|>
<|im_start|>assistant
<think>

</think>

Answer: (
```

**Front (adopted):** right after the chat header, before `Context:`, as far from the
question as possible.

```
<|im_start|>user
«9 newlines»Context:
Hi, my Stripe integration keeps failing and I'm losing sales. Please help ASAP.

Question: Which team should handle this
...
```

**Middle:** between the `Context:` label and the state text. The label and the state are
encoded separately here, so the tokens at that join can differ from an unpadded prompt.

```
<|im_start|>user
Context:
«9 newlines»Hi, my Stripe integration keeps failing and I'm losing sales. Please help ASAP.

Question: Which team should handle this
...
```

**End:** after the state, right before the first question: the placement closest to what
the model is asked.

```
<|im_start|>user
Context:
Hi, my Stripe integration keeps failing and I'm losing sales. Please help ASAP.«9 newlines»

Question: Which team should handle this
...
```

At the real block size, a 2,064-token shared part gets 288 pad tokens (up to 2,352 = 3 × 784).
All three placements cost the same; they differ only in how much they move answers.
Front moved the fewest (1.4% of JevBench answers in a worst-case test, vs 2.3% for end and
3.0% for middle), plausibly because a run of blank lines right after the header reads as
harmless whitespace, while one next to the question or inside the context sits where the
model is looking. A fourth idea, spreading the pads through the state, moved 8.6% and was
dropped.

## 7. The warm-up call, per model

A systemone request becomes N rows that share a long prefix. For vLLM to compute that prefix
only once, some row has to compute it first and leave it in the prefix cache before the others
look it up. That is what the **warm-up** does: the gateway sends one call first and the rest
after. Whether that helps depends entirely on how the model's cache decides what is reusable.

```
WARM_UP=row   request ──► call 1: row 1 alone ──► call 2: rows 2..N together
WARM_UP=off   request ──► call 1: rows 1..N together
```

It is set per profile ([`readout.py`](../../gateway/readout.py), `WARM_UP` and
`WARM_MIN_PREFIX_TOKENS`); the row warm-up only happens when there is more than one row and
the shared prefix is at least `WARM_MIN_PREFIX_TOKENS` long.

| Profile | Setting | Why |
|---|---|---|
| qwen3.6 / qwen3.8 | `WARM_UP=row`, threshold 784, front padding | Recurrent layers need a saved state at the prefix end |
| gemma-4-31b | `WARM_UP=off` plus vLLM `--prefix-cache-retention-interval 32` | Sliding-window blocks must be hashed densely; then no warm-up is fastest |

**Qwen (hybrid, recurrent layers).** vLLM saves a recurrent-state checkpoint only at the last
784-token boundary of a prefill. Row 1 is the padded prefix plus its question (~480 tokens,
less than one block), so its last boundary is exactly the end of the padded prefix: every later
row resumes from there. Rows sent together without a warm-up can't reuse each other, because
no one has saved that checkpoint yet. Warming with the *prefix alone* was tried and did worse
(1.47× instead of 1.05×; [DS-008](../results/archive/experiments/ds-008/README.md)).

**Gemma (sliding-window layers).** 50 of its 60 layers only look back 1,024 tokens, and by
default vLLM 0.30 hashes (makes reusable) their cache blocks only at the end of each prompt.
A row-1 warm-up therefore leaves reusable blocks around row 1's *end*, past the shared prefix,
where no sibling can use them. Measured directly: after the row-1 warm-up, row 2 reused **0**
tokens. With `--prefix-cache-retention-interval 32`, vLLM hashes those blocks along the whole
prompt, and blocks are registered as soon as they are allocated, so rows sent together in one
call can already share the prefix. The extra serial warm-up call then only adds latency:

| Gemma, `--quick`, 16 clients | Computed ÷ usage | Req/s | Cold p50 2048×16×26 |
|---|---|---|---|
| Row warm-up, default vLLM (before) | 1.71 | 0.5 | 1,660 ms |
| Prefix-only warm-up | 1.55 | 0.5 | 1,305 ms |
| Retention 32 + prefix / row warm-up | 1.36 / 1.38 | 0.6 | ~1,350 ms |
| **Retention 32, no warm-up (adopted)** | **1.00** | **0.8** | **1,286 ms** |

**Rule of thumb for a new model:** measure, don't guess. Send one multi-question request
straight to vLLM and read `vllm:prompt_tokens_cached_total` around each call: does row 2 reuse
the prefix after the warm-up call, and do rows sent together reuse each other? Details and the
vLLM source references: [DS-015](../results/archive/experiments/ds-015/README.md).

## Caveats

- **Server-wide counters:** vLLM's counters count all traffic, so these numbers assume
  the stack was otherwise idle (it was).
- **Sampling:** gauges are sampled every 0.25 s, so a short spike can be missed.
- **Small run:** `--quick` sends few requests (2 repeats per cell). The ratios are
  consistent across phases, but a full run gives firmer numbers.
- **Estimates:** the throughput and latency gains in §5 assume the prefill rate stays
  ~6k tokens/s.
- **Qwen only:** everything here is specific to the hybrid Qwen models. Gemma 4 has no
  recurrent layers and may cache at much finer granularity. A gemma `--quick` run would
  show it.

## Next steps

1. Run gemma-4-31b `--quick` for a non-hybrid comparison.
2. DS-008: confirm `--mamba-block-size` is ignored, then test padding. Judge it by
   computed ÷ usage and throughput here, and by the fidelity checks.
3. With padding, also check whether lowering `WARM_MIN_PREFIX_TOKENS` helps the cold mix.
