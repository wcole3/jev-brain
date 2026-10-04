# qwen3.6-27b benchmark (full, systemone only)

## Provenance

- timestamp: 2026-10-04T13:01:16.650695+00:00
- repo commit: 6204d00
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
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
- KV cache: 665 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 113 | 140 |
| cold | 256 | 1 | 26 | 178 | 180 |
| cold | 256 | 1 | 255 | 1054 | 1079 |
| cold | 256 | 4 | 2 | 457 | 525 |
| cold | 256 | 4 | 26 | 530 | 559 |
| cold | 256 | 4 | 255 | 2632 | 2705 |
| cold | 256 | 16 | 2 | 633 | 677 |
| cold | 256 | 16 | 26 | 949 | 985 |
| cold | 256 | 16 | 255 | 6477 | 7138 |
| cold | 256 | 64 | 2 | 1723 | 2005 |
| cold | 256 | 64 | 26 | 2861 | 2987 |
| cold | 256 | 64 | 255 | 23211 | 24243 |
| cold | 2048 | 1 | 2 | 924 | 1115 |
| cold | 2048 | 1 | 26 | 823 | 886 |
| cold | 2048 | 1 | 255 | 1586 | 1650 |
| cold | 2048 | 4 | 2 | 834 | 895 |
| cold | 2048 | 4 | 26 | 804 | 927 |
| cold | 2048 | 4 | 255 | 3218 | 3403 |
| cold | 2048 | 16 | 2 | 869 | 934 |
| cold | 2048 | 16 | 26 | 1468 | 1769 |
| cold | 2048 | 16 | 255 | 8723 | 8837 |
| cold | 2048 | 64 | 2 | 1785 | 1802 |
| cold | 2048 | 64 | 26 | 3419 | 3655 |
| cold | 2048 | 64 | 255 | 24013 | 24063 |
| cold | 8192 | 1 | 2 | 1619 | 1640 |
| cold | 8192 | 1 | 26 | 1778 | 1825 |
| cold | 8192 | 1 | 255 | 2702 | 2806 |
| cold | 8192 | 4 | 2 | 1961 | 1982 |
| cold | 8192 | 4 | 26 | 2072 | 2245 |
| cold | 8192 | 4 | 255 | 5685 | 5726 |
| cold | 8192 | 16 | 2 | 2172 | 2179 |
| cold | 8192 | 16 | 26 | 2736 | 2961 |
| cold | 8192 | 16 | 255 | 10099 | 10376 |
| cold | 8192 | 64 | 2 | 3436 | 3507 |
| cold | 8192 | 64 | 26 | 4952 | 5066 |
| cold | 8192 | 64 | 255 | 27772 | 27874 |
| warm | 2048 | 16 | 26 | 803 | 908 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 0.9 |
| 16 | 0.9 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.1 | 93.3 | 90.2 | 0.876 | 0.280 | 109 | 287 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.038 | 0.164 | 35.5 | 42.7 | 53 | 8 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990381 | 29091149 | 4367709 | 85.0 | 5148 | 41.0 | 6.4 | 62 | 0 |
| warm | 33462 | 245838 | 22398 | 90.9 | 96 | 9.3 | 2.5 | 0 | 0 |
| throughput x1 | 139709 | 1024325 | 142325 | 86.1 | 400 | 9.3 | 2.5 | 0 | 0 |
| throughput x4 | 173227 | 1270163 | 176483 | 86.1 | 496 | 29.2 | 8.8 | 1 | 0 |
| throughput x16 | 206782 | 1516001 | 210641 | 86.1 | 592 | 28.9 | 17.2 | 80 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 1.2 | 0.0 | 0 | 0 |
