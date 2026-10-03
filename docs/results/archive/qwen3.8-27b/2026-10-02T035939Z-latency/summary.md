# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-02T035939Z
- repo commit: 7a5d9b6
- host: RTX PRO 6000 Blackwell, 450/600 W, drv 580.173.02, PCIe 4x16, AMD EPYC 7742 64-Core Processor (256 thr), 504 GB, vast 53796429
- design: latency-v1, our rows
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: decider_chat
- option_orders: identity
- temperatures: {'decider_chat': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'header': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'question_first': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 104.7 | 724.7 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex 27B (board, its own sample) | 108.0 | n/a |
| Jevfire (Qwen3.8-27B-FP8) (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 355.4 |
| 4 | 268.0 |
| 5 | 491.0 |
| 6 | 649.9 |
| 10 | 380.4 |
| 12 | 71.9 |
| 20 | 72.8 |
| 21 | 62.1 |
| 22 | 1656.7 |
| 23 | 151.8 |
| 24 | 82.0 |
| 26 | 61.1 |
| 27 | 61.1 |
| 28 | 60.2 |
| 29 | 95.1 |
| 30 | 73.0 |
| 31 | 273.9 |
| 33 | 514.8 |
| 37 | 102.5 |
| 38 | 1880.3 |
| 39 | 123.0 |
| 40 | 62.7 |
| 41 | 72.8 |
| 42 | 151.5 |
| 44 | 71.8 |
| 48 | 182.7 |
| 50 | 255.6 |
| 56 | 426.5 |
| 57 | 100.2 |
| 58 | 72.1 |
| 59 | 253.6 |
| 61 | 123.6 |
| 62 | 249.4 |
