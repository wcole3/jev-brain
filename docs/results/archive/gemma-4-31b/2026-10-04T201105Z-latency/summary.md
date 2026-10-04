# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-04T201105Z
- repo commit: f0e5b9c
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
| **ours** | 127.3 | 713.4 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 210.0 |
| 4 | 303.0 |
| 5 | 499.4 |
| 6 | 655.3 |
| 10 | 375.6 |
| 12 | 100.2 |
| 20 | 72.2 |
| 21 | 69.6 |
| 22 | 1920.4 |
| 23 | 167.2 |
| 24 | 78.9 |
| 26 | 72.7 |
| 27 | 75.0 |
| 28 | 71.6 |
| 29 | 107.6 |
| 30 | 81.5 |
| 31 | 255.3 |
| 33 | 440.0 |
| 37 | 117.2 |
| 38 | 3120.7 |
| 39 | 151.8 |
| 40 | 71.7 |
| 41 | 107.1 |
| 42 | 166.1 |
| 44 | 86.9 |
| 48 | 223.9 |
| 50 | 237.7 |
| 56 | 275.3 |
| 57 | 86.5 |
| 58 | 87.4 |
| 59 | 224.1 |
| 61 | 133.1 |
| 62 | 225.5 |
