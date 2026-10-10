# gemma-4-31b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-09T235724Z
- repo commit: ee5e4be
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.71.05, PCIe 5x16, Intel(R) Core(TM) Ultra 9 285K (24 thr), 188 GB, vast 55115712
- design: latency-v1, our rows
- profile: gemma-4-31b-fp8
- hf_revision: d7242548c457ab4b45bd3adb8937f2659af4739d
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 67.9 | 612.9 |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 134.4 |
| 4 | 193.5 |
| 5 | 325.0 |
| 6 | 457.2 |
| 10 | 274.2 |
| 12 | 58.6 |
| 20 | 32.0 |
| 21 | 27.8 |
| 22 | 1400.0 |
| 23 | 103.9 |
| 24 | 36.7 |
| 26 | 37.2 |
| 27 | 41.2 |
| 28 | 36.5 |
| 29 | 66.3 |
| 30 | 49.9 |
| 31 | 161.1 |
| 33 | 195.1 |
| 37 | 77.0 |
| 38 | 2240.8 |
| 39 | 77.7 |
| 40 | 29.4 |
| 41 | 64.7 |
| 42 | 132.1 |
| 44 | 53.0 |
| 50 | 140.5 |
| 56 | 162.4 |
| 57 | 49.6 |
| 58 | 44.1 |
| 59 | 134.7 |
| 61 | 79.3 |
| 62 | 157.1 |
