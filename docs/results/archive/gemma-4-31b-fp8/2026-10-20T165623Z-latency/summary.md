# gemma-4-31b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T165623Z
- repo commit: 326d316
- host: RTX PRO 6000 Blackwell Server Edition, 600/600 W, drv 580.95.05, PCIe 5x16, Intel(R) Xeon(R) 6767P (256 thr), 1007 GB, vast 56910915
- design: latency-v1, our rows
- profile: gemma-4-31b-fp8
- hf_revision: d7242548c457ab4b45bd3adb8937f2659af4739d
- prompt_layout: blurb_header
- option_orders: top_p:0.9+reversed
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 4.064415802187677, 'score': 5.312632033618169, 'noul': 6.658402657273458}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 4.0800743849861645, 'score': 5.4011976215667685, 'noul': 7.147109801942421}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 100.9 | 274.1 | 359.5 | 696.4 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 146.1 |
| 4 | 399.8 |
| 5 | 659.1 |
| 6 | 606.9 |
| 10 | 292.6 |
| 12 | 78.0 |
| 20 | 45.4 |
| 21 | 41.3 |
| 22 | 2326.2 |
| 23 | 104.2 |
| 24 | 48.1 |
| 26 | 44.9 |
| 27 | 46.8 |
| 28 | 45.3 |
| 29 | 70.4 |
| 30 | 98.1 |
| 31 | 293.4 |
| 33 | 250.8 |
| 37 | 90.0 |
| 38 | 2234.5 |
| 39 | 68.7 |
| 40 | 51.5 |
| 41 | 75.5 |
| 42 | 139.8 |
| 44 | 61.3 |
| 50 | 203.4 |
| 56 | 204.5 |
| 57 | 103.6 |
| 58 | 57.7 |
| 59 | 138.9 |
| 61 | 91.4 |
| 62 | 206.0 |
