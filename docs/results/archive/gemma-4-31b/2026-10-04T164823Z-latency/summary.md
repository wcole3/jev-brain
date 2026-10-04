# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-04T164823Z
- repo commit: fd72395
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
| **ours** | 115.5 | 689.3 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 220.7 |
| 4 | 290.2 |
| 5 | 475.1 |
| 6 | 619.6 |
| 10 | 364.3 |
| 12 | 92.6 |
| 20 | 66.9 |
| 21 | 60.9 |
| 22 | 1879.5 |
| 23 | 152.7 |
| 24 | 72.8 |
| 26 | 63.2 |
| 27 | 70.5 |
| 28 | 65.3 |
| 29 | 98.4 |
| 30 | 71.5 |
| 31 | 238.0 |
| 33 | 397.8 |
| 37 | 101.6 |
| 38 | 2790.2 |
| 39 | 92.5 |
| 40 | 61.9 |
| 41 | 93.9 |
| 42 | 148.9 |
| 44 | 77.0 |
| 48 | 206.9 |
| 50 | 215.6 |
| 56 | 250.2 |
| 57 | 78.0 |
| 58 | 70.1 |
| 59 | 209.0 |
| 61 | 120.6 |
| 62 | 206.5 |
