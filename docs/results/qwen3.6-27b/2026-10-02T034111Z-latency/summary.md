# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-02T034111Z
- repo commit: 7a5d9b6
- host: RTX PRO 6000 Blackwell, 450/600 W, drv 595.71.05, PCIe 5x16, AMD Eng Sample: 100-000001535-05 (512 thr), 373 GB, vast 53796457
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- temperatures: {'decider_chat': {'choice': 1.943, 'score': 1.943, 'noul': 1.943}, 'header': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'question_first': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 97.2 | 681.4 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 292.2 |
| 4 | 252.9 |
| 5 | 464.6 |
| 6 | 618.0 |
| 10 | 363.8 |
| 12 | 65.5 |
| 20 | 66.6 |
| 21 | 49.4 |
| 22 | 1601.9 |
| 23 | 143.6 |
| 24 | 51.3 |
| 26 | 49.7 |
| 27 | 51.2 |
| 28 | 49.3 |
| 29 | 90.6 |
| 30 | 67.2 |
| 31 | 262.5 |
| 33 | 464.4 |
| 37 | 96.2 |
| 38 | 1708.9 |
| 39 | 92.6 |
| 40 | 49.1 |
| 41 | 67.0 |
| 42 | 143.1 |
| 44 | 66.8 |
| 48 | 173.8 |
| 50 | 244.7 |
| 56 | 394.0 |
| 57 | 68.4 |
| 58 | 67.2 |
| 59 | 240.5 |
| 61 | 118.3 |
| 62 | 238.1 |
