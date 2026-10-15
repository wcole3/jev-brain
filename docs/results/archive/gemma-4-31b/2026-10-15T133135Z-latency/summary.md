# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-15T133135Z
- repo commit: f4700ee
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 91.9 | 892.5 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 156.5 |
| 4 | 276.5 |
| 5 | 444.8 |
| 6 | 720.3 |
| 10 | 357.7 |
| 12 | 86.6 |
| 20 | 62.0 |
| 21 | 57.0 |
| 22 | 1688.3 |
| 23 | 133.1 |
| 24 | 64.1 |
| 26 | 58.6 |
| 27 | 63.1 |
| 28 | 57.9 |
| 29 | 86.6 |
| 30 | 66.8 |
| 31 | 212.8 |
| 33 | 283.6 |
| 37 | 106.0 |
| 38 | 2890.6 |
| 39 | 109.4 |
| 40 | 57.4 |
| 41 | 88.1 |
| 42 | 183.1 |
| 44 | 68.9 |
| 50 | 192.5 |
| 56 | 228.9 |
| 57 | 68.4 |
| 58 | 65.9 |
| 59 | 181.0 |
| 61 | 105.9 |
| 62 | 210.3 |
