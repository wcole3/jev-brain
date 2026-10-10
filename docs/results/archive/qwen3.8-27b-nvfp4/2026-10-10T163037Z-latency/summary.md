# qwen3.8-27b-nvfp4 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T163037Z
- repo commit: 9409223
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.8-27b-nvfp4
- hf_revision: 319f741cce68d7914884900c138a1fbb70a42f30
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.534912409014274, 'score': 1.6956928316925777, 'noul': 0.9175902098440983}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5971415409111187, 'score': 1.829572794304793, 'noul': 0.9633966437867898}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3876276536831984, 'score': 1.7744416557968425, 'noul': 0.9417765210190306}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 161.6 | 1833.1 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 719.1 |
| 4 | 480.2 |
| 5 | 1063.1 |
| 6 | 1570.4 |
| 10 | 1008.2 |
| 12 | 149.8 |
| 20 | 147.5 |
| 21 | 133.5 |
| 22 | 3372.0 |
| 23 | 396.0 |
| 24 | 157.3 |
| 26 | 135.8 |
| 27 | 123.3 |
| 28 | 157.0 |
| 29 | 136.5 |
| 30 | 124.5 |
| 31 | 545.4 |
| 33 | 858.8 |
| 37 | 138.4 |
| 38 | 3016.3 |
| 39 | 252.3 |
| 40 | 136.6 |
| 41 | 116.4 |
| 42 | 398.0 |
| 44 | 115.8 |
| 50 | 426.0 |
| 56 | 651.3 |
| 57 | 124.8 |
| 58 | 139.6 |
| 59 | 535.7 |
| 61 | 170.3 |
| 62 | 589.3 |
