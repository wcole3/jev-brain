# qwen3.6-27b long-context chat

## Provenance

- timestamp: 2026-10-25T172350Z
- repo commit: 6809b05-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 87 | 85.1 | 14.8 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 159 / 172 / 4 | 1058 / 1527 / 4 |
| Decision ms (median / p95 / n) | 127 / 168 / 4 | 2808 / 4917 / 24 |
| Fresh decision ms (median / p95 / n) | 661 / 701 / 4 | 3047 / 4850 / 22 |
