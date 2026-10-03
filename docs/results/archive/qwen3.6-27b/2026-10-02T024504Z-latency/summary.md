# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-02T024504Z
- repo commit: 5eb50c9
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- temperatures: {'decider_chat': {'choice': 1.943, 'score': 1.943, 'noul': 1.943}, 'header': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'question_first': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 95.8 | 630.7 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 332.0 |
| 4 | 237.0 |
| 5 | 446.5 |
| 6 | 570.6 |
| 10 | 321.4 |
| 12 | 85.9 |
| 20 | 85.6 |
| 21 | 79.6 |
| 22 | 1381.7 |
| 23 | 132.8 |
| 24 | 81.6 |
| 26 | 82.3 |
| 27 | 84.4 |
| 28 | 78.6 |
| 29 | 87.5 |
| 30 | 81.5 |
| 31 | 248.6 |
| 33 | 472.6 |
| 37 | 96.2 |
| 38 | 1596.3 |
| 39 | 153.1 |
| 40 | 86.2 |
| 41 | 87.1 |
| 42 | 129.3 |
| 44 | 80.8 |
| 48 | 159.2 |
| 50 | 243.6 |
| 56 | 409.7 |
| 57 | 85.8 |
| 58 | 81.6 |
| 59 | 245.1 |
| 61 | 106.9 |
| 62 | 245.5 |
