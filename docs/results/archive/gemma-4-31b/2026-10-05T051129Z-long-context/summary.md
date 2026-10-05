# gemma-4-31b long-context chat

## Provenance

- timestamp: 2026-10-05T051129Z
- repo commit: d102ce2
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- max_model_len: 65536
- systemone_max_len: 32768
- target tokens: 60000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 59757 | 78 | 33.9 | 15.9 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 88 / 1466 / 4 | 1345 / 1345 / 1 |
| Decision ms (median / p95 / n) | 60 / 1178 / 4 | 1922 / 8752 / 10 |
| Fresh decision ms (median / p95 / n) | 347 / 348 / 4 | 3406 / 10138 / 9 |
