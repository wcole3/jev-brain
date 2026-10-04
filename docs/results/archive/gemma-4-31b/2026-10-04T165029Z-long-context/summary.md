# gemma-4-31b long-context chat

## Provenance

- timestamp: 2026-10-04T165029Z
- repo commit: fd72395
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- max_model_len: 131072
- systemone_max_len: 32768
- target tokens: 120000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 119757 | 77 | 86.4 | 19.0 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 91 / 95 / 4 | 86352 / 86352 / 1 |
| Decision ms (median / p95 / n) | 63 / 95 / 4 | 209 / 85277 / 5 |
