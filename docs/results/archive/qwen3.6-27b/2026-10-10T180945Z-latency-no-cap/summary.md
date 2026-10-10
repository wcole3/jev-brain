# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T180945Z
- repo commit: 9409223
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- arm (DS-032 diagnosis): shipped profile without the token cap: EXTRA_ARGS=--scheduling-policy priority --speculative-config {"method":"mtp","num_speculative_tokens":3,"disable_eagle_block_drop":true}
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6464561210660535, 'score': 1.9262389103053306, 'noul': 1.3881277937743584}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.627044078638005, 'score': 1.957392235350462, 'noul': 1.2806898963469258}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4848491265570403, 'score': 8.036469832567235, 'noul': 1.146202489120627}, 'b': 0.2558914960106792, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 171.8 | 858.5 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 520.2 |
| 4 | 351.1 |
| 5 | 602.7 |
| 6 | 738.3 |
| 10 | 468.4 |
| 12 | 156.8 |
| 20 | 150.7 |
| 21 | 142.8 |
| 22 | 1602.5 |
| 23 | 205.6 |
| 24 | 149.2 |
| 26 | 144.5 |
| 27 | 136.9 |
| 28 | 137.0 |
| 29 | 151.0 |
| 30 | 153.1 |
| 31 | 350.0 |
| 33 | 675.8 |
| 37 | 161.2 |
| 38 | 2571.5 |
| 39 | 168.2 |
| 40 | 161.3 |
| 41 | 165.1 |
| 42 | 373.7 |
| 44 | 151.4 |
| 50 | 320.3 |
| 56 | 624.5 |
| 57 | 149.4 |
| 58 | 144.8 |
| 59 | 328.6 |
| 61 | 133.2 |
| 62 | 338.8 |
