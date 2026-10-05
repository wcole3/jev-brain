# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T064320Z
- repo commit: 6de9f1d
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
| **ours** | 103.9 | 709.5 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 380.7 |
| 4 | 249.6 |
| 5 | 485.3 |
| 6 | 665.7 |
| 10 | 332.9 |
| 12 | 87.4 |
| 20 | 86.4 |
| 21 | 87.3 |
| 22 | 1611.8 |
| 23 | 128.4 |
| 24 | 89.1 |
| 26 | 89.2 |
| 27 | 80.8 |
| 28 | 84.3 |
| 29 | 89.4 |
| 30 | 84.6 |
| 31 | 247.1 |
| 33 | 638.3 |
| 37 | 94.7 |
| 38 | 2361.9 |
| 39 | 158.3 |
| 40 | 81.7 |
| 41 | 90.6 |
| 42 | 126.7 |
| 44 | 87.5 |
| 48 | 168.6 |
| 50 | 239.2 |
| 56 | 408.7 |
| 57 | 92.1 |
| 58 | 87.1 |
| 59 | 237.0 |
| 61 | 106.2 |
| 62 | 243.8 |
