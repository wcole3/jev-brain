# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T115108Z
- repo commit: 54afc85-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: blurb_header_reread
- option_orders: min_n:4+reversed
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6408456729456102, 'score': 1.0, 'noul': 1.2122315701176378}, 'b': 0.0, 'source': 'qwen3.8-27b/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'blurb_header_reread': {'T': {'choice': 1.7391732643996622, 'score': 1.0, 'noul': 1.3956044971608574}, 'b': 0.0, 'source': 'qwen3.8-27b/blurb_header_reread/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.4961189013294809, 'score': 1.6648399367497366, 'noul': 0.972520554755731}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.535520473719803, 'score': 1.774876073414086, 'noul': 0.9625437832558383}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3508723711404127, 'score': 6.269890636485391, 'noul': 0.8313413948726119}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 301.8 | 671.2 | 932.0 | 1433.5 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 338.3 |
| 4 | 486.0 |
| 5 | 1015.1 |
| 6 | 981.8 |
| 10 | 707.9 |
| 12 | 179.5 |
| 20 | 148.8 |
| 21 | 161.4 |
| 22 | 4875.5 |
| 23 | 286.0 |
| 24 | 222.4 |
| 26 | 126.7 |
| 27 | 266.4 |
| 28 | 149.2 |
| 29 | 297.7 |
| 30 | 245.9 |
| 31 | 1023.6 |
| 33 | 1154.6 |
| 37 | 499.5 |
| 38 | 8795.4 |
| 39 | 183.2 |
| 40 | 146.5 |
| 41 | 221.7 |
| 42 | 360.6 |
| 44 | 188.7 |
| 50 | 1008.5 |
| 56 | 1250.8 |
| 57 | 234.9 |
| 58 | 172.2 |
| 59 | 494.6 |
| 61 | 311.8 |
| 62 | 655.5 |
