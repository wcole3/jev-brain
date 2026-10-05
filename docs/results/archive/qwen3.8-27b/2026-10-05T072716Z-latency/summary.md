# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T072716Z
- repo commit: 66b8531
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.4958925733915396, 'score': 1.6641806616549275, 'noul': 0.9701214258536706}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5360739185489443, 'score': 1.7751446114421117, 'noul': 0.9629807468103339}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3522738771932372, 'score': 6.26411640450269, 'noul': 0.8245982249217311}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 104.9 | 709.2 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex 27B (board, its own sample) | 108.0 | n/a |
| Jevfire (Qwen3.8-27B-FP8) (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 382.7 |
| 4 | 245.1 |
| 5 | 483.1 |
| 6 | 652.5 |
| 10 | 335.1 |
| 12 | 88.8 |
| 20 | 85.5 |
| 21 | 87.2 |
| 22 | 1600.6 |
| 23 | 126.4 |
| 24 | 89.1 |
| 26 | 87.8 |
| 27 | 99.9 |
| 28 | 85.4 |
| 29 | 89.7 |
| 30 | 84.9 |
| 31 | 246.8 |
| 33 | 633.9 |
| 37 | 96.1 |
| 38 | 2300.6 |
| 39 | 118.6 |
| 40 | 84.3 |
| 41 | 93.1 |
| 42 | 126.3 |
| 44 | 91.8 |
| 48 | 168.5 |
| 50 | 232.4 |
| 56 | 403.2 |
| 57 | 88.4 |
| 58 | 96.9 |
| 59 | 239.6 |
| 61 | 118.0 |
| 62 | 255.4 |
