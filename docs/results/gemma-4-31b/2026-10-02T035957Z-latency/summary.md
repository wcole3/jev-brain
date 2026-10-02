# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-02T035957Z
- repo commit: 7a5d9b6
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.84, PCIe 4x16, AMD Ryzen Threadripper 3960X 24-Core Processor (48 thr), 189 GB, vast 53799016
- design: latency-v1, our rows
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: decider_chat
- option_orders: identity
- temperatures: {'decider_chat': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'header': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'question_first': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 88.5 | 614.0 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 174.1 |
| 4 | 255.7 |
| 5 | 428.6 |
| 6 | 572.9 |
| 10 | 327.8 |
| 12 | 61.6 |
| 20 | 56.0 |
| 21 | 53.4 |
| 22 | 1743.0 |
| 23 | 137.0 |
| 24 | 57.7 |
| 26 | 53.3 |
| 27 | 54.7 |
| 28 | 53.1 |
| 29 | 84.4 |
| 30 | 63.4 |
| 31 | 217.2 |
| 33 | 289.7 |
| 37 | 89.1 |
| 38 | 1167.8 |
| 39 | 65.1 |
| 40 | 52.7 |
| 41 | 61.6 |
| 42 | 135.1 |
| 44 | 58.9 |
| 48 | 189.4 |
| 50 | 215.7 |
| 56 | 223.1 |
| 57 | 64.4 |
| 58 | 62.1 |
| 59 | 193.5 |
| 61 | 110.0 |
| 62 | 191.8 |
