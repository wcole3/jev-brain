# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-26T041951Z
- repo commit: e8b57ea-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.8-27b
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: blurb_header_reread
- option_orders: min_n:4+reversed
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 1.6408456729456102, 'score': 1.0, 'noul': 1.2122315701176378}, 'b': 0.0, 'source': 'qwen3.8-27b/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'blurb_header_reread': {'T': {'choice': 1.6694253320949457, 'score': 1.0, 'noul': 1.3442156081674206}, 'b': 0.0, 'source': 'qwen3.8-27b/blurb_header_reread/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.4961189013294809, 'score': 1.6648399367497366, 'noul': 0.972520554755731}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.535520473719803, 'score': 1.774876073414086, 'noul': 0.9625437832558383}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3508723711404127, 'score': 6.269890636485391, 'noul': 0.8313413948726119}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 213.1 | 498.8 | 718.6 | 997.8 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 332.4 |
| 4 | 392.7 |
| 5 | 849.1 |
| 6 | 910.4 |
| 10 | 519.6 |
| 12 | 96.5 |
| 20 | 88.2 |
| 21 | 89.5 |
| 22 | 3662.8 |
| 23 | 213.9 |
| 24 | 160.5 |
| 26 | 181.2 |
| 27 | 261.9 |
| 28 | 113.6 |
| 29 | 199.5 |
| 30 | 184.6 |
| 31 | 717.5 |
| 33 | 718.6 |
| 37 | 302.9 |
| 38 | 6339.8 |
| 39 | 163.5 |
| 40 | 106.2 |
| 41 | 117.8 |
| 42 | 244.7 |
| 44 | 98.8 |
| 50 | 384.8 |
| 56 | 947.9 |
| 57 | 168.4 |
| 58 | 135.7 |
| 59 | 359.2 |
| 61 | 199.7 |
| 62 | 547.7 |
