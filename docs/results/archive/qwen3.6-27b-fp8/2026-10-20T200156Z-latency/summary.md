# qwen3.6-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T200156Z
- repo commit: f97f710
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 615.71.09, PCIe 5x16, AMD EPYC 9334 32-Core Processor (64 thr), 188 GB, vast 56942374
- design: latency-v1, our rows
- profile: qwen3.6-27b-fp8
- hf_revision: e89b16ebf1988b3d6befa7de50abc2d76f26eb09
- prompt_layout: blurb_header
- option_orders: identity
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6087767463450138, 'score': 2.0371306533981115, 'noul': 1.2594265719567521}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/blurb_header/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.6585098155596096, 'score': 1.9436420520554476, 'noul': 1.4027279458983484}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.6323603603116188, 'score': 1.9743652236518074, 'noul': 1.2859386323824527}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.475862833432394, 'score': 7.858322898611463, 'noul': 1.2234832727963472}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 67.8 | 176.2 | 234.9 | 485.6 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 197.7 |
| 4 | 160.4 |
| 5 | 302.8 |
| 6 | 411.6 |
| 10 | 246.1 |
| 12 | 57.9 |
| 20 | 48.0 |
| 21 | 43.8 |
| 22 | 1022.0 |
| 23 | 93.0 |
| 24 | 44.3 |
| 26 | 43.8 |
| 27 | 44.3 |
| 28 | 43.8 |
| 29 | 60.1 |
| 30 | 58.4 |
| 31 | 160.8 |
| 33 | 267.2 |
| 37 | 68.2 |
| 38 | 1575.6 |
| 39 | 108.8 |
| 40 | 43.7 |
| 41 | 61.0 |
| 42 | 140.4 |
| 44 | 58.7 |
| 50 | 145.5 |
| 56 | 245.0 |
| 57 | 57.7 |
| 58 | 47.9 |
| 59 | 141.7 |
| 61 | 70.3 |
| 62 | 151.0 |
