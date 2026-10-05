# qwen3.6-27b benchmark (quick, with chat)

## Provenance

- timestamp: 2026-10-05T04:04:09.288450+00:00
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
- KV cache: 651 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 92 | 92 |
| cold | 256 | 1 | 26 | 167 | 167 |
| cold | 256 | 16 | 2 | 479 | 479 |
| cold | 256 | 16 | 26 | 818 | 818 |
| cold | 2048 | 1 | 2 | 407 | 407 |
| cold | 2048 | 1 | 26 | 550 | 550 |
| cold | 2048 | 16 | 2 | 794 | 794 |
| cold | 2048 | 16 | 26 | 1140 | 1140 |
| warm | 2048 | 16 | 26 | 701 | 701 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 74.0 | 100.0 | n/a | 0.852 | 0.361 | 88 | 124 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.187 | 0.344 | n/a | n/a | 0 | 0 |

| chat prompt | load | TTFT ms | chunks/s |
|---|---|---|---|
| short | none | 103 | 27.4 |
| long | none | 96 | 27.5 |
| short | 4 systemone | 276 | 2.2 |
| long | 4 systemone | 1283 | 2.3 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 58701 | 343582 | 61342 | 82.1 | 204 | 9.5 | 1.6 | 0 | 0 |
| warm | 16731 | 122919 | 12375 | 89.9 | 48 | 9.5 | 2.7 | 0 | 0 |
| throughput x1 | 50298 | 368757 | 51237 | 86.1 | 144 | 9.5 | 2.7 | 0 | 0 |
| throughput x4 | 67062 | 491676 | 68316 | 86.1 | 192 | 11.5 | 6.9 | 16 | 0 |
| throughput x16 | 106174 | 778487 | 108167 | 86.1 | 304 | 12.3 | 7.1 | 181 | 0 |
| jevbench | 11249 | 11249 | 11249 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
| chat | 2140403 | 15692741 | 2180501 | 86.1 | 8007 | 12.2 | 7.0 | 16 | 0 |
