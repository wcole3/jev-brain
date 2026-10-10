# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T175404Z
- repo commit: 9409223
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- arm (DS-032 diagnosis): shipped profile with MTP off: EXTRA_ARGS=--long-prefill-token-threshold 784 --max-num-batched-tokens 2352 --scheduling-policy priority, PREFIX_BLOCK=784, WARM_MIN_PREFIX_TOKENS=784
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6479149611375679, 'score': 1.9271133600869372, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration-784.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.626739845878971, 'score': 1.9577583066935726, 'noul': 1.2842455905297372}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration-784.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4836733616074274, 'score': 8.054659971948029, 'noul': 1.1446681550320104}, 'b': 0.2527877422356274, 'source': 'qwen3.6-27b/question_first/calibration-784.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 167.7 | 943.7 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 578.7 |
| 4 | 289.7 |
| 5 | 591.5 |
| 6 | 827.9 |
| 10 | 477.2 |
| 12 | 129.7 |
| 20 | 138.4 |
| 21 | 147.6 |
| 22 | 1898.5 |
| 23 | 188.0 |
| 24 | 142.3 |
| 26 | 136.3 |
| 27 | 143.4 |
| 28 | 148.5 |
| 29 | 135.6 |
| 30 | 141.6 |
| 31 | 330.5 |
| 33 | 764.5 |
| 37 | 145.8 |
| 38 | 2743.4 |
| 39 | 322.2 |
| 40 | 168.9 |
| 41 | 154.4 |
| 42 | 328.2 |
| 44 | 150.3 |
| 50 | 332.6 |
| 56 | 726.6 |
| 57 | 156.0 |
| 58 | 146.8 |
| 59 | 322.7 |
| 61 | 172.4 |
| 62 | 355.1 |
