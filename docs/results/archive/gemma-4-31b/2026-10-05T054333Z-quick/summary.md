# gemma-4-31b benchmark (quick, with chat)

## Provenance

- timestamp: 2026-10-05T05:43:33.617768+00:00
- repo commit: d102ce2
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
- systemone_priority: 0
- KV cache: 9947 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 90 | 90 |
| cold | 256 | 1 | 26 | 169 | 169 |
| cold | 256 | 16 | 2 | 265 | 265 |
| cold | 256 | 16 | 26 | 787 | 787 |
| cold | 2048 | 1 | 2 | 467 | 467 |
| cold | 2048 | 1 | 26 | 552 | 552 |
| cold | 2048 | 16 | 2 | 723 | 723 |
| cold | 2048 | 16 | 26 | 1303 | 1303 |
| warm | 2048 | 16 | 26 | 266 | 266 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 74.0 | 100.0 | n/a | 0.855 | 0.361 | 69 | 72 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.228 | 0.449 | n/a | n/a | 0 | 0 |

| chat prompt | load | TTFT ms | chunks/s |
|---|---|---|---|
| short | none | 63 | 15.7 |
| long | none | 88 | 19.9 |
| short | 4 systemone | 110 | 0.5 |
| long | 4 systemone | 4220 | 0.6 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 59217 | 301827 | 55299 | 81.7 | 204 | 19.4 | 3.3 | 0 | 0 |
| warm | 16839 | 117504 | 5920 | 95.0 | 48 | 13.7 | 3.4 | 0 | 0 |
| throughput x1 | 44995 | 314800 | 42544 | 86.5 | 128 | 19.4 | 6.5 | 0 | 0 |
| throughput x4 | 67497 | 472272 | 63856 | 86.5 | 192 | 41.0 | 28.7 | 31 | 0 |
| throughput x16 | 123742 | 865792 | 116896 | 86.5 | 352 | 46.6 | 35.2 | 204 | 0 |
| jevbench | 11846 | 11846 | 10118 | 14.6 | 50 | 0.0 | 0.0 | 0 | 0 |
| chat | 4094736 | 28649960 | 3870280 | 86.5 | 12950 | 48.8 | 28.8 | 44 | 0 |
