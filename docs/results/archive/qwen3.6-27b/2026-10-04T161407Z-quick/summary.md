# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-10-04T16:14:07.655250+00:00
- repo commit: fd72395
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 50
- profile: qwen3.6-27b
- hf_model: Qwen/Qwen3.6-27B
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: header
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: front
- prefix_block: 784
- prefix_pad_always: False
- warm_min_prefix_tokens: 784
- warm_up: row
- KV cache: 647 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 94 | 94 |
| cold | 256 | 1 | 26 | 167 | 167 |
| cold | 256 | 16 | 2 | 488 | 488 |
| cold | 256 | 16 | 26 | 804 | 804 |
| cold | 2048 | 1 | 2 | 429 | 429 |
| cold | 2048 | 1 | 26 | 484 | 484 |
| cold | 2048 | 16 | 2 | 751 | 751 |
| cold | 2048 | 16 | 26 | 1133 | 1133 |
| warm | 2048 | 16 | 26 | 709 | 709 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 74.0 | 100.0 | n/a | 0.852 | 0.361 | 86 | 103 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.169 | 0.343 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 58699 | 343582 | 61342 | 82.1 | 204 | 9.6 | 1.2 | 0 | 0 |
| warm | 16731 | 122919 | 12375 | 89.9 | 48 | 9.6 | 2.5 | 0 | 0 |
| throughput x1 | 50298 | 368757 | 51237 | 86.1 | 144 | 9.6 | 2.4 | 0 | 0 |
| throughput x4 | 67060 | 491676 | 68316 | 86.1 | 192 | 30.0 | 9.4 | 1 | 0 |
| throughput x16 | 95005 | 696541 | 96781 | 86.1 | 272 | 29.7 | 16.6 | 80 | 0 |
| jevbench | 11249 | 11249 | 11249 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
