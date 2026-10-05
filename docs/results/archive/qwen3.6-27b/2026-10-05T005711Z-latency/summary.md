# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T005711Z
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
| **ours** | 127.7 | 637.6 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 337.2 |
| 4 | 244.0 |
| 5 | 472.0 |
| 6 | 594.6 |
| 10 | 329.5 |
| 12 | 97.3 |
| 20 | 104.9 |
| 21 | 114.7 |
| 22 | 1331.5 |
| 23 | 132.9 |
| 24 | 98.5 |
| 26 | 111.2 |
| 27 | 105.7 |
| 28 | 99.8 |
| 29 | 121.2 |
| 30 | 117.7 |
| 31 | 262.2 |
| 33 | 498.1 |
| 37 | 109.6 |
| 38 | 1498.6 |
| 39 | 116.6 |
| 40 | 104.5 |
| 41 | 98.4 |
| 42 | 131.7 |
| 44 | 116.2 |
| 48 | 240.4 |
| 50 | 278.9 |
| 56 | 490.8 |
| 57 | 110.0 |
| 58 | 116.4 |
| 59 | 243.8 |
| 61 | 117.8 |
| 62 | 243.1 |
