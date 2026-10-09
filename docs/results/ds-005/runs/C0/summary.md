# ds005-qwen36-bf16 benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-09T10:33:08.854169+00:00
- repo commit: 98ba1fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: ds005-qwen36-bf16
- hf_model: Qwen/Qwen3.6-27B
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: header
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: front
- prefix_block: 800
- prefix_pad_always: False
- warm_min_prefix_tokens: 800
- warm_up: row
- systemone_priority: 1
- governor_duty: 0.6
- governor_wave: 8
- KV cache: 571 blocks × 800 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 800
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 104 | 110 |
| cold | 256 | 1 | 26 | 180 | 182 |
| cold | 256 | 1 | 255 | 1318 | 1395 |
| cold | 256 | 4 | 2 | 436 | 460 |
| cold | 256 | 4 | 26 | 496 | 530 |
| cold | 256 | 4 | 255 | 2946 | 2962 |
| cold | 256 | 16 | 2 | 549 | 560 |
| cold | 256 | 16 | 26 | 952 | 973 |
| cold | 256 | 16 | 255 | 6800 | 6961 |
| cold | 256 | 64 | 2 | 1369 | 1392 |
| cold | 256 | 64 | 26 | 3002 | 3051 |
| cold | 256 | 64 | 255 | 24226 | 24522 |
| cold | 2048 | 1 | 2 | 538 | 541 |
| cold | 2048 | 1 | 26 | 667 | 673 |
| cold | 2048 | 1 | 255 | 1874 | 1881 |
| cold | 2048 | 4 | 2 | 838 | 841 |
| cold | 2048 | 4 | 26 | 918 | 927 |
| cold | 2048 | 4 | 255 | 4739 | 4781 |
| cold | 2048 | 16 | 2 | 985 | 1010 |
| cold | 2048 | 16 | 26 | 1401 | 1437 |
| cold | 2048 | 16 | 255 | 8855 | 8881 |
| cold | 2048 | 64 | 2 | 1887 | 1903 |
| cold | 2048 | 64 | 26 | 3558 | 3608 |
| cold | 2048 | 64 | 255 | 26377 | 26487 |
| cold | 8192 | 1 | 2 | 2080 | 2082 |
| cold | 8192 | 1 | 26 | 2177 | 2208 |
| cold | 8192 | 1 | 255 | 3467 | 3518 |
| cold | 8192 | 4 | 2 | 2480 | 2518 |
| cold | 8192 | 4 | 26 | 2566 | 2592 |
| cold | 8192 | 4 | 255 | 10393 | 10452 |
| cold | 8192 | 16 | 2 | 2700 | 2730 |
| cold | 8192 | 16 | 26 | 3167 | 3223 |
| cold | 8192 | 16 | 255 | 14832 | 14839 |
| cold | 8192 | 64 | 2 | 3889 | 3946 |
| cold | 8192 | 64 | 26 | 5514 | 5555 |
| cold | 8192 | 64 | 255 | 33599 | 33657 |
| warm | 2048 | 16 | 26 | 844 | 878 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.9 |
| 16 | 0.9 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.2 | 93.3 | 90.4 | 0.876 | 0.280 | 107 | 289 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.040 | 0.166 | 35.7 | 42.7 | 52 | 8 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 114 | 75.2 |
| long | none | 138 | 60.7 |
| short | 4 systemone | 2643 | 32.1 |
| long | 4 systemone | 455 | 38.9 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990389 | 29558853 | 4767653 | 83.9 | 5148 | 97.0 | 11.2 | 61 | 0 |
| warm | 33462 | 250446 | 22446 | 91.0 | 96 | 28.4 | 12.1 | 2 | 0 |
| throughput x1 | 122948 | 918302 | 126302 | 86.2 | 352 | 28.4 | 8.9 | 2 | 0 |
| throughput x4 | 156468 | 1168748 | 160748 | 86.2 | 448 | 31.1 | 17.7 | 27 | 0 |
| throughput x16 | 195592 | 1460935 | 200935 | 86.2 | 560 | 34.0 | 18.8 | 200 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 3.0 | 0.0 | 0 | 0 |
| chat | 67061 | 500974 | 68974 | 86.2 | 1751 | 30.7 | 5.2 | 20 | 0 |
