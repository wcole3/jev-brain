# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T04:08:10.986716+00:00
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
| cold | 256 | 1 | 2 | 84 | 84 |
| cold | 256 | 1 | 26 | 130 | 130 |
| cold | 256 | 16 | 2 | 774 | 774 |
| cold | 256 | 16 | 26 | 1178 | 1178 |
| cold | 2048 | 1 | 2 | 360 | 360 |
| cold | 2048 | 1 | 26 | 427 | 427 |
| cold | 2048 | 16 | 2 | 1678 | 1678 |
| cold | 2048 | 16 | 26 | 2207 | 2207 |
| warm | 2048 | 16 | 26 | 1211 | 1211 |

| workers | requests/s |
|---|---|
| 1 | 0.5 |
| 4 | 0.5 |
| 16 | 0.5 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 84 | 96 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.078 | 0.417 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56248 | 278484 | 127956 | 54.1 | 210 | 9.8 | 3.3 | 3 | 0 |
| warm | 16185 | 114777 | 26969 | 76.5 | 51 | 12.8 | 5.1 | 2 | 0 |
| throughput x1 | 27031 | 192247 | 66807 | 65.2 | 85 | 9.2 | 4.6 | 3 | 0 |
| throughput x4 | 43249 | 307585 | 106881 | 65.3 | 136 | 14.9 | 9.9 | 41 | 0 |
| throughput x16 | 91910 | 653718 | 227222 | 65.2 | 289 | 14.9 | 11.7 | 212 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
