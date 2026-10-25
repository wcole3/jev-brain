# qwen3.8-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T153711Z
- repo commit: dba35fb-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.8-27b-fp8
- hf_revision: 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a
- prompt_layout: blurb_header_reread
- option_orders: min_n:4+reversed
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.5946131768841085, 'score': 1.0, 'noul': 1.1094642339110774}, 'b': 0.13848768261171268, 'source': 'qwen3.8-27b-fp8/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'blurb_header_reread': {'T': {'choice': 1.7391732643996622, 'score': 1.0, 'noul': 1.3956044971608574}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/blurb_header_reread/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.4847102978456486, 'score': 1.654764340913316, 'noul': 0.9427535974052343}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5169908033068626, 'score': 1.0, 'noul': 0.9589393732341274}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3239935203887572, 'score': 6.368543955447793, 'noul': 0.8118425256070971}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 248.4 | 531.1 | 722.5 | 1171.9 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 373.6 |
| 4 | 346.7 |
| 5 | 675.0 |
| 6 | 845.7 |
| 10 | 509.3 |
| 12 | 151.9 |
| 20 | 100.3 |
| 21 | 108.7 |
| 22 | 3540.5 |
| 23 | 254.9 |
| 24 | 170.7 |
| 26 | 147.6 |
| 27 | 202.0 |
| 28 | 96.7 |
| 29 | 181.6 |
| 30 | 179.7 |
| 31 | 830.7 |
| 33 | 1097.1 |
| 37 | 350.8 |
| 38 | 7094.9 |
| 39 | 117.9 |
| 40 | 105.7 |
| 41 | 139.4 |
| 42 | 299.3 |
| 44 | 159.4 |
| 50 | 833.7 |
| 56 | 1038.3 |
| 57 | 175.1 |
| 58 | 140.2 |
| 59 | 414.0 |
| 61 | 272.4 |
| 62 | 519.4 |
