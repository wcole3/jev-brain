# ds005-qwen38-bf16 benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-09T07:57:42.488314+00:00
- repo commit: 98ba1fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: ds005-qwen38-bf16
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
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
- KV cache: 571 blocks × 800 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 800
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 101 | 125 |
| cold | 256 | 1 | 26 | 180 | 181 |
| cold | 256 | 1 | 255 | 1311 | 1355 |
| cold | 256 | 4 | 2 | 435 | 486 |
| cold | 256 | 4 | 26 | 461 | 493 |
| cold | 256 | 4 | 255 | 2950 | 2962 |
| cold | 256 | 16 | 2 | 562 | 601 |
| cold | 256 | 16 | 26 | 940 | 969 |
| cold | 256 | 16 | 255 | 6861 | 6938 |
| cold | 256 | 64 | 2 | 1410 | 1457 |
| cold | 256 | 64 | 26 | 2948 | 3039 |
| cold | 256 | 64 | 255 | 23719 | 24371 |
| cold | 2048 | 1 | 2 | 534 | 538 |
| cold | 2048 | 1 | 26 | 681 | 695 |
| cold | 2048 | 1 | 255 | 1908 | 1938 |
| cold | 2048 | 4 | 2 | 891 | 909 |
| cold | 2048 | 4 | 26 | 939 | 952 |
| cold | 2048 | 4 | 255 | 4830 | 4845 |
| cold | 2048 | 16 | 2 | 960 | 994 |
| cold | 2048 | 16 | 26 | 1400 | 1413 |
| cold | 2048 | 16 | 255 | 8902 | 8959 |
| cold | 2048 | 64 | 2 | 1908 | 1983 |
| cold | 2048 | 64 | 26 | 3610 | 3630 |
| cold | 2048 | 64 | 255 | 26551 | 26639 |
| cold | 8192 | 1 | 2 | 2080 | 2085 |
| cold | 8192 | 1 | 26 | 2158 | 2228 |
| cold | 8192 | 1 | 255 | 3457 | 3465 |
| cold | 8192 | 4 | 2 | 2467 | 2482 |
| cold | 8192 | 4 | 26 | 2535 | 2546 |
| cold | 8192 | 4 | 255 | 10346 | 10354 |
| cold | 8192 | 16 | 2 | 2674 | 2682 |
| cold | 8192 | 16 | 26 | 3122 | 3136 |
| cold | 8192 | 16 | 255 | 14735 | 14844 |
| cold | 8192 | 64 | 2 | 3906 | 3974 |
| cold | 8192 | 64 | 26 | 5569 | 5578 |
| cold | 8192 | 64 | 255 | 33018 | 33580 |
| warm | 2048 | 16 | 26 | 831 | 849 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.9 |
| 16 | 0.9 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.7 | 93.1 | 90.4 | 0.918 | 0.145 | 99 | 279 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.033 | 0.154 | 35.0 | 42.7 | 54 | 6 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 107 | 61.9 |
| long | none | 127 | 46.7 |
| short | 4 systemone | 2611 | 15.1 |
| long | 4 systemone | 577 | 27.6 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990396 | 29558864 | 4753264 | 83.9 | 5148 | 97.0 | 11.1 | 61 | 0 |
| warm | 33462 | 250446 | 22446 | 91.0 | 96 | 28.4 | 11.0 | 2 | 0 |
| throughput x1 | 122948 | 918302 | 126302 | 86.2 | 352 | 28.4 | 9.1 | 2 | 0 |
| throughput x4 | 156465 | 1168748 | 160748 | 86.2 | 448 | 31.1 | 17.9 | 27 | 0 |
| throughput x16 | 195601 | 1460935 | 200935 | 86.2 | 560 | 34.0 | 19.0 | 200 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 3.0 | 0.0 | 0 | 0 |
| chat | 67063 | 501142 | 69142 | 86.2 | 1291 | 30.7 | 5.3 | 20 | 0 |
