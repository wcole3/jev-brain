# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T02:15:47.973814+00:00
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
- prefix_pad: off
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
| cold | 256 | 1 | 2 | 102 | 102 |
| cold | 256 | 1 | 26 | 135 | 135 |
| cold | 256 | 16 | 2 | 808 | 808 |
| cold | 256 | 16 | 26 | 1234 | 1234 |
| cold | 2048 | 1 | 2 | 372 | 372 |
| cold | 2048 | 1 | 26 | 449 | 449 |
| cold | 2048 | 16 | 2 | 1683 | 1683 |
| cold | 2048 | 16 | 26 | 2389 | 2389 |
| warm | 2048 | 16 | 26 | 1090 | 1090 |

| workers | requests/s |
|---|---|
| 1 | 0.4 |
| 4 | 0.5 |
| 16 | 0.5 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 87 | 161 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.078 | 0.417 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56239 | 266044 | 129628 | 51.3 | 204 | 9.2 | 3.5 | 2 | 0 |
| warm | 16185 | 108615 | 27079 | 75.1 | 48 | 12.2 | 5.0 | 2 | 0 |
| throughput x1 | 27032 | 181937 | 72177 | 60.3 | 80 | 8.9 | 4.4 | 2 | 0 |
| throughput x4 | 43247 | 291032 | 115416 | 60.3 | 128 | 11.7 | 7.3 | 47 | 0 |
| throughput x16 | 91911 | 618621 | 245437 | 60.3 | 272 | 10.2 | 8.5 | 213 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
