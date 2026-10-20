# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T174219Z
- repo commit: 18ab6ae
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.71.05, PCIe 5x16, Intel(R) Core(TM) Ultra 9 285K (24 thr), 188 GB, vast 56912441
- design: latency-v1, our rows
- layout: header
- option_orders: top_p:0.9+reversed
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: blurb_header
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.210749661448452, 'noul': 6.742793031492776}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.279869783685001, 'noul': 7.103855559793786}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 92.7 | 280.4 | 299.8 | 784.4 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 181.9 |
| 4 | 280.8 |
| 5 | 453.3 |
| 6 | 626.5 |
| 10 | 376.7 |
| 12 | 87.3 |
| 20 | 56.5 |
| 21 | 52.3 |
| 22 | 1800.3 |
| 23 | 139.8 |
| 24 | 63.2 |
| 26 | 55.1 |
| 27 | 62.8 |
| 28 | 54.7 |
| 29 | 90.8 |
| 30 | 67.2 |
| 31 | 228.8 |
| 33 | 286.4 |
| 37 | 110.5 |
| 38 | 2910.9 |
| 39 | 112.8 |
| 40 | 53.4 |
| 41 | 92.1 |
| 42 | 194.7 |
| 44 | 67.8 |
| 50 | 198.7 |
| 56 | 234.3 |
| 57 | 67.2 |
| 58 | 65.4 |
| 59 | 194.3 |
| 61 | 112.7 |
| 62 | 225.3 |
