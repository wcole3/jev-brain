# DS-023: local latency regression is host noise, not gateway code

**2026-10-05, qwen3.6-27b, decider_chat, latency-v1.** Six runs against one vLLM
(`MAX_MODEL_LEN` 262144, 600 W), alternating three gateways:
- the compose gateway at HEAD (Docker, `:9000`);
- the 5eb50c9 gateway on the host (`:9001`), the commit of the 96 ms reference;
- the HEAD gateway on the host (`:9002`).

The summaries' "repo commit" is the client's commit (HEAD) for every run.

| Run | Gateway | Median ms | p95 ms | Short / mid / long tercile ms |
|---|---|---|---|---|
| [003917Z](qwen3.6-27b/2026-10-05T003917Z-latency/summary.md) | Docker HEAD | 138.3 | 666 | 101 / 138 / 472 |
| [004245Z](qwen3.6-27b/2026-10-05T004245Z-latency/summary.md) | host 5eb50c9 | 137.9 | 624 | 106 / 122 / 437 |
| [004639Z](qwen3.6-27b/2026-10-05T004639Z-latency/summary.md) | host HEAD | 157.6 | 684 | 127 / 139 / 485 |
| [005024Z](qwen3.6-27b/2026-10-05T005024Z-latency/summary.md) | Docker HEAD | 139.8 | 706 | 114 / 123 / 462 |
| [005349Z](qwen3.6-27b/2026-10-05T005349Z-latency/summary.md) | host 5eb50c9 | 125.5 | 664 | 104 / 113 / 433 |
| [005711Z](qwen3.6-27b/2026-10-05T005711Z-latency/summary.md) | host HEAD | 127.7 | 638 | 105 / 120 / 431 |

Terciles are rows ranked by the first run's time.

- **Code is not the cause.**
  - The same gateway moves up to 30 ms between runs: host HEAD gave 157.6, then 127.7.
  - The old and new gateways run back to back differ by 2 ms: 125.5 against 127.7.
  - Since 5eb50c9 the decide path has gained only a few float operations (calibration v2).
- **The host is.**
  - Another project's CPU-bound jobs held 2 of 8 cores during these runs.
  - The GPU was at 87 °C with the SM clock at 2,542 of 3,090 MHz.
  - Long rows slowed too (431–485 ms here, against 405 ms at 5eb50c9), so the extra cost is
    not only a fixed CPU cost per request.
- **Clean hosts reach the reference.** Vast boxes on code at 3e58290 or later measured
  94–96 ms. Those are the numbers the README and the submission quote.
- **For local latency numbers:** run on an idle host and compare runs only within one
  session.
