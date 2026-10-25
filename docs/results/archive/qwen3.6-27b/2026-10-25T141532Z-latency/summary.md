# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T141532Z
- repo commit: 6a209a4-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: blurb_header_reread
- option_orders: identity
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6251477909763543, 'score': 2.061197148900324, 'noul': 1.264734324887902}, 'b': 0.0, 'source': 'qwen3.6-27b/blurb_header/calibration.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 1.659824132956001, 'score': 2.1314605853423614, 'noul': 1.5932935918585747}, 'b': 0.0, 'source': 'qwen3.6-27b/blurb_header_reread/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.6464561210660535, 'score': 1.9262389103053306, 'noul': 1.3881277937743584}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.627044078638005, 'score': 1.957392235350462, 'noul': 1.2806898963469258}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4848491265570403, 'score': 8.036469832567235, 'noul': 1.146202489120627}, 'b': 0.2558914960106792, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 162.8 | 399.8 | 494.1 | 901.2 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 292.0 |
| 4 | 242.9 |
| 5 | 497.6 |
| 6 | 636.9 |
| 10 | 529.3 |
| 12 | 134.9 |
| 20 | 103.8 |
| 21 | 95.0 |
| 22 | 1929.9 |
| 23 | 242.7 |
| 24 | 101.3 |
| 26 | 97.4 |
| 27 | 102.0 |
| 28 | 87.4 |
| 29 | 141.0 |
| 30 | 126.6 |
| 31 | 310.7 |
| 33 | 749.1 |
| 37 | 213.7 |
| 38 | 6168.0 |
| 39 | 123.2 |
| 40 | 99.2 |
| 41 | 140.4 |
| 42 | 273.7 |
| 44 | 127.1 |
| 50 | 402.6 |
| 56 | 886.0 |
| 57 | 120.0 |
| 58 | 109.7 |
| 59 | 380.1 |
| 61 | 224.1 |
| 62 | 382.5 |
