# qwen3.8-27b-nvfp4 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T165225Z
- repo commit: 326d316
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 580.178.04, PCIe 5x16, AMD Ryzen Threadripper PRO 7995WX 96-Cores (192 thr), 251 GB, vast 56910924
- design: latency-v1, our rows
- layout: header
- option_orders: min_n:4+reversed
- profile: qwen3.8-27b-nvfp4
- hf_revision: 319f741cce68d7914884900c138a1fbb70a42f30
- prompt_layout: blurb_header
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6807640584736696, 'score': 1.9672694770276271, 'noul': 1.1388145341309106}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.534912409014274, 'score': 1.6956928316925777, 'noul': 0.9175902098440983}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5971415409111187, 'score': 1.829572794304793, 'noul': 0.9633966437867898}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3876276536831984, 'score': 1.7744416557968425, 'noul': 0.9417765210190306}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 45.8 | 134.3 | 183.9 | 354.8 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 151.4 |
| 4 | 129.4 |
| 5 | 231.8 |
| 6 | 328.9 |
| 10 | 194.3 |
| 12 | 40.2 |
| 20 | 32.4 |
| 21 | 29.6 |
| 22 | 781.3 |
| 23 | 87.0 |
| 24 | 31.0 |
| 26 | 30.1 |
| 27 | 32.3 |
| 28 | 31.6 |
| 29 | 42.5 |
| 30 | 40.1 |
| 31 | 127.2 |
| 33 | 237.2 |
| 37 | 44.3 |
| 38 | 1154.7 |
| 39 | 77.9 |
| 40 | 29.0 |
| 41 | 43.7 |
| 42 | 111.7 |
| 44 | 40.3 |
| 50 | 114.0 |
| 56 | 184.2 |
| 57 | 32.6 |
| 58 | 31.8 |
| 59 | 114.0 |
| 61 | 50.0 |
| 62 | 118.1 |
