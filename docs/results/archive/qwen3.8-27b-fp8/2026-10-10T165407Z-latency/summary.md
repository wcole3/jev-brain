# qwen3.8-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T165407Z
- repo commit: 9409223
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.8-27b-fp8
- hf_revision: 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.4847102978456486, 'score': 1.654764340913316, 'noul': 0.9427535974052343}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5169908033068626, 'score': 1.0, 'noul': 0.9589393732341274}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3239935203887572, 'score': 6.368543955447793, 'noul': 0.8118425256070971}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 133.7 | 811.7 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 401.5 |
| 4 | 276.8 |
| 5 | 545.5 |
| 6 | 711.5 |
| 10 | 423.2 |
| 12 | 120.3 |
| 20 | 119.5 |
| 21 | 122.2 |
| 22 | 1583.9 |
| 23 | 180.9 |
| 24 | 117.4 |
| 26 | 112.3 |
| 27 | 110.7 |
| 28 | 114.5 |
| 29 | 110.2 |
| 30 | 131.9 |
| 31 | 277.7 |
| 33 | 624.6 |
| 37 | 116.0 |
| 38 | 2050.2 |
| 39 | 160.1 |
| 40 | 131.9 |
| 41 | 119.6 |
| 42 | 248.9 |
| 44 | 117.1 |
| 50 | 253.8 |
| 56 | 511.5 |
| 57 | 118.3 |
| 58 | 122.2 |
| 59 | 279.5 |
| 61 | 124.8 |
| 62 | 279.0 |
