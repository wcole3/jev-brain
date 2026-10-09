# ds005-gemma-fp8-kvfp8h benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-08T23:28:22.789617+00:00
- repo commit: 98ba1fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: ds005-gemma-fp8-kvfp8h
- hf_model: RedHatAI/gemma-4-31B-it-FP8-block
- hf_revision: d7242548c457ab4b45bd3adb8937f2659af4739d
- prompt_layout: header
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: off
- prefix_block: 0
- prefix_pad_always: False
- warm_min_prefix_tokens: 512
- warm_up: off
- systemone_priority: 0
- governor_duty: 0.5
- governor_wave: 8
- KV cache: 41423 blocks × 16 tokens
- cache_dtype: fp8_per_token_head
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 65 | 71 |
| cold | 256 | 1 | 26 | 119 | 121 |
| cold | 256 | 1 | 255 | 1020 | 1022 |
| cold | 256 | 4 | 2 | 108 | 109 |
| cold | 256 | 4 | 26 | 226 | 227 |
| cold | 256 | 4 | 255 | 1909 | 1920 |
| cold | 256 | 16 | 2 | 181 | 185 |
| cold | 256 | 16 | 26 | 545 | 562 |
| cold | 256 | 16 | 255 | 5613 | 5650 |
| cold | 256 | 64 | 2 | 579 | 590 |
| cold | 256 | 64 | 26 | 2062 | 2079 |
| cold | 256 | 64 | 255 | 21768 | 21823 |
| cold | 2048 | 1 | 2 | 390 | 393 |
| cold | 2048 | 1 | 26 | 462 | 462 |
| cold | 2048 | 1 | 255 | 1495 | 1498 |
| cold | 2048 | 4 | 2 | 445 | 619 |
| cold | 2048 | 4 | 26 | 568 | 749 |
| cold | 2048 | 4 | 255 | 2560 | 2747 |
| cold | 2048 | 16 | 2 | 577 | 742 |
| cold | 2048 | 16 | 26 | 978 | 1153 |
| cold | 2048 | 16 | 255 | 6803 | 6983 |
| cold | 2048 | 64 | 2 | 1131 | 1316 |
| cold | 2048 | 64 | 26 | 2720 | 2922 |
| cold | 2048 | 64 | 255 | 25251 | 25381 |
| cold | 8192 | 1 | 2 | 1778 | 1779 |
| cold | 8192 | 1 | 26 | 1879 | 1880 |
| cold | 8192 | 1 | 255 | 3213 | 3237 |
| cold | 8192 | 4 | 2 | 5176 | 5568 |
| cold | 8192 | 4 | 26 | 5348 | 5711 |
| cold | 8192 | 4 | 255 | 5930 | 6121 |
| cold | 8192 | 16 | 2 | 6890 | 7177 |
| cold | 8192 | 16 | 26 | 7496 | 7678 |
| cold | 8192 | 16 | 255 | 14984 | 15089 |
| cold | 8192 | 64 | 2 | 7625 | 7664 |
| cold | 8192 | 64 | 26 | 9996 | 10168 |
| cold | 8192 | 64 | 255 | 40355 | 40495 |
| warm | 2048 | 16 | 26 | 189 | 198 |

| workers | requests/s |
|---|---|
| 1 | 1.0 |
| 4 | 0.9 |
| 16 | 0.9 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.4 | 91.1 | 92.0 | 0.934 | 0.222 | 43 | 207 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.101 | 0.202 | 48.8 | 42.7 | 6 | 44 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 121 | 42.1 |
| long | none | 126 | 41.3 |
| short | 4 systemone | 7855 | 14.3 |
| long | 4 systemone | 2891 | 27.0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 4001961 | 26954375 | 4994727 | 81.5 | 5148 | 36.0 | 14.5 | 51 | 0 |
| warm | 33678 | 235008 | 6288 | 97.3 | 96 | 4.6 | 1.5 | 0 | 0 |
| throughput x1 | 168745 | 1180720 | 164048 | 86.1 | 480 | 5.5 | 3.0 | 0 | 0 |
| throughput x4 | 157501 | 1102096 | 175312 | 84.1 | 448 | 11.7 | 8.7 | 32 | 0 |
| throughput x16 | 230607 | 1613472 | 251328 | 84.4 | 656 | 13.7 | 12.1 | 206 | 0 |
| jevbench | 606246 | 606246 | 528918 | 12.8 | 1682 | 1.1 | 0.0 | 0 | 0 |
| chat | 84374 | 590488 | 93384 | 84.2 | 1574 | 11.5 | 2.2 | 8 | 0 |
