# qwen3.6-27b benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-07T12:54:54.181314+00:00
- repo commit: 286829d-dirty
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: qwen3.6-27b
- hf_model: Qwen/Qwen3.6-27B
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
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
- KV cache: 650 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 106 | 116 |
| cold | 256 | 1 | 26 | 174 | 176 |
| cold | 256 | 1 | 255 | 1306 | 1353 |
| cold | 256 | 4 | 2 | 453 | 456 |
| cold | 256 | 4 | 26 | 498 | 544 |
| cold | 256 | 4 | 255 | 2871 | 2944 |
| cold | 256 | 16 | 2 | 662 | 704 |
| cold | 256 | 16 | 26 | 1020 | 1082 |
| cold | 256 | 16 | 255 | 6865 | 7016 |
| cold | 256 | 64 | 2 | 1692 | 1704 |
| cold | 256 | 64 | 26 | 3299 | 3431 |
| cold | 256 | 64 | 255 | 24910 | 24968 |
| cold | 2048 | 1 | 2 | 660 | 782 |
| cold | 2048 | 1 | 26 | 711 | 939 |
| cold | 2048 | 1 | 255 | 1930 | 1949 |
| cold | 2048 | 4 | 2 | 911 | 942 |
| cold | 2048 | 4 | 26 | 1165 | 1351 |
| cold | 2048 | 4 | 255 | 4781 | 4898 |
| cold | 2048 | 16 | 2 | 1161 | 1190 |
| cold | 2048 | 16 | 26 | 1620 | 1639 |
| cold | 2048 | 16 | 255 | 8980 | 9199 |
| cold | 2048 | 64 | 2 | 2661 | 2723 |
| cold | 2048 | 64 | 26 | 4267 | 4286 |
| cold | 2048 | 64 | 255 | 27270 | 27881 |
| cold | 8192 | 1 | 2 | 2142 | 2150 |
| cold | 8192 | 1 | 26 | 2256 | 2274 |
| cold | 8192 | 1 | 255 | 3606 | 3633 |
| cold | 8192 | 4 | 2 | 2530 | 2567 |
| cold | 8192 | 4 | 26 | 2704 | 2805 |
| cold | 8192 | 4 | 255 | 9957 | 11022 |
| cold | 8192 | 16 | 2 | 3156 | 3244 |
| cold | 8192 | 16 | 26 | 3629 | 3691 |
| cold | 8192 | 16 | 255 | 15714 | 16336 |
| cold | 8192 | 64 | 2 | 6138 | 6353 |
| cold | 8192 | 64 | 26 | 7927 | 8180 |
| cold | 8192 | 64 | 255 | 35407 | 35819 |
| warm | 2048 | 16 | 26 | 1098 | 1117 |

| workers | requests/s |
|---|---|
| 1 | 0.6 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.2 | 93.3 | 90.4 | 0.876 | 0.280 | 158 | 363 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.035 | 0.164 | 35.7 | 42.7 | 52 | 8 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 152 | 23.0 |
| long | none | 142 | 23.6 |
| short | 4 systemone | 9741 | 12.3 |
| long | 4 systemone | 494 | 14.3 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990381 | 29558855 | 5240743 | 82.3 | 5148 | 20.3 | 5.0 | 62 | 0 |
| warm | 33462 | 250446 | 27006 | 89.2 | 96 | 7.1 | 2.9 | 5 | 0 |
| throughput x1 | 111768 | 834820 | 129220 | 84.5 | 320 | 7.1 | 2.2 | 5 | 0 |
| throughput x4 | 150877 | 1127007 | 174447 | 84.5 | 432 | 8.6 | 5.5 | 35 | 0 |
| throughput x16 | 178837 | 1335712 | 206752 | 84.5 | 512 | 8.8 | 5.7 | 204 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 1.2 | 0.0 | 0 | 0 |
| chat | 145291 | 1085348 | 168068 | 84.5 | 2340 | 8.6 | 1.2 | 20 | 0 |
