# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-01T152315Z
- repo commit: 8223ef9
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- temperatures: {'decider_chat': {'choice': 1.943, 'score': 1.943, 'noul': 1.943}, 'header': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'question_first': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 115.5 | 644.0 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 327.6 |
| 4 | 280.1 |
| 5 | 498.6 |
| 6 | 618.3 |
| 10 | 320.5 |
| 12 | 88.1 |
| 20 | 88.2 |
| 21 | 97.6 |
| 22 | 1306.6 |
| 23 | 137.8 |
| 24 | 98.4 |
| 26 | 92.2 |
| 27 | 87.4 |
| 28 | 118.4 |
| 29 | 92.7 |
| 30 | 95.9 |
| 31 | 249.0 |
| 33 | 470.5 |
| 37 | 107.4 |
| 38 | 1505.8 |
| 39 | 98.9 |
| 40 | 91.5 |
| 41 | 109.8 |
| 42 | 146.9 |
| 44 | 86.5 |
| 48 | 161.5 |
| 50 | 249.1 |
| 56 | 413.4 |
| 57 | 94.9 |
| 58 | 90.8 |
| 59 | 240.6 |
| 61 | 126.1 |
| 62 | 241.4 |
