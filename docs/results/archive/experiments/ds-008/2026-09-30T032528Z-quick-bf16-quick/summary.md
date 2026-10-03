# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T03:25:28.898370+00:00
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
- KV cache: 1304 blocks × 400 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: bfloat16
- mamba_block_size: 400
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 94 | 94 |
| cold | 256 | 1 | 26 | 184 | 184 |
| cold | 256 | 16 | 2 | 861 | 861 |
| cold | 256 | 16 | 26 | 1154 | 1154 |
| cold | 2048 | 1 | 2 | 379 | 379 |
| cold | 2048 | 1 | 26 | 434 | 434 |
| cold | 2048 | 16 | 2 | 722 | 722 |
| cold | 2048 | 16 | 26 | 1350 | 1350 |
| warm | 2048 | 16 | 26 | 476 | 476 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 84 | 99 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.060 | 0.417 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56232 | 265977 | 91977 | 65.4 | 204 | 5.6 | 1.2 | 0 | 0 |
| warm | 16185 | 108615 | 11815 | 89.1 | 48 | 5.6 | 0.9 | 0 | 0 |
| throughput x1 | 43253 | 291128 | 67128 | 76.9 | 128 | 5.6 | 1.6 | 0 | 0 |
| throughput x4 | 54064 | 363874 | 83874 | 76.9 | 160 | 9.9 | 5.4 | 44 | 0 |
| throughput x16 | 97321 | 655066 | 151066 | 76.9 | 288 | 10.5 | 7.8 | 179 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
