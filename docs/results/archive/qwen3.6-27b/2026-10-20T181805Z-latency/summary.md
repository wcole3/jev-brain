# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T181805Z
- repo commit: 18ab6ae
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 595.99.02, PCIe 5x16, AMD Ryzen 9 9950X 16-Core Processor (32 thr), 123 GB, vast 56910925
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
| **ours** | 630.1 | 1605.7 | 2237.9 | 4492.6 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.
Over 1000 ms: mean 1605.7, p80 2237.9

| catalog | median ms |
|---|---|
| 1 | 1713.7 |
| 4 | 1581.5 |
| 5 | 2904.2 |
| 6 | 3932.6 |
| 10 | 2284.6 |
| 12 | 533.1 |
| 20 | 406.0 |
| 21 | 304.6 |
| 22 | 9658.1 |
| 23 | 760.6 |
| 24 | 400.6 |
| 26 | 305.0 |
| 27 | 397.2 |
| 28 | 396.2 |
| 29 | 551.1 |
| 30 | 524.5 |
| 31 | 1556.0 |
| 33 | 2695.6 |
| 37 | 684.2 |
| 38 | 13021.5 |
| 39 | 1097.1 |
| 40 | 310.3 |
| 41 | 575.2 |
| 42 | 1350.7 |
| 44 | 549.5 |
| 50 | 1469.5 |
| 56 | 2244.1 |
| 57 | 538.0 |
| 58 | 413.3 |
| 59 | 1357.5 |
| 61 | 659.0 |
| 62 | 1470.6 |
