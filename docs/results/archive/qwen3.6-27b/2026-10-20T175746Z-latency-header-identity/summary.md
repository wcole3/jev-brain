# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T175746Z
- repo commit: 18ab6ae
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 595.99.02, PCIe 5x16, AMD Ryzen 9 9950X 16-Core Processor (32 thr), 123 GB, vast 56910925
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
| **ours** | 583.0 | 1632.5 | 2263.6 | 4586.7 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.
Over 1000 ms: mean 1632.5, p80 2263.6

| catalog | median ms |
|---|---|
| 1 | 1707.6 |
| 4 | 1613.2 |
| 5 | 3026.5 |
| 6 | 4088.2 |
| 10 | 2371.3 |
| 12 | 546.9 |
| 20 | 416.2 |
| 21 | 305.3 |
| 22 | 10034.0 |
| 23 | 782.9 |
| 24 | 414.6 |
| 26 | 310.7 |
| 27 | 413.8 |
| 28 | 310.1 |
| 29 | 567.9 |
| 30 | 539.7 |
| 31 | 1798.7 |
| 33 | 2826.4 |
| 37 | 680.7 |
| 38 | 13174.4 |
| 39 | 771.6 |
| 40 | 308.7 |
| 41 | 580.2 |
| 42 | 1325.4 |
| 44 | 554.0 |
| 50 | 1394.0 |
| 56 | 2293.0 |
| 57 | 431.8 |
| 58 | 426.7 |
| 59 | 1372.6 |
| 61 | 667.6 |
| 62 | 1508.1 |
