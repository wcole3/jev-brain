# ds005-gemma-fp8 benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-08T22:52:44.423804+00:00
- repo commit: 98ba1fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: ds005-gemma-fp8
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
- KV cache: 21040 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 63 | 66 |
| cold | 256 | 1 | 26 | 115 | 120 |
| cold | 256 | 1 | 255 | 924 | 928 |
| cold | 256 | 4 | 2 | 106 | 111 |
| cold | 256 | 4 | 26 | 219 | 220 |
| cold | 256 | 4 | 255 | 1747 | 1764 |
| cold | 256 | 16 | 2 | 187 | 192 |
| cold | 256 | 16 | 26 | 543 | 547 |
| cold | 256 | 16 | 255 | 5209 | 5225 |
| cold | 256 | 64 | 2 | 587 | 610 |
| cold | 256 | 64 | 26 | 2008 | 2041 |
| cold | 256 | 64 | 255 | 38819 | 38910 |
| cold | 2048 | 1 | 2 | 380 | 381 |
| cold | 2048 | 1 | 26 | 443 | 444 |
| cold | 2048 | 1 | 255 | 1342 | 1343 |
| cold | 2048 | 4 | 2 | 411 | 416 |
| cold | 2048 | 4 | 26 | 519 | 678 |
| cold | 2048 | 4 | 255 | 2322 | 2373 |
| cold | 2048 | 16 | 2 | 735 | 766 |
| cold | 2048 | 16 | 26 | 1101 | 1129 |
| cold | 2048 | 16 | 255 | 6346 | 6365 |
| cold | 2048 | 64 | 2 | 1281 | 1356 |
| cold | 2048 | 64 | 26 | 2627 | 2760 |
| cold | 2048 | 64 | 255 | 42980 | 43373 |
| cold | 8192 | 1 | 2 | 1592 | 1600 |
| cold | 8192 | 1 | 26 | 1670 | 1674 |
| cold | 8192 | 1 | 255 | 2810 | 2818 |
| cold | 8192 | 4 | 2 | 4579 | 5133 |
| cold | 8192 | 4 | 26 | 4807 | 5302 |
| cold | 8192 | 4 | 255 | 5318 | 5332 |
| cold | 8192 | 16 | 2 | 6133 | 6269 |
| cold | 8192 | 16 | 26 | 6653 | 7228 |
| cold | 8192 | 16 | 255 | 12951 | 13241 |
| cold | 8192 | 64 | 2 | 6812 | 7195 |
| cold | 8192 | 64 | 26 | 8813 | 9628 |
| cold | 8192 | 64 | 255 | 64719 | 65048 |
| warm | 2048 | 16 | 26 | 191 | 203 |

| workers | requests/s |
|---|---|
| 1 | 1.0 |
| 4 | 0.9 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.7 | 91.5 | 92.2 | 0.935 | 0.217 | 43 | 198 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.104 | 0.203 | 49.0 | 42.7 | 5 | 44 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 122 | 42.2 |
| long | none | 123 | 41.9 |
| short | 4 systemone | 7834 | 10.2 |
| long | 4 systemone | 840 | 24.7 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 4001943 | 26952850 | 7109778 | 73.6 | 5148 | 45.9 | 27.5 | 55 | 0 |
| warm | 33678 | 235008 | 7232 | 96.9 | 96 | 8.3 | 3.5 | 0 | 0 |
| throughput x1 | 168746 | 1180736 | 176352 | 85.1 | 480 | 10.1 | 5.9 | 0 | 0 |
| throughput x4 | 168740 | 1180640 | 192320 | 83.7 | 480 | 20.8 | 15.5 | 32 | 0 |
| throughput x16 | 236241 | 1652976 | 264496 | 84.0 | 672 | 25.3 | 21.8 | 206 | 0 |
| jevbench | 606246 | 606246 | 545446 | 10.0 | 1682 | 2.0 | 0.0 | 0 | 0 |
| chat | 89998 | 629832 | 103272 | 83.6 | 1557 | 23.8 | 3.5 | 19 | 0 |
