# qwen3.6-27b-fp8 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T000122Z
- repo commit: ee5e4be
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 615.71.09, PCIe 5x16, AMD Ryzen Threadripper PRO 9955WX 16-Cores (32 thr), 251 GB, vast 55115714
- design: latency-v1, our rows
- profile: qwen3.6-27b-fp8
- hf_revision: e89b16ebf1988b3d6befa7de50abc2d76f26eb09
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.6585098155596096, 'score': 1.9436420520554476, 'noul': 1.4027279458983484}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.6323603603116188, 'score': 1.9743652236518074, 'noul': 1.2859386323824527}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.475862833432394, 'score': 7.858322898611463, 'noul': 1.2234832727963472}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 54.8 | 446.6 |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 162.9 |
| 4 | 151.4 |
| 5 | 287.1 |
| 6 | 394.0 |
| 10 | 238.3 |
| 12 | 51.0 |
| 20 | 40.8 |
| 21 | 33.0 |
| 22 | 1001.7 |
| 23 | 82.6 |
| 24 | 36.1 |
| 26 | 33.2 |
| 27 | 35.9 |
| 28 | 33.0 |
| 29 | 53.2 |
| 30 | 50.8 |
| 31 | 155.9 |
| 33 | 260.1 |
| 37 | 63.4 |
| 38 | 1445.0 |
| 39 | 102.5 |
| 40 | 33.0 |
| 41 | 54.2 |
| 42 | 133.5 |
| 44 | 52.1 |
| 50 | 137.0 |
| 56 | 223.2 |
| 57 | 42.0 |
| 58 | 37.1 |
| 59 | 137.9 |
| 61 | 64.2 |
| 62 | 147.0 |
