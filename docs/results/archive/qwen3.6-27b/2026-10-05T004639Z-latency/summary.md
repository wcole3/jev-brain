# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T004639Z
- repo commit: 94d3f9d
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
| **ours** | 157.6 | 683.9 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 444.8 |
| 4 | 282.5 |
| 5 | 503.9 |
| 6 | 634.1 |
| 10 | 359.2 |
| 12 | 126.6 |
| 20 | 127.9 |
| 21 | 127.8 |
| 22 | 1417.5 |
| 23 | 156.8 |
| 24 | 128.1 |
| 26 | 173.5 |
| 27 | 135.3 |
| 28 | 141.6 |
| 29 | 118.0 |
| 30 | 126.7 |
| 31 | 380.1 |
| 33 | 605.6 |
| 37 | 145.1 |
| 38 | 1762.5 |
| 39 | 196.5 |
| 40 | 131.6 |
| 41 | 129.7 |
| 42 | 151.3 |
| 44 | 172.5 |
| 48 | 191.0 |
| 50 | 282.1 |
| 56 | 518.3 |
| 57 | 149.0 |
| 58 | 125.4 |
| 59 | 319.4 |
| 61 | 148.6 |
| 62 | 270.4 |
