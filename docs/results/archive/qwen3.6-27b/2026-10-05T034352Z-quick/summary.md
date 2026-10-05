# qwen3.6-27b benchmark (quick, with chat)

## Provenance

- timestamp: 2026-10-05T03:43:52.495532+00:00
- repo commit: ee88d8f
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
- systemone_priority: 0
- KV cache: 647 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 93 | 93 |
| cold | 256 | 1 | 26 | 168 | 168 |
| cold | 256 | 16 | 2 | 464 | 464 |
| cold | 256 | 16 | 26 | 822 | 822 |
| cold | 2048 | 1 | 2 | 448 | 448 |
| cold | 2048 | 1 | 26 | 561 | 561 |
| cold | 2048 | 16 | 2 | 819 | 819 |
| cold | 2048 | 16 | 26 | 1182 | 1182 |
| warm | 2048 | 16 | 26 | 712 | 712 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 74.0 | 100.0 | n/a | 0.852 | 0.361 | 85 | 110 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.187 | 0.341 | n/a | n/a | 0 | 0 |

| chat prompt | load | TTFT ms | chunks/s |
|---|---|---|---|
| short | none | 96 | 27.2 |
| long | none | 115 | 27.2 |
| short | 4 systemone | 317 | 2.2 |
| long | 4 systemone | 1375 | 2.2 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 58700 | 343584 | 61344 | 82.1 | 204 | 9.6 | 1.5 | 0 | 0 |
| warm | 16731 | 122919 | 12375 | 89.9 | 48 | 9.6 | 3.7 | 0 | 0 |
| throughput x1 | 50295 | 368757 | 51237 | 86.1 | 144 | 9.6 | 2.6 | 0 | 0 |
| throughput x4 | 67056 | 491676 | 68316 | 86.1 | 192 | 30.0 | 9.9 | 1 | 0 |
| throughput x16 | 100587 | 737514 | 102474 | 86.1 | 288 | 30.0 | 18.8 | 109 | 0 |
| jevbench | 11249 | 11249 | 11249 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
| chat | 2034142 | 14914254 | 2072334 | 86.1 | 7434 | 30.7 | 10.3 | 16 | 0 |
