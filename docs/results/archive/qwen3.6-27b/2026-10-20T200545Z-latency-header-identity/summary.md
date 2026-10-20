# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T200545Z
- repo commit: f97f710
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.71.05, PCIe 5x16, AMD Ryzen 9 9950X 16-Core Processor (32 thr), 188 GB, vast 56942372
- design: latency-v1, our rows
- layout: header
- option_orders: identity
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: blurb_header
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6251477909763543, 'score': 2.061197148900324, 'noul': 1.264734324887902}, 'b': 0.0, 'source': 'qwen3.6-27b/blurb_header/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.6464561210660535, 'score': 1.9262389103053306, 'noul': 1.3881277937743584}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.627044078638005, 'score': 1.957392235350462, 'noul': 1.2806898963469258}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4848491265570403, 'score': 8.036469832567235, 'noul': 1.146202489120627}, 'b': 0.2558914960106792, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 111.5 | 328.8 | 444.6 | 934.8 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 317.1 |
| 4 | 316.6 |
| 5 | 586.9 |
| 6 | 818.6 |
| 10 | 491.9 |
| 12 | 105.7 |
| 20 | 78.7 |
| 21 | 53.9 |
| 22 | 2081.4 |
| 23 | 162.8 |
| 24 | 77.5 |
| 26 | 56.7 |
| 27 | 75.9 |
| 28 | 56.3 |
| 29 | 109.4 |
| 30 | 105.3 |
| 31 | 329.2 |
| 33 | 537.2 |
| 37 | 132.2 |
| 38 | 2843.0 |
| 39 | 211.6 |
| 40 | 55.0 |
| 41 | 111.2 |
| 42 | 272.2 |
| 44 | 107.0 |
| 50 | 279.6 |
| 56 | 444.8 |
| 57 | 81.8 |
| 58 | 79.8 |
| 59 | 276.6 |
| 61 | 133.1 |
| 62 | 303.7 |
