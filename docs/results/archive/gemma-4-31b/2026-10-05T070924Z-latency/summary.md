# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T070924Z
- repo commit: 66b8531
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
| **ours** | 112.2 | 798.8 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 223.7 |
| 4 | 296.8 |
| 5 | 475.5 |
| 6 | 698.3 |
| 10 | 362.7 |
| 12 | 92.1 |
| 20 | 61.9 |
| 21 | 57.3 |
| 22 | 1856.1 |
| 23 | 145.6 |
| 24 | 65.8 |
| 26 | 59.8 |
| 27 | 64.8 |
| 28 | 59.8 |
| 29 | 94.3 |
| 30 | 70.1 |
| 31 | 229.9 |
| 33 | 371.6 |
| 37 | 94.5 |
| 38 | 2964.3 |
| 39 | 92.1 |
| 40 | 60.6 |
| 41 | 92.3 |
| 42 | 145.4 |
| 44 | 70.9 |
| 48 | 197.6 |
| 50 | 210.1 |
| 56 | 247.1 |
| 57 | 72.1 |
| 58 | 67.7 |
| 59 | 203.5 |
| 61 | 116.9 |
| 62 | 200.5 |
