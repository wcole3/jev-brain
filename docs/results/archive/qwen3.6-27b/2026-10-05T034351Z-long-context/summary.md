# qwen3.6-27b long-context chat

## Provenance

- timestamp: 2026-10-05T034351Z
- repo commit: ee88d8f
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 62 | 87.4 | 15.3 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 113 / 221 / 4 | 3727 / 7231 / 2 |
| Decision ms (median / p95 / n) | 90 / 888 / 4 | 818 / 1216 / 47 |
| Fresh decision ms (median / p95 / n) | 325 / 335 / 4 | 1245 / 1635 / 39 |
