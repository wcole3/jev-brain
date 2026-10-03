# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-02T194323Z
- repo commit: 6990a58
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
| **ours** | 126.7 | 657.4 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 341.3 |
| 4 | 274.7 |
| 5 | 467.5 |
| 6 | 621.7 |
| 10 | 363.3 |
| 12 | 114.8 |
| 20 | 119.8 |
| 21 | 117.8 |
| 22 | 1373.9 |
| 23 | 132.7 |
| 24 | 98.2 |
| 26 | 95.8 |
| 27 | 98.4 |
| 28 | 88.9 |
| 29 | 119.5 |
| 30 | 101.4 |
| 31 | 268.4 |
| 33 | 481.6 |
| 37 | 114.3 |
| 38 | 1569.6 |
| 39 | 103.2 |
| 40 | 98.5 |
| 41 | 114.0 |
| 42 | 129.9 |
| 44 | 98.0 |
| 48 | 173.1 |
| 50 | 247.2 |
| 56 | 429.0 |
| 57 | 98.5 |
| 58 | 93.7 |
| 59 | 248.9 |
| 61 | 111.8 |
| 62 | 259.9 |
