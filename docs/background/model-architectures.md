# Model architectures and what they mean for serving

This doc covers the three profiles in `profiles/*.env`: Qwen3.6-27B, Qwen3.8-27B and
Gemma 4 31B. It is based on each model's `config.json` at the pinned revision, the
vLLM v0.30.0 source, our startup logs and our bench results. Units: 1 KiB = 1,024 bytes,
1 MiB = 1,024 KiB, 1 GiB = 1,024 MiB.

## Short answer

- **The two Qwens are the same architecture.** Their configs differ only in the
  `transformers_version` field. Of their 64 layers, 48 are Gated DeltaNet (a
  recurrent layer with a fixed-size memory) and only 16 keep a per-token KV cache.
- **Qwen memory:** 64 KiB per token, plus a fixed ~147 MiB of recurrent state per
  request whatever its length.
- **Gemma memory:** 60 attention layers. Until the 1,024-token sliding window fills,
  every token costs 880 KiB, 14× Qwen. vLLM's accounting works out to ~505 KiB per
  token, which is why only ~50k KV tokens fit.
- **Why prefix caching on hybrid Qwen is 784-token granular:** vLLM makes one page of
  attention KV the same size as one saved recurrent state: 784 tokens × 4 KiB (one
  attention layer) = 3.06 MiB = one Gated DeltaNet layer's state. States are saved only at page ends, so a cache hit
  can only end on a multiple of 784. On v0.30.0, `--mamba-block-size` cannot change this.
- **Why `--max-num-seqs 256`:** vLLM refuses to start a hybrid model when
  `max_num_seqs` is larger than the whole block pool (638 or 665 blocks, depending on
  free memory at startup). The default of 1024 fails; 256 passes.
- **What this means for us:**
  - Qwen has memory to spare and is limited by compute, made worse by the coarse 784-token
    sharing ([prompt-sharing.md](prompt-sharing.md)).
  - Gemma is limited by KV memory. An fp8 KV cache (DS-005) should roughly double its
    capacity (estimate).

## 1. Three ways a layer remembers the past

Each layer of a language model keeps some memory of earlier tokens, so that the next
token doesn't have to reread the whole prompt. What that memory holds depends on the
layer type:

| Layer type | What it keeps | Memory as the prompt grows | Used by |
|---|---|---|---|
| **Full attention** | a key and a value vector (the "KV cache") for *every* earlier token | grows with every token | 16 Qwen layers, 10 Gemma layers |
| **Sliding-window attention** | K and V for only the last *W* tokens (W = 1,024 for Gemma) | grows until W tokens, then flat | 50 Gemma layers |
| **Linear attention: Gated DeltaNet** | one fixed-size matrix per head, updated in place for each token | flat from token 1 | 48 Qwen layers |

- **Gated DeltaNet** (Yang, Kautz & Hatamizadeh, ICLR 2025) is a linear-attention
  layer from the Mamba family. At each token it fades out old memory (the *gate*) and
  writes a targeted correction (the *delta rule*). Its memory is a d_k × d_v matrix per
  head, whatever the prompt length.
- **Hybrid model** here means one model that mixes layer types. In Qwen the pattern is
  16 × (3 Gated DeltaNet + 1 full attention); in Gemma it is 10 × (5 sliding + 1 full).
- **Recurrent state is not a KV cache.** It is overwritten at every token, so the state
  "after token 1,000" exists only if something saved a copy at that moment. That fact
  drives most of §4.

## 2. The three models

| | Qwen3.6-27B / Qwen3.8-27B | Gemma 4 31B |
|---|---|---|
| Parameters | 27B | 30.7B |
| Layers | 64: 48 Gated DeltaNet + 16 full attention | 60: 50 sliding window (W = 1,024) + 10 full attention |
| Attention KV heads × head dim | 4 × 256 (24 query heads) | sliding: 16 × 256; full: 4 × 512 |
| Gated DeltaNet | 16 QK heads, 48 V heads, head dim 128; state kept in fp32 (`mamba_ssm_dtype`) | none |
| Vision encoder | present; we serve with `--language-model-only` | ~550M params; kept for image chat (`LANGUAGE_MODEL_ONLY=0`) |
| Other | a multi-token-prediction head, unused (speculative decoding conflicts with label scoring, #42592) | `attention_k_eq_v` on the 10 full layers (see below) |

**Gemma's `attention_k_eq_v`:** the model card says the global layers use "unified Keys
and Values" to save memory. In vLLM v0.30.0 this saves weights only: the model code
loads the K weights into both the K and V slots ([gemma4.py][g4]). Keys and values then
get different norms (and RoPE only on keys), so the cache still stores both.

## 3. Memory per token and per request

The formula for one attention layer is 2 (K and V) × KV heads × head dim × 2 bytes
(bf16).

| | Arithmetic | Result |
|---|---|---|
| Qwen attention, per token | 2 × 4 × 256 × 2 B = 4 KiB per layer × 16 layers | **64 KiB** |
| Qwen Gated DeltaNet state, per layer | matrix: 48 × 128 × 128 × 4 B (fp32) = 3 MiB; plus conv: (16·128·2 + 48·128) channels × 3 × 2 B = 60 KiB | **3.06 MiB** (3,207,168 B) |
| Qwen state, per request | 3.06 MiB × 48 layers | **~147 MiB** |
| Gemma sliding window, per token | 2 × 16 × 256 × 2 B = 16 KiB × 50 layers | **800 KiB**, only for the last ~1k tokens |
| Gemma full attention, per token | 2 × 4 × 512 × 2 B = 8 KiB × 10 layers | **80 KiB**, for every token |

For one of our systemone rows (2,541 tokens, the largest row in the
[quick run](../results/qwen3.6-27b/2026-09-29T210957Z-quick/summary.md)):
- **Qwen:** 2,541 × 64 KiB + 147 MiB ≈ **306 MiB**.
- **Gemma:** the whole row is inside the window while it prefills, so 2,541 × 880 KiB
  ≈ **2.1 GiB**, about 7× Qwen.

## 4. How vLLM fits mixed layers into one pool

vLLM's **hybrid KV cache manager** keeps one memory pool, split into blocks that all
have the same *page size* (bytes). It groups layers of the same type into groups of
equal size (the smallest layer count, 16 for Qwen and 10 for Gemma). Every group draws
block ids from the same pool ([design doc][hkv], [kv_cache_utils.py][grp]).

**Qwen: 4 groups** (1 attention group + 3 Gated DeltaNet groups, 16 layers each).
- A saved recurrent state is a single 3.06 MiB page that doesn't split by token.
- So vLLM grows the attention block until one attention page is at least as big: 16 ×
  ⌈3,207,168 / (16 × 4,096)⌉ = **784 tokens**.
- It then pads the state page by the 4,096-byte difference (0.13%)
  ([interface.py `_align_hybrid_block_size`][align]).

```
one Gated DeltaNet state (one layer)    |██████████████████████████| 3,207,168 B
784 tokens of K+V (one attention layer) |██████████████████████████| 3,211,264 B
                                         = one page; one block = that page × 16 layers = 49 MiB
```

**"Align" mode** is what vLLM turns on for hybrid models when prefix caching is enabled
([config.py][cfg]):
- The recurrent state is saved only when a scheduler step ends on a multiple of the
  block size. Each running request holds at most two state pages per group: the previous
  step's state and the one being written ([MambaSpec][mspec]).
- A prefix-cache hit needs a saved state at the exact token where the hit ends. States
  exist only at multiples of 784, so hits are 784-token granular.
- In align mode vLLM also sets `mamba_block_size = block_size`
  ([interface.py L939–L940][align]), which overrides any `--mamba-block-size` you pass.

**Gemma: 6 groups** (5 sliding + 1 full, 10 layers each; our estimate from the grouping
rule).
- A full-attention page is half a sliding page (8 KiB vs 16 KiB per token), so vLLM
  doubles the full-attention block to keep pages equal: 32 tokens vs 16, if the backend
  default is 16 ([unify rule][unify]).
- With no recurrent layers, cache hits can land on any 32-token boundary (estimate). A
  sliding-window hit only needs the last 1,023 tokens still cached.

## 5. Reading vLLM's numbers

The startup line `GPU KV cache size: N tokens` does **not** count token slots. It is
blocks in the pool ÷ blocks one maximum-length request would need × `max_model_len`
([kv_cache_utils.py][cap]).

**Qwen3.6**: the startup log of 2026-09-28 (partly quoted in
[ds007-scheduling.md §0](../appendix/ds007-scheduling.md)) and `cache_config_info` in the
[quick run](../results/qwen3.6-27b/2026-09-29T210957Z-quick/summary.md). Qwen3.8 has the
identical config, so we expect the same, but haven't read its log.

```
Mamba cache mode is set to 'align' ... when prefix caching is enabled
Setting attention block size to 784 tokens to ensure that attention page size is >= mamba page size.
Padding mamba page size by 0.13% to ensure that mamba page size and attention page size are exactly equal.
GPU KV cache size: 453,973 tokens, Maximum concurrency for 32,768 tokens per request: 13.85x
kv lcm block sizes 784
```

- **Pool:** 665 blocks × 49 MiB = 31.8 GiB.
- **One 32,768-token request needs 48 blocks:** ⌈32,768 / 784⌉ = 42 attention blocks,
  plus 3 groups × 2 state pages = 6.
- **Check against the log:** 665 / 48 = 13.85×, and × 32,768 = **453,973**, as logged.

**Gemma 4 31B** (DS-011: 50,476 KV tokens with vision, 49,777 language-model-only). The
same formula, assuming vLLM's default 8,192-token prefill chunk:
- **Full group:** ⌈32,768 / 32⌉ = 1,024 blocks.
- **Each sliding group:** vLLM reserves the window plus every prefill chunk still in
  flight. With async scheduling that is 2 × 8,192 = 16,384 tokens
  ([SlidingWindowSpec][swspec], [vllm.py][inflight]).
  - That gives ⌈(1,023 + 16,384) / 16⌉ + 1 = 1,089 blocks per group, × 5 groups = 5,445.
- **Total:** 6,469 blocks × 2.5 MiB = 15.8 GiB for one 32k request, or **505 KiB per
  reported token**. That matches DS-011's ~505 KiB (≈ 80 + 800 × 17,407 / 32,768).
  - This is a real peak, not bookkeeping: while a long prompt prefills, its sliding
    layers hold up to ~17.4k tokens. Hence only 1.54× concurrency at 32k.
- **Pool:** the two token counts fit whole pools of exactly 9,965 and 9,827 blocks,
  ~24.3 and ~24.0 GiB (estimate). Dropping the vision tower freed no KV cache.

## 6. Why `--max-num-seqs 256` is required on hybrid Qwen

- **The check:** with Mamba-type layers and full CUDA graphs, v0.30.0 startup raises
  `max_num_seqs (…) exceeds available Mamba cache blocks (…)` when `max_num_seqs` is
  larger than the pool's block count, because each decode sequence in a captured graph
  needs one state block ([compilation.py][seqs]). The "Mamba cache blocks" in that
  message are the whole shared pool.
- **Our case:** at first bring-up the pool had 638 blocks at 0.90 GPU memory use (commit
  `723fe4e`); later startups got 665. vLLM's default of 1024 fails; 256 passes.
- **256 is a ceiling, not a reachable concurrency.** Each running request holds up to
  6 blocks of state, so 256 of them could need 1,536 blocks, more than the pool
  (estimate). In practice ~13 run at once, limited by compute
  ([prompt-sharing.md §5](prompt-sharing.md)).

## 7. What this means for us

**Prefix-sharing granularity.**
- **Qwen:** hits come in 784-token steps. A 2,064-token shared state reuses 1,568
  tokens, so each sibling row recomputes 496 ([prompt-sharing.md §2](prompt-sharing.md)).
- **Gemma:** hits should come in ~32-token steps (estimate). This may explain why Gemma,
  the bigger model, does 0.6 req/s on the 2,048×16×26 shape against Qwen's 0.4
  ([gemma](../results/gemma-4-31b/2026-09-28T000000Z/summary.md),
  [qwen3.6](../results/qwen3.6-27b/2026-09-28T000000Z/summary.md)). This is a hypothesis
  until a Gemma `--quick` run shows its cache hits.
- **DS-008 fixes, re-read against the v0.30.0 source** (none tested yet):
  - `--mamba-block-size 256/128` is overridden in align mode (§4), so it should do nothing.
  - Padding the shared part to a multiple of 784 still works.
  - A bf16 recurrent state (`--mamba-ssm-cache-dtype bfloat16`) would halve the state
    page and give 400-token blocks (formula estimate). Qwen's config asks for fp32, so
    it needs a fidelity check.

**Concurrency** (all estimates from §3–§5):

| | Qwen3.6 | Gemma 4 31B |
|---|---|---|
| Pool | 665 × 49 MiB = 31.8 GiB | ~24.3 GiB |
| One 2,541-token row, no sharing | 10 blocks (490 MiB): ~66 rows fit | ~2.1 GiB: ~11 rows fit |
| One 2,048×16×26 request, perfect sharing | not the limit (KV peak 12% measured) | 5,405 tokens × 880 KiB ≈ 4.5 GiB: ~5 fit |
| 32k-token chat requests (vLLM's figure) | 13.85× | 1.54× |

**Gemma is KV-bound, and there are two levers:**
- **fp8 KV cache (DS-005).** Weights take ~57 GiB (30.7B × 2 bytes); the pool is
  ~24 GiB. fp8 halves every attention page (880 → 440 KiB per token), so capacity should
  roughly double to ~100k reported tokens (estimate). It changes the logprobs, so it
  needs a decision-drift check and a refitted temperature.
- **Smaller prefill chunks.** The DS-007 `--max-num-batched-tokens` lever also shrinks
  the sliding-window reservation. At 2,048 it would be ~205 KiB per reported token,
  ~2.5× the capacity (formula estimate, untested).

**fp8 KV on Qwen coarsens sharing.** The attention page per token halves while the fp32
state doesn't, so the block would double to **1,568 tokens** (formula estimate). Qwen
isn't short of memory, so this only hurts, unless the state dtype shrinks too.

## Caveats

- **No live logs:** Qwen numbers come from the
  2026-09-28 startup excerpt (raw copy in `.firecrawl/ds007/`, git-ignored) and the quick
  run; Gemma's from DS-011 as recorded in DS-005 and `CLAUDE.md`.
- **Block counts vary by startup** with free GPU memory (638 vs 665 on Qwen).
- **Gemma assumptions:** the 16/32-token blocks and the 8,192-token chunk were not read
  from a Gemma log. The exact fit to both DS-011 token counts supports them.
- **v0.30.0 only:** align mode, grouping and sliding-window reservations change between
  vLLM releases.
- **Qwen state dtype:** fp32 comes from the config's `mamba_ssm_dtype`, which vLLM
  adopts by default. The logged 784 tokens and 0.13% pad confirm it (bf16 would give 400).
- **`prefix_match_unit`** (v0.30.0) makes hash matching finer, but "not how often
  states are stored", so on its own it doesn't beat 784.

## Sources

- **Our config:** [qwen3.6](../../profiles/qwen3.6-27b.env),
  [qwen3.8](../../profiles/qwen3.8-27b.env) and [gemma](../../profiles/gemma-4-31b.env)
  profiles, [compose.yaml](../../compose.yaml),
  [vllm-entrypoint.sh](../../docker/vllm-entrypoint.sh).
- **Model configs at the pinned revisions:**
  [Qwen3.6](https://huggingface.co/Qwen/Qwen3.6-27B/blob/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/config.json),
  [Qwen3.8](https://huggingface.co/Qwen/Qwen3.8-27B/blob/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0/config.json),
  [Gemma 4](https://huggingface.co/google/gemma-4-31B-it/blob/842da3794eaa0b77d5f08bae87a17459d91ff475/config.json).
- **Our results and research:** the
  [quick run](../results/qwen3.6-27b/2026-09-29T210957Z-quick/summary.md); full runs for
  [qwen3.6](../results/qwen3.6-27b/2026-09-28T000000Z/summary.md),
  [qwen3.8](../results/qwen3.8-27b/2026-09-28T000000Z/summary.md) and
  [gemma](../results/gemma-4-31b/2026-09-28T000000Z/summary.md);
  [ds007-scheduling.md](../appendix/ds007-scheduling.md);
  [prompt-sharing.md](prompt-sharing.md); [5-combined-server.md](../5-combined-server.md).
- **Model cards:** https://huggingface.co/Qwen/Qwen3.6-27B,
  https://huggingface.co/Qwen/Qwen3.8-27B, https://huggingface.co/google/gemma-4-31B-it
- **Gated DeltaNet paper:** https://arxiv.org/abs/2412.06464
- **vLLM design:** [hybrid KV cache manager][hkv];
  [Hybrid models as first-class citizens in vLLM](https://pytorch.org/blog/hybrid-models-as-first-class-citizens-in-vllm/)
  (page alignment and padding).
- **vLLM v0.30.0 source:** [`_align_hybrid_block_size`][align],
  [`MambaModelConfig`][cfg], [`MambaSpec`][mspec], [`SlidingWindowSpec`][swspec],
  [capacity][cap], [grouping][grp], [page unify][unify],
  [`max_in_flight_tokens`][inflight], [`max_num_seqs` check][seqs] (issue #34094),
  [Gated DeltaNet state shape][gdn], [gemma4.py][g4]. Raw copies are in
  `.firecrawl/background/model-architectures/`.

[hkv]: https://docs.vllm.ai/en/latest/design/hybrid_kv_cache_manager.html
[align]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/platforms/interface.py#L778-L962
[cfg]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/model_executor/models/config.py#L611-L656
[mspec]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/kv_cache_interface.py#L993-L1057
[swspec]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/kv_cache_interface.py#L807-L852
[cap]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/core/kv_cache_utils.py#L1067-L1100
[grp]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/core/kv_cache_utils.py#L1435-L1575
[unify]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/core/kv_cache_utils.py#L1365-L1427
[inflight]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/config/vllm.py#L589-L610
[seqs]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/config/compilation.py#L1520-L1543
[gdn]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/model_executor/layers/mamba/mamba_utils.py#L274-L295
[g4]: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/model_executor/models/gemma4.py#L433-L446
