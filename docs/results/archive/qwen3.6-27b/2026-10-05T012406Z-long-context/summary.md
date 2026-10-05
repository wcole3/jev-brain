# qwen3.6-27b long-context chat

## Provenance

- timestamp: 2026-10-05T012406Z
- repo commit: c37c95a
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 82 | 64.7 | 15.4 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 145 / 349 / 4 | 11888 / 11888 / 1 |
| Decision ms (median / p95 / n) | 117 / 1120 / 4 | 288 / 50828 / 7 |
| Fresh decision ms (median / p95 / n) | 356 / 400 / 4 | 604 / 63258 / 5 |
