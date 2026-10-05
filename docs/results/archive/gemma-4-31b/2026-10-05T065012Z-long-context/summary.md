# gemma-4-31b long-context chat

## Provenance

- timestamp: 2026-10-05T065012Z
- repo commit: 66b8531
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- max_model_len: 65536
- systemone_max_len: 32768
- target tokens: 60000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 59757 | 83 | 36.2 | 17.3 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 87 / 1478 / 4 | 470 / 701 / 2 |
| Decision ms (median / p95 / n) | 60 / 1179 / 4 | 1198 / 6907 / 17 |
| Fresh decision ms (median / p95 / n) | 359 / 360 / 4 | 1864 / 7402 / 14 |
