# gemma-4-31b benchmark (quick, with chat)

## Provenance

- timestamp: 2026-10-05T06:50:13.943556+00:00
- repo commit: 66b8531
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
- KV cache: 9942 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 89 | 89 |
| cold | 256 | 1 | 26 | 167 | 167 |
| cold | 256 | 16 | 2 | 271 | 271 |
| cold | 256 | 16 | 26 | 796 | 796 |
| cold | 2048 | 1 | 2 | 508 | 508 |
| cold | 2048 | 1 | 26 | 585 | 585 |
| cold | 2048 | 16 | 2 | 966 | 966 |
| cold | 2048 | 16 | 26 | 1259 | 1259 |
| warm | 2048 | 16 | 26 | 243 | 243 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.7 |
| 16 | 0.7 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 72.0 | 100.0 | n/a | 0.848 | 0.389 | 68 | 72 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.239 | 0.455 | n/a | n/a | 0 | 0 |

| chat prompt | load | TTFT ms | chunks/s |
|---|---|---|---|
| short | none | 64 | 16.1 |
| long | none | 86 | 19.6 |
| short | 4 systemone | 77 | 0.6 |
| long | 4 systemone | 2184 | 0.7 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 59229 | 301959 | 57607 | 80.9 | 204 | 21.2 | 6.9 | 0 | 0 |
| warm | 16839 | 117504 | 5952 | 94.9 | 48 | 17.6 | 6.6 | 0 | 0 |
| throughput x1 | 44997 | 314832 | 46736 | 85.2 | 128 | 21.3 | 12.5 | 0 | 0 |
| throughput x4 | 50621 | 354176 | 56544 | 84.0 | 144 | 43.8 | 31.3 | 32 | 0 |
| throughput x16 | 112486 | 786976 | 125792 | 84.0 | 320 | 52.4 | 44.1 | 217 | 0 |
| jevbench | 11846 | 11846 | 10118 | 14.6 | 50 | 0.0 | 0.0 | 0 | 0 |
| chat | 2767304 | 19362088 | 3162760 | 83.7 | 9169 | 50.1 | 37.7 | 16 | 0 |
