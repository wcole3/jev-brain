# DS-005: FP8 / NVFP4 weights and fp8 KV cache vs bf16

What does quantizing the weights or the KV cache cost `/v1/systemone` in accuracy and
calibration, and what does it buy? Owner goals: **Gemma KV headroom** and **Qwen decision
latency and throughput**. Measured 2026-10-08/09 on one RTX PRO 6000 (sm_120) with vLLM
v0.30.0. This report gives the Stage 1 screen; Stage 2 (collect + calibrate per picked
profile) is planned in
[2026-10-09-ds-005-stage2.md](../../superpowers/plans/2026-10-09-ds-005-stage2.md).

## Short answer (Stage 1 screen, all arms at T = 1)

- **FP8 weights on Qwen are close to lossless and faster.** On Qwen3.8 and Qwen3.6 alike:
  - 0.6-0.7% of JevBench answers flip, max |Δp| 0.13-0.25, accuracy within 0.4 points;
  - decision throughput rises ~1.4× (0.9 → 1.3 req/s at 4 and 16 workers);
  - chat decodes ~1.4-1.5× faster;
  - the KV pool grows 1.8×.
- **NVFP4 on Qwen3.8 is the fastest chat but drifts more.**
  - Chat runs ~2.1× faster and throughput matches FP8.
  - 2.6% of answers flip, max |Δp| 0.39. Its `lm_head` is NVFP4 too.
  - Single-worker decisions don't speed up, and the JevBench p95 rises to 343 ms.
- **Gemma: FP8 weights + fp8 KV give 3.3× the KV tokens.** This is the `fp8_per_token_head`
  arm (A3), with about 1.4× decision throughput and 1.7× chat speed.
  - Accuracy rises 1.3 points, almost all on one task (`panoramic:safety_severity`,
    24/100 rows), a systematic tilt rather than a general gain.
- **fp8 KV alone on Gemma moves probabilities least** (mean |Δp| ≤ 0.001, 0.7% flips), but
  each fp8-KV arm has a few flips whose bf16 top-two gap was near 1.0.
- **Not measured yet:** calibrated ECE (Stage 2) and the bf16 restart-noise floor (DS-028).

## Setup

- vLLM v0.30.0 with our patched rejection sampler (DS-004); gateway layout `header`, option
  orders `identity`; **no calibration on any arm** (T = 1, no noul offset), so arms compare
  like for like.
- Each arm: boot, then `scripts/bench.py --profile <arm> --chat` (cold and warm sweeps,
  throughput at 1/4/16 workers, JevBench 1,682 rows, chat alone and under 4 decision
  workers). Comparisons: `scripts/compare_runs.py <base> <arm>`
  ([comparisons.md](comparisons.md)).
- Quantized arms ran with `VLLM_USE_DEEP_GEMM=0` (DeepGEMM crashes or logs noise on sm_120).
- Arm profiles were throwaway copies of the shipped profiles with these changes:

| arm | base profile | weights (revision) | KV flag |
|---|---|---|---|
| A0 | `gemma-4-31b` | bf16 | auto (bf16) |
| A1a | `gemma-4-31b` | bf16 | `--kv-cache-dtype fp8` |
| A1b | `gemma-4-31b` | bf16 | `--kv-cache-dtype fp8_per_token_head` |
| A2 | `gemma-4-31b` | `RedHatAI/gemma-4-31B-it-FP8-block` (`d7242548c4`) | auto (bf16) |
| A3 | `gemma-4-31b` | `RedHatAI/gemma-4-31B-it-FP8-block` (`d7242548c4`) | `fp8_per_token_head` |
| B0 | `qwen3.8-27b` | bf16 | auto (bf16) |
| B1 | `qwen3.8-27b` | `Qwen/Qwen3.8-27B-FP8` (`017b9c7af6`) | `bfloat16` |
| B2 | `qwen3.8-27b` | `RadixArk/Qwen3.8-27B-NVFP4` (`319f741cce`) | `bfloat16` |
| C0 | `qwen3.6-27b` | bf16 | auto (bf16) |
| C1 | `qwen3.6-27b` | `Qwen/Qwen3.6-27B-FP8` (`e89b16ebf1`) | `bfloat16` |

- **Why `bfloat16` is forced on the quantized Qwen arms:** RadixArk declares an fp8
  `kv_cache_scheme`, so `auto` would pick fp8 KV, and fp8 KV with MTP corrupts output on
  sm_120 (vLLM #49010, still open).
- **Kernels picked** (startup logs in [logs/](logs/)):
  - FP8 block weights: `CutlassFp8BlockScaledMMKernel`;
  - NVFP4: `FlashInferCutlassNvFp4LinearKernel` for the MLPs and `FlashInferFP8ScaledMM` for
    attention;
  - Gemma attention: `TRITON_ATTN`, forced by its 256/512 head dims.

## Track A: Gemma 4 31B (KV headroom)

| arm | weights / KV GiB | KV tokens* | JevBench % | flips | mean / max \|Δp\| | ECE | JevBench p50 / p95 ms | req/s 1/4/16 | 8192×64×255 cold ms | chat tok/s long: alone / under load |
|---|---|---|---|---|---|---|---|---|---|---|
| A0 bf16 | 59.0 / 24.3 | 86,955 | 88.1 | — | — | 0.116 | 60 / 300 | 0.7/0.6/0.6 | 104,126 | 24.3 / 15.1 |
| A1a fp8 KV | 59.0 / 24.3 | 174,147 (2.0×) | 88.0 | 12 (0.7%) | 0.0010 / 0.99 | 0.115 | 66 / 308 | 0.7/0.7/0.7 | 74,005 | 22.7 / 13.9 |
| A1b fp8_per_token_head | 59.0 / 24.3 | 134,478 (1.55×) | 88.1 | 11 (0.7%) | 0.0007 / 0.84 | 0.115 | 60 / 306 | 0.7/0.6/0.6 | 98,342 | 24.5 / 14.6 |
| A2 FP8 weights | 31.7 / 51.4 | 184,022 (2.1×) | 89.7 | 38 (2.3%) | 0.0021 / 0.96 | 0.104 | 43 / 198 | 1.0/0.9/1.0 | 64,719 | 41.9 / 24.7 |
| A3 FP8 + fp8_per_token_head | 31.7 / 51.4 | 284,529 (3.3×) | 89.4 | 43 (2.6%) | 0.0028 / 0.99 | 0.101 | 43 / 207 | 1.0/0.9/0.9 | 40,355 | 41.3 / 27.0 |

\* vLLM's startup "GPU KV cache size" at `MAX_MODEL_LEN` 65,536. It moves with that
setting (DS-026), so it compares arms, not real maximum context.

- **FP8 accuracy is one task.** `panoramic:safety_severity` flips 24 of 100 rows on A2 and
  A3, all wrong → right, with a bf16 top-two gap of 0.996. Without it FP8 is about neutral
  (banking77 net −3 on A2, −6 on A3).
- **Plain `fp8` KV vs `fp8_per_token_head`:**
  - plain `fp8` gives more tokens (2.0× vs 1.55×) and faster long cold prefills;
  - but it casts the query to fp8 with scale 1.0;
  - per-token-head computes its scales on the fly, so the checkpoint's missing KV scales
    don't matter.

## Track B: Qwen3.8-27B (decision latency), MTP on, KV bf16

| arm | weights / KV GiB | KV tokens* | JevBench % | flips | mean / max \|Δp\| | ECE | JevBench p50 / p95 ms | warm 2048×16×26 ms | req/s 1/4/16 | 8192×64×255 cold ms | chat tok/s short / long, alone | chat tok/s long, under load |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B0 bf16 | 51.0 / 29.6 | 436,397 | 89.7 | — | — | 0.033 | 99 / 279 | 831 | 0.7/0.9/0.9 | 33,018 | 61.9 / 46.7 | 27.6 |
| B1 FP8 | 28.1 / 52.6 | 774,967 (1.8×) | 89.4 | 12 (0.7%) | 0.0011 / 0.13 | 0.027 | 93 / 222 | 641 | 1.0/1.3/1.3 | 22,900 | 92.0 / 70.2 | 38.4 |
| B2 NVFP4 | 19.8 / 60.3 | 888,079 (2.0×) | 90.2 | 43 (2.6%) | 0.0039 / 0.39 | 0.036 | 93 / 343 | 746 | 0.7/1.3/1.4 | 21,643 | 131.3 / 90.1 | 43.9 |

\* At `MAX_MODEL_LEN` 262,144; all Qwen arms keep 800-token blocks.

- **B1 flips are spread thin:** banking77 and invoice_processing are net −2 each, and no
  task stands out.
- **B2 drifts most on `panoramic:invoice_reconcile`:** 14/100 rows flip (net +6),
  consistent with its NVFP4 `lm_head` putting quantization error straight into the label
  logprobs.

## Qwen3.6-27B repeat of the FP8 arm

| | C0 bf16 | C1 FP8 |
|---|---|---|
| weights / KV GiB | 51.0 / 29.6 | 28.1 / 52.6 |
| KV tokens | 436,397 | 774,967 (1.8×) |
| JevBench % | 89.2 | 89.2 (+0.1) |
| flips; mean / max \|Δp\| | — | 10 (0.6%); 0.0014 / 0.25 |
| ECE | 0.040 | 0.041 |
| JevBench p50 / p95 ms | 107 / 289 | 104 / 250 |
| warm 2048×16×26 ms | 844 | 695 |
| req/s 1/4/16 | 0.7/0.9/0.9 | 0.9/1.3/1.3 |
| 8192×64×255 cold ms | 33,599 | 23,670 |
| chat tok/s short / long, alone | 75.2 / 60.7 | 105.3 / 88.0 |
| chat tok/s long, under load | 38.9 | 49.4 |
| MTP accepted drafts / mean length | 73.1% / 3.19 | 71.2% / 3.14 |

- Label tables match the bf16 tables exactly. The FP8 checkpoint also quantizes the MTP
  head, which costs ~2 points of draft acceptance.

## Caveats

- **One run per arm, no noise floor.** There is no bf16 restart-to-restart measurement for
  Gemma or Qwen3.8 (DS-028), so small flip counts may sit within restart noise.
- **Uncalibrated.** ECE here is at T = 1; calibrated ECE before/after refit is Stage 2.
- **MTP acceptance:**
  - B0 and B1 counters were lost when their containers were replaced;
  - B2's 41% (mean length 2.23, 492 drafts) came from a different capture than C0/C1 and
    is not comparable.
- **KV tokens are vLLM's reported figure** at each profile's `MAX_MODEL_LEN`, not a measured
  maximum context; the DS-017 targets (131k / 262k for Gemma) are untested.
- **Gemma FP8 chat template** differs from base by one trailing newline, so its label
  table's `tokenizer_sha256` differs; label ids are identical.
