# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-04T014354Z
- repo commit: 0aeee17
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.84, PCIe 5x16, AMD Ryzen 9 9950X3D 16-Core Processor (32 thr), 92 GB, vast 54088302
- design: latency-v1, our rows
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 105.7 | 614.8 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 186.3 |
| 4 | 257.5 |
| 5 | 420.7 |
| 6 | 575.7 |
| 10 | 328.7 |
| 12 | 83.3 |
| 20 | 54.3 |
| 21 | 51.4 |
| 22 | 1729.3 |
| 23 | 136.4 |
| 24 | 59.2 |
| 26 | 54.2 |
| 27 | 58.8 |
| 28 | 53.5 |
| 29 | 87.3 |
| 30 | 61.4 |
| 31 | 218.1 |
| 33 | 342.4 |
| 37 | 87.7 |
| 38 | 2316.9 |
| 39 | 88.0 |
| 40 | 52.2 |
| 41 | 86.4 |
| 42 | 137.8 |
| 44 | 63.9 |
| 48 | 188.0 |
| 50 | 197.2 |
| 56 | 229.2 |
| 57 | 63.5 |
| 58 | 60.5 |
| 59 | 192.8 |
| 61 | 110.2 |
| 62 | 192.5 |
