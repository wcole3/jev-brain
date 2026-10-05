# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T032726Z
- repo commit: c2e5f51
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6479149611375679, 'score': 1.9271133600869372, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.626739845878971, 'score': 1.9577583066935726, 'noul': 1.2842455905297372}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4836733616074274, 'score': 8.054659971948029, 'noul': 1.1446681550320104}, 'b': 0.2527877422356274, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 115.3 | 726.8 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 389.5 |
| 4 | 260.5 |
| 5 | 471.6 |
| 6 | 661.7 |
| 10 | 343.2 |
| 12 | 96.1 |
| 20 | 92.8 |
| 21 | 88.3 |
| 22 | 1484.8 |
| 23 | 133.8 |
| 24 | 93.3 |
| 26 | 97.0 |
| 27 | 96.0 |
| 28 | 92.6 |
| 29 | 104.8 |
| 30 | 95.5 |
| 31 | 280.5 |
| 33 | 624.7 |
| 37 | 110.3 |
| 38 | 2465.1 |
| 39 | 129.1 |
| 40 | 96.2 |
| 41 | 97.5 |
| 42 | 132.5 |
| 44 | 96.5 |
| 48 | 174.4 |
| 50 | 264.7 |
| 56 | 430.5 |
| 57 | 95.5 |
| 58 | 94.0 |
| 59 | 250.9 |
| 61 | 113.0 |
| 62 | 257.8 |
