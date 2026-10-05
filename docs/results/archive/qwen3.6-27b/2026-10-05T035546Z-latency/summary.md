# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T035546Z
- repo commit: ee88d8f
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
| **ours** | 117.6 | 737.6 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 385.6 |
| 4 | 251.5 |
| 5 | 506.2 |
| 6 | 665.0 |
| 10 | 344.1 |
| 12 | 101.4 |
| 20 | 104.4 |
| 21 | 102.5 |
| 22 | 1648.4 |
| 23 | 140.1 |
| 24 | 97.7 |
| 26 | 96.5 |
| 27 | 85.5 |
| 28 | 83.0 |
| 29 | 92.1 |
| 30 | 90.0 |
| 31 | 252.2 |
| 33 | 641.6 |
| 37 | 95.5 |
| 38 | 2455.9 |
| 39 | 122.6 |
| 40 | 84.5 |
| 41 | 93.9 |
| 42 | 133.3 |
| 44 | 93.7 |
| 48 | 169.2 |
| 50 | 236.5 |
| 56 | 446.8 |
| 57 | 90.7 |
| 58 | 109.0 |
| 59 | 260.0 |
| 61 | 133.5 |
| 62 | 261.8 |
