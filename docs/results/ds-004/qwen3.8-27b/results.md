# DS-004 results: Qwen3.8-27B (step 3)

Detailed results behind [the DS-004 report](../README.md). `compare_runs.py` output is in
[comparisons.md](comparisons.md).

Run 2026-10-07, local RTX PRO 6000, vLLM v0.30.0. Repeats the Qwen3.6 R800 setup
([Qwen3.6 §3](../qwen3.6-27b/results.md)) on Qwen3.8-27B. S8 and R8 are each a full
`scripts/bench.py --profile qwen3.8-27b --chat`: cold and warm sweeps, throughput,
JevBench (1,682 rows), chat alone and under 4 decision workers. Chat rate is completion
tokens/s from the usage chunk, excluding the first token.

| arm | vLLM | MTP | threshold / budget | block drop | gateway `PREFIX_BLOCK` | KV cache | folder |
|---|---|---|---|---|---|---|---|
| S8 | stock | off | 784 / 2352 | — | 784 | 650 blocks × 784 | `runs/S8/` |
| A8′ | S8's stack | off | 784 / 2352 | — | 784 | 650 blocks × 784 | `runs/A8prime/` |
| R8 | patched | 3 drafts | 800 / 2400 | off | 800 (+ `WARM_MIN_PREFIX_TOKENS=800`) | 571 blocks × 800 | `runs/R8/` |
| R8′ | R8's stack | 3 drafts | 800 / 2400 | off | 800 | 571 blocks × 800 | `runs/R8prime/` |

- Block size checked first: with MTP 3, vLLM logged "Setting attention block size to 800
  tokens" and "kv lcm block sizes 800" (`logs/R8-vllm-setup.log`). Qwen3.8 has the same
  GDN shapes as Qwen3.6 (conv kernel 4, 16 key / 48 value heads of 128), so the 800 / 2400
  cap and budget and `PREFIX_BLOCK=800` were kept unchanged. S8 logged 784.
- vLLM logged a KV size of 499,687 tokens for S8 and 436,397 for R8, the same as Qwen3.6.
- S8 is the shipped `profiles/qwen3.8-27b.env`. R8 is
  `profiles/spike/qwen3.8-27b-mtp-nodrop-800-pad800.env` with `compose.spike.yaml` and
  `compose.spike-pad800.yaml`.
- `compose.spike-pad800.yaml` now mounts `docker/spike/data/${PROFILE}`, so it serves
  both models. `docker/spike/data/qwen3.8-27b/` holds copies of all three layouts, stamped
  `prefix_block: 800`. T and b are unchanged (fitted at 784), and each file carries a
  comment saying so.
- A8′ and R8′ are JevBench-only under 4 streaming chats
  (`scripts/spike_chat_load.py --vllm`), run like A′/P′ in `../runbook.md`.
- No arm had an error row: 0 in the four `raw.jsonl` files and in both chat-load files.

## Systemone latency

### Cold sweep, p50 / p95 ms

A new state for every request (nonce).

| state tokens | questions | options | S8 | R8 |
|---|---|---|---|---|
| 256 | 1 | 2 | 114 / 122 | 124 / 142 |
| 256 | 1 | 26 | 172 / 192 | 162 / 189 |
| 256 | 1 | 255 | 1196 / 1236 | 1298 / 1321 |
| 256 | 4 | 2 | 459 / 523 | 523 / 579 |
| 256 | 4 | 26 | 474 / 519 | 509 / 534 |
| 256 | 4 | 255 | 2652 / 2684 | 2770 / 2779 |
| 256 | 16 | 2 | 503 / 531 | 540 / 552 |
| 256 | 16 | 26 | 866 / 918 | 917 / 963 |
| 256 | 16 | 255 | 6145 / 6213 | 6217 / 6346 |
| 256 | 64 | 2 | 1214 / 1217 | 1343 / 1388 |
| 256 | 64 | 26 | 2615 / 2706 | 2712 / 2757 |
| 256 | 64 | 255 | 21111 / 21165 | 21231 / 21764 |
| 2048 | 1 | 2 | 479 / 486 | 495 / 516 |
| 2048 | 1 | 26 | 583 / 627 | 611 / 658 |
| 2048 | 1 | 255 | 1668 / 1723 | 1688 / 1812 |
| 2048 | 4 | 2 | 766 / 782 | 837 / 858 |
| 2048 | 4 | 26 | 824 / 853 | 829 / 891 |
| 2048 | 4 | 255 | 4190 / 4254 | 4401 / 4423 |
| 2048 | 16 | 2 | 899 / 956 | 910 / 921 |
| 2048 | 16 | 26 | 1295 / 1316 | 1337 / 1380 |
| 2048 | 16 | 255 | 7917 / 7948 | 8140 / 8169 |
| 2048 | 64 | 2 | 1749 / 1792 | 1958 / 2017 |
| 2048 | 64 | 26 | 3209 / 3272 | 3245 / 3417 |
| 2048 | 64 | 255 | 22871 / 23735 | 23096 / 23656 |
| 8192 | 1 | 2 | 1893 / 1978 | 1889 / 1909 |
| 8192 | 1 | 26 | 1998 / 2040 | 1943 / 1948 |
| 8192 | 1 | 255 | 3140 / 3210 | 3115 / 3124 |
| 8192 | 4 | 2 | 2219 / 2310 | 2239 / 2280 |
| 8192 | 4 | 26 | 2259 / 2293 | 2340 / 2447 |
| 8192 | 4 | 255 | 8954 / 9133 | 9366 / 9599 |
| 8192 | 16 | 2 | 2377 / 2528 | 2495 / 2509 |
| 8192 | 16 | 26 | 2809 / 2880 | 2870 / 2897 |
| 8192 | 16 | 255 | 12874 / 12948 | 13210 / 13532 |
| 8192 | 64 | 2 | 3540 / 3579 | 3656 / 3707 |
| 8192 | 64 | 26 | 4761 / 4892 | 4989 / 5072 |
| 8192 | 64 | 255 | 29401 / 29858 | 29503 / 29959 |

- R8 p50 is 0.94-1.14× S8 (median 1.03×); 32 of 36 cells are slower.
- The largest gaps are 2-option multi-question cells: 256 × 4 q +14%, 2,048 × 64 q +12%,
  256 × 64 q +11%.
- No cell shows the up-to-6× multi-question slowdown that Qwen3.6's R arm (padding to 784)
  had.
- Qwen3.6 R800 had its 8,192-token single-question cells 15-20% faster than S. Here they
  are within 3% of S8.

### Warm sweep: 16 questions sharing one 2,048-token state, 26 options

| | S8 | R8 |
|---|---|---|
| p50 / p95 ms | 784 / 839 | 772 / 789 |

### Throughput

Requests of 2,048 state tokens, 16 questions and 26 options.

| workers | S8 | R8 |
|---|---|---|
| 1 | 0.77 req/s | 0.78 |
| 4 | 1.01 | 0.97 |
| 16 | 1.02 | 0.98 |

### Cached prompt tokens per phase (vLLM counters): cached % (computed tokens)

| phase | S8 | R8 |
|---|---|---|
| cold | 83.6 (4,775,386) | 84.0 (4,743,632) |
| warm | 90.9 (22,398) | 91.0 (22,446) |
| throughput x1 | 86.1 (136,632) | 86.2 (137,784) |
| throughput x4 | 86.1 (182,176) | 86.2 (183,712) |
| throughput x16 | 86.1 (250,492) | 86.2 (235,381) |
| jevbench | 0.0 (552,075) | 0.0 (552,075) |
| chat | 86.1 (114,110) | 86.2 (51,919) |

- With padding to 800, R8 reuses prefixes as S8 does. The figures match Qwen3.6 S / R800
  to within 0.1 points.
- KV peak in the cold sweep is 30.0% for S8 and 97.0% for R8, as on Qwen3.6 (30.0 / 97.0).
  No preemptions in either arm.
- The "chat" phase's counters also include the 4 decision workers that run during it.

## JevBench, idle

Rows by prompt length: 1,382 under 784 tokens, 300 at 784-1,568 tokens. The bands use
784 for every arm, as the Qwen3.6 report does. The 300 band rows are 997-1,049 tokens, so
they are above 800 too.

| arm | accuracy | overall p50 / p95 ms | < 784 p50 / p95 | 784-1,568 p50 / p95 | ECE |
|---|---|---|---|---|---|
| S8 | 89.7% | 108 / 267 | 104 / 131 | 259 / 293 | 0.063 |
| R8 | 89.7% | 114 / 284 | 110 / 145 | 269 / 317 | 0.056 |

- Band accuracy is 91.0% under 784 tokens and 84.0% at 784-1,568 in both arms.
- R8 costs +6 ms at p50 under 784 tokens and +10 ms in the band. On Qwen3.6, R800 cost
  +19 and +33 ms.

## Chat

One request per prompt, `max_tokens` 512. Under load, 4 workers send 2,048-token,
16-question decisions back to back.

| prompt | load | S8 tok/s, TTFT | R8 |
|---|---|---|---|
| short | none | 27.5, 138 ms | 63.7, 124 ms |
| long | none | 27.3, 126 ms | 45.0, 156 ms |
| short | 4 decision workers | 7.8, 6,814 ms | 17.9, 2,799 ms |
| long | 4 decision workers | 16.1, 275 ms | 32.7, 578 ms |

- These are single samples: TTFT under load swings by seconds with the decision queue.
- Spec-decode acceptance over the bench's 4 chats comes from vLLM's 10 s `SpecDecoding
  metrics` log lines (03:55:43-03:56:03 UTC, before the R8′ load started). It was 44.8% of
  1,158 draft tokens, mean accepted length 2.34.
- Qwen3.6 R800 had 73.7% of 1,599 draft tokens, length 3.21.
- The next log interval (03:56:16) overlaps the R8′ load start and is excluded. With it
  included, acceptance is 45.7%.

## R8′ against A8′ (JevBench under 4 streaming chats)

| arm | config | error rows | accuracy | p50 / p95 ms | < 784 p50 / p95 | 784-1,568 p50 / p95 | chats | chat p50 tok/s | chat p50 TTFT | acceptance |
|---|---|---|---|---|---|---|---|---|---|---|
| A8′ | stock, MTP off | 0 | 89.6% | 302 / 599 | 296 / 346 | 566 / 683 | 96 | 19.6 | 263 ms | — |
| **R8′** | patched, MTP, 800 / 2400, block drop off, pad 800 | 0 | 89.7% | 389 / 659 | 379 / 467 | 638 / 713 | 177 | 29.3 | 345 ms | 30.6%, length 1.92 |

- R8′ is 83 ms slower than A8′ at p50 under 784 tokens and 72 ms slower in the 784-1,568
  band. On Qwen3.6, R′ was 60 ms and 164 ms slower than A′.
- Chat p50 decode rose from 19.6 to 29.3 tok/s (1.49×), and 1.84× as many chats finished.
  On Qwen3.6 the rise was 18.5 → 37.8 tok/s (2.04×).
- Acceptance on the story prompts is 30.6% for Qwen3.8 against 50.0% for Qwen3.6 R′.
  Per-position acceptance during the load, weighted by drafts, is 0.533 / 0.255 / 0.130.
  vLLM warns that `num_speculative_tokens > 1` reruns the single MTP layer and may lower
  acceptance.

## Drift

Each cell is max / p99 of each row's max |Δp|. Bands are by prompt tokens. Flips are
counted with the largest baseline top-two gap among them.

There is **no stock restart pair for Qwen3.8**, so its own restart floor is unknown. The
yardstick is Qwen3.6's: a plain stock restart (A2 vs A) moved max |Δp| by 0.079, with
3 flips. The same-instance figures (A8′ vs S8, R8′ vs R8) are lower floors. On Qwen3.6, an idle
instance repeated itself bit for bit.

| comparison | < 784 | 784-1,568 | all | flips (largest baseline gap) |
|---|---|---|---|---|
| Qwen3.6 A2 vs A (stock restart, reference) | 0.042 / 0.024 | 0.079 / 0.046 | 0.079 / 0.030 | 3 (0.025) |
| A8′ vs S8 (same instance, load vs idle) | 0.032 / 0.017 | 0.021 / 0.014 | 0.032 / 0.017 | 2 (0.065) |
| R8′ vs R8 (same instance, load vs idle) | 0.033 / 0.026 | 0.024 / 0.017 | 0.033 / 0.024 | 3 (0.065) |
| **R8 vs S8** (across restart) | 0.033 / 0.029 | 0.059 / 0.032 | 0.059 / 0.029 | 7 (0.057) |
| **R8′ vs A8′** (across restart) | 0.045 / 0.030 | 0.059 / 0.038 | 0.059 / 0.031 | 6 (0.065) |

- No flip has a baseline top-two gap above 0.10. The largest is 0.065
  (`panoramic:avg_threshold:309`, R8′ vs R8 and R8′ vs A8′).
- R8 vs S8 and R8′ vs A8′ stay below Qwen3.6's restart figure (0.079) in every band. Their
  p99 is 0.029-0.038, against 0.024-0.046 for Qwen3.6 A2 vs A.
- R8 vs S8 has 7 flips, against 3 for Qwen3.6's restart pair. Of the 7, 3 are
  wrong→right, 3 right→wrong and 1 wrong→wrong. Accuracy is equal (89.7%).
- Within 3.8, the same-instance pairs reach 0.032-0.033. The cross-restart pairs reach
  0.059, which comes from `banking77:banking77:275`, the most sensitive set on Qwen3.6
  too. Without a 3.8 restart pair, the gap between 0.033 and 0.059 cannot be split
  between restart noise and MTP.
- Qwen3.6's outlier row (`typed_decisions:invoice_processing:1370`) moves by 0.013 here:
  its level-3 probability is 0.606 in S8 and A8′ and 0.592 in R8 and R8′.
- ECE is 0.063 in S8 and A8′, against 0.056 in R8 and 0.057 in R8′.
- `comparisons.md` hold the
  `compare_runs.py` output.

## Spike counter (`JEV-SPIKE`)

The counter logs the first and every 200th rejection-sampler step that carries label-id
rows.

- R8 bench, chat-under-decisions phase: step 1 only, 2 label-id rows
  (`logs/R8-spike.log`).
- R8′: the count runs on from the R8 bench on the same instance. It reached step 2,000,
  with 2,088 label-id rows in total (`logs/R8-and-R8prime-spike.log`). The patched path
  ran under chat load.

## Files

- Runs: `runs/S8/`, `runs/R8/`, `runs/A8prime/`, `runs/R8prime/`.
- Chat load: `runs/{A8prime,R8prime}/chat-load.{jsonl,txt}`.
- `logs/`:
  - vLLM setup lines: `{S8,R8}-vllm-setup.log`;
  - spike counter: `R8-spike.log`, `R8-and-R8prime-spike.log`;
  - bench stdout: `*-bench.out`.
- Config:
  - `profiles/spike/qwen3.8-27b-mtp-nodrop-800-pad800.env`;
  - `compose.spike-pad800.yaml` (now keyed on `${PROFILE}`);
  - `docker/spike/data/qwen3.8-27b/*/{calibration,labels}.json`.
