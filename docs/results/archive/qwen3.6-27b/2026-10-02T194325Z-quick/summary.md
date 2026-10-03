# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-10-02T19:43:25.085932+00:00
- repo commit: 6990a58
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
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
- KV cache: 665 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 108 | 108 |
| cold | 256 | 1 | 26 | 156 | 156 |
| cold | 256 | 16 | 2 | 492 | 492 |
| cold | 256 | 16 | 26 | 828 | 828 |
| cold | 2048 | 1 | 2 | 408 | 408 |
| cold | 2048 | 1 | 26 | 497 | 497 |
| cold | 2048 | 16 | 2 | 765 | 765 |
| cold | 2048 | 16 | 26 | 1120 | 1120 |
| warm | 2048 | 16 | 26 | 756 | 756 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 108 | 144 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.070 | 0.408 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56243 | 343310 | 61070 | 82.2 | 204 | 9.0 | 1.2 | 0 | 0 |
| warm | 16185 | 122919 | 12375 | 89.9 | 48 | 9.3 | 2.5 | 0 | 0 |
| throughput x1 | 48654 | 368757 | 51237 | 86.1 | 144 | 9.3 | 2.3 | 0 | 0 |
| throughput x4 | 64875 | 491676 | 68316 | 86.1 | 192 | 29.2 | 9.1 | 1 | 0 |
| throughput x16 | 91905 | 696541 | 96781 | 86.1 | 272 | 28.9 | 16.1 | 80 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
