# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-04T161833Z
- repo commit: fd72395
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
| **ours** | 106.6 | 638.8 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 376.8 |
| 4 | 250.8 |
| 5 | 444.2 |
| 6 | 571.0 |
| 10 | 341.3 |
| 12 | 87.3 |
| 20 | 82.8 |
| 21 | 78.1 |
| 22 | 1363.1 |
| 23 | 129.6 |
| 24 | 83.6 |
| 26 | 84.7 |
| 27 | 83.9 |
| 28 | 84.0 |
| 29 | 89.6 |
| 30 | 85.2 |
| 31 | 251.8 |
| 33 | 577.8 |
| 37 | 106.6 |
| 38 | 2289.8 |
| 39 | 121.1 |
| 40 | 83.7 |
| 41 | 106.5 |
| 42 | 129.1 |
| 44 | 88.1 |
| 48 | 175.0 |
| 50 | 239.0 |
| 56 | 410.5 |
| 57 | 88.7 |
| 58 | 85.5 |
| 59 | 239.7 |
| 61 | 108.7 |
| 62 | 234.2 |
