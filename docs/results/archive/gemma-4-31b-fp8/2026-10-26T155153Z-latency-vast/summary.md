# gemma-4-31b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T155153Z
- repo commit: 93ead2d
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 580.178.04, PCIe 5x16, AMD Ryzen Threadripper PRO 7995WX 96-Cores (192 thr), 251 GB, vast 57834132
- design: latency-v1, our rows
- profile: gemma-4-31b-fp8
- hf_revision: d7242548c457ab4b45bd3adb8937f2659af4739d
- prompt_layout: blurb_header_reread
- option_orders: top_p:0.9+reversed
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 4.064415802187677, 'score': 5.312632033618169, 'noul': 6.658402657273458}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread': {'T': {'choice': {'a': 6.848659791835596, 'b': -0.7918655897314246, 'floor': 0.05}, 'score': 5.301129957255362, 'noul': 7.148859552575357}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header_reread/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 4.0800743849861645, 'score': 5.4011976215667685, 'noul': 7.147109801942421}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.018926866464972, 'score': 5.366383698811015, 'noul': 7.327209275547249}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header_reread/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 112.6 | 342.1 | 454.7 | 829.8 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 148.7 |
| 4 | 453.1 |
| 5 | 741.8 |
| 6 | 656.9 |
| 10 | 465.7 |
| 12 | 81.3 |
| 20 | 36.6 |
| 21 | 33.4 |
| 22 | 3272.9 |
| 23 | 173.4 |
| 24 | 51.5 |
| 26 | 41.7 |
| 27 | 47.2 |
| 28 | 43.3 |
| 29 | 84.8 |
| 30 | 105.1 |
| 31 | 401.5 |
| 33 | 211.1 |
| 37 | 132.3 |
| 38 | 2646.4 |
| 39 | 80.9 |
| 40 | 42.2 |
| 41 | 105.1 |
| 42 | 213.2 |
| 44 | 81.2 |
| 50 | 357.5 |
| 56 | 192.5 |
| 57 | 92.2 |
| 58 | 66.8 |
| 59 | 306.7 |
| 61 | 148.2 |
| 62 | 300.4 |
