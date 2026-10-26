# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T032741Z
- repo commit: e8b57ea-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: blurb_header_reread
- option_orders: identity
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6251477909763543, 'score': 2.061197148900324, 'noul': 1.264734324887902}, 'b': 0.0, 'source': 'qwen3.6-27b/blurb_header/calibration.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 1.5901413753593128, 'score': 2.0411689590206805, 'noul': 1.425465365168322}, 'b': 0.0, 'source': 'qwen3.6-27b/blurb_header_reread/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.6464561210660535, 'score': 1.9262389103053306, 'noul': 1.3881277937743584}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.627044078638005, 'score': 1.957392235350462, 'noul': 1.2806898963469258}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4848491265570403, 'score': 8.036469832567235, 'noul': 1.146202489120627}, 'b': 0.2558914960106792, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 147.4 | 419.4 | 530.3 | 978.4 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 447.4 |
| 4 | 250.0 |
| 5 | 568.9 |
| 6 | 602.2 |
| 10 | 514.2 |
| 12 | 97.5 |
| 20 | 85.4 |
| 21 | 86.8 |
| 22 | 1835.1 |
| 23 | 210.6 |
| 24 | 88.6 |
| 26 | 108.3 |
| 27 | 103.9 |
| 28 | 109.6 |
| 29 | 104.5 |
| 30 | 99.6 |
| 31 | 272.7 |
| 33 | 1148.9 |
| 37 | 225.3 |
| 38 | 6441.0 |
| 39 | 175.3 |
| 40 | 159.2 |
| 41 | 175.5 |
| 42 | 253.4 |
| 44 | 98.8 |
| 50 | 274.5 |
| 56 | 829.0 |
| 57 | 97.7 |
| 58 | 96.4 |
| 59 | 356.0 |
| 61 | 208.2 |
| 62 | 345.1 |
