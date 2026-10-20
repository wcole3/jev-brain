# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-20T165511Z
- repo commit: 326d316
- host: RTX PRO 6000 Blackwell Server Edition, 600/600 W, drv 580.173.02, PCIe 5x16, AMD Ryzen Threadripper PRO 9975WX 32-Cores (64 thr), 188 GB, vast 56912443
- design: latency-v1, our rows
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: blurb_header
- option_orders: min_n:4+reversed
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6408456729456102, 'score': 1.0, 'noul': 1.2122315701176378}, 'b': 0.0, 'source': 'qwen3.8-27b/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.4961189013294809, 'score': 1.6648399367497366, 'noul': 0.972520554755731}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.535520473719803, 'score': 1.774876073414086, 'noul': 0.9625437832558383}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3508723711404127, 'score': 6.269890636485391, 'noul': 0.8313413948726119}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 155.8 | 328.6 | 410.9 | 814.9 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 262.4 |
| 4 | 409.7 |
| 5 | 769.6 |
| 6 | 681.2 |
| 10 | 358.7 |
| 12 | 79.6 |
| 20 | 64.9 |
| 21 | 58.0 |
| 22 | 2867.0 |
| 23 | 114.6 |
| 24 | 127.6 |
| 26 | 115.6 |
| 27 | 127.3 |
| 28 | 68.4 |
| 29 | 160.7 |
| 30 | 129.8 |
| 31 | 410.9 |
| 33 | 409.0 |
| 37 | 181.7 |
| 38 | 2085.0 |
| 39 | 157.1 |
| 40 | 57.8 |
| 41 | 81.8 |
| 42 | 210.2 |
| 44 | 79.9 |
| 50 | 356.3 |
| 56 | 349.1 |
| 57 | 130.9 |
| 58 | 125.8 |
| 59 | 208.3 |
| 61 | 95.1 |
| 62 | 284.8 |
