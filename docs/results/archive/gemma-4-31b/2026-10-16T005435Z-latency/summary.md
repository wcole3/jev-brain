# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-16T005435Z
- repo commit: d674515
- host: RTX PRO 6000 Blackwell, 560/600 W, drv 595.104.02, PCIe 5x16, AMD EPYC 9554 64-Core Processor (256 thr), 1385 GB, vast 56172708
- design: latency-v1, our rows
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 97.1 | 811.5 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 169.1 |
| 4 | 286.7 |
| 5 | 467.9 |
| 6 | 666.1 |
| 10 | 378.0 |
| 12 | 91.9 |
| 20 | 63.6 |
| 21 | 59.6 |
| 22 | 1816.4 |
| 23 | 141.9 |
| 24 | 68.4 |
| 26 | 61.3 |
| 27 | 67.7 |
| 28 | 61.6 |
| 29 | 94.4 |
| 30 | 72.2 |
| 31 | 228.2 |
| 33 | 299.1 |
| 37 | 113.8 |
| 38 | 3295.8 |
| 39 | 95.2 |
| 40 | 61.7 |
| 41 | 96.0 |
| 42 | 202.4 |
| 44 | 72.9 |
| 50 | 208.7 |
| 56 | 246.1 |
| 57 | 72.2 |
| 58 | 69.0 |
| 59 | 202.5 |
| 61 | 117.7 |
| 62 | 232.7 |
