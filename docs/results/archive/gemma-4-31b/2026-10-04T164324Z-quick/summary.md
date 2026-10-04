# gemma-4-31b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-10-04T16:43:24.607786+00:00
- repo commit: fd72395
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 50
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: off
- prefix_block: 0
- prefix_pad_always: False
- warm_min_prefix_tokens: 512
- warm_up: off
- KV cache: 9927 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 92 | 92 |
| cold | 256 | 1 | 26 | 176 | 176 |
| cold | 256 | 16 | 2 | 282 | 282 |
| cold | 256 | 16 | 26 | 821 | 821 |
| cold | 2048 | 1 | 2 | 478 | 478 |
| cold | 2048 | 1 | 26 | 567 | 567 |
| cold | 2048 | 16 | 2 | 747 | 747 |
| cold | 2048 | 16 | 26 | 1410 | 1410 |
| warm | 2048 | 16 | 26 | 316 | 316 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 72.0 | 100.0 | n/a | 0.848 | 0.389 | 73 | 87 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.226 | 0.457 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 59222 | 301937 | 55345 | 81.7 | 204 | 13.9 | 3.1 | 0 | 0 |
| warm | 16839 | 117504 | 5920 | 95.0 | 48 | 13.8 | 5.2 | 0 | 0 |
| throughput x1 | 44999 | 314864 | 42544 | 86.5 | 128 | 13.9 | 6.3 | 0 | 0 |
| throughput x4 | 61869 | 432864 | 58624 | 86.5 | 176 | 33.9 | 25.5 | 31 | 0 |
| throughput x16 | 129366 | 905136 | 122352 | 86.5 | 368 | 38.7 | 31.8 | 220 | 0 |
| jevbench | 11846 | 11846 | 10118 | 14.6 | 50 | 0.0 | 0.0 | 0 | 0 |
