# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-16T004644Z
- repo commit: d674515
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.99.02, PCIe 5x16, AMD Ryzen 9 9950X3D2 16-Core Processor (32 thr), 123 GB, vast 56172713
- design: latency-v1, our rows
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.4961189013294809, 'score': 1.6648399367497366, 'noul': 0.972520554755731}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.535520473719803, 'score': 1.774876073414086, 'noul': 0.9625437832558383}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3508723711404127, 'score': 6.269890636485391, 'noul': 0.8313413948726119}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 84.1 | 718.2 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 258.9 |
| 4 | 244.8 |
| 5 | 454.9 |
| 6 | 634.4 |
| 10 | 384.0 |
| 12 | 80.2 |
| 20 | 61.2 |
| 21 | 51.2 |
| 22 | 1590.3 |
| 23 | 124.2 |
| 24 | 59.7 |
| 26 | 50.3 |
| 27 | 58.8 |
| 28 | 52.2 |
| 29 | 82.5 |
| 30 | 79.5 |
| 31 | 247.7 |
| 33 | 407.7 |
| 37 | 99.2 |
| 38 | 2205.1 |
| 39 | 115.8 |
| 40 | 49.9 |
| 41 | 82.5 |
| 42 | 211.1 |
| 44 | 80.2 |
| 50 | 216.9 |
| 56 | 349.0 |
| 57 | 62.2 |
| 58 | 61.8 |
| 59 | 217.2 |
| 61 | 100.1 |
| 62 | 229.3 |
