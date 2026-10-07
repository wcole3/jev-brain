# qwen3.6-27b benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-07T02:35:09.115844+00:00
- repo commit: b88d7e8-dirty
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
- KV cache: 571 blocks × 800 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 800
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 116 | 128 |
| cold | 256 | 1 | 26 | 173 | 185 |
| cold | 256 | 1 | 255 | 1258 | 1306 |
| cold | 256 | 4 | 2 | 448 | 472 |
| cold | 256 | 4 | 26 | 485 | 512 |
| cold | 256 | 4 | 255 | 2798 | 2830 |
| cold | 256 | 16 | 2 | 547 | 620 |
| cold | 256 | 16 | 26 | 883 | 948 |
| cold | 256 | 16 | 255 | 6280 | 6326 |
| cold | 256 | 64 | 2 | 1302 | 1321 |
| cold | 256 | 64 | 26 | 2733 | 2823 |
| cold | 256 | 64 | 255 | 21647 | 22276 |
| cold | 2048 | 1 | 2 | 545 | 546 |
| cold | 2048 | 1 | 26 | 665 | 672 |
| cold | 2048 | 1 | 255 | 1744 | 1788 |
| cold | 2048 | 4 | 2 | 852 | 887 |
| cold | 2048 | 4 | 26 | 869 | 978 |
| cold | 2048 | 4 | 255 | 4429 | 4434 |
| cold | 2048 | 16 | 2 | 959 | 981 |
| cold | 2048 | 16 | 26 | 1339 | 1382 |
| cold | 2048 | 16 | 255 | 8053 | 8116 |
| cold | 2048 | 64 | 2 | 1814 | 1865 |
| cold | 2048 | 64 | 26 | 3208 | 3259 |
| cold | 2048 | 64 | 255 | 23736 | 23969 |
| cold | 8192 | 1 | 2 | 1884 | 1887 |
| cold | 8192 | 1 | 26 | 1985 | 2019 |
| cold | 8192 | 1 | 255 | 3108 | 3134 |
| cold | 8192 | 4 | 2 | 2318 | 2334 |
| cold | 8192 | 4 | 26 | 2319 | 2349 |
| cold | 8192 | 4 | 255 | 9383 | 9554 |
| cold | 8192 | 16 | 2 | 2515 | 2539 |
| cold | 8192 | 16 | 26 | 2859 | 2912 |
| cold | 8192 | 16 | 255 | 13329 | 13634 |
| cold | 8192 | 64 | 2 | 3726 | 3783 |
| cold | 8192 | 64 | 26 | 5083 | 5206 |
| cold | 8192 | 64 | 255 | 30493 | 31022 |
| warm | 2048 | 16 | 26 | 835 | 865 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.1 | 93.2 | 90.2 | 0.889 | 0.266 | 127 | 303 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.034 | 0.164 | 35.5 | 42.7 | 53 | 8 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 154 | 78.4 |
| long | none | 155 | 62.9 |
| short | 4 systemone | 2957 | 33.9 |
| long | 4 systemone | 826 | 36.6 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990406 | 29558855 | 4762055 | 83.9 | 5148 | 97.0 | 11.0 | 61 | 0 |
| warm | 33462 | 250446 | 22446 | 91.0 | 96 | 28.4 | 10.0 | 2 | 0 |
| throughput x1 | 128535 | 960043 | 132043 | 86.2 | 368 | 28.4 | 8.9 | 2 | 0 |
| throughput x4 | 178829 | 1335712 | 183712 | 86.2 | 512 | 31.1 | 18.1 | 27 | 0 |
| throughput x16 | 229123 | 1711381 | 235381 | 86.2 | 656 | 34.0 | 19.3 | 200 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 3.0 | 0.0 | 0 | 0 |
| chat | 67061 | 500974 | 68974 | 86.2 | 1901 | 34.0 | 4.6 | 16 | 0 |
