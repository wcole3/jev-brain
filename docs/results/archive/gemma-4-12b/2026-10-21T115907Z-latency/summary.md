# gemma-4-12b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-21T115907Z
- repo commit: 152cb2c
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-12b
- hf_revision: 707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7
- prompt_layout: blurb_header
- option_orders: top_p:0.9+reversed
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 3.984749995188946, 'score': 3.984749995188946, 'noul': 3.984749995188946}, 'b': 0.0, 'source': 'gemma-4-12b/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'header': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'question_first': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 4.035253781242961, 'score': 4.035253781242961, 'noul': 4.035253781242961}, 'b': 0.0, 'source': 'gemma-4-12b/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'header': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'question_first': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 83.1 | 182.4 | 220.6 | 465.6 |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 84.4 |
| 4 | 261.4 |
| 5 | 421.6 |
| 6 | 380.8 |
| 10 | 191.3 |
| 12 | 77.3 |
| 20 | 39.9 |
| 21 | 37.8 |
| 22 | 1317.7 |
| 23 | 102.5 |
| 24 | 71.5 |
| 26 | 40.0 |
| 27 | 38.2 |
| 28 | 69.9 |
| 29 | 75.3 |
| 30 | 79.1 |
| 31 | 214.3 |
| 33 | 225.2 |
| 37 | 78.8 |
| 38 | 1212.0 |
| 39 | 54.8 |
| 40 | 66.6 |
| 41 | 80.9 |
| 42 | 105.1 |
| 44 | 78.5 |
| 50 | 162.2 |
| 56 | 162.8 |
| 57 | 82.7 |
| 58 | 75.9 |
| 59 | 92.0 |
| 61 | 67.9 |
| 62 | 138.5 |
