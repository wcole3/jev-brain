# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-30T03:52:54.191892+00:00
- repo commit: f0d9429-dirty
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
| cold | 256 | 1 | 2 | 90 | 90 |
| cold | 256 | 1 | 26 | 172 | 172 |
| cold | 256 | 16 | 2 | 267 | 267 |
| cold | 256 | 16 | 26 | 750 | 750 |
| cold | 2048 | 1 | 2 | 370 | 370 |
| cold | 2048 | 1 | 26 | 431 | 431 |
| cold | 2048 | 16 | 2 | 668 | 668 |
| cold | 2048 | 16 | 26 | 1427 | 1427 |
| warm | 2048 | 16 | 26 | 373 | 373 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 81 | 89 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.078 | 0.417 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56244 | 311055 | 67455 | 78.3 | 204 | 5.8 | 0.8 | 14 | 0 |
| warm | 16185 | 125223 | 10023 | 92.0 | 48 | 5.8 | 1.1 | 0 | 0 |
| throughput x1 | 43252 | 333928 | 65128 | 80.5 | 128 | 5.8 | 1.4 | 0 | 0 |
| throughput x4 | 54060 | 417410 | 81410 | 80.5 | 160 | 10.2 | 5.2 | 29 | 0 |
| throughput x16 | 91907 | 709597 | 138397 | 80.5 | 272 | 10.3 | 7.7 | 179 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
