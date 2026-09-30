# qwen3.8-27b benchmark (full, systemone only)

## Provenance

- timestamp: 2026-09-30T05:07:30.396934+00:00
- repo commit: 5bab2e8
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: qwen3.8-27b
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
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
| cold | 256 | 1 | 2 | 89 | 94 |
| cold | 256 | 1 | 26 | 135 | 139 |
| cold | 256 | 1 | 255 | 894 | 898 |
| cold | 256 | 4 | 2 | 355 | 368 |
| cold | 256 | 4 | 26 | 401 | 408 |
| cold | 256 | 4 | 255 | 1952 | 1986 |
| cold | 256 | 16 | 2 | 435 | 440 |
| cold | 256 | 16 | 26 | 758 | 762 |
| cold | 256 | 16 | 255 | 5284 | 5317 |
| cold | 256 | 64 | 2 | 891 | 906 |
| cold | 256 | 64 | 26 | 2240 | 2256 |
| cold | 256 | 64 | 255 | 18737 | 18955 |
| cold | 2048 | 1 | 2 | 405 | 407 |
| cold | 2048 | 1 | 26 | 457 | 477 |
| cold | 2048 | 1 | 255 | 1290 | 1295 |
| cold | 2048 | 4 | 2 | 601 | 626 |
| cold | 2048 | 4 | 26 | 662 | 670 |
| cold | 2048 | 4 | 255 | 2600 | 2621 |
| cold | 2048 | 16 | 2 | 702 | 708 |
| cold | 2048 | 16 | 26 | 1050 | 1060 |
| cold | 2048 | 16 | 255 | 6149 | 6199 |
| cold | 2048 | 64 | 2 | 1250 | 1270 |
| cold | 2048 | 64 | 26 | 2636 | 2660 |
| cold | 2048 | 64 | 255 | 20472 | 20726 |
| cold | 8192 | 1 | 2 | 1444 | 1454 |
| cold | 8192 | 1 | 26 | 1555 | 1557 |
| cold | 8192 | 1 | 255 | 2463 | 2463 |
| cold | 8192 | 4 | 2 | 1726 | 1742 |
| cold | 8192 | 4 | 26 | 1806 | 1838 |
| cold | 8192 | 4 | 255 | 5008 | 5061 |
| cold | 8192 | 16 | 2 | 1910 | 1939 |
| cold | 8192 | 16 | 26 | 2284 | 2314 |
| cold | 8192 | 16 | 255 | 8896 | 8936 |
| cold | 8192 | 64 | 2 | 2752 | 2776 |
| cold | 8192 | 64 | 26 | 4165 | 4175 |
| cold | 8192 | 64 | 255 | 24441 | 24469 |
| warm | 2048 | 16 | 26 | 686 | 692 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 86.4 | 90.4 | 86.2 | 0.880 | 0.208 | 81 | 232 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.033 | 0.205 | 39.2 | 42.7 | 54 | 32 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3938057 | 26069515 | 4337035 | 83.4 | 5148 | 40.8 | 6.4 | 62 | 0 |
| warm | 32370 | 245838 | 22398 | 90.9 | 96 | 9.3 | 2.9 | 0 | 0 |
| throughput x1 | 151384 | 1147244 | 159404 | 86.1 | 448 | 9.3 | 2.4 | 0 | 0 |
| throughput x4 | 178409 | 1352109 | 187869 | 86.1 | 528 | 29.2 | 8.6 | 1 | 0 |
| throughput x16 | 232469 | 1761839 | 244799 | 86.1 | 688 | 29.1 | 17.8 | 80 | 0 |
| jevbench | 514943 | 514943 | 514943 | 0.0 | 1682 | 1.2 | 0.0 | 0 | 0 |
