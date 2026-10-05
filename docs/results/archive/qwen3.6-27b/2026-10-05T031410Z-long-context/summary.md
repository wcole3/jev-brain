# qwen3.6-27b long-context chat

## Provenance

- timestamp: 2026-10-05T031410Z
- repo commit: c2e5f51
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 95 | 79.7 | 14.8 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 117 / 229 / 4 | 1397 / 1397 / 1 |
| Decision ms (median / p95 / n) | 104 / 831 / 4 | 1357 / 2344 / 35 |
| Fresh decision ms (median / p95 / n) | 339 / 353 / 4 | 2036 / 3115 / 28 |
