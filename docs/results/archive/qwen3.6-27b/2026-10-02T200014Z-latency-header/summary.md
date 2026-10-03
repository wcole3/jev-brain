# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-02T200014Z
- repo commit: 6990a58
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- layout: header
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6479149611375679, 'score': 1.9271133600869372, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.626739845878971, 'score': 1.9577583066935726, 'noul': 1.2842455905297372}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4836733616074274, 'score': 8.054659971948029, 'noul': 1.1446681550320104}, 'b': 0.2527877422356274, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 119.7 | 674.5 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 394.6 |
| 4 | 257.6 |
| 5 | 468.3 |
| 6 | 592.9 |
| 10 | 362.0 |
| 12 | 93.2 |
| 20 | 92.1 |
| 21 | 95.2 |
| 22 | 1389.8 |
| 23 | 139.0 |
| 24 | 106.6 |
| 26 | 99.9 |
| 27 | 96.9 |
| 28 | 105.9 |
| 29 | 103.8 |
| 30 | 94.4 |
| 31 | 276.0 |
| 33 | 685.6 |
| 37 | 110.2 |
| 38 | 2292.0 |
| 39 | 171.8 |
| 40 | 103.7 |
| 41 | 118.7 |
| 42 | 136.3 |
| 44 | 95.7 |
| 48 | 196.3 |
| 50 | 258.0 |
| 56 | 483.9 |
| 57 | 100.6 |
| 58 | 97.0 |
| 59 | 251.7 |
| 61 | 115.2 |
| 62 | 246.3 |
