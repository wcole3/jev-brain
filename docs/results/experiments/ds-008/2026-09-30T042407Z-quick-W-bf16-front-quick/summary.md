# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T04:24:07.425915+00:00
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
| cold | 256 | 1 | 2 | 95 | 95 |
| cold | 256 | 1 | 26 | 183 | 183 |
| cold | 256 | 16 | 2 | 274 | 274 |
| cold | 256 | 16 | 26 | 697 | 697 |
| cold | 2048 | 1 | 2 | 372 | 372 |
| cold | 2048 | 1 | 26 | 437 | 437 |
| cold | 2048 | 16 | 2 | 895 | 895 |
| cold | 2048 | 16 | 26 | 1268 | 1268 |
| warm | 2048 | 16 | 26 | 681 | 681 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 86 | 96 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.086 | 0.415 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56237 | 325451 | 74651 | 77.1 | 210 | 6.1 | 0.9 | 0 | 0 |
| warm | 16185 | 132423 | 12823 | 90.3 | 51 | 6.1 | 0.6 | 0 | 0 |
| throughput x1 | 43253 | 353128 | 65128 | 81.6 | 136 | 6.1 | 1.4 | 0 | 0 |
| throughput x4 | 59474 | 485551 | 89551 | 81.6 | 187 | 11.6 | 6.0 | 47 | 0 |
| throughput x16 | 97320 | 794538 | 146538 | 81.6 | 306 | 12.3 | 8.1 | 207 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
