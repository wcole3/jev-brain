# DS-004 results: Qwen3.6-27B

Detailed results behind [the DS-004 report](../README.md). Three parts, in run order:

1. **Patched rejection sampler:** stock vs patched vLLM with MTP, idle and under chat load,
   and the block drop off (D′).
2. **The 784-1,568-token slowdown:** cause, step logs, and the realigned cap / budget.
3. **The realigned MTP profile:** full benches (sweeps, prefix sharing, throughput,
   JevBench, chat) with gateway padding 784 vs 800.

Runs are in `runs/<arm>/` (`raw.jsonl`, `summary.md`, and `chat-load.*` where chats ran),
`compare_runs.py` output in [comparisons.md](comparisons.md), logs in `logs/`. How the
arms were run: [runbook](../runbook.md).

## 1. Patched rejection sampler

Run 2026-10-06, local RTX PRO 6000, vLLM v0.30.0, shipped `qwen3.6-27b` profile. MTP arms
add `--speculative-config {"method":"mtp","num_speculative_tokens":3}`. Each arm is a
JevBench run through the gateway (1,682 rows); "chat load" is 4 streaming chats via
`scripts/spike_chat_load.py`. Runbook: `../runbook.md`.

| arm | vLLM | MTP | load | error rows | latency p50 / p95 (ms) |
|---|---|---|---|---|---|
| A | stock | off | idle | 0 | 115 / 286 |
| A′ | stock | off | chat | 0 | 327 / 631 |
| E | stock | on | chat | 1,682 (HTTP 500, `IndexError`) | — |
| P | patched | on | idle | 0 | 137 / 479 |
| P′ | patched | on | chat | 0 | 387 / 1,067 |

The patched path ran: the `JEV-SPIKE` counter logged 2,200 rejection-sampler steps with
label-id rows in P′, none in P.

### Probability drift

| comparison | max \|Δp\| | mean \|Δp\| | flips (largest baseline gap) |
|---|---|---|---|
| A′ vs A (stock noise under load) | 0.027 | 0.0001 | 2 (0.025) |
| P vs A (MTP on, patched path idle) | 0.077 | 0.0005 | 3 (0.025) |
| P′ vs P (patched path, load vs idle) | 0.066 | 0.0003 | 3 (0.034) |
| P′ vs A′ (the candidate vs stock under load) | 0.078 | 0.0006 | 4 (0.063) |
| P′ vs A (the candidate vs production) | 0.078 | 0.0006 | 2 (0.063) |

No flip has a baseline top-two gap above 0.10. Accuracy is 89.2% in A, A′ and P and
89.1% in P′.

The extra drift is restart noise, not MTP or the patch (§2, "Drift"): simply
restarting the stock MTP-off stack (A2 vs A) moves probabilities by up to 0.079, mostly in
the 784-1,568-token banking77 rows, with 3 flips. Within one running instance, results
repeat bit for bit. A′ vs A (same instance, load vs idle) is therefore a lower noise floor
than any comparison across restarts, which all the MTP arms are. Under load the patched
path adds little: P′ vs P p99 |Δp| is 0.023-0.028, against 0.015-0.017 for A′ vs A.

### Chat

| arm | chats | p50 decode tok/s | p50 TTFT | acceptance |
|---|---|---|---|---|
| A′ | 100 | 18.5 | 269 ms | — |
| P′ | 244 | 37.0 | 340 ms | 50.2% of drafts, mean accepted length 2.51 |

### Arm D′: `disable_eagle_block_drop`

Same patched build and MTP config, plus `"disable_eagle_block_drop":true` in the
speculative config (experimental vLLM option). Pnd is idle, Pnd′ is under chat load. Both
runs had 0 error rows, and the `JEV-SPIKE` counter fired under load.

| comparison | prompts < 784 tokens: max / p99 \|Δp\| | 784-1,568 tokens: max / p99 \|Δp\| |
|---|---|---|
| P vs A (block drop on, idle) | 0.047 / 0.024 | 0.077 / 0.055 |
| Pnd vs A (block drop off, idle) | **0.000 / 0.000** | 0.054 / 0.035 |
| P′ vs A′ (block drop on, load) | 0.047 / 0.024 | 0.078 / 0.048 |
| Pnd′ vs A′ (block drop off, load) | 0.038 / 0.020 | 0.044 / 0.035 |

Overall max |Δp|: Pnd vs A 0.054, Pnd′ vs A′ 0.044, Pnd′ vs Pnd 0.039 (P′ vs P was
0.066). No flip has a baseline gap above 0.10. Accuracy 89.1%.

With the block drop off, short prompts are bit-identical to MTP off when idle. The
784-1,568-token band still drifts, and its latency still rises, so the block drop is not
the whole cause there:

| arm | < 784 tokens p50 / p95 (ms) | 784-1,568 tokens p50 / p95 (ms) |
|---|---|---|
| A | 111 / 140 | 274 / 311 |
| P | 132 / 182 | 445 / 611 |
| Pnd | 132 / 164 | 441 / 612 |
| A′ | 322 / 377 | 607 / 707 |
| P′ | 376 / 468 | 1,012 / 1,162 |
| Pnd′ | 414 / 574 | 973 / 1,171 |

Chat under load with the block drop off: 253 chats, p50 35.1 tok/s, TTFT 365 ms, 50.0% of
drafts accepted (mean accepted length 2.50), against 37.0 tok/s and 50.2% with it on.
## 2. Why MTP slowed 784-1,568-token decisions

Run 2026-10-06/07, local RTX PRO 6000, vLLM v0.30.0. Follows §1.

### Question

With MTP on, JevBench decisions of 784-1,568 prompt tokens got ~60% slower even idle (p50
274 → 445 ms), while prompts under 784 tokens rose only ~20 ms. The same band also showed
more probability drift than prompts under 784. Prefix caching is not involved (cached % = 0
in every run). In JevBench the band is 300 banking77 rows of 784-1,049 tokens.

### Cause

MTP makes the KV block 800 tokens instead of 784, and the profile's
`--long-prefill-token-threshold 784` is now smaller than a block. In Mamba "align" mode
the scheduler then cuts every 800-token block into two prefill steps, 784 + 16. A
1,000-token prompt takes 3 engine steps instead of 2. At these sizes a step costs about the
same whatever its token count (16 tokens ≈ 123 ms, 784 tokens ≈ 131 ms), so the extra step
adds ~100+ ms.

The drift is not caused by this. Restarting the stock MTP-off stack moves probabilities by
about as much as MTP does (see "Drift").

### Source evidence (v0.30.0)

**Block size 784 → 800.**
- `model_executor/models/qwen3_5.py:399-418` passes `num_speculative_tokens` into the GDN state
  shape.
- `model_executor/layers/mamba/mamba_utils.py:274-295` sizes the conv state at
  `conv_kernel_size - 1 + num_spec` positions.
- Qwen3.6-27B: conv_dim 10,240, kernel 4, fp32 SSM state 48×128×128. A Mamba page is
  3,207,168 B with MTP off and 3,268,608 B with MTP 3.
- `platforms/interface.py:922-932` picks the attention block as 16 ×
  ceil(mamba page / (16 × 4,096 B per token)). That is 16 × 49 = 784, or 16 × 50 = 800.
  `:918-919` (align mode) then sets `mamba_block_size = block_size`.
- The logs agree: "Setting attention block size to 800 tokens" and "Padding mamba page size
  by 0.25%".

**How a prefill is chunked.**
- `v1/core/sched/scheduler.py:661-662` and `:1066-1068` cap each chunk at the threshold.
- `_mamba_block_aligned_split` (`:413-538`) then applies the align-mode rules:
  - `:471-479`: a non-final chunk is floored to a block boundary. If the floor is 0 and
    `block_size > threshold`, the chunk stays sub-block (784 tokens).
  - `:481` and `:507-512`: a chunk that starts mid-block must stop at the next block
    boundary. That is the 16-token step.
- With block 800 and threshold 784, every 800-token block costs two steps.
  `disable_eagle_block_drop` changes only `last_cache_position` (`:443-445`), which does not
  bind here. That is why Pnd behaved like P.

Predicted chunks (a replay of the code above). Real step logs agree with every one of them:

| prompt tokens | stock (block 784, thr 784) | MTP shipped (800, thr 784) | MTP realigned (800, thr 800) |
|---|---|---|---|
| 785 | 784, 1 | 784, 1 | 785 |
| 800 | 784, 16 | 784, 16 | 800 |
| 1,000 | 784, 216 | **784, 16, 200** | 800, 200 |
| 1,585 | 784, 784, 17 | **784, 16, 784, 1** | 800, 785 |
| 2,000 | 784, 784, 432 | **784, 16, 784, 16, 400** | 800, 800, 400 |

### Measurements

**Method.**
- A mounted copy of `scheduler.py` logs each engine step's scheduled tokens:
  `docker/spike/vllm/scheduler.py`, `compose.spike-steps.yaml`, `JEV-STEP` lines.
  Logs are in `logs/step-probe/*.log.gz`.
- `scripts/spike_step_probe.py` sends requests one at a time:
  - synthetic random-token prompts of fixed lengths straight to vLLM (5 reps each);
  - 40 + 40 JevBench rows (< 784 and 784-1,568) through the gateway.
- vLLM's `iteration_tokens_total` cannot count steps: the frontend logs one iteration per
  request.

Configs:

| tag | vLLM | MTP | threshold / budget | block |
|---|---|---|---|---|
| stock (A, A2) | stock | off | 784 / 2352 | 784 |
| P, P2 | patched | on (block drop on) | 784 / 2352 | 800 |
| Pnd | patched | on (block drop off) | 784 / 2352 | 800 |
| R | patched | on (block drop off) | **800 / 2400** | 800 |

Config R is `profiles/spike/qwen3.6-27b-mtp-nodrop-800.env`.

**Engine steps for the 300 band rows (full JevBench, step log):**

| config | steps per band row | median step time |
|---|---|---|
| A2 | 2 (all 300) | 784-chunk 126 ms |
| P2 | 3 (all 300) | 784-chunk 131 ms, 16-chunk 123 ms |
| R | 2 (284), 1 (16 rows of 784-800 tokens) | 800-chunk 143 ms |

**Synthetic prompts, p50 ms (logged chunks for the MTP runs):**

| tokens | stock | P | R |
|---|---|---|---|
| 784 | 156 | 165 [784] | 169 [784] |
| 800 | 266 | 251 [784, 16] | 169 [800] |
| 801 | 265 | 302 [784, 16, 1] | 234 [800, 1] |
| 1,000 | 273 | 349 [784, 16, 200] | 276 [800, 200] |
| 1,500 | 310 | 385 [784, 16, 700] | 321 [800, 700] |
| 1,600 | 422 | 511 [784, 16, 784, 16] | 340 [800, 800] |
| 2,000 | 413 | 595 [784, 16, 784, 16, 400] | 434 [800, 800, 400] |

**Full JevBench, idle, p50 / p95 ms by band:**

| run | < 784 | 784-1,568 | overall | accuracy |
|---|---|---|---|---|
| A (stock) | 111 / 140 | 274 / 311 | 115 / 286 | 89.2% |
| A2 (stock, restart) | 102 / 134 | 259 / 311 | 106 / 274 | 89.2% |
| P (MTP, shipped) | 132 / 182 | 445 / 611 | 137 / 479 | 89.2% |
| P2 (P rerun) | 117 / 164 | 373 / 470 | 123 / 412 | 89.2% |
| Pnd (block drop off) | 132 / 164 | 441 / 612 | 136 / 467 | 89.1% |
| **R (MTP, realigned)** | 131 / 176 | **291 / 370** | 137 / 325 | 89.2% |

- In the band, the shipped MTP config costs +99 to +186 ms at p50. P and P2 vary by
  ~70 ms between runs.
- R brings the band back to +17 to +32 ms over stock. That is the same MTP cost seen under
  784 tokens, now on 2 steps instead of 1.
- The 40 + 40 row probe agrees. Band p50: stock 287, P 347, R 276 ms. Under 784: 126, 104,
  113 ms.

### Drift

Same metrics as §1: max |Δp|, and p99 of each row's max |Δp|.

| comparison | < 784: max / p99 | 784-1,568: max / p99 | flips |
|---|---|---|---|
| **A2 vs A (stock restart)** | 0.042 / 0.024 | **0.079 / 0.049** | 3 |
| P2 vs A | 0.048 / 0.024 | 0.053 / 0.051 | 0 |
| Pnd vs A | 0.000 / 0.000 | 0.054 / 0.035 | 2 |
| R vs A | 0.038 / 0.023 | 0.074 / 0.064 | 2 |
| R vs A2 | 0.048 / 0.024 | 0.055 / 0.043 | 3 |
| P2 vs A2 | 0.048 / 0.024 | 0.051 / 0.039 | 3 |

- A stock restart drifts as much as any MTP run, and most in banking77, whose 77 close
  options make it the most sensitive set. The band's "extra drift" is therefore within the
  restart-to-restart floor and is not caused by the 784 + 16 chunking. Realigning does not
  reduce it.
- Within one running instance, results repeat exactly. The probe rows matched the full
  bench bit for bit on P2 and on R.
- Pnd matching A exactly under 784 tokens was luck between two instances, not a property of
  block drop off. A2, a stock restart, does not match A.
- No flip has a baseline top-two gap above 0.10.

### What this means for the MTP profile (facts; the owner decides)

- With MTP 3 on Qwen3.6-27B, the KV block is 800 tokens. Any threshold below 800 splits
  every block into two prefill steps. This applies to chat prefills too (from the code; not
  measured under chat load). A long prompt then needs twice the steps per 800 tokens.
- `--long-prefill-token-threshold 800 --max-num-batched-tokens 2400` (budget − threshold =
  1,600 > 800) restores stock step counts. Idle results: band p50 291 ms, accuracy 89.2%,
  drift at the stock restart floor.
- Not measured for R: behaviour under chat load (P′/Pnd′ equivalents), chat tok/s, and
  whether DS-025's "budget − threshold > block" margin should also cover the 1 + 3 tokens a
  drafting chat decode takes.
- The gateway's `PREFIX_BLOCK`/`WARM_MIN_PREFIX_TOKENS` stay at 784 in R, because
  `calibration.json` stamps `prefix_block` and the gateway refuses a mismatch. With MTP,
  vLLM's cache block is 800, so front padding of multi-row requests (DS-008) would not
  land on block boundaries. That does not touch single-row JevBench, but it matters for
  multi-question decisions. Fixing it means a new calibration stamp.
## 3. The realigned MTP profile (step 2b)

Run 2026-10-07, local RTX PRO 6000, vLLM v0.30.0. Each arm is a full
`scripts/bench.py --profile qwen3.6-27b --chat`: cold and warm sweeps, throughput,
JevBench (1,682 rows), chat alone and under 4 decision workers. Chat rate is completion
tokens/s from the usage chunk (`bench.py` no longer counts chunks), excluding the first
token. Follows §1 and §2.

| arm | vLLM | MTP | threshold / budget | block drop | gateway `PREFIX_BLOCK` | KV cache | folder |
|---|---|---|---|---|---|---|---|
| S | stock | off | 784 / 2352 | — | 784 | 650 blocks × 784 | `runs/S/` |
| R | patched | 3 drafts | 800 / 2400 | off | 784 | 571 blocks × 800 | `runs/R-full/` |
| R800 | patched | 3 drafts | 800 / 2400 | off | 800 (+ `WARM_MIN_PREFIX_TOKENS=800`) | 571 blocks × 800 | `runs/R800/` |
| R′ | R's stack | 3 drafts | 800 / 2400 | off | 784 | 571 blocks × 800 | `runs/Rprime/` |

- vLLM logged a KV size of 499,687 tokens for S and 436,397 tokens for R and R800.
- R is `profiles/spike/qwen3.6-27b-mtp-nodrop-800.env` with `compose.spike.yaml`.
  The earlier `runs/R/` folder is the idle JevBench-only run from §2.
- R800 uses `profiles/spike/qwen3.6-27b-mtp-nodrop-800-pad800.env` with
  `compose.spike-pad800.yaml`. That override mounts `docker/spike/data/qwen3.6-27b/` over
  the gateway's data: copies of all three layouts with the calibration stamp
  `prefix_block: 800`. T and b are unchanged (fitted at 784), and each file carries a
  comment saying so. The gateway checks every layout's stamp, so a header-only copy
  failed at startup. Labels and the other stamp fields pass unchanged.
- R′ is JevBench-only under 4 streaming chats (`scripts/spike_chat_load.py --vllm`), run
  like A′/P′ in `../runbook.md`.
- No arm had an error row.

### Systemone latency

#### Cold sweep, p50 / p95 ms

A new state for every request (nonce).

| state tokens | questions | options | S | R | R800 |
|---|---|---|---|---|---|
| 256 | 1 | 2 | 121 / 164 | 113 / 121 | 116 / 128 |
| 256 | 1 | 26 | 184 / 229 | 172 / 184 | 173 / 185 |
| 256 | 1 | 255 | 1176 / 1275 | 1229 / 1249 | 1258 / 1306 |
| 256 | 4 | 2 | 439 / 464 | 813 / 849 | 448 / 472 |
| 256 | 4 | 26 | 452 / 462 | 825 / 854 | 485 / 512 |
| 256 | 4 | 255 | 2722 / 2778 | 3151 / 3232 | 2798 / 2830 |
| 256 | 16 | 2 | 533 / 591 | 2021 / 2044 | 547 / 620 |
| 256 | 16 | 26 | 896 / 923 | 2326 / 2389 | 883 / 948 |
| 256 | 16 | 255 | 6250 / 6467 | 7901 / 7911 | 6280 / 6326 |
| 256 | 64 | 2 | 1206 / 1232 | 7180 / 8026 | 1302 / 1321 |
| 256 | 64 | 26 | 2589 / 2667 | 8779 / 9220 | 2733 / 2823 |
| 256 | 64 | 255 | 21904 / 23056 | 27580 / 27641 | 21647 / 22276 |
| 2048 | 1 | 2 | 560 / 621 | 510 / 545 | 545 / 546 |
| 2048 | 1 | 26 | 643 / 681 | 639 / 657 | 665 / 672 |
| 2048 | 1 | 255 | 1826 / 1871 | 1731 / 1733 | 1744 / 1788 |
| 2048 | 4 | 2 | 900 / 986 | 1492 / 1949 | 852 / 887 |
| 2048 | 4 | 26 | 881 / 972 | 1553 / 1791 | 869 / 978 |
| 2048 | 4 | 255 | 4644 / 4882 | 3859 / 3888 | 4429 / 4434 |
| 2048 | 16 | 2 | 1060 / 1207 | 2913 / 3186 | 959 / 981 |
| 2048 | 16 | 26 | 1467 / 1798 | 3003 / 3458 | 1339 / 1382 |
| 2048 | 16 | 255 | 8002 / 8071 | 8875 / 9088 | 8053 / 8116 |
| 2048 | 64 | 2 | 1718 / 1723 | 9635 / 9725 | 1814 / 1865 |
| 2048 | 64 | 26 | 3244 / 3319 | 11731 / 11998 | 3208 / 3259 |
| 2048 | 64 | 255 | 24032 / 24154 | 31697 / 31728 | 23736 / 23969 |
| 8192 | 1 | 2 | 2367 / 2427 | 1899 / 1910 | 1884 / 1887 |
| 8192 | 1 | 26 | 2070 / 2134 | 1984 / 1996 | 1985 / 2019 |
| 8192 | 1 | 255 | 3249 / 4373 | 3213 / 3225 | 3108 / 3134 |
| 8192 | 4 | 2 | 2272 / 2318 | 2432 / 2469 | 2318 / 2334 |
| 8192 | 4 | 26 | 2298 / 2335 | 6907 / 7171 | 2319 / 2349 |
| 8192 | 4 | 255 | 9376 / 9912 | 9404 / 9491 | 9383 / 9554 |
| 8192 | 16 | 2 | 2555 / 2594 | 3995 / 4076 | 2515 / 2539 |
| 8192 | 16 | 26 | 2834 / 2888 | 8880 / 8951 | 2859 / 2912 |
| 8192 | 16 | 255 | 13011 / 13244 | 15212 / 15262 | 13329 / 13634 |
| 8192 | 64 | 2 | 3602 / 3683 | 10508 / 10588 | 3726 / 3783 |
| 8192 | 64 | 26 | 4828 / 5092 | 16442 / 16857 | 5083 / 5206 |
| 8192 | 64 | 255 | 29740 / 30285 | 39444 / 39460 | 30493 / 31022 |

- Single-question requests: R and R800 are within about ±10% of S. Most cells are a
  little faster; 8192-token states are 15-20% faster at 2 options.
- Multi-question requests on R are up to 6× slower than S. 255-option cells are hit least
  (1.0-1.3×); 2,048 × 4 q × 255 options is 17% faster. Examples: 64 q × 2 options,
  1,206 → 7,180 ms (256-token state) and 1,718 → 9,635 ms (2,048-token state). 16 q × 26
  options at 8,192 tokens: 2,834 → 8,880 ms.
- R800 brings every multi-question cell back to within about ±10% of S.

#### Warm sweep: 16 questions sharing one 2,048-token state, 26 options

| | S | R | R800 |
|---|---|---|---|
| p50 / p95 ms | 781 / 817 | 1,328 / 1,438 | 835 / 865 |

#### Throughput

Requests of 2,048 state tokens, 16 questions and 26 options.

| workers | S | R | R800 |
|---|---|---|---|
| 1 | 0.79 req/s | 0.33 | 0.74 |
| 4 | 1.00 | 0.34 | 0.96 |
| 16 | 1.01 | 0.35 | 0.97 |

#### Cached prompt tokens per phase (vLLM counters): cached % (computed tokens)

| phase | S | R | R800 |
|---|---|---|---|
| cold | 83.6 (4,777,732) | 72.8 (7,913,551) | 83.9 (4,762,055) |
| warm | 90.9 (22,398) | 80.4 (48,238) | 91.0 (22,446) |
| throughput x1 | 86.1 (136,632) | 62.5 (153,730) | 86.2 (132,043) |
| throughput x4 | 86.1 (182,176) | 61.6 (204,649) | 86.2 (183,712) |
| throughput x16 | 86.1 (244,799) | 62.3 (385,925) | 86.2 (235,381) |
| jevbench | 0.0 (552,075) | 0.0 (552,075) | 0.0 (552,075) |
| chat | 86.1 (148,100) | 61.0 (127,866) | 86.2 (68,974) |

- R computes more prompt tokens than S: 1.66× in the cold sweep (same requests), and
  about 2.7× per throughput request.
- With the gateway padding shared prefixes to 784 while vLLM caches in 800-token blocks,
  the shared prefix ends mid-block, so rows after the first lose their prefix hit.
  `PREFIX_BLOCK=800` restores stock cache reuse.
- The "chat" phase's counters also include the 4 decision workers that run during it.

### JevBench, idle

Rows by prompt length: 1,382 under 784 tokens, 300 at 784-1,568 tokens.

| arm | accuracy | overall p50 / p95 ms | < 784 p50 / p95 | 784-1,568 p50 / p95 | ECE |
|---|---|---|---|---|---|
| S | 89.2% | 106 / 270 | 103 / 128 | 259 / 308 | 0.034 |
| R | 89.2% | 132 / 318 | 127 / 164 | 302 / 346 | 0.035 |
| R800 | 89.1% | 127 / 303 | 122 / 151 | 292 / 330 | 0.034 |

Band accuracy is 90.2-90.3% under 784 tokens and 84.0-84.3% at 784-1,568 in every arm.
JevBench rows are single questions, so padding never applies and R and R800 should match;
they differ by 5-10 ms.

### Chat

One request per prompt, `max_tokens` 512. Under load, 4 workers send 2,048-token,
16-question decisions back to back.

| prompt | load | S tok/s, TTFT | R | R800 |
|---|---|---|---|---|
| short | none | 27.0, 127 ms | 73.1, 136 ms | 78.4, 154 ms |
| long | none | 26.7, 133 ms | 62.9, 144 ms | 62.9, 155 ms |
| short | 4 decision workers | 14.4, 7,357 ms | 35.2, 3,323 ms | 33.9, 2,957 ms |
| long | 4 decision workers | 16.0, 498 ms | 38.5, 687 ms | 36.6, 826 ms |

- These are single samples: TTFT under load swings by seconds with the decision queue.
- Spec-decode acceptance over the bench's 4 chats (2 alone, 2 under load), from
  `/metrics` deltas:
  - R: 74.4% of 1,551 draft tokens, mean accepted length 3.23;
  - R800: 73.7% of 1,599, mean accepted length 3.21.
- These short technical prompts accept more drafts than the story prompts of the chat-load
  runs (about 50%).

### R′ against A′ and P′ (JevBench under 4 streaming chats)

| arm | config | error rows | accuracy | p50 / p95 ms | < 784 p50 / p95 | 784-1,568 p50 / p95 | chats | chat p50 tok/s | chat p50 TTFT | acceptance |
|---|---|---|---|---|---|---|---|---|---|---|
| A′ | stock, MTP off | 0 | 89.2% | 327 / 631 | 322 / 377 | 607 / 707 | 100 | 18.5 | 269 ms | — |
| P′ | patched, MTP, 784 / 2352 | 0 | 89.1% | 387 / 1,067 | 376 / 468 | 1,012 / 1,162 | 244 | 37.0 | 340 ms | 50.2%, length 2.51 |
| Pnd′ | P′ + block drop off | 0 | 89.1% | 428 / 1,037 | 414 / 574 | 973 / 1,171 | 253 | 35.1 | 365 ms | 50.0%, length 2.50 |
| **R′** | patched, MTP, 800 / 2400, block drop off | 0 | 89.2% | 391 / 825 | 382 / 489 | 771 / 993 | 235 | 37.8 | 355 ms | 50.0%, length 2.50 |

- In the 784-1,568 band, R′ is 241 ms faster than P′ at p50 and 164 ms slower than A′.
- Under 784 tokens, R′ is within 6 ms of P′ and 60 ms slower than A′.
- Chat under R′ matches P′.

### Drift

Each cell is max / p99 of each row's max |Δp|. The yardstick is the stock restart floor:
A2 vs A gives max 0.079, 3 flips (§2). The in-instance figure (A′ vs A,
0.027) does not apply across restarts, and every comparison below is across restarts
except R′ vs R.

| comparison | < 784 | 784-1,568 | all | flips (largest baseline gap) |
|---|---|---|---|---|
| A2 vs A (stock restart, reference) | 0.042 / 0.024 | 0.079 / 0.049 | 0.079 / 0.030 | 3 (0.025) |
| S vs A (stock restart) | 0.048 / 0.024 | 0.059 / 0.052 | 0.059 / 0.030 | 2 (0.063) |
| R vs S | 0.081 / 0.024 | 0.061 / 0.056 | 0.081 / 0.030 | 3 (0.036) |
| R800 vs R | 0.047 / 0.024 | 0.055 / 0.046 | 0.055 / 0.030 | 2 (0.019) |
| R800 vs S | 0.080 / 0.024 | 0.064 / 0.049 | 0.080 / 0.030 | 3 (0.031) |
| R′ vs R (same instance, chat load vs idle) | 0.045 / 0.024 | 0.035 / 0.027 | 0.045 / 0.024 | 1 (0.049) |
| R′ vs A′ | 0.105 / 0.024 | 0.054 / 0.042 | 0.105 / 0.030 | 6 (0.049) |
| R′ vs P′ | 0.140 / 0.024 | 0.057 / 0.046 | 0.140 / 0.029 | 4 (0.049) |

- No flip has a baseline top-two gap above 0.10.
- Accuracy is 89.1-89.2% everywhere.
- Every max above 0.079 comes from one row, `typed_decisions:invoice_processing:1370`
  (score type, T = 1.958, 397 tokens). Its level-2 probability takes discrete values from
  instance to instance: 0.266 (A2, R, P, P′), 0.300 (A, A′, Pnd), 0.324 (S) and 0.405
  (R, R′).
  - It is identical in R and R′, so the shift comes with the instance, not with load.
  - Without that row, the new comparisons' max is 0.045-0.064.
- p99 stays at 0.024 under 784 tokens and 0.027-0.056 in the band, the same as the stock
  restart.
- `comparisons.md`
  hold the `compare_runs.py` output.

### Spike counter (`JEV-SPIKE`)

The counter logs the first and every 200th rejection-sampler step that carries label-id
rows.

- R′: the count runs on from the R bench, on the same instance. It reached step 2,000,
  with 2,071 label-id rows in total (`logs/R-and-Rprime-spike.log`). The
  patched path ran under chat load.
- R bench, chat-under-decisions phase: step 1 only, 2 label-id rows. There were fewer
  than 200 such steps, since only 2 chats ran against the decision load.
  The same holds for R800.
- Logs: `logs/R-full-spike.log` and `logs/R800-spike.log`.
- No other bench phase runs a chat, so there were no drafting steps to share with
  decisions.

## Files

- `runs/`: every arm. A, A′ (`Aprime`), E, P, P′ (`Pprime`), Pnd, Pnd′ (`Pndprime`) are §1;
  A2, P2 and R (idle JevBench, 800 / 2400) are §2; S, R-full (R in §3), R800, R′ (`Rprime`)
  are §3.
- `comparisons.md`: all `compare_runs.py` output.
- `logs/`: vLLM setup lines, `JEV-SPIKE` counter logs, and `step-probe/` (probe records
  and gzipped `JEV-STEP` scheduler logs).
- Spike code, on branch `spike/ds-004-mtp` only: `docker/spike/vllm/` (patched rejection
  sampler, step-logging scheduler), `compose.spike*.yaml`, `profiles/spike/`,
  `docker/spike/data/`, `scripts/spike_*.py`.
