# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T04:17:07.515519+00:00
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
| cold | 256 | 1 | 2 | 92 | 92 |
| cold | 256 | 1 | 26 | 151 | 151 |
| cold | 256 | 16 | 2 | 514 | 514 |
| cold | 256 | 16 | 26 | 844 | 844 |
| cold | 2048 | 1 | 2 | 379 | 379 |
| cold | 2048 | 1 | 26 | 440 | 440 |
| cold | 2048 | 16 | 2 | 935 | 935 |
| cold | 2048 | 16 | 26 | 1315 | 1315 |
| warm | 2048 | 16 | 26 | 1006 | 1006 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 79 | 87 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.078 | 0.417 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56232 | 362117 | 79877 | 77.9 | 216 | 11.0 | 1.5 | 0 | 0 |
| warm | 16185 | 129975 | 17863 | 86.3 | 51 | 11.0 | 1.6 | 0 | 0 |
| throughput x1 | 43251 | 346600 | 64360 | 81.4 | 136 | 11.0 | 3.0 | 0 | 0 |
| throughput x4 | 59476 | 476575 | 88495 | 81.4 | 187 | 12.8 | 7.9 | 47 | 0 |
| throughput x16 | 102730 | 823175 | 151287 | 81.6 | 323 | 12.8 | 9.1 | 207 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
