# gemma-4-31b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T14:22:35.618142+00:00
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
- warm_min_prefix_tokens: 512
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
| cold | 256 | 1 | 2 | 92 | 92 |
| cold | 256 | 1 | 26 | 164 | 164 |
| cold | 256 | 16 | 2 | 268 | 268 |
| cold | 256 | 16 | 26 | 724 | 724 |
| cold | 2048 | 1 | 2 | 442 | 442 |
| cold | 2048 | 1 | 26 | 519 | 519 |
| cold | 2048 | 16 | 2 | 1123 | 1123 |
| cold | 2048 | 16 | 26 | 1660 | 1660 |
| warm | 2048 | 16 | 26 | 279 | 279 |

| workers | requests/s |
|---|---|
| 1 | 0.6 |
| 4 | 0.6 |
| 16 | 0.5 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 78.0 | 100.0 | n/a | 0.870 | 0.306 | 70 | 76 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.216 | 0.432 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56765 | 266690 | 68546 | 74.3 | 204 | 14.1 | 2.6 | 0 | 0 |
| warm | 16293 | 108768 | 7584 | 93.0 | 48 | 11.8 | 1.3 | 0 | 0 |
| throughput x1 | 38095 | 255040 | 52544 | 79.4 | 112 | 14.3 | 4.9 | 0 | 0 |
| throughput x4 | 48988 | 328048 | 67632 | 79.4 | 144 | 33.7 | 21.9 | 24 | 0 |
| throughput x16 | 87075 | 582960 | 148784 | 74.5 | 256 | 39.5 | 32.5 | 178 | 0 |
| jevbench | 10698 | 10698 | 8906 | 16.8 | 50 | 0.0 | 0.0 | 0 | 0 |
