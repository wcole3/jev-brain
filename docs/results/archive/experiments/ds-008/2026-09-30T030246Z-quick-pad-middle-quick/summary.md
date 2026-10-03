# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T03:02:46.252759+00:00
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
- prefix_pad: middle
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
| cold | 256 | 1 | 2 | 88 | 88 |
| cold | 256 | 1 | 26 | 136 | 136 |
| cold | 256 | 16 | 2 | 422 | 422 |
| cold | 256 | 16 | 26 | 751 | 751 |
| cold | 2048 | 1 | 2 | 411 | 411 |
| cold | 2048 | 1 | 26 | 481 | 481 |
| cold | 2048 | 16 | 2 | 679 | 679 |
| cold | 2048 | 16 | 26 | 1016 | 1016 |
| warm | 2048 | 16 | 26 | 713 | 713 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 1.1 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 75 | 84 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.065 | 0.415 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56238 | 343305 | 61065 | 82.2 | 204 | 9.3 | 1.1 | 0 | 0 |
| warm | 16185 | 122919 | 12375 | 89.9 | 48 | 9.3 | 3.4 | 0 | 0 |
| throughput x1 | 54065 | 409730 | 56930 | 86.1 | 160 | 9.3 | 2.4 | 0 | 0 |
| throughput x4 | 64878 | 491676 | 68316 | 86.1 | 192 | 29.2 | 9.0 | 1 | 0 |
| throughput x16 | 108128 | 819460 | 113860 | 86.1 | 320 | 28.9 | 16.1 | 80 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
