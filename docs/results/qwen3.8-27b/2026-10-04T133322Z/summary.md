# qwen3.8-27b benchmark (full, systemone only)

## Provenance

- timestamp: 2026-10-04T13:33:22.513705+00:00
- repo commit: 19aaa7b
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: qwen3.8-27b
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: header
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: front
- prefix_block: 784
- prefix_pad_always: False
- warm_min_prefix_tokens: 784
- warm_up: row
- KV cache: 665 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 141 | 158 |
| cold | 256 | 1 | 26 | 189 | 264 |
| cold | 256 | 1 | 255 | 1090 | 1116 |
| cold | 256 | 4 | 2 | 472 | 501 |
| cold | 256 | 4 | 26 | 494 | 554 |
| cold | 256 | 4 | 255 | 2585 | 2659 |
| cold | 256 | 16 | 2 | 517 | 543 |
| cold | 256 | 16 | 26 | 839 | 888 |
| cold | 256 | 16 | 255 | 6386 | 6576 |
| cold | 256 | 64 | 2 | 1270 | 1317 |
| cold | 256 | 64 | 26 | 2761 | 2913 |
| cold | 256 | 64 | 255 | 22564 | 22874 |
| cold | 2048 | 1 | 2 | 454 | 491 |
| cold | 2048 | 1 | 26 | 550 | 571 |
| cold | 2048 | 1 | 255 | 1541 | 1636 |
| cold | 2048 | 4 | 2 | 742 | 920 |
| cold | 2048 | 4 | 26 | 794 | 869 |
| cold | 2048 | 4 | 255 | 3276 | 3326 |
| cold | 2048 | 16 | 2 | 980 | 1043 |
| cold | 2048 | 16 | 26 | 1354 | 1414 |
| cold | 2048 | 16 | 255 | 7246 | 7336 |
| cold | 2048 | 64 | 2 | 1740 | 1848 |
| cold | 2048 | 64 | 26 | 3361 | 3549 |
| cold | 2048 | 64 | 255 | 22905 | 23378 |
| cold | 8192 | 1 | 2 | 1566 | 1570 |
| cold | 8192 | 1 | 26 | 1713 | 1722 |
| cold | 8192 | 1 | 255 | 2661 | 2679 |
| cold | 8192 | 4 | 2 | 1916 | 1917 |
| cold | 8192 | 4 | 26 | 1965 | 1975 |
| cold | 8192 | 4 | 255 | 5497 | 5540 |
| cold | 8192 | 16 | 2 | 2105 | 2124 |
| cold | 8192 | 16 | 26 | 2524 | 2544 |
| cold | 8192 | 16 | 255 | 9653 | 9671 |
| cold | 8192 | 64 | 2 | 3297 | 3328 |
| cold | 8192 | 64 | 26 | 4691 | 4859 |
| cold | 8192 | 64 | 255 | 26619 | 26734 |
| warm | 2048 | 16 | 26 | 756 | 771 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.7 | 93.1 | 90.2 | 0.920 | 0.140 | 97 | 262 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.053 | 0.154 | 35.2 | 42.7 | 54 | 7 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990382 | 29091154 | 4370850 | 85.0 | 5148 | 41.0 | 6.5 | 62 | 0 |
| warm | 33462 | 245838 | 22398 | 90.9 | 96 | 9.3 | 4.1 | 0 | 0 |
| throughput x1 | 145294 | 1065298 | 148018 | 86.1 | 416 | 9.3 | 2.3 | 0 | 0 |
| throughput x4 | 178815 | 1311136 | 182176 | 86.1 | 512 | 29.2 | 8.7 | 1 | 0 |
| throughput x16 | 223543 | 1638920 | 227720 | 86.1 | 640 | 29.2 | 17.4 | 80 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 1.2 | 0.0 | 0 | 0 |
