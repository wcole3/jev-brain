# qwen3.6-27b benchmark (quick, with chat)

## Provenance

- timestamp: 2026-10-05T01:24:08.567178+00:00
- repo commit: c37c95a
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
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
| cold | 256 | 1 | 2 | 218 | 218 |
| cold | 256 | 1 | 26 | 261 | 261 |
| cold | 256 | 16 | 2 | 1024 | 1024 |
| cold | 256 | 16 | 26 | 1098 | 1098 |
| cold | 2048 | 1 | 2 | 564 | 564 |
| cold | 2048 | 1 | 26 | 655 | 655 |
| cold | 2048 | 16 | 2 | 1205 | 1205 |
| cold | 2048 | 16 | 26 | 1281 | 1281 |
| warm | 2048 | 16 | 26 | 1078 | 1078 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 74.0 | 100.0 | n/a | 0.852 | 0.361 | 114 | 179 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.187 | 0.344 | n/a | n/a | 0 | 0 |

| chat prompt | load | TTFT ms | chunks/s |
|---|---|---|---|
| short | none | 104 | 25.7 |
| long | none | 141 | 26.5 |
| short | 4 systemone | 605 | 1.7 |
| long | 4 systemone | 1691 | 1.8 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 58700 | 343581 | 61341 | 82.1 | 204 | 9.6 | 0.5 | 0 | 0 |
| warm | 16731 | 122919 | 12375 | 89.9 | 48 | 9.0 | 1.9 | 0 | 0 |
| throughput x1 | 44708 | 327784 | 45544 | 86.1 | 128 | 9.6 | 1.7 | 0 | 0 |
| throughput x4 | 67050 | 491676 | 68316 | 86.1 | 192 | 30.0 | 9.2 | 1 | 0 |
| throughput x16 | 95004 | 696541 | 96781 | 86.1 | 272 | 29.7 | 16.4 | 80 | 0 |
| jevbench | 11249 | 11249 | 11249 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
| chat | 2397434 | 17577499 | 2442379 | 86.1 | 8420 | 30.7 | 8.6 | 16 | 0 |
