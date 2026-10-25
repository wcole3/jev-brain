# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T125945Z
- repo commit: 41acb16-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- layout: blurb_header_reread_noq
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: blurb_header_reread
- option_orders: min_n:4+reversed
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6408456729456102, 'score': 1.0, 'noul': 1.2122315701176378}, 'b': 0.0, 'source': 'qwen3.8-27b/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'blurb_header_reread': {'T': {'choice': 1.7391732643996622, 'score': 1.0, 'noul': 1.3956044971608574}, 'b': 0.0, 'source': 'qwen3.8-27b/blurb_header_reread/calibration.json', 'orders': 'min_n:4+reversed'}, 'blurb_header_reread_noq': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'decider_chat': {'T': {'choice': 1.4961189013294809, 'score': 1.6648399367497366, 'noul': 0.972520554755731}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.535520473719803, 'score': 1.774876073414086, 'noul': 0.9625437832558383}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3508723711404127, 'score': 6.269890636485391, 'noul': 0.8313413948726119}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 271.2 | 591.1 | 834.7 | 1443.0 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 433.7 |
| 4 | 432.5 |
| 5 | 912.4 |
| 6 | 901.7 |
| 10 | 578.5 |
| 12 | 125.5 |
| 20 | 129.1 |
| 21 | 120.9 |
| 22 | 4087.3 |
| 23 | 285.4 |
| 24 | 172.2 |
| 26 | 235.6 |
| 27 | 116.7 |
| 28 | 150.1 |
| 29 | 205.1 |
| 30 | 183.2 |
| 31 | 906.2 |
| 33 | 1129.7 |
| 37 | 432.9 |
| 38 | 7815.9 |
| 39 | 185.1 |
| 40 | 169.5 |
| 41 | 154.2 |
| 42 | 282.9 |
| 44 | 140.1 |
| 50 | 568.5 |
| 56 | 1443.0 |
| 57 | 215.1 |
| 58 | 154.2 |
| 59 | 448.0 |
| 61 | 232.7 |
| 62 | 482.3 |
