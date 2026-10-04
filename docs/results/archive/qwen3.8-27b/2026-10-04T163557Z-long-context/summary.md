# qwen3.8-27b long-context chat

## Provenance

- timestamp: 2026-10-04T163557Z
- repo commit: fd72395
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 95 | 66.3 | 19.4 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 106 / 113 / 4 | 216 / 225 / 3 |
| Decision ms (median / p95 / n) | 81 / 109 / 4 | 5011 / 8942 / 14 |
