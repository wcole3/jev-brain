# qwen3.6-27b long-context chat

## Provenance

- timestamp: 2026-10-05T063258Z
- repo commit: 6de9f1d
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 86 | 86.1 | 15.6 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 116 / 323 / 4 | 763 / 1040 / 2 |
| Decision ms (median / p95 / n) | 92 / 750 / 4 | 788 / 1190 / 49 |
| Fresh decision ms (median / p95 / n) | 319 / 321 / 4 | 1217 / 1603 / 40 |
