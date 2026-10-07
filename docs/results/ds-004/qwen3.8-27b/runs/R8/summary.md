# qwen3.8-27b benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-07T03:31:29.836151+00:00
- repo commit: b88d7e8-dirty
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
| cold | 256 | 1 | 2 | 124 | 142 |
| cold | 256 | 1 | 26 | 162 | 189 |
| cold | 256 | 1 | 255 | 1298 | 1321 |
| cold | 256 | 4 | 2 | 523 | 579 |
| cold | 256 | 4 | 26 | 509 | 534 |
| cold | 256 | 4 | 255 | 2770 | 2779 |
| cold | 256 | 16 | 2 | 540 | 552 |
| cold | 256 | 16 | 26 | 917 | 963 |
| cold | 256 | 16 | 255 | 6217 | 6346 |
| cold | 256 | 64 | 2 | 1343 | 1388 |
| cold | 256 | 64 | 26 | 2712 | 2757 |
| cold | 256 | 64 | 255 | 21231 | 21764 |
| cold | 2048 | 1 | 2 | 495 | 516 |
| cold | 2048 | 1 | 26 | 611 | 658 |
| cold | 2048 | 1 | 255 | 1688 | 1812 |
| cold | 2048 | 4 | 2 | 837 | 858 |
| cold | 2048 | 4 | 26 | 829 | 891 |
| cold | 2048 | 4 | 255 | 4401 | 4423 |
| cold | 2048 | 16 | 2 | 910 | 921 |
| cold | 2048 | 16 | 26 | 1337 | 1380 |
| cold | 2048 | 16 | 255 | 8140 | 8169 |
| cold | 2048 | 64 | 2 | 1958 | 2017 |
| cold | 2048 | 64 | 26 | 3245 | 3417 |
| cold | 2048 | 64 | 255 | 23096 | 23656 |
| cold | 8192 | 1 | 2 | 1889 | 1909 |
| cold | 8192 | 1 | 26 | 1943 | 1948 |
| cold | 8192 | 1 | 255 | 3115 | 3124 |
| cold | 8192 | 4 | 2 | 2239 | 2280 |
| cold | 8192 | 4 | 26 | 2340 | 2447 |
| cold | 8192 | 4 | 255 | 9366 | 9599 |
| cold | 8192 | 16 | 2 | 2495 | 2509 |
| cold | 8192 | 16 | 26 | 2870 | 2897 |
| cold | 8192 | 16 | 255 | 13210 | 13532 |
| cold | 8192 | 64 | 2 | 3656 | 3707 |
| cold | 8192 | 64 | 26 | 4989 | 5072 |
| cold | 8192 | 64 | 255 | 29503 | 29959 |
| warm | 2048 | 16 | 26 | 772 | 789 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.7 | 92.9 | 90.4 | 0.920 | 0.140 | 114 | 284 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.056 | 0.154 | 35.0 | 42.7 | 54 | 6 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 124 | 63.7 |
| long | none | 156 | 45.0 |
| short | 4 systemone | 2799 | 17.9 |
| long | 4 systemone | 578 | 32.7 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990356 | 29558832 | 4743632 | 84.0 | 5148 | 97.0 | 10.9 | 61 | 0 |
| warm | 33462 | 250446 | 22446 | 91.0 | 96 | 28.4 | 8.3 | 2 | 0 |
| throughput x1 | 134116 | 1001784 | 137784 | 86.2 | 384 | 28.4 | 8.2 | 2 | 0 |
| throughput x4 | 178829 | 1335712 | 183712 | 86.2 | 512 | 31.1 | 17.5 | 27 | 0 |
| throughput x16 | 229123 | 1711381 | 235381 | 86.2 | 656 | 34.0 | 19.0 | 200 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 3.0 | 0.0 | 0 | 0 |
| chat | 50298 | 375919 | 51919 | 86.2 | 1263 | 29.5 | 3.9 | 3 | 0 |
