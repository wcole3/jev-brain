# ds005-qwen38-fp8 benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-09T08:29:56.138940+00:00
- repo commit: 98ba1fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: ds005-qwen38-fp8
- hf_model: Qwen/Qwen3.8-27B-FP8
- hf_revision: 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a
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
- KV cache: 1014 blocks × 800 tokens
- cache_dtype: bfloat16
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 800
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 98 | 100 |
| cold | 256 | 1 | 26 | 131 | 148 |
| cold | 256 | 1 | 255 | 913 | 961 |
| cold | 256 | 4 | 2 | 378 | 380 |
| cold | 256 | 4 | 26 | 380 | 401 |
| cold | 256 | 4 | 255 | 2105 | 2113 |
| cold | 256 | 16 | 2 | 444 | 468 |
| cold | 256 | 16 | 26 | 697 | 704 |
| cold | 256 | 16 | 255 | 4646 | 4668 |
| cold | 256 | 64 | 2 | 982 | 1001 |
| cold | 256 | 64 | 26 | 2091 | 2096 |
| cold | 256 | 64 | 255 | 15799 | 15924 |
| cold | 2048 | 1 | 2 | 378 | 412 |
| cold | 2048 | 1 | 26 | 467 | 484 |
| cold | 2048 | 1 | 255 | 1305 | 1344 |
| cold | 2048 | 4 | 2 | 638 | 661 |
| cold | 2048 | 4 | 26 | 660 | 673 |
| cold | 2048 | 4 | 255 | 3288 | 3315 |
| cold | 2048 | 16 | 2 | 722 | 793 |
| cold | 2048 | 16 | 26 | 1018 | 1050 |
| cold | 2048 | 16 | 255 | 6016 | 6035 |
| cold | 2048 | 64 | 2 | 1387 | 1394 |
| cold | 2048 | 64 | 26 | 2375 | 2496 |
| cold | 2048 | 64 | 255 | 17488 | 17896 |
| cold | 8192 | 1 | 2 | 1418 | 1429 |
| cold | 8192 | 1 | 26 | 1465 | 1480 |
| cold | 8192 | 1 | 255 | 2374 | 2384 |
| cold | 8192 | 4 | 2 | 1738 | 1767 |
| cold | 8192 | 4 | 26 | 1783 | 1788 |
| cold | 8192 | 4 | 255 | 7058 | 7105 |
| cold | 8192 | 16 | 2 | 1917 | 1964 |
| cold | 8192 | 16 | 26 | 2222 | 2234 |
| cold | 8192 | 16 | 255 | 10049 | 10089 |
| cold | 8192 | 64 | 2 | 2954 | 2964 |
| cold | 8192 | 64 | 26 | 3989 | 4010 |
| cold | 8192 | 64 | 255 | 22900 | 23138 |
| warm | 2048 | 16 | 26 | 641 | 654 |

| workers | requests/s |
|---|---|
| 1 | 1.0 |
| 4 | 1.3 |
| 16 | 1.3 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.4 | 92.8 | 90.2 | 0.913 | 0.159 | 93 | 222 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.027 | 0.156 | 35.2 | 42.7 | 54 | 7 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 110 | 92.0 |
| long | none | 128 | 70.2 |
| short | 4 systemone | 2587 | 17.2 |
| long | 4 systemone | 539 | 38.4 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990379 | 29558835 | 4735635 | 84.0 | 5148 | 60.5 | 6.2 | 60 | 0 |
| warm | 33462 | 250446 | 22446 | 91.0 | 96 | 16.0 | 6.2 | 2 | 0 |
| throughput x1 | 167657 | 1252230 | 172230 | 86.2 | 480 | 16.0 | 4.4 | 2 | 0 |
| throughput x4 | 229120 | 1711381 | 235381 | 86.2 | 656 | 17.5 | 10.2 | 27 | 0 |
| throughput x16 | 268247 | 2003568 | 275568 | 86.2 | 768 | 19.2 | 10.9 | 200 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 1.7 | 0.0 | 0 | 0 |
| chat | 44710 | 334178 | 46178 | 86.2 | 1216 | 14.0 | 2.1 | 8 | 0 |
