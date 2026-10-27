# gemma-4-31b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T154731Z
- repo commit: 93ead2d
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 580.178.04, PCIe 5x16, AMD Ryzen Threadripper PRO 7995WX 96-Cores (192 thr), 251 GB, vast 57834132
- design: latency-v1, our rows
- layout: header
- option_orders: top_p:0.9+reversed
- profile: gemma-4-31b-fp8
- hf_revision: d7242548c457ab4b45bd3adb8937f2659af4739d
- prompt_layout: blurb_header_reread
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 4.064415802187677, 'score': 5.312632033618169, 'noul': 6.658402657273458}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread': {'T': {'choice': {'a': 6.848659791835596, 'b': -0.7918655897314246, 'floor': 0.05}, 'score': 5.301129957255362, 'noul': 7.148859552575357}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header_reread/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 4.0800743849861645, 'score': 5.4011976215667685, 'noul': 7.147109801942421}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.018926866464972, 'score': 5.366383698811015, 'noul': 7.327209275547249}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header_reread/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 67.2 | 235.9 | 248.6 | 730.4 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 120.1 |
| 4 | 214.1 |
| 5 | 349.8 |
| 6 | 627.6 |
| 10 | 302.9 |
| 12 | 60.9 |
| 20 | 36.7 |
| 21 | 33.1 |
| 22 | 1539.4 |
| 23 | 108.7 |
| 24 | 39.7 |
| 26 | 35.8 |
| 27 | 39.5 |
| 28 | 35.2 |
| 29 | 65.8 |
| 30 | 50.0 |
| 31 | 172.3 |
| 33 | 201.7 |
| 37 | 79.7 |
| 38 | 2488.4 |
| 39 | 80.2 |
| 40 | 34.5 |
| 41 | 66.0 |
| 42 | 146.3 |
| 44 | 51.3 |
| 50 | 151.6 |
| 56 | 162.1 |
| 57 | 50.8 |
| 58 | 41.6 |
| 59 | 147.4 |
| 61 | 81.9 |
| 62 | 170.6 |
