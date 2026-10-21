# gemma-4-12b-qat latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-21T115055Z
- repo commit: 152cb2c
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-12b-qat
- hf_revision: 1d2c2d7f2466070e69d6fb3fd5ce9a7d75f2f6ee
- prompt_layout: blurb_header
- option_orders: top_p:0.9+reversed
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 2.9343492139450453, 'score': 2.9343492139450453, 'noul': 2.206278444481428}, 'b': 0.0, 'source': 'gemma-4-12b-qat/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'header': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'question_first': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 3.0074889638490045, 'score': 12.941782505400122, 'noul': 2.244027515792647}, 'b': 0.0, 'source': 'gemma-4-12b-qat/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'header': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'question_first': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 82.2 | 181.1 | 221.0 | 450.3 |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 110.7 |
| 4 | 251.7 |
| 5 | 410.7 |
| 6 | 387.4 |
| 10 | 159.1 |
| 12 | 74.4 |
| 20 | 41.9 |
| 21 | 64.0 |
| 22 | 1244.8 |
| 23 | 99.1 |
| 24 | 68.5 |
| 26 | 36.6 |
| 27 | 34.7 |
| 28 | 66.0 |
| 29 | 69.6 |
| 30 | 72.5 |
| 31 | 208.9 |
| 33 | 207.6 |
| 37 | 73.2 |
| 38 | 1287.4 |
| 39 | 67.0 |
| 40 | 67.7 |
| 41 | 75.4 |
| 42 | 100.2 |
| 44 | 77.9 |
| 50 | 160.0 |
| 56 | 168.0 |
| 57 | 77.4 |
| 58 | 76.0 |
| 59 | 86.2 |
| 61 | 59.1 |
| 62 | 134.4 |
