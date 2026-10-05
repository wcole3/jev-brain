# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T053624Z
- repo commit: d102ce2
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 114.2 | 667.0 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 214.5 |
| 4 | 280.5 |
| 5 | 455.3 |
| 6 | 611.0 |
| 10 | 348.8 |
| 12 | 91.0 |
| 20 | 61.7 |
| 21 | 57.6 |
| 22 | 1774.8 |
| 23 | 146.6 |
| 24 | 65.9 |
| 26 | 61.3 |
| 27 | 64.9 |
| 28 | 61.9 |
| 29 | 95.2 |
| 30 | 69.3 |
| 31 | 230.1 |
| 33 | 366.3 |
| 37 | 95.7 |
| 38 | 2688.7 |
| 39 | 91.4 |
| 40 | 59.8 |
| 41 | 92.6 |
| 42 | 146.7 |
| 44 | 71.7 |
| 48 | 199.0 |
| 50 | 209.0 |
| 56 | 244.7 |
| 57 | 72.4 |
| 58 | 69.2 |
| 59 | 204.2 |
| 61 | 118.2 |
| 62 | 202.8 |
