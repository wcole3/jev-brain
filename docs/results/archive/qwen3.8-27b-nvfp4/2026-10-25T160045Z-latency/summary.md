# qwen3.8-27b-nvfp4 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T160045Z
- repo commit: dba35fb-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.8-27b-nvfp4
- hf_revision: 319f741cce68d7914884900c138a1fbb70a42f30
- prompt_layout: blurb_header_reread
- option_orders: min_n:4+reversed
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6807640584736696, 'score': 1.9672694770276271, 'noul': 1.1388145341309106}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'blurb_header_reread': {'T': {'choice': 1.7391732643996622, 'score': 1.0, 'noul': 1.3956044971608574}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/blurb_header_reread/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.534912409014274, 'score': 1.6956928316925777, 'noul': 0.9175902098440983}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5971415409111187, 'score': 1.829572794304793, 'noul': 0.9633966437867898}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3876276536831984, 'score': 1.7744416557968425, 'noul': 0.9417765210190306}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 487.3 | 1009.5 | 1272.0 | 2880.5 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.
Over 1000 ms: mean 1009.5, p80 1272.0

| catalog | median ms |
|---|---|
| 1 | 441.6 |
| 4 | 584.3 |
| 5 | 1288.8 |
| 6 | 1275.5 |
| 10 | 1009.7 |
| 12 | 343.4 |
| 20 | 147.8 |
| 21 | 139.1 |
| 22 | 7094.7 |
| 23 | 452.1 |
| 24 | 277.9 |
| 26 | 281.0 |
| 27 | 301.7 |
| 28 | 147.2 |
| 29 | 436.2 |
| 30 | 460.0 |
| 31 | 2080.6 |
| 33 | 1597.8 |
| 37 | 867.5 |
| 38 | 10543.0 |
| 39 | 327.6 |
| 40 | 140.3 |
| 41 | 364.3 |
| 42 | 644.1 |
| 44 | 435.7 |
| 50 | 2087.0 |
| 56 | 1508.5 |
| 57 | 350.8 |
| 58 | 279.3 |
| 59 | 1034.0 |
| 61 | 457.0 |
| 62 | 959.1 |
