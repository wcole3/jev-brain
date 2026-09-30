# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T04:25:29.840390+00:00
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
- prefix_pad: spread
- prefix_block: 400
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
| cold | 256 | 1 | 2 | 86 | 86 |
| cold | 256 | 1 | 26 | 174 | 174 |
| cold | 256 | 16 | 2 | 258 | 258 |
| cold | 256 | 16 | 26 | 737 | 737 |
| cold | 2048 | 1 | 2 | 397 | 397 |
| cold | 2048 | 1 | 26 | 458 | 458 |
| cold | 2048 | 16 | 2 | 957 | 957 |
| cold | 2048 | 16 | 26 | 1347 | 1347 |
| warm | 2048 | 16 | 26 | 718 | 718 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 84 | 94 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.086 | 0.415 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56237 | 325447 | 74647 | 77.1 | 210 | 6.1 | 0.9 | 14 | 0 |
| warm | 16185 | 132423 | 12823 | 90.3 | 51 | 6.1 | 1.1 | 0 | 0 |
| throughput x1 | 43252 | 353128 | 65128 | 81.6 | 136 | 6.1 | 1.7 | 0 | 0 |
| throughput x4 | 54057 | 441410 | 81410 | 81.6 | 170 | 11.6 | 5.8 | 47 | 0 |
| throughput x16 | 97316 | 794538 | 146538 | 81.6 | 306 | 12.3 | 8.1 | 207 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
