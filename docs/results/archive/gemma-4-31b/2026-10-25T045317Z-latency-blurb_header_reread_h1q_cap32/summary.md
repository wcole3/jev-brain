# gemma-4-31b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T045317Z
- repo commit: 6b44484-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- layout: blurb_header_reread_h1q_cap32
- profile: gemma-4-31b
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: blurb_header_reread
- option_orders: top_p:0.9+reversed
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.210749661448452, 'noul': 6.742793031492776}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread': {'T': {'choice': 3.982799623803248, 'score': 5.301129957255362, 'noul': 7.148859552575357}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread_h1q': {'T': {'choice': 4.221712636500382, 'score': 5.582782776787617, 'noul': 7.215888568945056}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread_h1q/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread_h1q_cap32': {'T': {'choice': 4.221712636500382, 'score': 5.582782776787617, 'noul': 7.215888568945056}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread_h1q_cap32/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread_h1q_noq2': {'T': {'choice': 4.221712636500382, 'score': 5.582782776787617, 'noul': 7.215888568945056}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread_h1q_noq2/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread_h1q_once': {'T': {'choice': 4.221712636500382, 'score': 5.582782776787617, 'noul': 7.215888568945056}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread_h1q_once/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread_h1q_opts': {'T': {'choice': 4.221712636500382, 'score': 5.582782776787617, 'noul': 7.215888568945056}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread_h1q_opts/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.279869783685001, 'noul': 7.103855559793786}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.018926866464972, 'score': 5.366383698811015, 'noul': 7.327209275547249}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread_h1q': {'T': {'choice': 4.237977221643095, 'score': 5.651830088699138, 'noul': 7.513954458122036}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread_h1q/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread_h1q_cap32': {'T': {'choice': 4.237977221643095, 'score': 5.651830088699138, 'noul': 7.513954458122036}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread_h1q_cap32/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread_h1q_noq2': {'T': {'choice': 4.237977221643095, 'score': 5.651830088699138, 'noul': 7.513954458122036}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread_h1q_noq2/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread_h1q_once': {'T': {'choice': 4.237977221643095, 'score': 5.651830088699138, 'noul': 7.513954458122036}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread_h1q_once/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread_h1q_opts': {'T': {'choice': 4.237977221643095, 'score': 5.651830088699138, 'noul': 7.513954458122036}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header_reread_h1q_opts/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 199.4 | 439.6 | 637.2 | 962.5 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 224.4 |
| 4 | 585.5 |
| 5 | 957.5 |
| 6 | 746.9 |
| 10 | 613.7 |
| 12 | 142.9 |
| 20 | 92.4 |
| 21 | 65.1 |
| 22 | 3685.6 |
| 23 | 276.0 |
| 24 | 94.7 |
| 26 | 66.3 |
| 27 | 88.0 |
| 28 | 67.8 |
| 29 | 172.3 |
| 30 | 187.9 |
| 31 | 638.0 |
| 33 | 313.8 |
| 37 | 202.4 |
| 38 | 2673.9 |
| 39 | 114.4 |
| 40 | 66.9 |
| 41 | 174.2 |
| 42 | 298.5 |
| 44 | 142.8 |
| 50 | 487.0 |
| 56 | 263.5 |
| 57 | 173.9 |
| 58 | 110.6 |
| 59 | 392.5 |
| 61 | 203.2 |
| 62 | 447.8 |
