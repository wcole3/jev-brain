# Sprint: the Planned queue (DS-007, DS-021, DS-023, DS-025, DS-026)

**Goal:** close out the five Planned tickets. Most are clean-up or short experiments.

**Status 2026-10-05:** review done; DS-023 and DS-026 resolved without code changes;
DS-025 and DS-007 need one shared GPU sweep (owner OK, ~3 h).

## Review findings

| Ticket | Finding | State |
|---|---|---|
| DS-026 gemma KV "shrink" | A reporting artefact. vLLM's figure = pool ÷ blocks per max-length request × max length, and gemma reserves ~5,445 sliding-window blocks per request whatever its length. The formula reproduces the 32k, 65k and 131k logs exactly; the pool stayed ~9.93–9.97k blocks. 65k kept. | Docs `d37a50d`; completion requested |
| DS-023 local latency +18–30 ms | Not code. Old (5eb50c9) and HEAD gateways against one vLLM, run back to back, differ by 2 ms; the same gateway varies by up to 30 ms between runs while other jobs load the CPU and the GPU runs at 87 °C. Vast boxes on current code hit 94–96 ms. | [A/B](../../results/archive/ds-023-latency-ab.md) `dc64e7d`; completion requested |
| DS-025 long prefill stalls | The ticket's fix named flags that don't exist in vLLM 0.30. Cause, from source: the long prompt takes the whole 8,192-token step until its last chunk, so nothing else gets admitted. On Qwen only 352 tokens per step stay free, so a real decision on a new state (>352 uncached tokens) would wait the whole 66 s; our 200-token probe hid this. The lever is `--long-prefill-token-threshold`. Priority scheduling doesn't help. | Ticket rewritten; [appendix §2a](../../appendix/ds007-scheduling.md); probe fixed `94d3f9d` |
| DS-007 chat starved by decisions | Its P0–P3/M1–M2 prefix rows were done in DS-008. Its baseline (2026-09-28, decider_chat, 32k) is stale. The same restarts serve DS-025, so run them as one sweep. | Plan below |
| DS-021 simple-jev prompt pieces | Its premise is gone: header gives qwen3.8 56.01, above simple-jev's 55.7. More layout search on the Index adds selection risk ([submission doc](../../decision-index-submission.md#selection-risk)). | Recommend close |

Other fixes made during the review:
- the gemma profile comment blamed KV for the stall; the cause is the step budget;
- `CLAUDE.md`'s "gemma is KV-bound at ~50k" is now pool-based.

## GPU sweep (DS-025 + DS-007)

**Where:** local box at 600 W, on an idle host; latency comparisons only within the sweep
(DS-023). Restart per row with
`EXTRA_ARGS="<profile's own args> <row args>" docker compose --env-file profiles/<p>.env up -d`.

**Per row:**
1. `scripts/long_context.py`: 200k tokens on Qwen, 60k on gemma, with the new fresh-state decision probe.
2. `bench.py --chat`: chat alone and under 4 systemone workers.
3. `latency.py`: idle latency-v1.

About 15 minutes per row with a warm restart.

| Row | Profile | Args added | Answers |
|---|---|---|---|
| S0 | qwen3.6 | none (baseline) | DS-025 and DS-007 baselines on current settings |
| S1–S3 | qwen3.6 | `--long-prefill-token-threshold` 3136 / 2352 / 1568 | DS-025 |
| B1–B3 | qwen3.6 | best T + `--max-num-batched-tokens` 2048 / 1568 / 784 | DS-007: does a smaller step budget keep chat decode up under decisions? |
| P1 | qwen3.6 | best row + `--scheduling-policy priority`, gateway `priority: 1` | DS-007 A1: chat TTFT while decisions queue (needs a gateway flag) |
| G0–G2 | gemma | none / T 4096 / T 2560 | DS-025 (keep T ≥ 2,560, the largest image/video item) |
| Q8 | qwen3.8 | best qwen3.6 row | confirm only; same architecture |

**Pass bar:**
- **DS-025:** with a long chat prefilling, decision p95 under 1 s and short-chat TTFT under 2 s.
- **DS-007:** chat TTFT p50 ≤ 0.5 s, ≥ 10 chunks/s under 4 workers, systemone ≥ 0.32 req/s, 0 preemptions.
- **Both:** idle latency within 5 ms of S0.
- **Shipping:** the chosen args go into each profile's `EXTRA_ARGS`. Rows longer than T
  are chunked differently, so a shipped T also needs a live stability check
  (`tests/live`) and a JevBench `--quick` accuracy check.

**Order:**
1. S0–S3, the DS-025 fix, about 1 h.
2. B and P rows, about 1 h.
3. G rows and Q8, about 1 h.

Stop after step 1 if T alone meets both pass bars.

## Not in this sprint

DS-027 (tie rate; Jev wire-format sign-off), DS-022, DS-024, and the Decision Index
submission items (owner decisions in the submission doc).
