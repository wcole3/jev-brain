# gemma-4-31b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T14:31:37.111877+00:00
- repo commit: 96975fe-dirty
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 50
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: decider_chat
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: off
- prefix_block: 0
- prefix_pad_always: False
- warm_min_prefix_tokens: 2048
- warm_up: row
- KV cache: 9965 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 105 | 105 |
| cold | 256 | 1 | 26 | 185 | 185 |
| cold | 256 | 16 | 2 | 300 | 300 |
| cold | 256 | 16 | 26 | 796 | 796 |
| cold | 2048 | 1 | 2 | 477 | 477 |
| cold | 2048 | 1 | 26 | 574 | 574 |
| cold | 2048 | 16 | 2 | 822 | 822 |
| cold | 2048 | 16 | 26 | 1388 | 1388 |
| warm | 2048 | 16 | 26 | 324 | 324 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.8 |
| 16 | 0.6 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 78.0 | 100.0 | n/a | 0.870 | 0.306 | 70 | 74 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.216 | 0.430 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56771 | 266756 | 56324 | 78.9 | 204 | 14.3 | 3.1 | 0 | 0 |
| warm | 16293 | 108768 | 5536 | 94.9 | 48 | 13.7 | 4.3 | 0 | 0 |
| throughput x1 | 43545 | 291600 | 43792 | 85.0 | 128 | 14.3 | 4.9 | 0 | 0 |
| throughput x4 | 65316 | 437376 | 65664 | 85.0 | 192 | 41.3 | 19.9 | 3 | 0 |
| throughput x16 | 87083 | 583088 | 120240 | 79.4 | 256 | 36.2 | 31.3 | 162 | 0 |
| jevbench | 10698 | 10698 | 8906 | 16.8 | 50 | 0.0 | 0.0 | 0 | 0 |
