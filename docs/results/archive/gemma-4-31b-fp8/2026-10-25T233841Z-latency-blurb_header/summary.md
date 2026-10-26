# gemma-4-31b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T233841Z
- repo commit: 3f1843f-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- layout: blurb_header
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
| **ours** | 94.3 | 267.7 | 355.8 | 709.5 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 130.2 |
| 4 | 381.9 |
| 5 | 659.5 |
| 6 | 574.6 |
| 10 | 294.4 |
| 12 | 67.1 |
| 20 | 45.2 |
| 21 | 41.8 |
| 22 | 2307.4 |
| 23 | 106.5 |
| 24 | 49.4 |
| 26 | 43.5 |
| 27 | 45.8 |
| 28 | 43.9 |
| 29 | 68.5 |
| 30 | 99.9 |
| 31 | 332.4 |
| 33 | 231.5 |
| 37 | 85.5 |
| 38 | 2283.3 |
| 39 | 69.1 |
| 40 | 45.3 |
| 41 | 67.8 |
| 42 | 130.9 |
| 44 | 56.6 |
| 50 | 190.1 |
| 56 | 180.9 |
| 57 | 94.9 |
| 58 | 54.4 |
| 59 | 132.6 |
| 61 | 78.3 |
| 62 | 192.1 |
