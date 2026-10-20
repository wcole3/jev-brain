# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T201005Z
- repo commit: f97f710
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.71.05, PCIe 5x16, AMD Ryzen 9 9950X 16-Core Processor (32 thr), 188 GB, vast 56942372
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: blurb_header
- option_orders: identity
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6251477909763543, 'score': 2.061197148900324, 'noul': 1.264734324887902}, 'b': 0.0, 'source': 'qwen3.6-27b/blurb_header/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.6464561210660535, 'score': 1.9262389103053306, 'noul': 1.3881277937743584}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.627044078638005, 'score': 1.957392235350462, 'noul': 1.2806898963469258}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4848491265570403, 'score': 8.036469832567235, 'noul': 1.146202489120627}, 'b': 0.2558914960106792, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 131.5 | 339.6 | 446.7 | 976.8 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 330.9 |
| 4 | 330.6 |
| 5 | 608.9 |
| 6 | 838.1 |
| 10 | 500.0 |
| 12 | 108.6 |
| 20 | 81.1 |
| 21 | 57.1 |
| 22 | 2110.2 |
| 23 | 165.6 |
| 24 | 79.8 |
| 26 | 57.8 |
| 27 | 78.0 |
| 28 | 76.7 |
| 29 | 111.4 |
| 30 | 107.2 |
| 31 | 331.9 |
| 33 | 546.3 |
| 37 | 134.1 |
| 38 | 2861.1 |
| 39 | 214.1 |
| 40 | 57.1 |
| 41 | 112.3 |
| 42 | 277.0 |
| 44 | 108.3 |
| 50 | 301.3 |
| 56 | 447.2 |
| 57 | 106.7 |
| 58 | 81.1 |
| 59 | 279.9 |
| 61 | 134.5 |
| 62 | 304.6 |
