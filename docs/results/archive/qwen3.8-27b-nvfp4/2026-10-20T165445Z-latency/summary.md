# qwen3.8-27b-nvfp4 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T165445Z
- repo commit: 326d316
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 580.178.04, PCIe 5x16, AMD Ryzen Threadripper PRO 7995WX 96-Cores (192 thr), 251 GB, vast 56910924
- design: latency-v1, our rows
- profile: qwen3.8-27b-nvfp4
- hf_revision: 319f741cce68d7914884900c138a1fbb70a42f30
- prompt_layout: blurb_header
- option_orders: min_n:4+reversed
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6807640584736696, 'score': 1.9672694770276271, 'noul': 1.1388145341309106}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.534912409014274, 'score': 1.6956928316925777, 'noul': 0.9175902098440983}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5971415409111187, 'score': 1.829572794304793, 'noul': 0.9633966437867898}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3876276536831984, 'score': 1.7744416557968425, 'noul': 0.9417765210190306}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 88.3 | 180.2 | 226.4 | 450.9 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 142.8 |
| 4 | 225.6 |
| 5 | 402.4 |
| 6 | 376.3 |
| 10 | 194.9 |
| 12 | 43.0 |
| 20 | 32.6 |
| 21 | 29.0 |
| 22 | 1596.1 |
| 23 | 87.4 |
| 24 | 57.6 |
| 26 | 55.6 |
| 27 | 56.3 |
| 28 | 29.0 |
| 29 | 87.8 |
| 30 | 80.4 |
| 31 | 214.4 |
| 33 | 233.3 |
| 37 | 93.2 |
| 38 | 1173.8 |
| 39 | 93.2 |
| 40 | 30.9 |
| 41 | 43.5 |
| 42 | 113.9 |
| 44 | 43.8 |
| 50 | 186.6 |
| 56 | 186.5 |
| 57 | 78.8 |
| 58 | 41.4 |
| 59 | 120.1 |
| 61 | 53.2 |
| 62 | 155.0 |
