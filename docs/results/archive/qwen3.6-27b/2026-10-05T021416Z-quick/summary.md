# qwen3.6-27b benchmark (quick, with chat)

## Provenance

- timestamp: 2026-10-05T02:14:16.539668+00:00
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
| cold | 256 | 1 | 2 | 140 | 140 |
| cold | 256 | 1 | 26 | 242 | 242 |
| cold | 256 | 16 | 2 | 621 | 621 |
| cold | 256 | 16 | 26 | 888 | 888 |
| cold | 2048 | 1 | 2 | 447 | 447 |
| cold | 2048 | 1 | 26 | 511 | 511 |
| cold | 2048 | 16 | 2 | 848 | 848 |
| cold | 2048 | 16 | 26 | 1121 | 1121 |
| warm | 2048 | 16 | 26 | 752 | 752 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 1.1 |
| 16 | 1.1 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 74.0 | 100.0 | n/a | 0.852 | 0.361 | 131 | 203 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.187 | 0.341 | n/a | n/a | 0 | 0 |

| chat prompt | load | TTFT ms | chunks/s |
|---|---|---|---|
| short | none | 142 | 25.9 |
| long | none | 127 | 26.1 |
| short | 4 systemone | 607 | 1.8 |
| long | 4 systemone | 1443 | 1.7 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 58703 | 343583 | 61343 | 82.1 | 204 | 9.6 | 1.1 | 0 | 0 |
| warm | 16731 | 122919 | 12375 | 89.9 | 48 | 9.6 | 3.5 | 0 | 0 |
| throughput x1 | 50293 | 368757 | 51237 | 86.1 | 144 | 9.6 | 2.2 | 0 | 0 |
| throughput x4 | 67057 | 491676 | 68316 | 86.1 | 192 | 30.0 | 8.9 | 1 | 0 |
| throughput x16 | 111774 | 819460 | 113860 | 86.1 | 320 | 31.0 | 16.4 | 80 | 0 |
| jevbench | 11249 | 11249 | 11249 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
| chat | 2749536 | 20158798 | 2801038 | 86.1 | 9696 | 30.7 | 8.8 | 16 | 0 |
