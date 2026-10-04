# qwen3.6-27b long-context chat

## Provenance

- timestamp: 2026-10-04T162053Z
- repo commit: fd72395
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 77 | 66.8 | 20.2 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 105 / 108 / 4 | 6235 / 6235 / 1 |
| Decision ms (median / p95 / n) | 89 / 103 / 4 | 5132 / 9005 / 13 |
