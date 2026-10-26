# gemma-4-31b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T013742Z
- repo commit: 46fe77f-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- option_orders: top_p:0.9+reversed
- profile: gemma-4-31b-fp8
- hf_revision: d7242548c457ab4b45bd3adb8937f2659af4739d
- prompt_layout: blurb_header_reread
- option_orders_images: identity
- calibration: {'blurb_header': {'T': {'choice': 4.064415802187677, 'score': 5.312632033618169, 'noul': 6.658402657273458}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'blurb_header_reread': {'T': {'choice': 3.982799623803248, 'score': 5.301129957255362, 'noul': 7.148859552575357}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header_reread/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 4.0800743849861645, 'score': 5.4011976215667685, 'noul': 7.147109801942421}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.018926866464972, 'score': 5.366383698811015, 'noul': 7.327209275547249}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/blurb_header_reread/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 98.4 | 288.4 | 344.0 | 903.3 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 116.8 |
| 4 | 183.0 |
| 5 | 889.0 |
| 6 | 525.9 |
| 10 | 214.9 |
| 12 | 65.3 |
| 20 | 46.4 |
| 21 | 43.9 |
| 22 | 3537.7 |
| 23 | 98.3 |
| 24 | 48.9 |
| 26 | 44.0 |
| 27 | 46.6 |
| 28 | 42.5 |
| 29 | 66.0 |
| 30 | 122.6 |
| 31 | 456.9 |
| 33 | 208.6 |
| 37 | 74.4 |
| 38 | 2066.9 |
| 39 | 75.7 |
| 40 | 39.5 |
| 41 | 63.2 |
| 42 | 98.6 |
| 44 | 52.1 |
| 50 | 286.1 |
| 56 | 170.1 |
| 57 | 105.8 |
| 58 | 45.4 |
| 59 | 142.1 |
| 61 | 73.7 |
| 62 | 146.0 |
