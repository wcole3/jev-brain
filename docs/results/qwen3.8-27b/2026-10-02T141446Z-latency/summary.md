# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-02T141446Z
- repo commit: 7f927b0
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 595.84, PCIe 5x16, Intel(R) Core(TM) Ultra 7 265K (20 thr), 125 GB, vast 53868967
- design: latency-v1, our rows
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: decider_chat
- option_orders: identity
- temperatures: {'decider_chat': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'header': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'question_first': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 90.2 | 623.9 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex 27B (board, its own sample) | 108.0 | n/a |
| Jevfire (Qwen3.8-27B-FP8) (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 273.4 |
| 4 | 232.7 |
| 5 | 428.5 |
| 6 | 570.7 |
| 10 | 333.8 |
| 12 | 61.7 |
| 20 | 63.6 |
| 21 | 49.2 |
| 22 | 1476.0 |
| 23 | 134.0 |
| 24 | 51.9 |
| 26 | 49.8 |
| 27 | 51.8 |
| 28 | 49.7 |
| 29 | 84.7 |
| 30 | 63.2 |
| 31 | 243.7 |
| 33 | 406.4 |
| 37 | 89.6 |
| 38 | 1574.2 |
| 39 | 87.1 |
| 40 | 49.6 |
| 41 | 64.1 |
| 42 | 134.4 |
| 44 | 64.8 |
| 48 | 161.6 |
| 50 | 231.7 |
| 56 | 380.9 |
| 57 | 66.1 |
| 58 | 64.3 |
| 59 | 228.2 |
| 61 | 111.5 |
| 62 | 225.6 |
