# qwen3.6-27b benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-07T00:51:57.706087+00:00
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
- prefix_block: 784
- prefix_pad_always: False
- warm_min_prefix_tokens: 784
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
| cold | 256 | 1 | 2 | 121 | 164 |
| cold | 256 | 1 | 26 | 184 | 229 |
| cold | 256 | 1 | 255 | 1176 | 1275 |
| cold | 256 | 4 | 2 | 439 | 464 |
| cold | 256 | 4 | 26 | 452 | 462 |
| cold | 256 | 4 | 255 | 2722 | 2778 |
| cold | 256 | 16 | 2 | 533 | 591 |
| cold | 256 | 16 | 26 | 896 | 923 |
| cold | 256 | 16 | 255 | 6250 | 6467 |
| cold | 256 | 64 | 2 | 1206 | 1232 |
| cold | 256 | 64 | 26 | 2589 | 2667 |
| cold | 256 | 64 | 255 | 21904 | 23056 |
| cold | 2048 | 1 | 2 | 560 | 621 |
| cold | 2048 | 1 | 26 | 643 | 681 |
| cold | 2048 | 1 | 255 | 1826 | 1871 |
| cold | 2048 | 4 | 2 | 900 | 986 |
| cold | 2048 | 4 | 26 | 881 | 972 |
| cold | 2048 | 4 | 255 | 4644 | 4882 |
| cold | 2048 | 16 | 2 | 1060 | 1207 |
| cold | 2048 | 16 | 26 | 1467 | 1798 |
| cold | 2048 | 16 | 255 | 8002 | 8071 |
| cold | 2048 | 64 | 2 | 1718 | 1723 |
| cold | 2048 | 64 | 26 | 3244 | 3319 |
| cold | 2048 | 64 | 255 | 24032 | 24154 |
| cold | 8192 | 1 | 2 | 2367 | 2427 |
| cold | 8192 | 1 | 26 | 2070 | 2134 |
| cold | 8192 | 1 | 255 | 3249 | 4373 |
| cold | 8192 | 4 | 2 | 2272 | 2318 |
| cold | 8192 | 4 | 26 | 2298 | 2335 |
| cold | 8192 | 4 | 255 | 9376 | 9912 |
| cold | 8192 | 16 | 2 | 2555 | 2594 |
| cold | 8192 | 16 | 26 | 2834 | 2888 |
| cold | 8192 | 16 | 255 | 13011 | 13244 |
| cold | 8192 | 64 | 2 | 3602 | 3683 |
| cold | 8192 | 64 | 26 | 4828 | 5092 |
| cold | 8192 | 64 | 255 | 29740 | 30285 |
| warm | 2048 | 16 | 26 | 781 | 817 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.2 | 93.2 | 90.4 | 0.889 | 0.266 | 106 | 270 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.034 | 0.164 | 35.7 | 42.7 | 52 | 8 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 127 | 27.0 |
| long | none | 133 | 26.7 |
| short | 4 systemone | 7357 | 14.4 |
| long | 4 systemone | 498 | 16.0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990354 | 29091140 | 4777732 | 83.6 | 5148 | 30.0 | 5.1 | 61 | 0 |
| warm | 33462 | 245838 | 22398 | 90.9 | 96 | 8.3 | 3.5 | 2 | 0 |
| throughput x1 | 134120 | 983352 | 136632 | 86.1 | 384 | 8.3 | 2.5 | 2 | 0 |
| throughput x4 | 178814 | 1311136 | 182176 | 86.1 | 512 | 10.6 | 6.0 | 27 | 0 |
| throughput x16 | 240312 | 1761839 | 244799 | 86.1 | 688 | 10.6 | 6.6 | 200 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 0.0 | 0.0 | 0 | 0 |
| chat | 145300 | 1065380 | 148100 | 86.1 | 2098 | 9.2 | 1.2 | 17 | 0 |
