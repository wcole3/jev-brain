# qwen3.6-27b long-context chat

## Provenance

- timestamp: 2026-10-05T040408Z
- repo commit: ee88d8f
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 81 | 77.2 | 15.5 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 140 / 168 / 4 | 1282 / 1282 / 1 |
| Decision ms (median / p95 / n) | 93 / 814 / 4 | 1345 / 2149 / 34 |
| Fresh decision ms (median / p95 / n) | 323 / 361 / 4 | 2016 / 2842 / 27 |
