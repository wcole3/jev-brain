# qwen3.6-27b long-context chat

## Provenance

- timestamp: 2026-10-05T042450Z
- repo commit: ee88d8f
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 98 | 78.7 | 15.0 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 135 / 247 / 4 | 1112 / 1112 / 1 |
| Decision ms (median / p95 / n) | 98 / 823 / 4 | 326 / 69762 / 8 |
| Fresh decision ms (median / p95 / n) | 319 / 321 / 4 | 587 / 77320 / 6 |
