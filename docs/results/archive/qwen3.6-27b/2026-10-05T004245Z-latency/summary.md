# qwen3.6-27b latency (latency-v1 design)

## Provenance

- timestamp: 2026-10-05T004245Z
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
| **ours** | 137.9 | 624.4 |
| Decider chat · Qwen3.6-27B (board, its own sample) | 83.6 | n/a |
| Jev (hosted API, latency over HTTPS) (board, its own sample) | 524.1 | n/a |

Answered 750 of 750 timed rows.

| catalog | median ms |
|---|---|
| 1 | 511.3 |
| 4 | 257.0 |
| 5 | 464.2 |
| 6 | 584.4 |
| 10 | 306.1 |
| 12 | 108.1 |
| 20 | 100.5 |
| 21 | 94.1 |
| 22 | 1289.3 |
| 23 | 154.4 |
| 24 | 102.7 |
| 26 | 94.2 |
| 27 | 95.7 |
| 28 | 100.5 |
| 29 | 100.9 |
| 30 | 98.9 |
| 31 | 252.2 |
| 33 | 495.0 |
| 37 | 127.7 |
| 38 | 1503.4 |
| 39 | 142.8 |
| 40 | 113.5 |
| 41 | 97.4 |
| 42 | 145.6 |
| 44 | 88.9 |
| 48 | 242.8 |
| 50 | 266.0 |
| 56 | 520.2 |
| 57 | 135.5 |
| 58 | 129.1 |
| 59 | 379.7 |
| 61 | 154.3 |
| 62 | 254.3 |
