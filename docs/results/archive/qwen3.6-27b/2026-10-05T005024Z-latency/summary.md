# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T005024Z
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
| **ours** | 139.8 | 705.8 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 427.2 |
| 4 | 456.2 |
| 5 | 638.7 |
| 6 | 629.5 |
| 10 | 333.7 |
| 12 | 108.2 |
| 20 | 104.2 |
| 21 | 93.4 |
| 22 | 1341.3 |
| 23 | 270.9 |
| 24 | 138.7 |
| 26 | 186.2 |
| 27 | 186.1 |
| 28 | 167.9 |
| 29 | 108.2 |
| 30 | 105.4 |
| 31 | 259.4 |
| 33 | 519.6 |
| 37 | 128.3 |
| 38 | 1502.4 |
| 39 | 103.6 |
| 40 | 98.3 |
| 41 | 124.1 |
| 42 | 139.0 |
| 44 | 111.8 |
| 48 | 169.5 |
| 50 | 282.5 |
| 56 | 456.7 |
| 57 | 111.6 |
| 58 | 100.5 |
| 59 | 249.2 |
| 61 | 118.4 |
| 62 | 234.3 |
