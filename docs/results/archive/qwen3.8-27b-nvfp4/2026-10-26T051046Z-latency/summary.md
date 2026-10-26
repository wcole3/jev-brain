# qwen3.8-27b-nvfp4 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T051046Z
- repo commit: e8b57ea-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.8-27b-nvfp4
- hf_revision: 319f741cce68d7914884900c138a1fbb70a42f30
- prompt_layout: blurb_header_reread
- option_orders: min_n:4+reversed
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6807640584736696, 'score': 1.9672694770276271, 'noul': 1.1388145341309106}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'blurb_header_reread': {'T': {'choice': 1.6694253320949457, 'score': 1.0, 'noul': 1.3442156081674206}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/blurb_header_reread/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.534912409014274, 'score': 1.6956928316925777, 'noul': 0.9175902098440983}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5971415409111187, 'score': 1.829572794304793, 'noul': 0.9633966437867898}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3876276536831984, 'score': 1.7744416557968425, 'noul': 0.9417765210190306}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 232.5 | 558.7 | 794.9 | 1224.1 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 386.4 |
| 4 | 418.2 |
| 5 | 834.8 |
| 6 | 973.3 |
| 10 | 741.8 |
| 12 | 88.8 |
| 20 | 86.0 |
| 21 | 85.8 |
| 22 | 4929.8 |
| 23 | 294.6 |
| 24 | 161.8 |
| 26 | 87.0 |
| 27 | 160.8 |
| 28 | 87.0 |
| 29 | 197.4 |
| 30 | 164.3 |
| 31 | 1001.6 |
| 33 | 832.0 |
| 37 | 371.5 |
| 38 | 6111.6 |
| 39 | 156.2 |
| 40 | 87.4 |
| 41 | 207.1 |
| 42 | 302.4 |
| 44 | 88.4 |
| 50 | 651.2 |
| 56 | 925.4 |
| 57 | 174.8 |
| 58 | 96.4 |
| 59 | 474.6 |
| 61 | 295.4 |
| 62 | 602.7 |
