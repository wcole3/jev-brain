# qwen3.8-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-10-02T03:59:40.745110+00:00
- repo commit: 7a5d9b6
- host: RTX PRO 6000 Blackwell, 450/600 W, drv 580.173.02, PCIe 4x16, AMD EPYC 7742 64-Core Processor (256 thr), 504 GB, vast 53796429
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 50
- profile: qwen3.8-27b
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
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
| cold | 256 | 1 | 2 | 98 | 98 |
| cold | 256 | 1 | 26 | 182 | 182 |
| cold | 256 | 16 | 2 | 508 | 508 |
| cold | 256 | 16 | 26 | 998 | 998 |
| cold | 2048 | 1 | 2 | 510 | 510 |
| cold | 2048 | 1 | 26 | 582 | 582 |
| cold | 2048 | 16 | 2 | 903 | 903 |
| cold | 2048 | 16 | 26 | 1368 | 1368 |
| warm | 2048 | 16 | 26 | 876 | 876 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 92.0 | 85.7 | n/a | 0.968 | 0.056 | 75 | 84 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.176 | 0.200 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56238 | 343304 | 61064 | 82.2 | 204 | 9.5 | 1.7 | 0 | 0 |
| warm | 16185 | 122919 | 12375 | 89.9 | 48 | 9.5 | 2.9 | 0 | 0 |
| throughput x1 | 43256 | 327784 | 45544 | 86.1 | 128 | 9.5 | 1.9 | 0 | 0 |
| throughput x4 | 64878 | 491676 | 68316 | 86.1 | 192 | 29.7 | 8.7 | 1 | 0 |
| throughput x16 | 86499 | 655568 | 91088 | 86.1 | 256 | 29.4 | 16.8 | 79 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
