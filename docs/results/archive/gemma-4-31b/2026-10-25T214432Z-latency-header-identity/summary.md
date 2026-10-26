# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T214432Z
- repo commit: 3f1843f
- host: RTX PRO 6000 Blackwell, 550/600 W, drv 595.71.05, PCIe 5x16, Intel(R) Core(TM) i9-14900K (32 thr), 126 GB, vast 57722417
- design: latency-v1, our rows
- layout: header
- option_orders: top_p:0.9+reversed
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: blurb_header_reread
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.210749661448452, 'noul': 6.742793031492776}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread': {'T': {'choice': 4.0203754009072075, 'score': 5.38542849820243, 'noul': 7.214539306366964}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.279869783685001, 'noul': 7.103855559793786}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.039817995497652, 'score': 5.45121018579514, 'noul': 7.520177606094354}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 103.5 | 299.3 | 351.1 | 782.2 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 197.4 |
| 4 | 307.9 |
| 5 | 500.2 |
| 6 | 686.6 |
| 10 | 412.1 |
| 12 | 97.2 |
| 20 | 66.9 |
| 21 | 63.0 |
| 22 | 1952.6 |
| 23 | 155.1 |
| 24 | 71.7 |
| 26 | 62.8 |
| 27 | 64.9 |
| 28 | 65.1 |
| 29 | 101.8 |
| 30 | 76.1 |
| 31 | 250.3 |
| 33 | 318.2 |
| 37 | 121.3 |
| 38 | 2591.1 |
| 39 | 102.1 |
| 40 | 64.1 |
| 41 | 101.4 |
| 42 | 213.1 |
| 44 | 76.9 |
| 50 | 220.0 |
| 56 | 258.4 |
| 57 | 76.6 |
| 58 | 74.3 |
| 59 | 215.1 |
| 61 | 124.7 |
| 62 | 246.8 |
