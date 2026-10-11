# DS-004: MTP speculative decoding alongside systemone

Can chat run MTP (multi-token prediction) speculative decoding while `/v1/systemone` stays
exact, and what does it cost? Measured 2026-10-06/07 on one RTX PRO 6000 with vLLM
v0.30.0, for Qwen3.6-27B and Qwen3.8-27B. Gemma 4 31B was dropped after the offline check
(below). This report gives the numbers; the decision per profile is the owner's.

## Short answer

- **Stock vLLM v0.30.0 cannot do it.** With MTP on, any step that holds a drafting request
  goes through the rejection sampler, which drops `logprob_token_ids`. Decision rows then
  fail with HTTP 500 (`IndexError`). Under steady chat load that was **1,682 of 1,682** rows.
- **A ~15-line patch to the rejection sampler fixes it.** It reuses the normal sampler's
  label-id path. With the patch: 0 errors in every run, and the patched path demonstrably
  ran (about 2,000 rejection-sampler steps with label-id rows per loaded JevBench run).
- **Hybrid Qwen also needs two settings changed.** MTP makes the KV block 800 tokens
  instead of 784:
  - the prefill cap and budget must move from 784 / 2352 to **800 / 2400**, or prompts of
    784 tokens and up take an extra engine step (+~100 ms);
  - the gateway must pad shared prefixes to **800**, or multi-question decisions lose
    prefix reuse (up to 6× slower, throughput 1.01 → 0.35 req/s). That needs a new
    calibration stamp (DS-029).
- **With the patch and both settings:** chat decodes **2.0× faster** under decision load
  on Qwen3.6 and **1.5×** on Qwen3.8. Decisions cost +6 to +33 ms idle and +60 to +164 ms
  under chat load. Accuracy is unchanged. Probability drift is within what a plain server
  restart produces (Qwen3.6); Qwen3.8 has no restart measurement.
- **A top-K readout is not a substitute.** Offline, reading `logprobs=K` instead of label
  ids moved Gemma's calibrated probabilities by up to 0.6-0.8; Qwen's by up to 0.07-0.12 at
  K = 64.

## Per profile

"Stock" is the shipped profile with MTP off. "MTP" is the patched rejection sampler, 3
draft tokens, cap / budget 800 / 2400, `disable_eagle_block_drop`, gateway padding 800.
Idle rows come from a full `bench.py --chat`; "under chat load" is JevBench with 4
streaming chats running.

| | Qwen3.6 stock | Qwen3.6 MTP | Qwen3.8 stock | Qwen3.8 MTP |
|---|---|---|---|---|
| JevBench accuracy | 89.2% | 89.1% | 89.7% | 89.7% |
| Max \|Δp\| vs stock, idle (flips; largest baseline gap) | — | 0.080 (3; 0.031) | — | 0.059 (7; 0.057) |
| Max \|Δp\| vs stock, under chat load | — | 0.105¹ (6; 0.049) | — | 0.059 (6; 0.065) |
| Stock restart vs stock (noise floor) | 0.079 (3; 0.025) | | not measured | |
| Decision p50 idle, < 784 / 784-1,568 tokens | 103 / 259 ms | 122 / 292 ms | 104 / 259 ms | 110 / 269 ms |
| Decision p50 under chat load, same bands | 322 / 607 ms | 382 / 771 ms² | 296 / 566 ms | 379 / 638 ms |
| Warm sweep p50 (16 questions, 2,048-token shared state) | 781 ms | 835 ms | 784 ms | 772 ms |
| Throughput, 16 workers | 1.01 req/s | 0.97 | 1.02 | 0.98 |
| Cached prompt tokens (throughput) | 86.1% | 86.2% | 86.1% | 86.2% |
| Chat alone, short / long prompt | 27.0 / 26.7 tok/s | 78.4 / 62.9 | 27.5 / 27.3 | 63.7 / 45.0 |
| Chat under load, p50 per chat | 18.5 tok/s | **37.8** (2.04×) | 19.6 | **29.3** (1.49×) |
| Chat TTFT under load, p50 | 269 ms | 355 ms | 263 ms | 345 ms |
| Draft acceptance, story / bench prompts | — | 50.0% / 73.7% | — | 30.6% / 44.8% |
| KV cache | 650 × 784 tokens | 571 × 800 (−13%) | 650 × 784 | 571 × 800 (−13%) |

1. One score row (`invoice_processing:1370`) takes a different discrete value on each
   server start; it is identical within an instance, load or idle. Without it the max is
   0.064.
2. Measured with gateway padding 784; JevBench rows are single questions, so padding does
   not apply to them.

No flip in any comparison had a baseline top-two gap above 0.10. Drift across restarts
(0.079 on stock Qwen3.6) is much larger than within one instance (0.027 under load), so
every MTP comparison here, being across restarts, is judged against the restart figure.
That noise is measured in [DS-028](../ds-028/README.md): ~0.03 p99, up to 0.15 on rare rows, MTP on or off.

## What each finding rests on

| Finding | Where |
|---|---|
| Top-K readout error, all three models, K = 20/32/64 | [topk-sim.md](topk-sim.md) |
| Stock failure (arm E), patch arms, block drop off (D′) | [Qwen3.6 results §1](qwen3.6-27b/results.md) |
| Why 784-1,568-token prompts slowed: 784 + 16 prefill steps; restart noise | [Qwen3.6 results §2](qwen3.6-27b/results.md) |
| Realigned profile, padding 784 vs 800, full benches | [Qwen3.6 results §3](qwen3.6-27b/results.md) |
| Qwen3.8 with the realigned profile | [Qwen3.8 results](qwen3.8-27b/results.md) |
| Every `compare_runs.py` output | [Qwen3.6](qwen3.6-27b/comparisons.md), [Qwen3.8](qwen3.8-27b/comparisons.md) |
| How the arms were run | [runbook.md](runbook.md) |
| The patch, written up for vLLM (draft, not posted) | [upstream-pr.md](upstream-pr.md) |
| How it works | [KV caches](../../background/kv-cache.md), [speculative decoding and Mamba](../../background/speculative-decoding-and-mamba.md) |

## What shipping MTP on a Qwen profile takes

Shipped as the Qwen default on 2026-10-07 (`profiles/qwen3.*-27b.env`). The spike code
(`docker/spike/`, `compose.spike*.yaml`, `profiles/spike/`, `scripts/spike_*.py`) named in
the results docs was removed then; it is not in the repo.

- The patched rejection sampler (`docker/vllm/`), mounted over the pinned image in
  `compose.yaml` until a vLLM release has the fix.
- `--speculative-config {"method":"mtp","num_speculative_tokens":3,"disable_eagle_block_drop":true}`,
  `--long-prefill-token-threshold 800 --max-num-batched-tokens 2400` (budget − cap = 1,600,
  above the 800-token block, per DS-025).
- Gateway `PREFIX_BLOCK=800` and `WARM_MIN_PREFIX_TOKENS=800`. The shipped calibration is
  stamped 800 with the 784-fitted temperatures until DS-029 refits. Padding stays 800 with
  MTP off, so turning MTP off only removes `--speculative-config`.
- 13% less KV cache (436,397 vs 499,687 tokens).

## Not covered

- **Restart noise on Qwen3.8** (no restart pair) and its cause on either model (DS-028).
- **`disable_eagle_block_drop`** is marked experimental in vLLM. Its acceptance effect was
  below what these runs resolve (50.0% vs 50.2%).
- **Draft count.** Only 3 draft tokens were tested. Qwen3.8's per-position acceptance under
  load was 0.53 / 0.26 / 0.13.
- **Long chats.** Chat prompts here were short; chats with long contexts, and chat prefill
  under the 800 cap, were not measured.
- **Gemma 4 31B**, dropped after the top-K check; with the patch a top-K readout is not
  needed, so Gemma could be retested with its separate drafter.
