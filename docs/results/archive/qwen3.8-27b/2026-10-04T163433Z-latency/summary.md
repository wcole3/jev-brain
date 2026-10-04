# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-04T163433Z
- repo commit: fd72395
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
| **ours** | 106.3 | 649.4 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex 27B (board, its own sample) | 108.0 | n/a |
| Jevfire (Qwen3.8-27B-FP8) (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 407.1 |
| 4 | 251.4 |
| 5 | 454.9 |
| 6 | 582.2 |
| 10 | 340.1 |
| 12 | 89.8 |
| 20 | 85.1 |
| 21 | 83.3 |
| 22 | 1369.6 |
| 23 | 130.1 |
| 24 | 86.3 |
| 26 | 86.1 |
| 27 | 84.6 |
| 28 | 82.1 |
| 29 | 90.9 |
| 30 | 85.6 |
| 31 | 255.4 |
| 33 | 627.4 |
| 37 | 98.6 |
| 38 | 2291.6 |
| 39 | 169.7 |
| 40 | 84.9 |
| 41 | 102.4 |
| 42 | 129.2 |
| 44 | 91.0 |
| 48 | 174.0 |
| 50 | 245.1 |
| 56 | 414.4 |
| 57 | 92.2 |
| 58 | 89.6 |
| 59 | 245.1 |
| 61 | 109.0 |
| 62 | 243.0 |
