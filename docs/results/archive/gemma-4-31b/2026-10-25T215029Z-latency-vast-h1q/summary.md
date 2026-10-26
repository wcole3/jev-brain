# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T215029Z
- repo commit: 3f1843f
- host: RTX PRO 6000 Blackwell, 550/600 W, drv 595.71.05, PCIe 5x16, Intel(R) Core(TM) i9-14900K (32 thr), 126 GB, vast 57722417
- design: latency-v1, our rows
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: blurb_header_reread
- option_orders: top_p:0.9+reversed
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.210749661448452, 'noul': 6.742793031492776}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread': {'T': {'choice': 4.0203754009072075, 'score': 5.38542849820243, 'noul': 7.214539306366964}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.279869783685001, 'noul': 7.103855559793786}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.039817995497652, 'score': 5.45121018579514, 'noul': 7.520177606094354}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 214.9 | 469.1 | 677.4 | 1057.7 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 244.8 |
| 4 | 632.0 |
| 5 | 1053.4 |
| 6 | 789.0 |
| 10 | 672.1 |
| 12 | 155.7 |
| 20 | 102.0 |
| 21 | 74.1 |
| 22 | 3974.2 |
| 23 | 298.1 |
| 24 | 104.2 |
| 26 | 75.6 |
| 27 | 98.8 |
| 28 | 76.1 |
| 29 | 186.8 |
| 30 | 205.3 |
| 31 | 689.4 |
| 33 | 334.3 |
| 37 | 219.4 |
| 38 | 2532.3 |
| 39 | 125.7 |
| 40 | 75.4 |
| 41 | 190.3 |
| 42 | 324.0 |
| 44 | 155.4 |
| 50 | 476.0 |
| 56 | 285.5 |
| 57 | 185.4 |
| 58 | 119.8 |
| 59 | 412.5 |
| 61 | 212.6 |
| 62 | 481.0 |
