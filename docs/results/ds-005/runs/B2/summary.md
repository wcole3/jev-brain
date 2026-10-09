# ds005-qwen38-nvfp4 benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-09T08:56:16.481116+00:00
- repo commit: 98ba1fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: ds005-qwen38-nvfp4
- hf_model: RadixArk/Qwen3.8-27B-NVFP4
- hf_revision: 319f741cce68d7914884900c138a1fbb70a42f30
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
- KV cache: 1162 blocks × 800 tokens
- cache_dtype: bfloat16
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 800
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 95 | 102 |
| cold | 256 | 1 | 26 | 247 | 264 |
| cold | 256 | 1 | 255 | 1613 | 1732 |
| cold | 256 | 4 | 2 | 497 | 524 |
| cold | 256 | 4 | 26 | 524 | 588 |
| cold | 256 | 4 | 255 | 3705 | 3860 |
| cold | 256 | 16 | 2 | 675 | 688 |
| cold | 256 | 16 | 26 | 915 | 973 |
| cold | 256 | 16 | 255 | 5591 | 5654 |
| cold | 256 | 64 | 2 | 1311 | 1323 |
| cold | 256 | 64 | 26 | 2058 | 2326 |
| cold | 256 | 64 | 255 | 15090 | 15353 |
| cold | 2048 | 1 | 2 | 718 | 753 |
| cold | 2048 | 1 | 26 | 817 | 843 |
| cold | 2048 | 1 | 255 | 2386 | 2491 |
| cold | 2048 | 4 | 2 | 982 | 1006 |
| cold | 2048 | 4 | 26 | 1050 | 1095 |
| cold | 2048 | 4 | 255 | 4899 | 4919 |
| cold | 2048 | 16 | 2 | 1206 | 1220 |
| cold | 2048 | 16 | 26 | 1432 | 1513 |
| cold | 2048 | 16 | 255 | 6892 | 6972 |
| cold | 2048 | 64 | 2 | 1895 | 1900 |
| cold | 2048 | 64 | 26 | 2688 | 2886 |
| cold | 2048 | 64 | 255 | 16534 | 17012 |
| cold | 8192 | 1 | 2 | 2466 | 2483 |
| cold | 8192 | 1 | 26 | 2610 | 2677 |
| cold | 8192 | 1 | 255 | 3987 | 4033 |
| cold | 8192 | 4 | 2 | 2914 | 2931 |
| cold | 8192 | 4 | 26 | 2907 | 2962 |
| cold | 8192 | 4 | 255 | 8797 | 8956 |
| cold | 8192 | 16 | 2 | 3171 | 3235 |
| cold | 8192 | 16 | 26 | 3415 | 3455 |
| cold | 8192 | 16 | 255 | 11023 | 11161 |
| cold | 8192 | 64 | 2 | 4249 | 4273 |
| cold | 8192 | 64 | 26 | 4899 | 5164 |
| cold | 8192 | 64 | 255 | 21643 | 21868 |
| warm | 2048 | 16 | 26 | 746 | 762 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 1.3 |
| 16 | 1.4 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 90.2 | 93.3 | 91.7 | 0.905 | 0.159 | 93 | 343 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.036 | 0.154 | 38.2 | 42.7 | 40 | 12 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 119 | 131.3 |
| long | none | 99 | 90.1 |
| short | 4 systemone | 2983 | 17.7 |
| long | 4 systemone | 748 | 43.9 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990385 | 29558853 | 4738053 | 84.0 | 5148 | 52.8 | 4.2 | 60 | 0 |
| warm | 33462 | 250446 | 22446 | 91.0 | 96 | 14.0 | 3.3 | 2 | 0 |
| throughput x1 | 117355 | 876561 | 120561 | 86.2 | 336 | 14.0 | 2.6 | 2 | 0 |
| throughput x4 | 223540 | 1669640 | 229640 | 86.2 | 640 | 15.2 | 8.0 | 27 | 0 |
| throughput x16 | 296186 | 2212273 | 304273 | 86.2 | 848 | 16.7 | 9.3 | 200 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 1.5 | 0.0 | 0 | 0 |
| chat | 44706 | 334178 | 46178 | 86.2 | 1224 | 14.0 | 1.6 | 6 | 0 |
