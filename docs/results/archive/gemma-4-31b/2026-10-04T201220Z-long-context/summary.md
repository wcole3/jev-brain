# gemma-4-31b long-context chat

## Provenance

- timestamp: 2026-10-04T201220Z
- repo commit: f0e5b9c
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- max_model_len: 65536
- systemone_max_len: 32768
- target tokens: 60000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 59757 | 75 | 32.2 | 18.3 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 107 / 112 / 4 | 32224 / 32224 / 1 |
| Decision ms (median / p95 / n) | 67 / 107 / 4 | 204 / 31149 / 5 |
