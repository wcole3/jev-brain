# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T041612Z
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
| **ours** | 104.9 | 685.4 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 389.4 |
| 4 | 251.8 |
| 5 | 457.5 |
| 6 | 621.1 |
| 10 | 341.6 |
| 12 | 89.0 |
| 20 | 88.8 |
| 21 | 80.7 |
| 22 | 1493.8 |
| 23 | 129.0 |
| 24 | 86.8 |
| 26 | 82.4 |
| 27 | 87.3 |
| 28 | 85.5 |
| 29 | 90.0 |
| 30 | 86.5 |
| 31 | 256.0 |
| 33 | 598.0 |
| 37 | 102.9 |
| 38 | 2291.4 |
| 39 | 166.5 |
| 40 | 87.8 |
| 41 | 90.8 |
| 42 | 128.4 |
| 44 | 90.6 |
| 48 | 170.1 |
| 50 | 238.0 |
| 56 | 407.5 |
| 57 | 89.3 |
| 58 | 84.8 |
| 59 | 263.4 |
| 61 | 104.7 |
| 62 | 240.4 |
