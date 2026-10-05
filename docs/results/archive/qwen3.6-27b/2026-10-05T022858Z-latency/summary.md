# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T022858Z
- repo commit: c37c95a
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6479149611375679, 'score': 1.9271133600869372, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.626739845878971, 'score': 1.9577583066935726, 'noul': 1.2842455905297372}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4836733616074274, 'score': 8.054659971948029, 'noul': 1.1446681550320104}, 'b': 0.2527877422356274, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 134.7 | 696.8 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 395.8 |
| 4 | 251.7 |
| 5 | 487.4 |
| 6 | 637.2 |
| 10 | 344.7 |
| 12 | 113.0 |
| 20 | 112.7 |
| 21 | 103.1 |
| 22 | 1374.4 |
| 23 | 138.6 |
| 24 | 98.2 |
| 26 | 101.2 |
| 27 | 104.0 |
| 28 | 90.7 |
| 29 | 105.5 |
| 30 | 96.0 |
| 31 | 257.8 |
| 33 | 655.6 |
| 37 | 139.4 |
| 38 | 2416.6 |
| 39 | 145.8 |
| 40 | 143.9 |
| 41 | 131.6 |
| 42 | 155.4 |
| 44 | 132.4 |
| 48 | 225.1 |
| 50 | 280.5 |
| 56 | 492.5 |
| 57 | 119.4 |
| 58 | 124.1 |
| 59 | 257.7 |
| 61 | 118.0 |
| 62 | 246.5 |
