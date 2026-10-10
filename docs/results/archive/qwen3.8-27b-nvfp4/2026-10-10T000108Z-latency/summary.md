# qwen3.8-27b-nvfp4 latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-10T000108Z
- repo commit: ee5e4be
- host: RTX PRO 6000 Blackwell, 575/600 W, drv 595.84, PCIe 4x16, AMD EPYC 7742 64-Core Processor (256 thr), 1008 GB, vast 55115710
- design: latency-v1, our rows
- profile: qwen3.8-27b-nvfp4
- hf_revision: 319f741cce68d7914884900c138a1fbb70a42f30
- prompt_layout: header
- option_orders: identity
- calibration: {'decider_chat': {'T': {'choice': 1.534912409014274, 'score': 1.6956928316925777, 'noul': 0.9175902098440983}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5971415409111187, 'score': 1.829572794304793, 'noul': 0.9633966437867898}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3876276536831984, 'score': 1.7744416557968425, 'noul': 0.9417765210190306}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 63.7 | 696.3 |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 290.5 |
| 4 | 229.1 |
| 5 | 457.0 |
| 6 | 619.7 |
| 10 | 392.4 |
| 12 | 64.3 |
| 20 | 63.9 |
| 21 | 63.2 |
| 22 | 1495.0 |
| 23 | 172.7 |
| 24 | 60.1 |
| 26 | 59.4 |
| 27 | 59.3 |
| 28 | 59.4 |
| 29 | 61.3 |
| 30 | 60.6 |
| 31 | 224.2 |
| 33 | 459.2 |
| 37 | 62.7 |
| 38 | 1849.6 |
| 39 | 113.7 |
| 40 | 60.0 |
| 41 | 62.1 |
| 42 | 223.0 |
| 44 | 61.2 |
| 50 | 225.5 |
| 56 | 353.4 |
| 57 | 61.2 |
| 58 | 60.9 |
| 59 | 225.6 |
| 61 | 62.9 |
| 62 | 225.5 |
