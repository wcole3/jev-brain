# gemma-4-12b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T023713Z
- repo commit: e8b57ea-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-12b
- hf_revision: 707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7
- prompt_layout: blurb_header_reread
- option_orders: identity
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 4.035253781242961, 'score': 4.035253781242961, 'noul': 4.035253781242961}, 'b': 0.0, 'source': 'gemma-4-12b/blurb_header/calibration.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.02985209393941, 'score': 4.02985209393941, 'noul': 3.7595472755324946}, 'b': 0.0, 'source': 'gemma-4-12b/blurb_header_reread/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'header': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'question_first': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 63.9 | 145.3 | 178.4 | 358.9 |
| AJev lora7 (Gemma 4 12B) (board, its own sample) | 69.1 | n/a | n/a | n/a |
| decisio 0.4.0 (Gemma 4 12B) (board, its own sample) | 37.8 | n/a | n/a | n/a |
| Winnow-12B (board, its own sample) | 72.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 80.4 |
| 4 | 125.3 |
| 5 | 202.3 |
| 6 | 284.0 |
| 10 | 238.1 |
| 12 | 52.1 |
| 20 | 36.3 |
| 21 | 34.6 |
| 22 | 857.5 |
| 23 | 91.2 |
| 24 | 41.2 |
| 26 | 37.2 |
| 27 | 39.9 |
| 28 | 38.6 |
| 29 | 53.6 |
| 30 | 48.7 |
| 31 | 128.2 |
| 33 | 140.1 |
| 37 | 80.6 |
| 38 | 1172.1 |
| 39 | 51.6 |
| 40 | 36.7 |
| 41 | 60.7 |
| 42 | 116.9 |
| 44 | 52.5 |
| 50 | 143.8 |
| 56 | 113.8 |
| 57 | 46.5 |
| 58 | 45.6 |
| 59 | 148.4 |
| 61 | 93.7 |
| 62 | 161.2 |
