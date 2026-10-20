# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T174655Z
- repo commit: 18ab6ae
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.71.05, PCIe 5x16, Intel(R) Core(TM) Ultra 9 285K (24 thr), 188 GB, vast 56912441
- design: latency-v1, our rows
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: blurb_header
- option_orders: top_p:0.9+reversed
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.210749661448452, 'noul': 6.742793031492776}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.279869783685001, 'noul': 7.103855559793786}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 124.8 | 361.1 | 504.9 | 954.5 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 209.9 |
| 4 | 574.3 |
| 5 | 938.1 |
| 6 | 763.1 |
| 10 | 408.3 |
| 12 | 91.7 |
| 20 | 66.7 |
| 21 | 57.0 |
| 22 | 3078.2 |
| 23 | 143.0 |
| 24 | 67.4 |
| 26 | 59.2 |
| 27 | 66.2 |
| 28 | 57.8 |
| 29 | 94.9 |
| 30 | 125.3 |
| 31 | 432.2 |
| 33 | 348.4 |
| 37 | 116.6 |
| 38 | 3566.2 |
| 39 | 90.1 |
| 40 | 54.4 |
| 41 | 92.1 |
| 42 | 196.2 |
| 44 | 87.6 |
| 50 | 279.3 |
| 56 | 256.7 |
| 57 | 121.3 |
| 58 | 66.0 |
| 59 | 194.8 |
| 61 | 113.2 |
| 62 | 277.6 |
