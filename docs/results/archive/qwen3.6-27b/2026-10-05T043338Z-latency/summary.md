# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T043338Z
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
| **ours** | 116.5 | 748.3 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 442.9 |
| 4 | 249.9 |
| 5 | 504.6 |
| 6 | 703.3 |
| 10 | 335.9 |
| 12 | 89.6 |
| 20 | 89.9 |
| 21 | 83.5 |
| 22 | 1616.7 |
| 23 | 129.9 |
| 24 | 86.8 |
| 26 | 91.0 |
| 27 | 84.5 |
| 28 | 99.4 |
| 29 | 90.9 |
| 30 | 86.8 |
| 31 | 252.2 |
| 33 | 653.9 |
| 37 | 99.6 |
| 38 | 2383.8 |
| 39 | 126.6 |
| 40 | 102.4 |
| 41 | 106.1 |
| 42 | 146.3 |
| 44 | 119.6 |
| 48 | 169.5 |
| 50 | 240.5 |
| 56 | 415.6 |
| 57 | 95.2 |
| 58 | 87.8 |
| 59 | 244.7 |
| 61 | 119.5 |
| 62 | 248.8 |
