# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T165056Z
- repo commit: 326d316
- host: RTX PRO 6000 Blackwell Server Edition, 600/600 W, drv 580.173.02, PCIe 5x16, AMD Ryzen Threadripper PRO 9975WX 32-Cores (64 thr), 188 GB, vast 56912443
- design: latency-v1, our rows
- layout: header
- option_orders: min_n:4+reversed
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: blurb_header
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6408456729456102, 'score': 1.0, 'noul': 1.2122315701176378}, 'b': 0.0, 'source': 'qwen3.8-27b/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.4961189013294809, 'score': 1.6648399367497366, 'noul': 0.972520554755731}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.535520473719803, 'score': 1.774876073414086, 'noul': 0.9625437832558383}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3508723711404127, 'score': 6.269890636485391, 'noul': 0.8313413948726119}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 82.6 | 240.2 | 348.3 | 645.4 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 265.1 |
| 4 | 226.3 |
| 5 | 428.9 |
| 6 | 583.7 |
| 10 | 356.5 |
| 12 | 79.4 |
| 20 | 64.6 |
| 21 | 56.9 |
| 22 | 1429.1 |
| 23 | 114.6 |
| 24 | 64.3 |
| 26 | 68.3 |
| 27 | 67.9 |
| 28 | 58.0 |
| 29 | 81.1 |
| 30 | 78.2 |
| 31 | 231.0 |
| 33 | 391.5 |
| 37 | 91.7 |
| 38 | 2088.8 |
| 39 | 155.8 |
| 40 | 56.9 |
| 41 | 81.7 |
| 42 | 204.6 |
| 44 | 79.2 |
| 50 | 208.7 |
| 56 | 349.0 |
| 57 | 73.7 |
| 58 | 65.4 |
| 59 | 207.3 |
| 61 | 92.9 |
| 62 | 216.2 |
