# qwen3.6-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T044047Z
- repo commit: e8b57ea-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b-fp8
- hf_revision: e89b16ebf1988b3d6befa7de50abc2d76f26eb09
- prompt_layout: blurb_header_reread
- option_orders: identity
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6087767463450138, 'score': 2.0371306533981115, 'noul': 1.2594265719567521}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/blurb_header/calibration.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 1.5901413753593128, 'score': 2.0411689590206805, 'noul': 1.425465365168322}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/blurb_header_reread/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.6585098155596096, 'score': 1.9436420520554476, 'noul': 1.4027279458983484}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.6323603603116188, 'score': 1.9743652236518074, 'noul': 1.2859386323824527}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.475862833432394, 'score': 7.858322898611463, 'noul': 1.2234832727963472}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 121.7 | 312.6 | 384.6 | 833.8 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 328.0 |
| 4 | 193.2 |
| 5 | 384.6 |
| 6 | 480.4 |
| 10 | 400.1 |
| 12 | 79.3 |
| 20 | 79.7 |
| 21 | 81.9 |
| 22 | 1298.0 |
| 23 | 185.7 |
| 24 | 83.8 |
| 26 | 78.9 |
| 27 | 82.4 |
| 28 | 77.9 |
| 29 | 84.9 |
| 30 | 82.0 |
| 31 | 214.2 |
| 33 | 693.5 |
| 37 | 135.9 |
| 38 | 5321.0 |
| 39 | 167.5 |
| 40 | 84.1 |
| 41 | 120.6 |
| 42 | 204.9 |
| 44 | 88.8 |
| 50 | 273.5 |
| 56 | 833.8 |
| 57 | 92.2 |
| 58 | 101.3 |
| 59 | 307.9 |
| 61 | 204.3 |
| 62 | 282.7 |
