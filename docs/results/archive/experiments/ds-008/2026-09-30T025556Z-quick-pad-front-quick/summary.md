# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T02:55:56.620231+00:00
- repo commit: f0d9429
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 50
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
| cold | 256 | 1 | 2 | 85 | 85 |
| cold | 256 | 1 | 26 | 139 | 139 |
| cold | 256 | 16 | 2 | 440 | 440 |
| cold | 256 | 16 | 26 | 748 | 748 |
| cold | 2048 | 1 | 2 | 378 | 378 |
| cold | 2048 | 1 | 26 | 441 | 441 |
| cold | 2048 | 16 | 2 | 731 | 731 |
| cold | 2048 | 16 | 26 | 1006 | 1006 |
| warm | 2048 | 16 | 26 | 654 | 654 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 1.1 |
| 16 | 1.1 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 79 | 89 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.065 | 0.415 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56244 | 343309 | 61069 | 82.2 | 204 | 9.3 | 1.3 | 0 | 0 |
| warm | 16185 | 122919 | 12375 | 89.9 | 48 | 9.3 | 2.8 | 0 | 0 |
| throughput x1 | 54060 | 409730 | 56930 | 86.1 | 160 | 9.3 | 2.3 | 0 | 0 |
| throughput x4 | 64883 | 491676 | 68316 | 86.1 | 192 | 29.2 | 9.1 | 1 | 0 |
| throughput x16 | 108126 | 819460 | 113860 | 86.1 | 320 | 28.9 | 16.1 | 80 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
