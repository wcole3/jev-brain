# qwen3.8-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T124823Z
- repo commit: 41acb16-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
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
| **ours** | 287.9 | 622.0 | 822.3 | 1272.3 |
| simple-jev · Qwen3.8-27B (board, its own sample) | 373.0 | n/a | n/a | n/a |
| reflex Qwen3.8-27B-FP8 (wide choice) (board, its own sample) | 108.3 | n/a | n/a | n/a |
| Jevfire Qwen3.8-27B (board, its own sample) | 89.6 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 421.3 |
| 4 | 437.1 |
| 5 | 871.5 |
| 6 | 990.9 |
| 10 | 580.8 |
| 12 | 174.5 |
| 20 | 126.8 |
| 21 | 148.5 |
| 22 | 4046.9 |
| 23 | 263.7 |
| 24 | 197.5 |
| 26 | 154.8 |
| 27 | 231.9 |
| 28 | 132.4 |
| 29 | 271.0 |
| 30 | 244.8 |
| 31 | 845.7 |
| 33 | 1121.2 |
| 37 | 398.2 |
| 38 | 7904.0 |
| 39 | 192.5 |
| 40 | 124.5 |
| 41 | 164.1 |
| 42 | 291.4 |
| 44 | 175.8 |
| 50 | 928.2 |
| 56 | 1159.4 |
| 57 | 233.2 |
| 58 | 169.4 |
| 59 | 454.3 |
| 61 | 280.7 |
| 62 | 581.5 |
