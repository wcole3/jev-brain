# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T060512Z
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
| **ours** | 113.6 | 670.8 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 226.6 |
| 4 | 281.8 |
| 5 | 457.1 |
| 6 | 606.6 |
| 10 | 349.5 |
| 12 | 91.7 |
| 20 | 62.9 |
| 21 | 59.2 |
| 22 | 1795.7 |
| 23 | 147.3 |
| 24 | 66.6 |
| 26 | 61.1 |
| 27 | 67.4 |
| 28 | 63.1 |
| 29 | 95.1 |
| 30 | 70.7 |
| 31 | 230.8 |
| 33 | 381.6 |
| 37 | 94.9 |
| 38 | 2645.5 |
| 39 | 91.7 |
| 40 | 60.4 |
| 41 | 93.0 |
| 42 | 147.7 |
| 44 | 72.9 |
| 48 | 196.8 |
| 50 | 207.2 |
| 56 | 246.2 |
| 57 | 72.9 |
| 58 | 68.8 |
| 59 | 204.7 |
| 61 | 117.7 |
| 62 | 202.8 |
