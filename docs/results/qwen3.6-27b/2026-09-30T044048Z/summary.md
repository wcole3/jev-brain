# qwen3.6-27b benchmark (full, systemone only)

## Provenance

- timestamp: 2026-09-30T04:40:48.718457+00:00
- repo commit: 5bab2e8
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: qwen3.6-27b
- hf_model: Qwen/Qwen3.6-27B
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: front
- prefix_block: 784
- prefix_pad_always: False
- warm_min_prefix_tokens: 784
- KV cache: 665 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 86 | 102 |
| cold | 256 | 1 | 26 | 137 | 157 |
| cold | 256 | 1 | 255 | 896 | 900 |
| cold | 256 | 4 | 2 | 363 | 397 |
| cold | 256 | 4 | 26 | 407 | 427 |
| cold | 256 | 4 | 255 | 2031 | 2037 |
| cold | 256 | 16 | 2 | 448 | 450 |
| cold | 256 | 16 | 26 | 765 | 776 |
| cold | 256 | 16 | 255 | 5388 | 5408 |
| cold | 256 | 64 | 2 | 910 | 914 |
| cold | 256 | 64 | 26 | 2292 | 2310 |
| cold | 256 | 64 | 255 | 18834 | 18971 |
| cold | 2048 | 1 | 2 | 416 | 419 |
| cold | 2048 | 1 | 26 | 472 | 486 |
| cold | 2048 | 1 | 255 | 1318 | 1325 |
| cold | 2048 | 4 | 2 | 608 | 616 |
| cold | 2048 | 4 | 26 | 662 | 673 |
| cold | 2048 | 4 | 255 | 2633 | 2661 |
| cold | 2048 | 16 | 2 | 711 | 715 |
| cold | 2048 | 16 | 26 | 1052 | 1065 |
| cold | 2048 | 16 | 255 | 6200 | 6227 |
| cold | 2048 | 64 | 2 | 1240 | 1257 |
| cold | 2048 | 64 | 26 | 2691 | 2700 |
| cold | 2048 | 64 | 255 | 20549 | 20771 |
| cold | 8192 | 1 | 2 | 1439 | 1465 |
| cold | 8192 | 1 | 26 | 1575 | 1619 |
| cold | 8192 | 1 | 255 | 2464 | 2477 |
| cold | 8192 | 4 | 2 | 1726 | 1750 |
| cold | 8192 | 4 | 26 | 1804 | 1816 |
| cold | 8192 | 4 | 255 | 5066 | 5107 |
| cold | 8192 | 16 | 2 | 1894 | 1908 |
| cold | 8192 | 16 | 26 | 2311 | 2336 |
| cold | 8192 | 16 | 255 | 8853 | 8984 |
| cold | 8192 | 64 | 2 | 2769 | 2829 |
| cold | 8192 | 64 | 26 | 4185 | 4229 |
| cold | 8192 | 64 | 255 | 24194 | 24284 |
| warm | 2048 | 16 | 26 | 708 | 732 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 84.3 | 91.9 | 83.5 | 0.816 | 0.382 | 83 | 236 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.053 | 0.228 | 35.2 | 42.7 | 75 | 28 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3938049 | 26069512 | 4337032 | 83.4 | 5148 | 40.8 | 6.5 | 62 | 0 |
| warm | 32370 | 245838 | 22398 | 90.9 | 96 | 9.3 | 3.9 | 0 | 0 |
| throughput x1 | 151383 | 1147244 | 159404 | 86.1 | 448 | 9.3 | 2.5 | 0 | 0 |
| throughput x4 | 178407 | 1352109 | 187869 | 86.1 | 528 | 29.2 | 8.7 | 1 | 0 |
| throughput x16 | 232465 | 1761839 | 244799 | 86.1 | 688 | 29.1 | 17.9 | 80 | 0 |
| jevbench | 514943 | 514943 | 514943 | 0.0 | 1682 | 1.2 | 0.0 | 0 | 0 |
