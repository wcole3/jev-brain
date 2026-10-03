# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-02T195633Z
- repo commit: 6990a58
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- layout: decider_chat
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6479149611375679, 'score': 1.9271133600869372, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.626739845878971, 'score': 1.9577583066935726, 'noul': 1.2842455905297372}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4836733616074274, 'score': 8.054659971948029, 'noul': 1.1446681550320104}, 'b': 0.2527877422356274, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 114.5 | 637.4 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 462.9 |
| 4 | 269.7 |
| 5 | 507.7 |
| 6 | 583.2 |
| 10 | 317.3 |
| 12 | 91.6 |
| 20 | 92.1 |
| 21 | 89.3 |
| 22 | 1298.1 |
| 23 | 158.9 |
| 24 | 95.1 |
| 26 | 91.6 |
| 27 | 90.6 |
| 28 | 94.6 |
| 29 | 93.1 |
| 30 | 92.7 |
| 31 | 254.1 |
| 33 | 539.9 |
| 37 | 118.8 |
| 38 | 1522.9 |
| 39 | 101.6 |
| 40 | 92.3 |
| 41 | 91.7 |
| 42 | 129.8 |
| 44 | 110.1 |
| 48 | 173.0 |
| 50 | 253.2 |
| 56 | 430.4 |
| 57 | 96.1 |
| 58 | 104.2 |
| 59 | 271.8 |
| 61 | 133.9 |
| 62 | 254.8 |
