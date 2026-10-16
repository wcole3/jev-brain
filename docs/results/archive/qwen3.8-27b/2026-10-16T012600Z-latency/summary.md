# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-16T012600Z
- repo commit: f200e45
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
| **ours** | 84.7 | 717.6 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 260.1 |
| 4 | 245.0 |
| 5 | 455.6 |
| 6 | 634.8 |
| 10 | 383.4 |
| 12 | 80.3 |
| 20 | 61.3 |
| 21 | 51.4 |
| 22 | 1586.5 |
| 23 | 124.3 |
| 24 | 58.8 |
| 26 | 51.3 |
| 27 | 59.1 |
| 28 | 52.6 |
| 29 | 83.1 |
| 30 | 79.7 |
| 31 | 248.0 |
| 33 | 407.4 |
| 37 | 99.4 |
| 38 | 2198.0 |
| 39 | 116.1 |
| 40 | 50.3 |
| 41 | 82.7 |
| 42 | 210.9 |
| 44 | 80.6 |
| 50 | 216.8 |
| 56 | 349.4 |
| 57 | 63.0 |
| 58 | 61.4 |
| 59 | 216.2 |
| 61 | 100.2 |
| 62 | 229.4 |
