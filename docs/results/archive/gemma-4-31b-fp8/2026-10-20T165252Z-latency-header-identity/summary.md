# gemma-4-31b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T165252Z
- repo commit: 326d316
- host: RTX PRO 6000 Blackwell Server Edition, 600/600 W, drv 580.95.05, PCIe 5x16, Intel(R) Xeon(R) 6767P (256 thr), 1007 GB, vast 56910915
- design: latency-v1, our rows
- layout: header
- option_orders: top_p:0.9+reversed
- profile: gemma-4-31b-fp8
- hf_revision: d7242548c457ab4b45bd3adb8937f2659af4739d
- prompt_layout: blurb_header
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 4.064415802187677, 'score': 5.312632033618169, 'noul': 6.658402657273458}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 4.0800743849861645, 'score': 5.4011976215667685, 'noul': 7.147109801942421}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 69.9 | 219.2 | 215.9 | 670.3 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 139.3 |
| 4 | 197.5 |
| 5 | 326.8 |
| 6 | 551.6 |
| 10 | 270.9 |
| 12 | 62.8 |
| 20 | 45.2 |
| 21 | 41.4 |
| 22 | 1332.9 |
| 23 | 100.4 |
| 24 | 47.5 |
| 26 | 43.9 |
| 27 | 47.2 |
| 28 | 42.9 |
| 29 | 67.8 |
| 30 | 52.2 |
| 31 | 158.1 |
| 33 | 203.9 |
| 37 | 74.0 |
| 38 | 2148.4 |
| 39 | 67.4 |
| 40 | 42.9 |
| 41 | 67.4 |
| 42 | 128.1 |
| 44 | 54.4 |
| 50 | 139.1 |
| 56 | 156.4 |
| 57 | 51.2 |
| 58 | 47.2 |
| 59 | 135.4 |
| 61 | 77.1 |
| 62 | 150.0 |
