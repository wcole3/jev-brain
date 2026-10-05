# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T050422Z
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
| **ours** | 113.6 | 671.6 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 213.8 |
| 4 | 283.2 |
| 5 | 456.1 |
| 6 | 611.2 |
| 10 | 348.4 |
| 12 | 91.0 |
| 20 | 61.9 |
| 21 | 58.3 |
| 22 | 1799.3 |
| 23 | 146.2 |
| 24 | 66.3 |
| 26 | 59.6 |
| 27 | 65.2 |
| 28 | 62.4 |
| 29 | 95.0 |
| 30 | 69.1 |
| 31 | 234.1 |
| 33 | 374.8 |
| 37 | 97.1 |
| 38 | 2705.6 |
| 39 | 117.5 |
| 40 | 60.1 |
| 41 | 92.1 |
| 42 | 147.2 |
| 44 | 72.2 |
| 48 | 197.4 |
| 50 | 206.7 |
| 56 | 248.1 |
| 57 | 72.3 |
| 58 | 67.6 |
| 59 | 203.1 |
| 61 | 116.8 |
| 62 | 200.7 |
