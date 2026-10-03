# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-03T134506Z
- repo commit: 3e58290
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.84, PCIe 5x16, AMD Ryzen 7 9800X3D 8-Core Processor (16 thr), 92 GB, vast 54017287
- design: latency-v1, our rows
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: decider_chat
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.4958925733915396, 'score': 1.6641806616549275, 'noul': 0.9701214258536706}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5360739185489443, 'score': 1.7751446114421117, 'noul': 0.9629807468103339}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3522738771932372, 'score': 6.26411640450269, 'noul': 0.8245982249217311}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 77.2 | 537.0 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex 27B (board, its own sample) | 108.0 | n/a |
| Jevfire (Qwen3.8-27B-FP8) (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 277.7 |
| 4 | 201.0 |
| 5 | 372.0 |
| 6 | 494.0 |
| 10 | 285.9 |
| 12 | 56.3 |
| 20 | 57.7 |
| 21 | 48.2 |
| 22 | 1262.9 |
| 23 | 114.0 |
| 24 | 50.9 |
| 26 | 49.1 |
| 27 | 51.4 |
| 28 | 48.9 |
| 29 | 73.9 |
| 30 | 57.1 |
| 31 | 209.1 |
| 33 | 370.7 |
| 37 | 77.3 |
| 38 | 1362.4 |
| 39 | 107.1 |
| 40 | 49.0 |
| 41 | 57.8 |
| 42 | 113.6 |
| 44 | 57.8 |
| 48 | 136.5 |
| 50 | 199.1 |
| 56 | 321.1 |
| 57 | 58.9 |
| 58 | 58.1 |
| 59 | 199.3 |
| 61 | 93.9 |
| 62 | 197.6 |
