# DS-025 / DS-007 scheduler sweep (2026-10-05)

**Question:**
- **DS-025:** can decisions and short chats stay responsive while one long chat prefills?
- **DS-007:** can chat keep decoding while decisions load the server?

**Setup:**
- Local RTX PRO 6000. Power 600 W for rows S0–S2, then 540 W after a GPU driver crash, which was not caused by the settings.
- Each row is a fresh vLLM start with the listed arguments added to the profile's own.
- Each row ran three tools:
  - `scripts/long_context.py`: one 200k chat (Qwen) or 60k chat (gemma), with probes alongside it;
  - `bench.py --quick --chat`: chat under 4 systemone workers, throughput, JevBench quick;
  - `latency.py`: idle latency-v1.
- Driver and logs: `.cache/sweep/` (git-ignored).

## Results

**Meaning of the arguments:**
- T is `--long-prefill-token-threshold`: the most prompt tokens one request may take per step.
- B is `--max-num-batched-tokens`: the step budget for everything. The default is 8192.
- "prio" is `--scheduling-policy priority` plus gateway `SYSTEMONE_PRIORITY=1`, so chat is admitted ahead of decisions.

**Columns:**
- "During" columns measure while the long chat prefills.
- **Worst decision** is the slowest probe after dropping the start-up spike (see below). "Whole prefill" means the probe waited for the entire prefill.
- **Fresh** decisions send a new, never-cached ~1.5k-token state each time.

| Row | Args | Long-prompt TTFT s | Worst decision s | Worst fresh decision s | Chat chunks/s under 4 workers | Systemone req/s ×4 | JevBench quick % | Long-context run |
|---|---|---|---|---|---|---|---|---|
| S0 | none (qwen3.6) | 64.7 | whole prefill (51) | whole prefill (63) | 1.8 | 1.0 | 74.0 | [run](qwen3.6-27b/2026-10-05T012406Z-long-context/summary.md) |
| S1 | T 3136 | 67.9 | 3.0 | 4.4 | 1.8 | 1.1 | 74.0 | [run](qwen3.6-27b/2026-10-05T014821Z-long-context/summary.md) |
| S2 | T 2352 | 70.2 | 3.2 | 4.2 | 1.7 | 1.1 | 74.0 | [run](qwen3.6-27b/2026-10-05T021415Z-long-context/summary.md) |
| S3 | T 1568 | 79.7 | 2.3 | 3.1 | 1.9 | 1.0 | 74.0 | [run](qwen3.6-27b/2026-10-05T031410Z-long-context/summary.md) |
| S4 | T 784 | 87.4 | 1.2 | 1.6 | 2.2 | 1.0 | 74.0 | [run](qwen3.6-27b/2026-10-05T034351Z-long-context/summary.md) |
| B1 | T 1568, B 3136 | 77.2 | 2.1 | 2.8 | 2.3 | 1.0 | 74.0 | [run](qwen3.6-27b/2026-10-05T040408Z-long-context/summary.md) |
| B2 | T 784, B 1568 | 78.7 | whole prefill (70) | whole prefill (77) | 4.8 | 1.0 | 74.0 | [run](qwen3.6-27b/2026-10-05T042450Z-long-context/summary.md) |
| B3 | T 784, B 2352 | 85.9 | 1.2 | 1.6 | 3.0 | 1.0 | 74.0 | [run](qwen3.6-27b/2026-10-05T061411Z-long-context/summary.md) |
| **P1** | **T 784, B 2352, prio** | 86.1 | 1.2 | 1.6 | 3.0 | 1.0 | 74.0 | [run](qwen3.6-27b/2026-10-05T063258Z-long-context/summary.md) |
| Q8 | P1 on qwen3.8 | 84.5 | 1.2 | 1.6 | 3.0 | 1.0 | 90.0 | [run](qwen3.8-27b/2026-10-05T071843Z-long-context/summary.md) |
| G0 | none (gemma) | 33.7 | whole prefill (33) | whole prefill (32) | 0.5 | 0.8 | 72.0 | [run](gemma-4-31b/2026-10-05T044058Z-long-context/summary.md) |
| G1 | T 4096 | 33.9 | 5.9 | 6.2 | 0.5 | 0.8 | 72.0 | [run](gemma-4-31b/2026-10-05T051129Z-long-context/summary.md) |
| G2 | T 2560 | 35.0 | 3.8 | 3.8 | 0.6 | 0.8 | 74.0 | [run](gemma-4-31b/2026-10-05T054332Z-long-context/summary.md) |
| G3 | T 1024, video off | 36.2 | 1.8 | 2.5 | 0.7 | 0.7 | 72.0 | [run](gemma-4-31b/2026-10-05T065012Z-long-context/summary.md) |

Idle latency medians ranged 104–135 ms with no pattern by row: host noise, as in DS-023.
Live suite on P1 settings: 14/14 pass.

## What we learned

- **The threshold fixes DS-025.** Without it, a long prompt takes every step and everything
  else waits for the whole prefill. On Qwen, T = 784 keeps decisions at or below 1.2 s at
  200k, at a cost of +33% long-prompt TTFT (65 → 86 s).
  - Each step costs ~0.4 s at long context however small the chunk, so the gains shrink
    as T drops.
- **Qwen rule: B − T must exceed 784.** In B2 (B 1568, T 784) less than one 784-token Mamba
  block was left per step. A decision then got nothing and blocked the queue for the whole
  prefill.
- **Priority helps chat TTFT, not chat speed.** P1 cut short-chat TTFT during a long
  prefill (6.5 s → 1.0 s) and under decision load (long prompt 2.1 s → 1.2 s), with 0
  preemptions.
- **DS-007 isn't solved by vLLM settings.** Chat under 4 decision workers went from 1.8 to
  3.0 chunks/s on Qwen and stayed at 0.5–0.7 on gemma, against a ≥ 10 bar. Smaller budgets
  (B2: 4.8) break DS-025. The remaining lever is the gateway governor: fewer decision rows
  in flight while chat streams (DS-007 task G1).
- **The ~7 s start-up spike is a one-time warm-up.** The first long prefill after a vLLM
  start stalls the next decision ~7 s, at any length (60k gemma, 200k Qwen).
  - vLLM's API server stays responsive throughout, and tokenizing 200k tokens takes 0.45 s.
  - A second long prompt on the same process, uncached, shows no spike (spike test in
    `.cache/sweep/spike*.txt`).
- **Gemma needs T ≤ ~1k for ~2 s decisions.** That requires `--limit-mm-per-prompt
  {"video":0}`, because a video item is 2,496 tokens and an item larger than T is never
  scheduled. Images are at most 280 tokens. Gemma's throughput dropped 0.8 → 0.7 req/s
  at T 1024.

## DS-007 decision governor (2026-10-05, branch ds-007-governor)

**Setup:**
- Profiles at their shipped vLLM settings (P1 for Qwen, G3 for gemma). Only the gateway's `GOVERNOR_DUTY`/`GOVERNOR_WAVE` changed between rows.
- Probe (`.cache/sweep/gov.py`): 4 decision workers sending fresh 2,048-token states × 16 questions × 26 options, plus back-to-back 512-token streaming chats, for 60 s.
- Decisions per second counts only those finished while chat streamed.
- n = 2–4 chats per row, so TTFT is noisy. The duty-1.0 rows' TTFT includes waiting behind full decision batches.

| Profile | Duty:wave | Chat TTFT p50 ms | Chat chunks/s | Decisions/s while chat streams | Decision p50 ms |
|---|---|---|---|---|---|
| qwen3.6 | 1.0 (off) | 4,393 | 3.0 | 0.98 | 3,916 |
| qwen3.6 | 0.3:4 | 372 | 23.0 | 0.20 | 18,807 |
| qwen3.6 | 0.15:4 | 230 | 25.3 | 0.11 | 34,751 |
| qwen3.6 | 0.3:2 | 252 | 23.2 | 0.11 | 26,012 |
| qwen3.6 | 0.5:4 | 3,948 (n=2) | 18.6 | 0.26 | 12,660 |
| qwen3.6 | 0.5:8 | 352 | 18.2 | 0.38 | 10,526 |
| **qwen3.6** | **0.6:8 (shipped)** | **367** | **16.8** | **0.46** | **8,716** |
| gemma | 1.0 (off) | 10,472 | 0.6 | 0.67 | 5,866 |
| gemma | 0.3:4 | 831 | 14.7 | 0.20 | 23,736 |
| gemma | 0.15:4 | 448 | 17.1 | 0.16 | 5,800 |
| gemma | 0.5:4 | 785 | 12.3 | 0.31 | 15,083 |
| **gemma** | **0.5:8 (shipped)** | **643** | **10.7** | **0.32** | **13,514** |

- **The pass bar is ≥ 10 chunks/s, ≥ 0.32 decisions/s and TTFT ≤ 0.5 s.**
  - Qwen 0.6:8 meets all three.
  - Gemma 0.5:8 meets the first two; its TTFT of 0.64 s is just over.
- **Bigger waves help decisions at the same duty** (0.5:4 → 0.5:8). Each call carries more rows, so more of each decision runs per gap.
- **Decisions are slower only while a chat streams.** With no chat decoding the governor passes calls straight through.
- **Live suite** on qwen3.6 at 0.6:8: 14/14. The chat-disconnect abort test passed, and the gateway showed 0 chats decoding afterwards.
- qwen3.8 shares Qwen's settings because the architecture is the same; it was not measured.
