# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-10-02T03:41:12.695220+00:00
- repo commit: 7a5d9b6
- host: RTX PRO 6000 Blackwell, 450/600 W, drv 595.71.05, PCIe 5x16, AMD Eng Sample: 100-000001535-05 (512 thr), 373 GB, vast 53796457
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
- prefix_block: 784
- prefix_pad_always: False
- warm_min_prefix_tokens: 784
- warm_up: row
- KV cache: 654 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 94 | 94 |
| cold | 256 | 1 | 26 | 175 | 175 |
| cold | 256 | 16 | 2 | 464 | 464 |
| cold | 256 | 16 | 26 | 947 | 947 |
| cold | 2048 | 1 | 2 | 493 | 493 |
| cold | 2048 | 1 | 26 | 565 | 565 |
| cold | 2048 | 16 | 2 | 774 | 774 |
| cold | 2048 | 16 | 26 | 1265 | 1265 |
| warm | 2048 | 16 | 26 | 770 | 770 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 68 | 70 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.051 | 0.418 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56243 | 343304 | 61064 | 82.2 | 204 | 9.5 | 1.9 | 0 | 0 |
| warm | 16185 | 122919 | 12375 | 89.9 | 48 | 9.5 | 2.4 | 0 | 0 |
| throughput x1 | 43257 | 327784 | 45544 | 86.1 | 128 | 9.5 | 2.5 | 0 | 0 |
| throughput x4 | 64877 | 491676 | 68316 | 86.1 | 192 | 29.7 | 9.2 | 1 | 0 |
| throughput x16 | 86508 | 655568 | 91088 | 86.1 | 256 | 29.4 | 17.0 | 79 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
