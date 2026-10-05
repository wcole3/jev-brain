# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T005349Z
- repo commit: 94d3f9d
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- design: latency-v1, our rows
- profile: qwen3.6-27b
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- calibration: None
- vllm_version: 0.30.0

| entry | median ms | p95 ms |
|---|---|---|
| **ours** | 125.5 | 663.5 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 383.2 |
| 4 | 262.0 |
| 5 | 472.5 |
| 6 | 597.1 |
| 10 | 331.1 |
| 12 | 105.9 |
| 20 | 101.7 |
| 21 | 96.3 |
| 22 | 1306.3 |
| 23 | 137.0 |
| 24 | 105.7 |
| 26 | 132.9 |
| 27 | 113.2 |
| 28 | 99.5 |
| 29 | 118.1 |
| 30 | 108.8 |
| 31 | 279.6 |
| 33 | 531.1 |
| 37 | 107.8 |
| 38 | 1541.6 |
| 39 | 96.0 |
| 40 | 95.9 |
| 41 | 108.9 |
| 42 | 158.6 |
| 44 | 95.3 |
| 48 | 204.7 |
| 50 | 254.7 |
| 56 | 452.8 |
| 57 | 103.8 |
| 58 | 98.9 |
| 59 | 252.2 |
| 61 | 120.2 |
| 62 | 247.5 |
