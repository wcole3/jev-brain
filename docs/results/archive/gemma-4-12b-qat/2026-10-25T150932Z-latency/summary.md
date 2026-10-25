# gemma-4-12b-qat latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T150932Z
- repo commit: dba35fb-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-12b-qat
- hf_revision: 1d2c2d7f2466070e69d6fb3fd5ce9a7d75f2f6ee
- prompt_layout: blurb_header_reread
- option_orders: identity
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 3.0074889638490045, 'score': 12.941782505400122, 'noul': 2.244027515792647}, 'b': 0.0, 'source': 'gemma-4-12b-qat/blurb_header/calibration.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.018175387617537, 'score': 4.018175387617537, 'noul': 4.018175387617537}, 'b': 0.0, 'source': 'gemma-4-12b-qat/blurb_header_reread/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'header': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'question_first': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 83.2 | 161.7 | 204.2 | 394.9 |
| AJev lora7 (Gemma 4 12B) (board, its own sample) | 69.1 | n/a | n/a | n/a |
| decisio 0.4.0 (Gemma 4 12B) (board, its own sample) | 37.8 | n/a | n/a | n/a |
| Winnow-12B (board, its own sample) | 72.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 96.0 |
| 4 | 126.9 |
| 5 | 212.4 |
| 6 | 287.5 |
| 10 | 243.2 |
| 12 | 80.1 |
| 20 | 46.0 |
| 21 | 38.4 |
| 22 | 911.7 |
| 23 | 110.9 |
| 24 | 47.8 |
| 26 | 44.3 |
| 27 | 44.3 |
| 28 | 43.7 |
| 29 | 76.5 |
| 30 | 69.3 |
| 31 | 142.7 |
| 33 | 132.7 |
| 37 | 92.9 |
| 38 | 1243.0 |
| 39 | 77.6 |
| 40 | 40.7 |
| 41 | 81.1 |
| 42 | 125.9 |
| 44 | 74.4 |
| 50 | 177.8 |
| 56 | 116.2 |
| 57 | 59.8 |
| 58 | 52.3 |
| 59 | 159.7 |
| 61 | 99.1 |
| 62 | 173.2 |
