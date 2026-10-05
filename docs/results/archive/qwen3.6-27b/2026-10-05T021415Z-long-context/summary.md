# qwen3.6-27b long-context chat

## Provenance

- timestamp: 2026-10-05T021415Z
- repo commit: c37c95a
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 93 | 70.2 | 13.6 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 161 / 667 / 4 | 1679 / 1679 / 1 |
| Decision ms (median / p95 / n) | 109 / 1006 / 4 | 1776 / 3188 / 27 |
| Fresh decision ms (median / p95 / n) | 342 / 356 / 4 | 2315 / 4198 / 22 |
