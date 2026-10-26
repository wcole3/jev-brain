# gemma-4-12b-qat latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T042800Z
- repo commit: e8b57ea-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-12b-qat
- hf_revision: 1d2c2d7f2466070e69d6fb3fd5ce9a7d75f2f6ee
- prompt_layout: blurb_header_reread
- option_orders: identity
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 3.0074889638490045, 'score': 12.941782505400122, 'noul': 2.244027515792647}, 'b': 0.0, 'source': 'gemma-4-12b-qat/blurb_header/calibration.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.02985209393941, 'score': 4.02985209393941, 'noul': 3.7595472755324946}, 'b': 0.0, 'source': 'gemma-4-12b-qat/blurb_header_reread/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'header': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'question_first': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 65.8 | 142.5 | 172.7 | 365.4 |
| AJev lora7 (Gemma 4 12B) (board, its own sample) | 69.1 | n/a | n/a | n/a |
| decisio 0.4.0 (Gemma 4 12B) (board, its own sample) | 37.8 | n/a | n/a | n/a |
| Winnow-12B (board, its own sample) | 72.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 79.8 |
| 4 | 118.6 |
| 5 | 201.4 |
| 6 | 283.8 |
| 10 | 211.6 |
| 12 | 49.2 |
| 20 | 34.6 |
| 21 | 33.2 |
| 22 | 853.3 |
| 23 | 89.6 |
| 24 | 38.8 |
| 26 | 39.0 |
| 27 | 37.0 |
| 28 | 38.1 |
| 29 | 52.0 |
| 30 | 44.1 |
| 31 | 122.8 |
| 33 | 142.5 |
| 37 | 77.6 |
| 38 | 1200.2 |
| 39 | 47.9 |
| 40 | 34.5 |
| 41 | 60.2 |
| 42 | 108.5 |
| 44 | 48.8 |
| 50 | 132.3 |
| 56 | 107.8 |
| 57 | 43.2 |
| 58 | 47.2 |
| 59 | 147.7 |
| 61 | 91.8 |
| 62 | 146.9 |
