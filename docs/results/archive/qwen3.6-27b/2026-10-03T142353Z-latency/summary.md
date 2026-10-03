# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-03T142353Z
- repo commit: 3e58290
- host: RTX PRO 6000 Blackwell, 547/600 W, drv 610.43.02, PCIe 4x16, AMD Ryzen 9 5900XT 16-Core Processor (32 thr), 121 GB, vast 54020844
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6479149611375679, 'score': 1.9271133600869372, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.626739845878971, 'score': 1.9577583066935726, 'noul': 1.2842455905297372}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4836733616074274, 'score': 8.054659971948029, 'noul': 1.1446681550320104}, 'b': 0.2527877422356274, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 95.7 | 583.2 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 280.7 |
| 4 | 222.5 |
| 5 | 381.4 |
| 6 | 505.0 |
| 10 | 313.7 |
| 12 | 74.9 |
| 20 | 57.4 |
| 21 | 48.4 |
| 22 | 1296.4 |
| 23 | 116.4 |
| 24 | 56.7 |
| 26 | 50.2 |
| 27 | 57.2 |
| 28 | 50.1 |
| 29 | 77.1 |
| 30 | 58.5 |
| 31 | 229.3 |
| 33 | 514.1 |
| 37 | 82.3 |
| 38 | 2113.4 |
| 39 | 147.1 |
| 40 | 49.8 |
| 41 | 79.3 |
| 42 | 122.6 |
| 44 | 78.7 |
| 48 | 166.2 |
| 50 | 224.5 |
| 56 | 342.7 |
| 57 | 62.1 |
| 58 | 59.8 |
| 59 | 213.2 |
| 61 | 102.7 |
| 62 | 213.0 |
