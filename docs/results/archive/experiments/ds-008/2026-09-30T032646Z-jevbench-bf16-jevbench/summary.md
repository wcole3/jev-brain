# qwen3.6-27b benchmark (full, JevBench only)

## Provenance

- timestamp: 2026-09-30T03:26:46.094687+00:00
- repo commit: f0d9429
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
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

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 84.3 | 91.9 | 83.5 | 0.816 | 0.382 | 85 | 243 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.068 | 0.228 | 35.5 | 42.7 | 74 | 29 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| jevbench | 514943 | 514943 | 514143 | 0.2 | 1682 | 0.7 | 0.0 | 0 | 0 |
