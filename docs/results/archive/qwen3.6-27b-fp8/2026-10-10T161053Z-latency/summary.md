# qwen3.6-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T161053Z
- repo commit: 9409223
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b-fp8
- hf_revision: e89b16ebf1988b3d6befa7de50abc2d76f26eb09
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6585098155596096, 'score': 1.9436420520554476, 'noul': 1.4027279458983484}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.6323603603116188, 'score': 1.9743652236518074, 'noul': 1.2859386323824527}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.475862833432394, 'score': 7.858322898611463, 'noul': 1.2234832727963472}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 187.6 | 994.5 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 506.4 |
| 4 | 377.7 |
| 5 | 717.5 |
| 6 | 829.4 |
| 10 | 496.9 |
| 12 | 134.9 |
| 20 | 152.2 |
| 21 | 162.3 |
| 22 | 1854.9 |
| 23 | 206.9 |
| 24 | 143.0 |
| 26 | 147.5 |
| 27 | 144.6 |
| 28 | 121.5 |
| 29 | 140.4 |
| 30 | 136.8 |
| 31 | 318.1 |
| 33 | 707.3 |
| 37 | 189.2 |
| 38 | 2388.3 |
| 39 | 363.8 |
| 40 | 165.2 |
| 41 | 130.2 |
| 42 | 341.1 |
| 44 | 183.5 |
| 50 | 514.8 |
| 56 | 784.1 |
| 57 | 164.9 |
| 58 | 178.3 |
| 59 | 373.3 |
| 61 | 162.5 |
| 62 | 376.4 |
