# ds005-gemma-bf16 benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-08T20:28:40.850120+00:00
- repo commit: 98ba1fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: ds005-gemma-bf16
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
- KV cache: 9942 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 109 | 110 |
| cold | 256 | 1 | 26 | 183 | 188 |
| cold | 256 | 1 | 255 | 1389 | 1416 |
| cold | 256 | 4 | 2 | 159 | 163 |
| cold | 256 | 4 | 26 | 320 | 336 |
| cold | 256 | 4 | 255 | 2516 | 2528 |
| cold | 256 | 16 | 2 | 276 | 284 |
| cold | 256 | 16 | 26 | 809 | 818 |
| cold | 256 | 16 | 255 | 7504 | 7566 |
| cold | 256 | 64 | 2 | 798 | 824 |
| cold | 256 | 64 | 26 | 2896 | 2942 |
| cold | 256 | 64 | 255 | 56860 | 56998 |
| cold | 2048 | 1 | 2 | 553 | 556 |
| cold | 2048 | 1 | 26 | 642 | 643 |
| cold | 2048 | 1 | 255 | 1932 | 1938 |
| cold | 2048 | 4 | 2 | 617 | 865 |
| cold | 2048 | 4 | 26 | 841 | 1062 |
| cold | 2048 | 4 | 255 | 3280 | 3515 |
| cold | 2048 | 16 | 2 | 772 | 1006 |
| cold | 2048 | 16 | 26 | 1600 | 1608 |
| cold | 2048 | 16 | 255 | 9423 | 9520 |
| cold | 2048 | 64 | 2 | 1698 | 1730 |
| cold | 2048 | 64 | 26 | 3931 | 3955 |
| cold | 2048 | 64 | 255 | 65022 | 65450 |
| cold | 8192 | 1 | 2 | 2277 | 2280 |
| cold | 8192 | 1 | 26 | 2395 | 2399 |
| cold | 8192 | 1 | 255 | 3908 | 3916 |
| cold | 8192 | 4 | 2 | 6456 | 6698 |
| cold | 8192 | 4 | 26 | 6706 | 6963 |
| cold | 8192 | 4 | 255 | 7094 | 7115 |
| cold | 8192 | 16 | 2 | 9178 | 9402 |
| cold | 8192 | 16 | 26 | 9633 | 9898 |
| cold | 8192 | 16 | 255 | 19195 | 19207 |
| cold | 8192 | 64 | 2 | 10873 | 11339 |
| cold | 8192 | 64 | 26 | 13637 | 13902 |
| cold | 8192 | 64 | 255 | 104126 | 110626 |
| warm | 2048 | 16 | 26 | 250 | 253 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.6 |
| 16 | 0.6 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 88.1 | 91.9 | 91.7 | 0.931 | 0.232 | 60 | 300 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.116 | 0.231 | 49.4 | 42.7 | 5 | 47 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 189 | 24.6 |
| long | none | 209 | 24.3 |
| short | 4 systemone | 8620 | 8.2 |
| long | 4 systemone | 1316 | 15.1 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 4001925 | 26954046 | 7796126 | 71.1 | 5148 | 97.8 | 55.1 | 56 | 0 |
| warm | 33678 | 235008 | 8256 | 96.5 | 96 | 21.2 | 9.3 | 0 | 0 |
| throughput x1 | 118120 | 826480 | 118192 | 85.7 | 336 | 21.3 | 12.3 | 0 | 0 |
| throughput x4 | 118122 | 826512 | 133520 | 83.8 | 336 | 43.7 | 32.7 | 32 | 0 |
| throughput x16 | 185614 | 1298704 | 208880 | 83.9 | 528 | 52.4 | 45.2 | 217 | 0 |
| jevbench | 606246 | 606246 | 545702 | 10.0 | 1682 | 4.1 | 0.1 | 0 | 0 |
| chat | 112487 | 787096 | 127704 | 83.8 | 1646 | 50.7 | 7.6 | 19 | 0 |
