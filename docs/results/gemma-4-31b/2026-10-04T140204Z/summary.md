# gemma-4-31b benchmark (full, systemone only)

## Provenance

- timestamp: 2026-10-04T14:02:04.892400+00:00
- repo commit: 19aaa7b
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: off
- prefix_block: 0
- prefix_pad_always: False
- warm_min_prefix_tokens: 512
- warm_up: off
- KV cache: 9965 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 94 | 100 |
| cold | 256 | 1 | 26 | 175 | 178 |
| cold | 256 | 1 | 255 | 1308 | 1311 |
| cold | 256 | 4 | 2 | 168 | 168 |
| cold | 256 | 4 | 26 | 324 | 349 |
| cold | 256 | 4 | 255 | 2593 | 2596 |
| cold | 256 | 16 | 2 | 284 | 288 |
| cold | 256 | 16 | 26 | 828 | 840 |
| cold | 256 | 16 | 255 | 14761 | 14795 |
| cold | 256 | 64 | 2 | 818 | 886 |
| cold | 256 | 64 | 26 | 2960 | 2976 |
| cold | 256 | 64 | 255 | 55737 | 55881 |
| cold | 2048 | 1 | 2 | 516 | 542 |
| cold | 2048 | 1 | 26 | 607 | 615 |
| cold | 2048 | 1 | 255 | 1890 | 1897 |
| cold | 2048 | 4 | 2 | 590 | 607 |
| cold | 2048 | 4 | 26 | 809 | 812 |
| cold | 2048 | 4 | 255 | 3281 | 3285 |
| cold | 2048 | 16 | 2 | 789 | 796 |
| cold | 2048 | 16 | 26 | 1402 | 1426 |
| cold | 2048 | 16 | 255 | 16437 | 16456 |
| cold | 2048 | 64 | 2 | 1541 | 1583 |
| cold | 2048 | 64 | 26 | 3667 | 3723 |
| cold | 2048 | 64 | 255 | 60377 | 60501 |
| cold | 8192 | 1 | 2 | 2228 | 2229 |
| cold | 8192 | 1 | 26 | 2334 | 2337 |
| cold | 8192 | 1 | 255 | 3815 | 3818 |
| cold | 8192 | 4 | 2 | 2347 | 2352 |
| cold | 8192 | 4 | 26 | 2582 | 2587 |
| cold | 8192 | 4 | 255 | 5495 | 5498 |
| cold | 8192 | 16 | 2 | 2644 | 2648 |
| cold | 8192 | 16 | 26 | 3382 | 3388 |
| cold | 8192 | 16 | 255 | 21020 | 21061 |
| cold | 8192 | 64 | 2 | 3899 | 4214 |
| cold | 8192 | 64 | 26 | 6242 | 6274 |
| cold | 8192 | 64 | 255 | 74242 | 74326 |
| warm | 2048 | 16 | 26 | 264 | 277 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 88.2 | 91.9 | 91.7 | 0.934 | 0.222 | 65 | 283 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.043 | 0.170 | 49.4 | 42.7 | 5 | 47 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 4001929 | 26953687 | 6438519 | 76.1 | 5148 | 62.7 | 32.1 | 62 | 0 |
| warm | 33678 | 235008 | 7040 | 97.0 | 96 | 11.8 | 3.2 | 0 | 0 |
| throughput x1 | 123739 | 865744 | 117008 | 86.5 | 352 | 13.9 | 6.2 | 0 | 0 |
| throughput x4 | 146238 | 1023168 | 138208 | 86.5 | 416 | 33.8 | 26.1 | 31 | 0 |
| throughput x16 | 213740 | 1495520 | 202048 | 86.5 | 608 | 37.9 | 32.9 | 220 | 0 |
| jevbench | 606246 | 606246 | 545702 | 10.0 | 1682 | 0.0 | 0.0 | 0 | 0 |
