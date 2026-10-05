# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T020208Z
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
| **ours** | 116.8 | 665.2 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 478.0 |
| 4 | 255.3 |
| 5 | 472.4 |
| 6 | 582.1 |
| 10 | 326.9 |
| 12 | 92.7 |
| 20 | 92.2 |
| 21 | 86.1 |
| 22 | 1396.9 |
| 23 | 138.1 |
| 24 | 94.1 |
| 26 | 89.9 |
| 27 | 91.1 |
| 28 | 87.4 |
| 29 | 94.5 |
| 30 | 94.1 |
| 31 | 252.3 |
| 33 | 629.0 |
| 37 | 116.1 |
| 38 | 2219.6 |
| 39 | 125.3 |
| 40 | 91.3 |
| 41 | 101.0 |
| 42 | 127.8 |
| 44 | 93.7 |
| 48 | 173.0 |
| 50 | 256.9 |
| 56 | 422.9 |
| 57 | 96.8 |
| 58 | 109.2 |
| 59 | 259.1 |
| 61 | 123.1 |
| 62 | 260.0 |
