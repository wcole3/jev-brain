# qwen3.6-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T195938Z
- repo commit: f97f710
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 615.71.09, PCIe 5x16, AMD EPYC 9334 32-Core Processor (64 thr), 188 GB, vast 56942374
- design: latency-v1, our rows
- layout: header
- option_orders: identity
- profile: qwen3.6-27b-fp8
- hf_revision: e89b16ebf1988b3d6befa7de50abc2d76f26eb09
- prompt_layout: blurb_header
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6087767463450138, 'score': 2.0371306533981115, 'noul': 1.2594265719567521}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/blurb_header/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.6585098155596096, 'score': 1.9436420520554476, 'noul': 1.4027279458983484}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.6323603603116188, 'score': 1.9743652236518074, 'noul': 1.2859386323824527}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.475862833432394, 'score': 7.858322898611463, 'noul': 1.2234832727963472}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 60.7 | 173.2 | 241.5 | 477.6 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 179.5 |
| 4 | 156.3 |
| 5 | 295.5 |
| 6 | 406.9 |
| 10 | 242.7 |
| 12 | 57.4 |
| 20 | 46.8 |
| 21 | 42.6 |
| 22 | 1014.4 |
| 23 | 92.2 |
| 24 | 44.2 |
| 26 | 42.7 |
| 27 | 42.7 |
| 28 | 42.1 |
| 29 | 58.6 |
| 30 | 56.7 |
| 31 | 159.2 |
| 33 | 274.0 |
| 37 | 67.8 |
| 38 | 1562.9 |
| 39 | 107.6 |
| 40 | 43.6 |
| 41 | 60.4 |
| 42 | 138.2 |
| 44 | 57.8 |
| 50 | 142.4 |
| 56 | 245.0 |
| 57 | 48.6 |
| 58 | 44.7 |
| 59 | 139.8 |
| 61 | 69.8 |
| 62 | 149.6 |
