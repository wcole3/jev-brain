# qwen3.8-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T045400Z
- repo commit: e8b57ea-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.8-27b-fp8
- hf_revision: 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a
- prompt_layout: blurb_header_reread
- option_orders: min_n:4+reversed
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.5946131768841085, 'score': 1.0, 'noul': 1.1094642339110774}, 'b': 0.13848768261171268, 'source': 'qwen3.8-27b-fp8/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'blurb_header_reread': {'T': {'choice': 1.6694253320949457, 'score': 1.0, 'noul': 1.3442156081674206}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/blurb_header_reread/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.4847102978456486, 'score': 1.654764340913316, 'noul': 0.9427535974052343}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5169908033068626, 'score': 1.0, 'noul': 0.9589393732341274}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3239935203887572, 'score': 6.368543955447793, 'noul': 0.8118425256070971}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 164.5 | 379.6 | 531.4 | 816.1 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 302.4 |
| 4 | 258.4 |
| 5 | 558.3 |
| 6 | 634.8 |
| 10 | 407.7 |
| 12 | 80.0 |
| 20 | 83.6 |
| 21 | 82.8 |
| 22 | 2674.3 |
| 23 | 189.5 |
| 24 | 147.3 |
| 26 | 73.0 |
| 27 | 147.5 |
| 28 | 83.3 |
| 29 | 118.7 |
| 30 | 123.7 |
| 31 | 571.2 |
| 33 | 693.2 |
| 37 | 258.8 |
| 38 | 5364.3 |
| 39 | 156.4 |
| 40 | 82.6 |
| 41 | 110.7 |
| 42 | 188.7 |
| 44 | 84.0 |
| 50 | 348.3 |
| 56 | 794.7 |
| 57 | 151.0 |
| 58 | 86.6 |
| 59 | 282.3 |
| 61 | 185.4 |
| 62 | 390.0 |
