# gemma-4-31b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T14:24:16.936087+00:00
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
- warm_up: prefix
- KV cache: 9965 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 93 | 93 |
| cold | 256 | 1 | 26 | 166 | 166 |
| cold | 256 | 16 | 2 | 274 | 274 |
| cold | 256 | 16 | 26 | 760 | 760 |
| cold | 2048 | 1 | 2 | 460 | 460 |
| cold | 2048 | 1 | 26 | 542 | 542 |
| cold | 2048 | 16 | 2 | 775 | 775 |
| cold | 2048 | 16 | 26 | 1305 | 1305 |
| warm | 2048 | 16 | 26 | 289 | 289 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 0.8 |
| 16 | 0.5 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 78.0 | 100.0 | n/a | 0.870 | 0.306 | 70 | 73 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.216 | 0.432 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56766 | 279141 | 56421 | 79.8 | 210 | 14.4 | 2.9 | 0 | 0 |
| warm | 16293 | 114933 | 5557 | 95.2 | 51 | 13.7 | 3.4 | 0 | 0 |
| throughput x1 | 43540 | 308052 | 43860 | 85.8 | 136 | 14.6 | 5.6 | 0 | 0 |
| throughput x4 | 65315 | 462163 | 65875 | 85.7 | 204 | 40.9 | 20.3 | 9 | 0 |
| throughput x16 | 97961 | 693049 | 151865 | 78.1 | 306 | 41.2 | 32.4 | 175 | 0 |
| jevbench | 10698 | 10698 | 8906 | 16.8 | 50 | 0.0 | 0.0 | 0 | 0 |
