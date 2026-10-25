# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T180258Z
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
- vllm_version: 0.30.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 282.1 | 511.0 | 823.6 | 1217.7 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 290.5 |
| 4 | 516.4 |
| 5 | 1020.5 |
| 6 | 825.6 |
| 10 | 621.1 |
| 12 | 139.7 |
| 20 | 114.6 |
| 21 | 69.7 |
| 22 | 4569.9 |
| 23 | 283.2 |
| 24 | 184.5 |
| 26 | 137.4 |
| 27 | 183.7 |
| 28 | 89.5 |
| 29 | 322.9 |
| 30 | 274.3 |
| 31 | 941.7 |
| 33 | 483.8 |
| 37 | 323.1 |
| 38 | 2572.1 |
| 39 | 180.7 |
| 40 | 68.8 |
| 41 | 164.6 |
| 42 | 323.8 |
| 44 | 139.4 |
| 50 | 940.1 |
| 56 | 390.3 |
| 57 | 229.0 |
| 58 | 181.1 |
| 59 | 446.0 |
| 61 | 242.1 |
| 62 | 567.3 |
