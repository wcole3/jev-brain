# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T003917Z
- repo commit: 94d3f9d
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6479149611375679, 'score': 1.9271133600869372, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.626739845878971, 'score': 1.9577583066935726, 'noul': 1.2842455905297372}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4836733616074274, 'score': 8.054659971948029, 'noul': 1.1446681550320104}, 'b': 0.2527877422356274, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 138.3 | 666.5 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 533.0 |
| 4 | 316.0 |
| 5 | 504.6 |
| 6 | 584.1 |
| 10 | 325.9 |
| 12 | 110.7 |
| 20 | 103.8 |
| 21 | 108.2 |
| 22 | 1253.9 |
| 23 | 147.4 |
| 24 | 102.6 |
| 26 | 106.6 |
| 27 | 94.6 |
| 28 | 102.5 |
| 29 | 110.2 |
| 30 | 135.3 |
| 31 | 284.7 |
| 33 | 529.9 |
| 37 | 117.3 |
| 38 | 1561.9 |
| 39 | 205.1 |
| 40 | 129.4 |
| 41 | 119.8 |
| 42 | 155.4 |
| 44 | 128.8 |
| 48 | 222.4 |
| 50 | 261.2 |
| 56 | 524.1 |
| 57 | 111.4 |
| 58 | 97.4 |
| 59 | 269.7 |
| 61 | 122.2 |
| 62 | 247.7 |
