# gemma-4-31b benchmark (quick, with chat)

## Provenance

- timestamp: 2026-10-05T05:11:30.929977+00:00
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
| cold | 256 | 1 | 2 | 91 | 91 |
| cold | 256 | 1 | 26 | 168 | 168 |
| cold | 256 | 16 | 2 | 270 | 270 |
| cold | 256 | 16 | 26 | 781 | 781 |
| cold | 2048 | 1 | 2 | 463 | 463 |
| cold | 2048 | 1 | 26 | 553 | 553 |
| cold | 2048 | 16 | 2 | 718 | 718 |
| cold | 2048 | 16 | 26 | 1287 | 1287 |
| warm | 2048 | 16 | 26 | 255 | 255 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 72.0 | 100.0 | n/a | 0.848 | 0.389 | 68 | 74 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.229 | 0.455 | n/a | n/a | 0 | 0 |

| chat prompt | load | TTFT ms | chunks/s |
|---|---|---|---|
| short | none | 63 | 17.7 |
| long | none | 88 | 20.3 |
| short | 4 systemone | 87 | 0.5 |
| long | 4 systemone | 4886 | 0.5 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 59224 | 301954 | 55330 | 81.7 | 204 | 13.9 | 2.8 | 0 | 0 |
| warm | 16839 | 117504 | 5920 | 95.0 | 48 | 13.5 | 3.4 | 0 | 0 |
| throughput x1 | 44997 | 314832 | 42512 | 86.5 | 128 | 13.9 | 6.1 | 0 | 0 |
| throughput x4 | 67499 | 472304 | 63888 | 86.5 | 192 | 33.7 | 26.7 | 31 | 0 |
| throughput x16 | 129372 | 905232 | 122352 | 86.5 | 368 | 37.2 | 31.4 | 220 | 0 |
| jevbench | 11846 | 11846 | 10118 | 14.6 | 50 | 0.0 | 0.0 | 0 | 0 |
| chat | 4972156 | 34788840 | 4700392 | 86.5 | 15535 | 34.9 | 26.5 | 44 | 0 |
