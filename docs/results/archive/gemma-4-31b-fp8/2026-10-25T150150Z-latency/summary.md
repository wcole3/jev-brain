# gemma-4-31b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T150150Z
- repo commit: dba35fb-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-31b-fp8
- hf_revision: d7242548c457ab4b45bd3adb8937f2659af4739d
- prompt_layout: blurb_header_reread
- option_orders: top_p:0.9+reversed
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 4.064415802187677, 'score': 5.312632033618169, 'noul': 6.658402657273458}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread': {'T': {'choice': 4.0203754009072075, 'score': 5.38542849820243, 'noul': 7.214539306366964}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header_reread/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 4.0800743849861645, 'score': 5.4011976215667685, 'noul': 7.147109801942421}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.039817995497652, 'score': 5.45121018579514, 'noul': 7.520177606094354}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header_reread/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 135.5 | 329.0 | 431.9 | 789.7 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 158.5 |
| 4 | 400.8 |
| 5 | 673.8 |
| 6 | 603.6 |
| 10 | 431.7 |
| 12 | 107.1 |
| 20 | 68.4 |
| 21 | 50.1 |
| 22 | 2848.0 |
| 23 | 188.0 |
| 24 | 70.2 |
| 26 | 56.0 |
| 27 | 63.0 |
| 28 | 52.3 |
| 29 | 118.1 |
| 30 | 135.6 |
| 31 | 441.5 |
| 33 | 239.9 |
| 37 | 132.8 |
| 38 | 2307.0 |
| 39 | 81.1 |
| 40 | 71.8 |
| 41 | 118.8 |
| 42 | 203.5 |
| 44 | 103.8 |
| 50 | 320.7 |
| 56 | 196.8 |
| 57 | 125.1 |
| 58 | 75.7 |
| 59 | 271.1 |
| 61 | 143.3 |
| 62 | 302.5 |
