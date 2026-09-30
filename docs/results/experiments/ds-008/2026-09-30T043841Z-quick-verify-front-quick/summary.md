# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T04:38:41.975625+00:00
- repo commit: 1d22b96-dirty
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
| cold | 256 | 1 | 2 | 86 | 86 |
| cold | 256 | 1 | 26 | 147 | 147 |
| cold | 256 | 16 | 2 | 433 | 433 |
| cold | 256 | 16 | 26 | 763 | 763 |
| cold | 2048 | 1 | 2 | 372 | 372 |
| cold | 2048 | 1 | 26 | 431 | 431 |
| cold | 2048 | 16 | 2 | 670 | 670 |
| cold | 2048 | 16 | 26 | 982 | 982 |
| warm | 2048 | 16 | 26 | 646 | 646 |

| workers | requests/s |
|---|---|
| 1 | 1.0 |
| 4 | 1.1 |
| 16 | 1.1 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 82 | 103 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.078 | 0.417 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56249 | 343310 | 61070 | 82.2 | 204 | 9.0 | 1.5 | 0 | 0 |
| warm | 16185 | 122919 | 12375 | 89.9 | 48 | 9.3 | 2.7 | 0 | 0 |
| throughput x1 | 59470 | 450703 | 62623 | 86.1 | 176 | 9.3 | 2.3 | 0 | 0 |
| throughput x4 | 70288 | 532649 | 74009 | 86.1 | 208 | 29.2 | 8.5 | 1 | 0 |
| throughput x16 | 108128 | 819460 | 113860 | 86.1 | 320 | 28.9 | 16.2 | 80 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
