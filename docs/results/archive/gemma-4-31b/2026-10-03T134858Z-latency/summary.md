# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-03T134858Z
- repo commit: 3e58290
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 615.71.09, PCIe 4x16, AMD EPYC 7532 32-Core Processor (128 thr), 1008 GB, vast 54017289
- design: latency-v1, our rows
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: decider_chat
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 94.8 | 656.7 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 172.5 |
| 4 | 270.8 |
| 5 | 453.4 |
| 6 | 620.8 |
| 10 | 340.7 |
| 12 | 65.8 |
| 20 | 59.5 |
| 21 | 56.0 |
| 22 | 1798.7 |
| 23 | 142.2 |
| 24 | 58.8 |
| 26 | 57.8 |
| 27 | 59.0 |
| 28 | 61.9 |
| 29 | 91.0 |
| 30 | 68.8 |
| 31 | 229.3 |
| 33 | 319.1 |
| 37 | 95.3 |
| 38 | 1248.3 |
| 39 | 71.4 |
| 40 | 56.3 |
| 41 | 66.7 |
| 42 | 141.4 |
| 44 | 60.5 |
| 48 | 196.0 |
| 50 | 225.0 |
| 56 | 233.9 |
| 57 | 69.8 |
| 58 | 66.7 |
| 59 | 199.5 |
| 61 | 115.3 |
| 62 | 197.9 |
