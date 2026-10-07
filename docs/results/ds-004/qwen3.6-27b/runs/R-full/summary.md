# qwen3.6-27b benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-07T01:27:04.977204+00:00
- repo commit: b88d7e8-dirty
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
| cold | 256 | 1 | 2 | 113 | 121 |
| cold | 256 | 1 | 26 | 172 | 184 |
| cold | 256 | 1 | 255 | 1229 | 1249 |
| cold | 256 | 4 | 2 | 813 | 849 |
| cold | 256 | 4 | 26 | 825 | 854 |
| cold | 256 | 4 | 255 | 3151 | 3232 |
| cold | 256 | 16 | 2 | 2021 | 2044 |
| cold | 256 | 16 | 26 | 2326 | 2389 |
| cold | 256 | 16 | 255 | 7901 | 7911 |
| cold | 256 | 64 | 2 | 7180 | 8026 |
| cold | 256 | 64 | 26 | 8779 | 9220 |
| cold | 256 | 64 | 255 | 27580 | 27641 |
| cold | 2048 | 1 | 2 | 510 | 545 |
| cold | 2048 | 1 | 26 | 639 | 657 |
| cold | 2048 | 1 | 255 | 1731 | 1733 |
| cold | 2048 | 4 | 2 | 1492 | 1949 |
| cold | 2048 | 4 | 26 | 1553 | 1791 |
| cold | 2048 | 4 | 255 | 3859 | 3888 |
| cold | 2048 | 16 | 2 | 2913 | 3186 |
| cold | 2048 | 16 | 26 | 3003 | 3458 |
| cold | 2048 | 16 | 255 | 8875 | 9088 |
| cold | 2048 | 64 | 2 | 9635 | 9725 |
| cold | 2048 | 64 | 26 | 11731 | 11998 |
| cold | 2048 | 64 | 255 | 31697 | 31728 |
| cold | 8192 | 1 | 2 | 1899 | 1910 |
| cold | 8192 | 1 | 26 | 1984 | 1996 |
| cold | 8192 | 1 | 255 | 3213 | 3225 |
| cold | 8192 | 4 | 2 | 2432 | 2469 |
| cold | 8192 | 4 | 26 | 6907 | 7171 |
| cold | 8192 | 4 | 255 | 9404 | 9491 |
| cold | 8192 | 16 | 2 | 3995 | 4076 |
| cold | 8192 | 16 | 26 | 8880 | 8951 |
| cold | 8192 | 16 | 255 | 15212 | 15262 |
| cold | 8192 | 64 | 2 | 10508 | 10588 |
| cold | 8192 | 64 | 26 | 16442 | 16857 |
| cold | 8192 | 64 | 255 | 39444 | 39460 |
| warm | 2048 | 16 | 26 | 1328 | 1438 |

| workers | requests/s |
|---|---|
| 1 | 0.3 |
| 4 | 0.3 |
| 16 | 0.4 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.2 | 93.3 | 90.2 | 0.889 | 0.266 | 132 | 318 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.035 | 0.164 | 35.5 | 42.7 | 53 | 8 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 136 | 73.1 |
| long | none | 144 | 62.9 |
| short | 4 systemone | 3323 | 35.2 |
| long | 4 systemone | 687 | 38.5 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990371 | 29091151 | 7913551 | 72.8 | 5148 | 81.2 | 9.4 | 62 | 0 |
| warm | 33462 | 245838 | 48238 | 80.4 | 96 | 17.4 | 7.3 | 14 | 0 |
| throughput x1 | 55882 | 409730 | 153730 | 62.5 | 160 | 11.8 | 6.7 | 14 | 0 |
| throughput x4 | 72648 | 532649 | 204649 | 61.6 | 208 | 12.3 | 9.8 | 51 | 0 |
| throughput x16 | 139719 | 1024325 | 385925 | 62.3 | 400 | 13.5 | 9.9 | 230 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 3.0 | 0.0 | 0 | 0 |
| chat | 44707 | 327866 | 127866 | 61.0 | 1796 | 18.8 | 5.7 | 38 | 0 |
