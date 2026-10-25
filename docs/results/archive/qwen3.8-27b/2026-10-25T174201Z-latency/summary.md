# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T174201Z
- repo commit: 6809b05
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 595.84, PCIe 4x16, AMD Ryzen Threadripper 3960X 24-Core Processor (48 thr), 189 GB
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
| **ours** | 282.3 | 546.8 | 846.3 | 1269.9 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 287.7 |
| 4 | 511.0 |
| 5 | 1018.3 |
| 6 | 846.8 |
| 10 | 620.9 |
| 12 | 139.9 |
| 20 | 114.8 |
| 21 | 70.3 |
| 22 | 4564.1 |
| 23 | 282.7 |
| 24 | 185.6 |
| 26 | 137.4 |
| 27 | 183.9 |
| 28 | 89.4 |
| 29 | 323.6 |
| 30 | 275.2 |
| 31 | 941.7 |
| 33 | 592.8 |
| 37 | 323.5 |
| 38 | 4446.9 |
| 39 | 181.6 |
| 40 | 68.3 |
| 41 | 164.5 |
| 42 | 322.9 |
| 44 | 139.3 |
| 50 | 942.8 |
| 56 | 626.1 |
| 57 | 228.6 |
| 58 | 181.1 |
| 59 | 446.1 |
| 61 | 241.5 |
| 62 | 567.2 |
