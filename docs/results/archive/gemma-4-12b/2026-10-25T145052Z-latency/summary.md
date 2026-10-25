# gemma-4-12b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-25T145052Z
- repo commit: dba35fb-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: gemma-4-12b
- hf_revision: 707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7
- prompt_layout: blurb_header_reread
- option_orders: identity
- option_orders_images: 
- calibration: {'blurb_header': {'T': {'choice': 4.035253781242961, 'score': 4.035253781242961, 'noul': 4.035253781242961}, 'b': 0.0, 'source': 'gemma-4-12b/blurb_header/calibration.json', 'orders': 'identity'}, 'blurb_header_reread': {'T': {'choice': 4.018175387617537, 'score': 4.018175387617537, 'noul': 4.018175387617537}, 'b': 0.0, 'source': 'gemma-4-12b/blurb_header_reread/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'header': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'question_first': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}
- other_calibrations: {}
- vllm_version: 0.32.0

| entry | median ms | mean ms | p80 ms | p95 ms |
|---|---|---|---|---|
| **ours** | 85.9 | 165.9 | 206.0 | 397.1 |
| AJev lora7 (Gemma 4 12B) (board, its own sample) | 69.1 | n/a | n/a | n/a |
| decisio 0.4.0 (Gemma 4 12B) (board, its own sample) | 37.8 | n/a | n/a | n/a |
| Winnow-12B (board, its own sample) | 72.5 | n/a | n/a | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a | n/a | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 94.0 |
| 4 | 131.9 |
| 5 | 212.8 |
| 6 | 306.4 |
| 10 | 243.0 |
| 12 | 68.8 |
| 20 | 52.3 |
| 21 | 52.4 |
| 22 | 935.8 |
| 23 | 120.1 |
| 24 | 49.1 |
| 26 | 42.4 |
| 27 | 55.6 |
| 28 | 46.0 |
| 29 | 76.8 |
| 30 | 64.8 |
| 31 | 144.3 |
| 33 | 134.6 |
| 37 | 94.3 |
| 38 | 1333.4 |
| 39 | 63.5 |
| 40 | 47.1 |
| 41 | 86.8 |
| 42 | 131.0 |
| 44 | 74.9 |
| 50 | 178.9 |
| 56 | 128.0 |
| 57 | 63.6 |
| 58 | 54.3 |
| 59 | 155.2 |
| 61 | 94.5 |
| 62 | 161.1 |
