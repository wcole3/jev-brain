# gemma-4-31b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-10-15T19:09:57.138556+00:00
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
- warm_min_prefix_tokens: 1024
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
| cold | 256 | 1 | 2 | 100 | 100 |
| cold | 256 | 1 | 26 | 163 | 163 |
| cold | 256 | 16 | 2 | 261 | 261 |
| cold | 256 | 16 | 26 | 737 | 737 |
| cold | 2048 | 1 | 2 | 494 | 494 |
| cold | 2048 | 1 | 26 | 571 | 571 |
| cold | 2048 | 16 | 2 | 797 | 797 |
| cold | 2048 | 16 | 26 | 1314 | 1314 |
| warm | 2048 | 16 | 26 | 321 | 321 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 0.9 |
| 16 | 0.6 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 72.0 | 100.0 | n/a | 0.848 | 0.389 | 71 | 77 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.229 | 0.456 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 59218 | 315431 | 55559 | 82.4 | 210 | 13.8 | 4.0 | 0 | 0 |
| warm | 16839 | 124215 | 6007 | 95.2 | 51 | 11.5 | 1.4 | 0 | 0 |
| throughput x1 | 44999 | 332855 | 42615 | 87.2 | 136 | 13.9 | 6.8 | 0 | 0 |
| throughput x4 | 67502 | 499342 | 64014 | 87.2 | 204 | 41.0 | 22.1 | 7 | 0 |
| throughput x16 | 89999 | 665727 | 135487 | 79.6 | 272 | 82.2 | 48.7 | 152 | 2 |
| jevbench | 11846 | 11846 | 10118 | 14.6 | 50 | 0.0 | 0.0 | 0 | 0 |
