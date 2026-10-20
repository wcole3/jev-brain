# qwen3.8-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T165434Z
- repo commit: 326d316
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.71.05, PCIe 4x16, AMD EPYC 7452 32-Core Processor (64 thr), 441 GB, vast 56910917
- design: latency-v1, our rows
- layout: header
- option_orders: min_n:4+reversed
- profile: qwen3.8-27b-fp8
- hf_revision: 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a
- prompt_layout: blurb_header
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.5946131768841085, 'score': 1.0, 'noul': 1.1094642339110774}, 'b': 0.13848768261171268, 'source': 'qwen3.8-27b-fp8/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.4847102978456486, 'score': 1.654764340913316, 'noul': 0.9427535974052343}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5169908033068626, 'score': 1.0, 'noul': 0.9589393732341274}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3239935203887572, 'score': 6.368543955447793, 'noul': 0.8118425256070971}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 68.3 | 184.5 | 253.6 | 473.1 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 196.7 |
| 4 | 158.7 |
| 5 | 312.7 |
| 6 | 422.4 |
| 10 | 243.5 |
| 12 | 62.0 |
| 20 | 61.6 |
| 21 | 60.8 |
| 22 | 1019.7 |
| 23 | 90.7 |
| 24 | 60.9 |
| 26 | 59.2 |
| 27 | 59.0 |
| 28 | 59.1 |
| 29 | 61.7 |
| 30 | 62.1 |
| 31 | 159.8 |
| 33 | 288.1 |
| 37 | 68.8 |
| 38 | 1682.8 |
| 39 | 113.7 |
| 40 | 63.7 |
| 41 | 62.1 |
| 42 | 135.8 |
| 44 | 61.4 |
| 50 | 140.7 |
| 56 | 265.2 |
| 57 | 61.6 |
| 58 | 68.2 |
| 59 | 146.0 |
| 61 | 69.4 |
| 62 | 149.5 |
