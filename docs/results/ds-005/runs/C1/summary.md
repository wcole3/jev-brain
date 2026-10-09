# ds005-qwen36-fp8 benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-09T11:05:08.531730+00:00
- repo commit: 98ba1fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: ds005-qwen36-fp8
- hf_model: Qwen/Qwen3.6-27B-FP8
- hf_revision: e89b16ebf1988b3d6befa7de50abc2d76f26eb09
- prompt_layout: header
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: front
- prefix_block: 800
- prefix_pad_always: False
- warm_min_prefix_tokens: 800
- warm_up: row
- systemone_priority: 1
- governor_duty: 0.6
- governor_wave: 8
- KV cache: 1014 blocks × 800 tokens
- cache_dtype: bfloat16
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 800
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 108 | 113 |
| cold | 256 | 1 | 26 | 143 | 173 |
| cold | 256 | 1 | 255 | 991 | 1122 |
| cold | 256 | 4 | 2 | 409 | 430 |
| cold | 256 | 4 | 26 | 410 | 440 |
| cold | 256 | 4 | 255 | 2334 | 2365 |
| cold | 256 | 16 | 2 | 496 | 526 |
| cold | 256 | 16 | 26 | 746 | 795 |
| cold | 256 | 16 | 255 | 4796 | 4866 |
| cold | 256 | 64 | 2 | 1056 | 1073 |
| cold | 256 | 64 | 26 | 2130 | 2206 |
| cold | 256 | 64 | 255 | 16062 | 16624 |
| cold | 2048 | 1 | 2 | 409 | 435 |
| cold | 2048 | 1 | 26 | 519 | 556 |
| cold | 2048 | 1 | 255 | 1387 | 1439 |
| cold | 2048 | 4 | 2 | 725 | 760 |
| cold | 2048 | 4 | 26 | 754 | 761 |
| cold | 2048 | 4 | 255 | 3419 | 3447 |
| cold | 2048 | 16 | 2 | 800 | 812 |
| cold | 2048 | 16 | 26 | 1090 | 1147 |
| cold | 2048 | 16 | 255 | 6166 | 6234 |
| cold | 2048 | 64 | 2 | 1433 | 1442 |
| cold | 2048 | 64 | 26 | 2535 | 2676 |
| cold | 2048 | 64 | 255 | 17940 | 18245 |
| cold | 8192 | 1 | 2 | 1484 | 1565 |
| cold | 8192 | 1 | 26 | 1530 | 1565 |
| cold | 8192 | 1 | 255 | 2445 | 2491 |
| cold | 8192 | 4 | 2 | 1888 | 1905 |
| cold | 8192 | 4 | 26 | 1845 | 1859 |
| cold | 8192 | 4 | 255 | 7250 | 7336 |
| cold | 8192 | 16 | 2 | 2049 | 2086 |
| cold | 8192 | 16 | 26 | 2346 | 2387 |
| cold | 8192 | 16 | 255 | 10241 | 10388 |
| cold | 8192 | 64 | 2 | 3072 | 3151 |
| cold | 8192 | 64 | 26 | 4042 | 4152 |
| cold | 8192 | 64 | 255 | 23670 | 23762 |
| warm | 2048 | 16 | 26 | 695 | 714 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 1.3 |
| 16 | 1.3 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.2 | 93.2 | 90.6 | 0.878 | 0.275 | 104 | 250 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.041 | 0.166 | 35.8 | 42.7 | 51 | 8 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 118 | 105.3 |
| long | none | 119 | 88.0 |
| short | 4 systemone | 2799 | 41.0 |
| long | 4 systemone | 313 | 49.4 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990358 | 29558854 | 4738854 | 84.0 | 5148 | 60.5 | 6.1 | 61 | 0 |
| warm | 33462 | 250446 | 22446 | 91.0 | 96 | 16.0 | 6.6 | 2 | 0 |
| throughput x1 | 156474 | 1168748 | 160748 | 86.2 | 448 | 16.0 | 4.4 | 2 | 0 |
| throughput x4 | 229115 | 1711381 | 235381 | 86.2 | 656 | 17.5 | 9.8 | 27 | 0 |
| throughput x16 | 268239 | 2003568 | 275568 | 86.2 | 768 | 19.2 | 10.9 | 200 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 1.7 | 0.0 | 0 | 0 |
| chat | 67062 | 500974 | 68974 | 86.2 | 1842 | 16.6 | 2.6 | 32 | 0 |
