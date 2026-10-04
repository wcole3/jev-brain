# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-04T024731Z
- repo commit: 8a14b18
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.84, PCIe 4x16, AMD Ryzen Threadripper 3960X 24-Core Processor (48 thr), 189 GB, vast 54093767
- design: latency-v1, our rows
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.4958925733915396, 'score': 1.6641806616549275, 'noul': 0.9701214258536706}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5360739185489443, 'score': 1.7751446114421117, 'noul': 0.9629807468103339}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3522738771932372, 'score': 6.26411640450269, 'noul': 0.8245982249217311}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 94.2 | 580.3 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex 27B (board, its own sample) | 108.0 | n/a |
| Jevfire (Qwen3.8-27B-FP8) (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 285.4 |
| 4 | 221.7 |
| 5 | 382.0 |
| 6 | 505.0 |
| 10 | 310.2 |
| 12 | 76.6 |
| 20 | 59.9 |
| 21 | 51.6 |
| 22 | 1285.5 |
| 23 | 117.8 |
| 24 | 59.3 |
| 26 | 53.6 |
| 27 | 59.2 |
| 28 | 52.9 |
| 29 | 79.4 |
| 30 | 61.1 |
| 31 | 227.2 |
| 33 | 528.2 |
| 37 | 80.6 |
| 38 | 2182.5 |
| 39 | 144.7 |
| 40 | 51.6 |
| 41 | 78.0 |
| 42 | 118.5 |
| 44 | 78.4 |
| 48 | 159.4 |
| 50 | 211.0 |
| 56 | 329.2 |
| 57 | 61.5 |
| 58 | 61.0 |
| 59 | 203.2 |
| 61 | 97.8 |
| 62 | 201.6 |
