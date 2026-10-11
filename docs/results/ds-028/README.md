# DS-028: restart-to-restart decision noise

Restarting the same vLLM stack moves `/v1/systemone` label probabilities. How much, and why?
Measured 2026-10-11 on one RTX PRO 6000 (510 W) with vLLM v0.30.0, Qwen3.6-27B (bf16),
JevBench only (1,682 rows), idle. Stopped after the floor measurement: the owner judged the
variance acceptable, so the cause was bounded, not pinned down.

## Short answer

- **A restart moves a typical row by ~0.03 (p99), and a few rows by up to 0.15.** That holds
  for the shipped MTP profile and for MTP off alike.
- **Within one running instance, results repeat bit for bit.** A rerun on the same instance
  matched exactly in both arms.
- **The noise is discrete, chosen at startup.** The worst row took only 4 distinct value sets
  across 8 restarts, and the same sets appear in both arms.
- **The two-instance MTP match in DS-004 (R800 vs default-mtp, max |Δp| 0.0000) was luck.**
  MTP does not make restarts reproducible.
- **Decision: the variance is acceptable.** No change to test limits or the stack.

## Arms

| arm | settings | restarts |
|---|---|---|
| M | shipped profile: MTP 3, cap / budget 800 / 2400, `PREFIX_BLOCK=800` | 4 (+1 same-instance rerun) |
| N | MTP off: 784 / 2352, `PREFIX_BLOCK=784` (loads `calibration-784.json`) | 4 (+1 same-instance rerun) |

Each restart was a full `docker compose down` / `up` followed by `scripts/bench.py --jevbench-only`.
`TRITON_PRINT_AUTOTUNING=1` was set on every start. That setting only logs; it does not
change which kernel runs.

## Drift

Max |Δp| over every pair of restarts in an arm, and p99 of each row's max |Δp|. Bands
are by gateway-reported input tokens (padding included).

| arm | max | p99 | < 784 max | 784-1,568 max | flips per pair | same-instance rerun |
|---|---|---|---|---|---|---|
| M (MTP on) | 0.153 | 0.032 | 0.153 | 0.074 | 1-4 | identical |
| N (MTP off) | 0.144 | 0.031 | 0.144 | 0.091 | 3-5 | identical |

- Only 4 of 1,682 rows moved more than 0.05 in the worst pair (M-2 vs M-3).
- The largest mover is `typed_decisions:invoice_processing:1370`, a 397-token score row. Its
  levels 2 / 3 swap between ~0.27 / 0.57 and ~0.42 / 0.42. The expected level then crosses a
  rounding boundary, so its answer flips even though the top-two gap is 0.31.
- Banking77 (77 close options, 1,000+ tokens) drifts 0.05-0.09 and causes the other flips.
  No banking77 flip had a baseline top-two gap above 0.10.
- These figures match DS-004's single stock restart pair (0.079 max, 3 flips) in shape, with a
  longer tail now that there are more pairs.

## What it is not

- **Triton FLA autotune:** on sm_120 with CUDA 13 the GDN prefill uses FlashInfer
  (`Using FlashInfer GDN prefill kernel`), not the autotuned Triton chunk kernels.
  `TRITON_PRINT_AUTOTUNING` printed no Triton tuning on any start.
- **FlashInfer autotune:** it runs at startup but saved 0 configs on every start.
- **KV layout:** KV cache size was identical within each arm (436,397 tokens for M, 499,687
  tokens for N).
- **Batching:** the bench sends rows one at a time, and same-instance reruns are exact.
- **Prompt length alone:** whether a row matches across two restarts does not follow from
  its token count.

Not tested (left open): `VLLM_TRITON_FORCE_FIRST_CONFIG=1`, FlashInfer autotune off,
the Triton GDN prefill backend, and cuBLAS determinism settings.

## What this means

- Comparisons across restarts (A/B arms, `tests/live/test_offline_matches_live.py`) carry
  this floor: ~0.03 typical, up to ~0.15 on rare rows, and a few flips per 1,682 rows.
- The stability test (`tests/live/test_stability.py`) compares within one instance, so its 0.05
  soft limit is unaffected.
- To tell a real change from restart noise, compare it against several restarts of the
  baseline, not one.

## Files

Kept locally in `.cache/ds028/` (git-ignored):
- `restart_loop.sh ARM COUNT [--repeat]` runs the restart loop.
- `compare_arm.py DIR...` compares every pair of runs.
- `runs/<arm>-<i>/` holds `bench/raw.jsonl`, `vllm.log`, `gateway.log`, `env.txt`.
