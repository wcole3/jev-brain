# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T152806Z
- repo commit: 9409223
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6464561210660535, 'score': 1.9262389103053306, 'noul': 1.3881277937743584}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.627044078638005, 'score': 1.957392235350462, 'noul': 1.2806898963469258}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4848491265570403, 'score': 8.036469832567235, 'noul': 1.146202489120627}, 'b': 0.2558914960106792, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 176.0 | 995.1 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 515.7 |
| 4 | 333.6 |
| 5 | 682.2 |
| 6 | 854.4 |
| 10 | 518.8 |
| 12 | 158.2 |
| 20 | 146.9 |
| 21 | 157.5 |
| 22 | 1988.5 |
| 23 | 208.1 |
| 24 | 156.6 |
| 26 | 152.7 |
| 27 | 160.5 |
| 28 | 165.9 |
| 29 | 160.3 |
| 30 | 161.9 |
| 31 | 346.0 |
| 33 | 623.3 |
| 37 | 164.2 |
| 38 | 2651.8 |
| 39 | 317.0 |
| 40 | 159.4 |
| 41 | 168.1 |
| 42 | 301.6 |
| 44 | 140.0 |
| 50 | 341.9 |
| 56 | 675.0 |
| 57 | 147.1 |
| 58 | 164.5 |
| 59 | 324.7 |
| 61 | 159.2 |
| 62 | 337.9 |
