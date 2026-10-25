# qwen3.8-27b long-context chat

## Provenance

- timestamp: 2026-10-25T173535Z
- repo commit: 6809b05-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- max_model_len: 262144
- systemone_max_len: 32768
- target tokens: 200000

## Long request

| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |
| --- | --- | --- | --- |
| 199756 | 116 | 84.3 | 14.6 |

## Other traffic meanwhile

| Measure | Idle | During long request |
| --- | --- | --- |
| Short chat TTFT ms (median / p95 / n) | 147 / 151 / 4 | 884 / 1840 / 19 |
| Decision ms (median / p95 / n) | 145 / 998 / 4 | 1114 / 3422 / 38 |
| Fresh decision ms (median / p95 / n) | 614 / 635 / 4 | 2422 / 3777 / 26 |
