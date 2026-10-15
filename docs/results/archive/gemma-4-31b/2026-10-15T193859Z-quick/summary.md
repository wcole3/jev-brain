# gemma-4-31b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-10-15T19:38:59.347686+00:00
- repo commit: 545e91f-dirty
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
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
- warm_min_prefix_tokens: 4096
- warm_up: prefix
- systemone_priority: 0
- governor_duty: 0.5
- governor_wave: 8
- KV cache: 9943 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 92 | 92 |
| cold | 256 | 1 | 26 | 168 | 168 |
| cold | 256 | 16 | 2 | 278 | 278 |
| cold | 256 | 16 | 26 | 752 | 752 |
| cold | 2048 | 1 | 2 | 492 | 492 |
| cold | 2048 | 1 | 26 | 567 | 567 |
| cold | 2048 | 16 | 2 | 941 | 941 |
| cold | 2048 | 16 | 26 | 1434 | 1434 |
| warm | 2048 | 16 | 26 | 261 | 261 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 0.7 |
| 16 | 0.7 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 72.0 | 100.0 | n/a | 0.848 | 0.389 | 76 | 83 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.225 | 0.454 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 59233 | 302008 | 58776 | 80.5 | 204 | 21.1 | 5.7 | 0 | 0 |
| warm | 16839 | 117504 | 6976 | 94.1 | 48 | 21.2 | 9.0 | 0 | 0 |
| throughput x1 | 44994 | 314784 | 46848 | 85.1 | 128 | 21.3 | 11.3 | 0 | 0 |
| throughput x4 | 50627 | 354272 | 57664 | 83.7 | 144 | 43.9 | 30.7 | 32 | 0 |
| throughput x16 | 112492 | 787072 | 126848 | 83.9 | 320 | 52.2 | 43.8 | 217 | 0 |
| jevbench | 11846 | 11846 | 10118 | 14.6 | 50 | 0.0 | 0.0 | 0 | 0 |
