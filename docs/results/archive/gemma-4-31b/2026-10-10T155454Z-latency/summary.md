# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T155454Z
- repo commit: 9409223
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 112.7 | 875.3 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 199.0 |
| 4 | 291.3 |
| 5 | 471.2 |
| 6 | 754.7 |
| 10 | 386.3 |
| 12 | 93.1 |
| 20 | 68.5 |
| 21 | 64.2 |
| 22 | 1798.9 |
| 23 | 147.0 |
| 24 | 73.9 |
| 26 | 66.1 |
| 27 | 71.7 |
| 28 | 66.5 |
| 29 | 98.9 |
| 30 | 81.2 |
| 31 | 237.2 |
| 33 | 301.0 |
| 37 | 122.1 |
| 38 | 3044.6 |
| 39 | 147.8 |
| 40 | 75.7 |
| 41 | 105.9 |
| 42 | 220.2 |
| 44 | 78.5 |
| 50 | 233.7 |
| 56 | 277.0 |
| 57 | 90.7 |
| 58 | 83.7 |
| 59 | 210.1 |
| 61 | 126.3 |
| 62 | 238.5 |
