# qwen3.6-27b benchmark (quick, with chat)

## Provenance

- timestamp: 2026-10-05T06:32:59.729227+00:00
- repo commit: 6de9f1d
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
- systemone_priority: 1
- KV cache: 650 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 88 | 88 |
| cold | 256 | 1 | 26 | 165 | 165 |
| cold | 256 | 16 | 2 | 474 | 474 |
| cold | 256 | 16 | 26 | 829 | 829 |
| cold | 2048 | 1 | 2 | 449 | 449 |
| cold | 2048 | 1 | 26 | 575 | 575 |
| cold | 2048 | 16 | 2 | 834 | 834 |
| cold | 2048 | 16 | 26 | 1213 | 1213 |
| warm | 2048 | 16 | 26 | 726 | 726 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 74.0 | 100.0 | n/a | 0.852 | 0.361 | 87 | 108 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.167 | 0.343 | n/a | n/a | 0 | 0 |

| chat prompt | load | TTFT ms | chunks/s |
|---|---|---|---|
| short | none | 89 | 27.5 |
| long | none | 109 | 27.6 |
| short | 4 systemone | 226 | 2.9 |
| long | 4 systemone | 1170 | 3.0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 58703 | 343583 | 61343 | 82.1 | 204 | 9.6 | 2.1 | 2 | 0 |
| warm | 16731 | 122919 | 12375 | 89.9 | 48 | 8.3 | 3.0 | 2 | 0 |
| throughput x1 | 50297 | 368757 | 51237 | 86.1 | 144 | 8.3 | 2.7 | 2 | 0 |
| throughput x4 | 67064 | 491676 | 68316 | 86.1 | 192 | 10.6 | 5.8 | 27 | 0 |
| throughput x16 | 111767 | 819460 | 113860 | 86.1 | 320 | 9.9 | 6.4 | 200 | 0 |
| jevbench | 11249 | 11249 | 11249 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
| chat | 1542420 | 11308630 | 1571350 | 86.1 | 6074 | 10.5 | 6.1 | 24 | 0 |
