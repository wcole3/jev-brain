# DS-005: FP8 / NVFP4 weights and fp8 KV cache vs bf16

What does quantizing the weights or the KV cache cost `/v1/systemone` in accuracy and
calibration, and what does it buy? Owner goals: **Gemma KV headroom** and **Qwen decision
latency and throughput**. Measured 2026-10-08/09 on one RTX PRO 6000 (sm_120) with vLLM
v0.30.0. This report gives the Stage 1 screen and the Stage 2 calibration of the picked profiles
(plan:
[2026-10-09-ds-005-stage2.md](../../superpowers/plans/2026-10-09-ds-005-stage2.md)).

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
- **Calibrated (Stage 2, below):** on the shipped `header` layout, every quantized profile
  refits to choice and noul temperatures within 0.06 of its bf16 base. Eval accuracy is
  within 0.008 per type and choice/noul ECE within about 0.01. Two gate outcomes differ (below).
- **Not measured yet:** the bf16 restart-noise floor (DS-028) and full Index runs on the
  quantized profiles.

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

## Stage 2: calibrated profiles (2026-10-09)

The four arms the owner picked became profiles (`qwen3.8-27b-fp8`, `qwen3.8-27b-nvfp4`,
`qwen3.6-27b-fp8`, `gemma-4-31b-fp8`).
- **Collection:** each collected the calib (5,547) and eval (8,517) splits on its own
  rented vast.ai RTX PRO 6000 box, with the same ok/unsupported counts as bf16.
- **Fit:** `scripts/calibrate.py` fitted the temperatures on calib and judged them on eval.
- **Table:** shows the shipped `header` layout. The other layouts are in each calibration
  summary.
- **Columns:** accuracy is per question type on eval. ECE is eval, before the fit (T = 1) →
  after.

| profile | choice acc | choice ECE | choice T | score ECE | score T | noul acc | noul ECE | noul T | b | JevBench p50 / p95 ms* | weights / KV GiB* | KV tokens* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3.8-27b (bf16) | 0.824 | 0.041 → 0.045 | 1.536 | 0.135 → 0.182 | 1.775 pooled | 0.889 | 0.035 → 0.029 | 0.963 | 0 | 99 / 279 | 51.0 / 29.6 | 436,397 |
| qwen3.8-27b-fp8 | 0.822 | 0.047 → 0.044 | 1.517 | 0.149 → 0.149 | 1.000 (gate: none) | 0.890 | 0.031 → 0.027 | 0.959 | 0 | 93 / 222 | 28.1 / 52.6 | 774,967 |
| qwen3.8-27b-nvfp4 | 0.816 | 0.063 → 0.026 | 1.597 | 0.133 → 0.163 | 1.830 pooled | 0.892 | 0.036 → 0.033 | 0.963 | 0 | 93 / 343 | 19.8 / 60.3 | 888,079 |
| qwen3.6-27b (bf16) | 0.817 | 0.079 → 0.033 | 1.627 | 0.181 → 0.199 | 1.957 pooled | 0.895 | 0.040 → 0.024 | 1.281 | 0 | 107 / 289 | 51.0 / 29.6 | 436,397 |
| qwen3.6-27b-fp8 | 0.812 | 0.087 → 0.034 | 1.632 | 0.189 → 0.209 | 1.974 pooled | 0.892 | 0.039 → 0.027 | 1.286 | 0 | 104 / 250 | 28.1 / 52.6 | 774,967 |
| gemma-4-31b (bf16) | 0.830 | 0.167 → 0.079 | 4.263 | 0.324 → 0.170 | 5.603 pooled | 0.884 | 0.115 → 0.051 | 7.609 | 0 | 60 / 300 | 59.0 / 24.3 | 86,955 |
| gemma-4-31b-fp8 | 0.832 | 0.165 → 0.076 | 4.269 | 0.322 → 0.178 | 5.570 pooled | 0.886 | 0.111 → 0.053 | 7.571 | 0 | 43 / 207 | 31.7 / 51.4 | 284,529 |

\* Stage 1 screen, uncalibrated; KV tokens at each profile's `MAX_MODEL_LEN` (65,536 for
Gemma, 262,144 for Qwen).

- **Quantization barely changes the fit on `header`.** Choice T moves by at most 0.06 and
  noul T by at most 0.04, against each profile's bf16 base. Eval accuracy moves by at most
  0.008 per type.
- **Gemma FP8, decider_chat:** the gate picked the pooled T (5.36) for choice where bf16 Gemma
  ships its fitted T (4.12). ECE and accuracy there match bf16 within 0.01.
- **Score T on Qwen3.8 FP8 stays at 1.** The gate found that neither the fitted nor the
  pooled T improved eval ECE (0.149 either way). The bf16 base ships its pooled T 1.775,
  which raises eval ECE from 0.135 to 0.182 under the same rule.
- **Noul offset b in other layouts:**
  - Gemma FP8 ships b in decider_chat (−0.66) and question_first (−0.51), as bf16 Gemma does
    (−0.64, −0.46).
  - Qwen3.6 FP8 doesn't ship b in question_first. Its accuracy gain (+0.015) has a 95%
    interval touching 0, while bf16 Qwen3.6 ships b = 0.256 there.
- **Calibration summaries:** `docs/results/archive/<profile>/2026-10-09T*-calibrate/summary.md`.

## Recommendation

The owner decides the defaults; these are the trade-offs as measured.

**Gemma KV headroom: `gemma-4-31b-fp8`.**
- **Gains:** 3.3× the KV tokens of bf16 (284,529 vs 86,955 at the same `MAX_MODEL_LEN`).
  About 1.4× decision throughput and 1.7× chat decode. Calibration matches bf16 after its
  own fit.
- **Costs:** 2.6% of JevBench answers flip at T = 1. Most flips are one systematic tilt,
  `panoramic:safety_severity` (+24 of 100 rows); elsewhere it is about neutral.
- **Unmeasured:** the DS-017 context targets (131k / 262k), restart noise (DS-028), and a
  full Index run. That run matters if this becomes the DS-030 submission.

**Qwen decision latency: FP8 (`qwen3.8-27b-fp8`, `qwen3.6-27b-fp8`).**
- **Gains:** about 1.4× decision throughput, a lower JevBench p95, about 1.4-1.5× chat, and
  1.8× KV.
- **Costs:** the smallest drift of all arms (0.6-0.7% flips, max |Δp| 0.13-0.25), and
  calibration matches bf16. The FP8 MTP head costs about 2 points of draft acceptance
  (Qwen3.6).

**Qwen chat speed: `qwen3.8-27b-nvfp4`.**
- **Gains:** about 2.1× chat decode and 2.0× KV. Calibrated choice ECE is the best of the
  Qwen3.8 profiles (0.026).
- **Costs:**
  - the most drift (2.6% flips, max |Δp| 0.39), consistent with its NVFP4 `lm_head`;
  - no single-worker decision speed-up, and a worse JevBench p95 (343 ms).
- **MTP acceptance:** measured for B2 only, on a different capture from C0/C1, so not
  comparable.

## Caveats

- **One run per arm, no noise floor.** There is no bf16 restart-to-restart measurement for
  Gemma or Qwen3.8 (DS-028), so small flip counts may sit within restart noise.
- **Stage 1 is uncalibrated.** Its ECE is at T = 1; Stage 2 has the calibrated numbers.
- **Stage 2 hosts:** collects ran on four different rented hosts. bf16 noise (~0.03) applies
  between them and this machine.
- **MTP acceptance:**
  - B0 and B1 counters were lost when their containers were replaced;
  - B2's 41% (mean length 2.23, 492 drafts) came from a different capture than C0/C1 and
    is not comparable.
- **KV tokens are vLLM's reported figure** at each profile's `MAX_MODEL_LEN`, not a measured
  maximum context; the DS-017 targets (131k / 262k for Gemma) are untested.
- **Gemma FP8 chat template** differs from base by one trailing newline, so its label
  table's `tokenizer_sha256` differs; label ids are identical.
