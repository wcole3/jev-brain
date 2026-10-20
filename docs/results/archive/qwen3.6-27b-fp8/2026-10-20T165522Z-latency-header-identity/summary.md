# qwen3.6-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T165522Z
- repo commit: 326d316
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 590.48.01, PCIe 4x16, AMD EPYC 7642 48-Core Processor (192 thr), 1008 GB, vast 56910928
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
| **ours** | 227.4 | 658.4 | 899.4 | 1826.5 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 636.2 |
| 4 | 618.1 |
| 5 | 1204.7 |
| 6 | 1633.6 |
| 10 | 936.9 |
| 12 | 212.9 |
| 20 | 181.3 |
| 21 | 120.8 |
| 22 | 4013.0 |
| 23 | 329.2 |
| 24 | 150.5 |
| 26 | 121.5 |
| 27 | 151.9 |
| 28 | 120.3 |
| 29 | 221.4 |
| 30 | 208.1 |
| 31 | 642.4 |
| 33 | 1052.6 |
| 37 | 273.5 |
| 38 | 5783.4 |
| 39 | 320.5 |
| 40 | 121.9 |
| 41 | 227.2 |
| 42 | 521.9 |
| 44 | 215.2 |
| 50 | 544.5 |
| 56 | 901.8 |
| 57 | 185.8 |
| 58 | 157.3 |
| 59 | 536.0 |
| 61 | 266.3 |
| 62 | 597.0 |
