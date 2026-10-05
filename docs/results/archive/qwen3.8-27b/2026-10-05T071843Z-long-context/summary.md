# qwen3.8-27b long-context chat

## Provenance

- timestamp: 2026-10-05T071843Z
- repo commit: 66b8531
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 121 | 84.5 | 14.8 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 105 / 266 / 4 | 800 / 6545 / 9 |
| Decision ms (median / p95 / n) | 94 / 794 / 4 | 774 / 1160 / 50 |
| Fresh decision ms (median / p95 / n) | 309 / 311 / 4 | 1214 / 1561 / 41 |
