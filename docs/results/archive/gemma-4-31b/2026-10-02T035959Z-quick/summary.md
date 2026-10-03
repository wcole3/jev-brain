# gemma-4-31b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-10-02T03:59:59.023847+00:00
- repo commit: 7a5d9b6
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.84, PCIe 4x16, AMD Ryzen Threadripper 3960X 24-Core Processor (48 thr), 189 GB, vast 53799016
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 50
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: decider_chat
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: off
- prefix_block: 0
- prefix_pad_always: False
- warm_min_prefix_tokens: 512
- warm_up: off
- KV cache: 9717 blocks × 16 tokens
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
| cold | 256 | 16 | 2 | 286 | 286 |
| cold | 256 | 16 | 26 | 788 | 788 |
| cold | 2048 | 1 | 2 | 470 | 470 |
| cold | 2048 | 1 | 26 | 563 | 563 |
| cold | 2048 | 16 | 2 | 758 | 758 |
| cold | 2048 | 16 | 26 | 1318 | 1318 |
| warm | 2048 | 16 | 26 | 206 | 206 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 78.0 | 100.0 | n/a | 0.870 | 0.306 | 64 | 70 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.211 | 0.416 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56763 | 266718 | 56286 | 78.9 | 204 | 14.8 | 3.8 | 0 | 0 |
| warm | 16293 | 108768 | 5536 | 94.9 | 48 | 14.2 | 3.5 | 0 | 0 |
| throughput x1 | 43535 | 291440 | 43632 | 85.0 | 128 | 14.8 | 5.0 | 0 | 0 |
| throughput x4 | 54431 | 364496 | 54672 | 85.0 | 160 | 35.0 | 25.5 | 32 | 0 |
| throughput x16 | 125173 | 838048 | 125600 | 85.0 | 368 | 35.4 | 30.6 | 220 | 0 |
| jevbench | 10698 | 10698 | 8906 | 16.8 | 50 | 0.0 | 0.0 | 0 | 0 |
