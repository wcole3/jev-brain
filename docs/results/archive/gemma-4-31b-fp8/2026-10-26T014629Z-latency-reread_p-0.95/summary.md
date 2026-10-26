# gemma-4-31b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T014629Z
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
| **ours** | 115.7 | 327.5 | 477.1 | 933.6 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 161.0 |
| 4 | 541.4 |
| 5 | 917.3 |
| 6 | 605.6 |
| 10 | 438.6 |
| 12 | 69.6 |
| 20 | 47.9 |
| 21 | 47.8 |
| 22 | 3585.7 |
| 23 | 95.5 |
| 24 | 53.2 |
| 26 | 43.3 |
| 27 | 41.8 |
| 28 | 40.5 |
| 29 | 65.0 |
| 30 | 138.3 |
| 31 | 459.0 |
| 33 | 228.3 |
| 37 | 103.7 |
| 38 | 2235.8 |
| 39 | 81.8 |
| 40 | 47.7 |
| 41 | 76.3 |
| 42 | 105.1 |
| 44 | 61.4 |
| 50 | 370.8 |
| 56 | 187.5 |
| 57 | 118.5 |
| 58 | 53.5 |
| 59 | 149.3 |
| 61 | 78.2 |
| 62 | 222.0 |
