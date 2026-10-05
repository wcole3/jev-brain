# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T013715Z
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
| **ours** | 130.6 | 697.4 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 371.2 |
| 4 | 271.2 |
| 5 | 490.2 |
| 6 | 604.2 |
| 10 | 348.8 |
| 12 | 109.8 |
| 20 | 105.6 |
| 21 | 91.9 |
| 22 | 1294.2 |
| 23 | 139.8 |
| 24 | 93.8 |
| 26 | 87.4 |
| 27 | 87.7 |
| 28 | 87.4 |
| 29 | 93.8 |
| 30 | 90.9 |
| 31 | 245.8 |
| 33 | 736.2 |
| 37 | 128.7 |
| 38 | 2324.7 |
| 39 | 198.9 |
| 40 | 104.9 |
| 41 | 113.6 |
| 42 | 157.2 |
| 44 | 120.7 |
| 48 | 220.6 |
| 50 | 321.2 |
| 56 | 540.1 |
| 57 | 122.7 |
| 58 | 104.5 |
| 59 | 245.9 |
| 61 | 124.4 |
| 62 | 259.2 |
