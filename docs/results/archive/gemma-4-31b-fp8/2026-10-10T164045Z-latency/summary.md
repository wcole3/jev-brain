# gemma-4-31b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T164045Z
- repo commit: 9409223
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-31b-fp8
- hf_revision: d7242548c457ab4b45bd3adb8937f2659af4739d
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 72.2 | 623.0 |
| Decider chat · Gemma-4-31B (board, its own sample) | 108.5 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 121.8 |
| 4 | 199.5 |
| 5 | 339.8 |
| 6 | 471.2 |
| 10 | 274.2 |
| 12 | 67.6 |
| 20 | 47.4 |
| 21 | 45.6 |
| 22 | 1396.3 |
| 23 | 109.2 |
| 24 | 52.7 |
| 26 | 47.3 |
| 27 | 50.0 |
| 28 | 47.0 |
| 29 | 68.5 |
| 30 | 55.7 |
| 31 | 163.4 |
| 33 | 203.7 |
| 37 | 80.6 |
| 38 | 2255.5 |
| 39 | 80.3 |
| 40 | 50.0 |
| 41 | 70.5 |
| 42 | 137.1 |
| 44 | 60.8 |
| 50 | 146.9 |
| 56 | 161.7 |
| 57 | 56.3 |
| 58 | 55.1 |
| 59 | 136.9 |
| 61 | 84.4 |
| 62 | 156.8 |
