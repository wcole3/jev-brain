# gemma-4-31b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T14:33:09.400276+00:00
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
- warm_min_prefix_tokens: 1000000
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
| cold | 256 | 1 | 2 | 91 | 91 |
| cold | 256 | 1 | 26 | 173 | 173 |
| cold | 256 | 16 | 2 | 282 | 282 |
| cold | 256 | 16 | 26 | 768 | 768 |
| cold | 2048 | 1 | 2 | 462 | 462 |
| cold | 2048 | 1 | 26 | 548 | 548 |
| cold | 2048 | 16 | 2 | 753 | 753 |
| cold | 2048 | 16 | 26 | 1286 | 1286 |
| warm | 2048 | 16 | 26 | 227 | 227 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 78.0 | 100.0 | n/a | 0.870 | 0.306 | 71 | 74 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.216 | 0.430 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56770 | 266815 | 56383 | 78.9 | 204 | 14.6 | 3.2 | 0 | 0 |
| warm | 16293 | 108768 | 5536 | 94.9 | 48 | 13.8 | 3.5 | 0 | 0 |
| throughput x1 | 43538 | 291488 | 43680 | 85.0 | 128 | 14.6 | 5.5 | 0 | 0 |
| throughput x4 | 59874 | 400944 | 60208 | 85.0 | 176 | 33.6 | 25.2 | 32 | 0 |
| throughput x16 | 119740 | 801760 | 120288 | 85.0 | 352 | 37.8 | 33.4 | 207 | 0 |
| jevbench | 10698 | 10698 | 8906 | 16.8 | 50 | 0.0 | 0.0 | 0 | 0 |
