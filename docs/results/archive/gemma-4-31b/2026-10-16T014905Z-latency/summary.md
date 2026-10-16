# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-16T014905Z
- repo commit: bf428eb
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.104.02, PCIe 5x16, AMD EPYC 9554 64-Core Processor (256 thr), 1385 GB, vast 56172708
- design: latency-v1, our rows
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 95.5 | 875.7 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 168.0 |
| 4 | 288.5 |
| 5 | 466.0 |
| 6 | 778.5 |
| 10 | 373.7 |
| 12 | 91.1 |
| 20 | 63.2 |
| 21 | 59.5 |
| 22 | 1793.6 |
| 23 | 139.6 |
| 24 | 67.1 |
| 26 | 61.0 |
| 27 | 67.2 |
| 28 | 61.5 |
| 29 | 93.2 |
| 30 | 70.8 |
| 31 | 225.5 |
| 33 | 294.4 |
| 37 | 111.8 |
| 38 | 3054.3 |
| 39 | 117.1 |
| 40 | 60.2 |
| 41 | 94.9 |
| 42 | 191.9 |
| 44 | 71.8 |
| 50 | 199.2 |
| 56 | 240.0 |
| 57 | 70.6 |
| 58 | 68.8 |
| 59 | 192.7 |
| 61 | 112.6 |
| 62 | 220.4 |
