# ds005-gemma-kvfp8 benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-08T21:19:47.625871+00:00
- repo commit: 98ba1fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: ds005-gemma-kvfp8
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
- systemone_priority: 0
- governor_duty: 0.5
- governor_wave: 8
- KV cache: 19911 blocks × 16 tokens
- cache_dtype: fp8
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 89 | 89 |
| cold | 256 | 1 | 26 | 166 | 167 |
| cold | 256 | 1 | 255 | 1238 | 1242 |
| cold | 256 | 4 | 2 | 156 | 161 |
| cold | 256 | 4 | 26 | 327 | 328 |
| cold | 256 | 4 | 255 | 2324 | 2337 |
| cold | 256 | 16 | 2 | 267 | 270 |
| cold | 256 | 16 | 26 | 761 | 776 |
| cold | 256 | 16 | 255 | 6814 | 6899 |
| cold | 256 | 64 | 2 | 752 | 778 |
| cold | 256 | 64 | 26 | 2696 | 2720 |
| cold | 256 | 64 | 255 | 49958 | 50117 |
| cold | 2048 | 1 | 2 | 524 | 524 |
| cold | 2048 | 1 | 26 | 603 | 604 |
| cold | 2048 | 1 | 255 | 1766 | 1769 |
| cold | 2048 | 4 | 2 | 790 | 810 |
| cold | 2048 | 4 | 26 | 979 | 990 |
| cold | 2048 | 4 | 255 | 2969 | 3204 |
| cold | 2048 | 16 | 2 | 935 | 950 |
| cold | 2048 | 16 | 26 | 1455 | 1495 |
| cold | 2048 | 16 | 255 | 7731 | 8011 |
| cold | 2048 | 64 | 2 | 1418 | 1638 |
| cold | 2048 | 64 | 26 | 3523 | 3810 |
| cold | 2048 | 64 | 255 | 53538 | 53907 |
| cold | 8192 | 1 | 2 | 2047 | 2050 |
| cold | 8192 | 1 | 26 | 2149 | 2151 |
| cold | 8192 | 1 | 255 | 3446 | 3452 |
| cold | 8192 | 4 | 2 | 5693 | 6186 |
| cold | 8192 | 4 | 26 | 5895 | 6546 |
| cold | 8192 | 4 | 255 | 6163 | 6429 |
| cold | 8192 | 16 | 2 | 7485 | 8403 |
| cold | 8192 | 16 | 26 | 8571 | 10471 |
| cold | 8192 | 16 | 255 | 15408 | 15565 |
| cold | 8192 | 64 | 2 | 8661 | 8905 |
| cold | 8192 | 64 | 26 | 10584 | 11068 |
| cold | 8192 | 64 | 255 | 74005 | 74088 |
| warm | 2048 | 16 | 26 | 244 | 253 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.7 |
| 16 | 0.7 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 88.0 | 91.3 | 91.8 | 0.932 | 0.227 | 66 | 308 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.115 | 0.231 | 49.3 | 42.7 | 5 | 46 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 212 | 23.0 |
| long | none | 224 | 22.7 |
| short | 4 systemone | 9151 | 6.7 |
| long | 4 systemone | 1227 | 13.9 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 4001955 | 26954436 | 7110212 | 73.6 | 5148 | 48.4 | 28.6 | 55 | 0 |
| warm | 33678 | 235008 | 7232 | 96.9 | 96 | 8.8 | 2.8 | 0 | 0 |
| throughput x1 | 123744 | 865824 | 133760 | 84.6 | 352 | 10.6 | 6.4 | 0 | 0 |
| throughput x4 | 134997 | 944592 | 152560 | 83.8 | 384 | 21.9 | 16.8 | 32 | 0 |
| throughput x16 | 196847 | 1377152 | 219392 | 84.1 | 560 | 26.1 | 22.9 | 206 | 0 |
| jevbench | 606246 | 606246 | 545478 | 10.0 | 1682 | 2.1 | 0.1 | 0 | 0 |
| chat | 106869 | 747848 | 122856 | 83.6 | 1578 | 25.1 | 3.4 | 40 | 0 |
