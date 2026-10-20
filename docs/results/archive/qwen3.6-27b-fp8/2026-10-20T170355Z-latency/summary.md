# qwen3.6-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T170355Z
- repo commit: 326d316
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 590.48.01, PCIe 4x16, AMD EPYC 7642 48-Core Processor (192 thr), 1008 GB, vast 56910928
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
| **ours** | 259.9 | 668.1 | 900.6 | 1851.6 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 676.2 |
| 4 | 637.3 |
| 5 | 1210.6 |
| 6 | 1631.1 |
| 10 | 934.9 |
| 12 | 215.2 |
| 20 | 181.3 |
| 21 | 120.1 |
| 22 | 3973.6 |
| 23 | 328.5 |
| 24 | 150.7 |
| 26 | 122.0 |
| 27 | 151.6 |
| 28 | 147.2 |
| 29 | 222.5 |
| 30 | 210.8 |
| 31 | 624.7 |
| 33 | 1075.5 |
| 37 | 269.3 |
| 38 | 5795.7 |
| 39 | 443.4 |
| 40 | 125.8 |
| 41 | 230.5 |
| 42 | 540.2 |
| 44 | 218.8 |
| 50 | 576.0 |
| 56 | 901.4 |
| 57 | 211.2 |
| 58 | 182.6 |
| 59 | 540.2 |
| 61 | 271.4 |
| 62 | 599.6 |
