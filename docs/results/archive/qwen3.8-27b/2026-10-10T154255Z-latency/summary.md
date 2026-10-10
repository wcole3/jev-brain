# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T154255Z
- repo commit: 9409223
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.4961189013294809, 'score': 1.6648399367497366, 'noul': 0.972520554755731}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.535520473719803, 'score': 1.774876073414086, 'noul': 0.9625437832558383}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3508723711404127, 'score': 6.269890636485391, 'noul': 0.8313413948726119}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 128.9 | 763.9 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 378.6 |
| 4 | 290.7 |
| 5 | 523.3 |
| 6 | 686.3 |
| 10 | 427.1 |
| 12 | 101.1 |
| 20 | 102.1 |
| 21 | 104.5 |
| 22 | 1590.5 |
| 23 | 139.3 |
| 24 | 106.4 |
| 26 | 96.7 |
| 27 | 99.6 |
| 28 | 100.0 |
| 29 | 106.8 |
| 30 | 119.2 |
| 31 | 283.5 |
| 33 | 591.3 |
| 37 | 128.4 |
| 38 | 2441.5 |
| 39 | 241.7 |
| 40 | 113.4 |
| 41 | 122.1 |
| 42 | 271.5 |
| 44 | 120.9 |
| 50 | 296.7 |
| 56 | 495.7 |
| 57 | 118.2 |
| 58 | 111.4 |
| 59 | 281.9 |
| 61 | 133.0 |
| 62 | 268.1 |
