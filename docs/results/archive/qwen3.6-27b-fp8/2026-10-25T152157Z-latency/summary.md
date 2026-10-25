# qwen3.6-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T152157Z
- repo commit: dba35fb-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b-fp8
- hf_revision: e89b16ebf1988b3d6befa7de50abc2d76f26eb09
- prompt_layout: blurb_header_reread
- option_orders: identity
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6087767463450138, 'score': 2.0371306533981115, 'noul': 1.2594265719567521}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/blurb_header/calibration.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 1.659824132956001, 'score': 2.1314605853423614, 'noul': 1.5932935918585747}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/blurb_header_reread/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.6585098155596096, 'score': 1.9436420520554476, 'noul': 1.4027279458983484}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.6323603603116188, 'score': 1.9743652236518074, 'noul': 1.2859386323824527}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.475862833432394, 'score': 7.858322898611463, 'noul': 1.2234832727963472}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 151.4 | 344.9 | 408.6 | 835.5 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 294.3 |
| 4 | 208.5 |
| 5 | 408.6 |
| 6 | 512.0 |
| 10 | 398.5 |
| 12 | 122.8 |
| 20 | 87.7 |
| 21 | 88.1 |
| 22 | 1437.1 |
| 23 | 207.0 |
| 24 | 89.6 |
| 26 | 88.4 |
| 27 | 90.8 |
| 28 | 83.9 |
| 29 | 128.9 |
| 30 | 120.5 |
| 31 | 282.9 |
| 33 | 759.6 |
| 37 | 190.5 |
| 38 | 5757.5 |
| 39 | 117.5 |
| 40 | 95.0 |
| 41 | 129.0 |
| 42 | 229.6 |
| 44 | 126.8 |
| 50 | 316.2 |
| 56 | 834.4 |
| 57 | 105.6 |
| 58 | 93.8 |
| 59 | 323.5 |
| 61 | 205.9 |
| 62 | 311.0 |
