# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T062414Z
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
| **ours** | 103.8 | 711.1 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 414.2 |
| 4 | 249.4 |
| 5 | 492.8 |
| 6 | 655.4 |
| 10 | 335.6 |
| 12 | 89.7 |
| 20 | 86.7 |
| 21 | 84.8 |
| 22 | 1621.7 |
| 23 | 127.5 |
| 24 | 86.5 |
| 26 | 85.1 |
| 27 | 82.5 |
| 28 | 83.6 |
| 29 | 91.7 |
| 30 | 86.0 |
| 31 | 250.4 |
| 33 | 640.4 |
| 37 | 99.6 |
| 38 | 2332.7 |
| 39 | 122.6 |
| 40 | 88.0 |
| 41 | 89.2 |
| 42 | 126.9 |
| 44 | 89.6 |
| 48 | 171.1 |
| 50 | 241.3 |
| 56 | 401.5 |
| 57 | 90.1 |
| 58 | 85.4 |
| 59 | 234.4 |
| 61 | 105.1 |
| 62 | 240.3 |
