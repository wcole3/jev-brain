# qwen3.6-27b benchmark (full, JevBench only)

## Provenance

- timestamp: 2026-09-30T03:54:15.453078+00:00
- repo commit: f0d9429-dirty
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
- prefix_pad: front
- prefix_block: 400
- prefix_pad_always: True
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
| 1682 | 0 | 84.1 | 92.0 | 83.4 | 0.826 | 0.386 | 160 | 288 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.065 | 0.227 | 35.4 | 42.7 | 75 | 29 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| jevbench | 514943 | 1035314 | 752114 | 27.4 | 1682 | 0.8 | 0.0 | 0 | 0 |
