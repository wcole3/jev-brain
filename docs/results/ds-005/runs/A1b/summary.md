# ds005-gemma-kvfp8h benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-08T22:02:10.851149+00:00
- repo commit: 98ba1fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: ds005-gemma-kvfp8h
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
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
- KV cache: 19578 blocks × 16 tokens
- cache_dtype: fp8_per_token_head
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 94 | 98 |
| cold | 256 | 1 | 26 | 181 | 185 |
| cold | 256 | 1 | 255 | 1484 | 1486 |
| cold | 256 | 4 | 2 | 169 | 173 |
| cold | 256 | 4 | 26 | 337 | 359 |
| cold | 256 | 4 | 255 | 2804 | 2817 |
| cold | 256 | 16 | 2 | 257 | 264 |
| cold | 256 | 16 | 26 | 820 | 829 |
| cold | 256 | 16 | 255 | 8209 | 8233 |
| cold | 256 | 64 | 2 | 794 | 805 |
| cold | 256 | 64 | 26 | 3041 | 3076 |
| cold | 256 | 64 | 255 | 59545 | 60981 |
| cold | 2048 | 1 | 2 | 573 | 575 |
| cold | 2048 | 1 | 26 | 666 | 667 |
| cold | 2048 | 1 | 255 | 2077 | 2082 |
| cold | 2048 | 4 | 2 | 638 | 888 |
| cold | 2048 | 4 | 26 | 1083 | 1110 |
| cold | 2048 | 4 | 255 | 3525 | 3786 |
| cold | 2048 | 16 | 2 | 776 | 1023 |
| cold | 2048 | 16 | 26 | 1631 | 1653 |
| cold | 2048 | 16 | 255 | 9261 | 9299 |
| cold | 2048 | 64 | 2 | 1676 | 1697 |
| cold | 2048 | 64 | 26 | 3738 | 3769 |
| cold | 2048 | 64 | 255 | 65420 | 66046 |
| cold | 8192 | 1 | 2 | 2458 | 2461 |
| cold | 8192 | 1 | 26 | 2565 | 2567 |
| cold | 8192 | 1 | 255 | 4302 | 4321 |
| cold | 8192 | 4 | 2 | 7252 | 7456 |
| cold | 8192 | 4 | 26 | 7488 | 8011 |
| cold | 8192 | 4 | 255 | 7829 | 8073 |
| cold | 8192 | 16 | 2 | 9468 | 10641 |
| cold | 8192 | 16 | 26 | 10048 | 10574 |
| cold | 8192 | 16 | 255 | 19929 | 20517 |
| cold | 8192 | 64 | 2 | 10306 | 10385 |
| cold | 8192 | 64 | 26 | 13203 | 13593 |
| cold | 8192 | 64 | 255 | 98342 | 99972 |
| warm | 2048 | 16 | 26 | 221 | 237 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.6 |
| 16 | 0.6 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 88.1 | 91.2 | 92.2 | 0.934 | 0.222 | 60 | 306 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.115 | 0.232 | 49.0 | 42.7 | 5 | 44 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 191 | 24.7 |
| long | none | 206 | 24.5 |
| short | 4 systemone | 13913 | 12.8 |
| long | 4 systemone | 1299 | 14.6 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 4001949 | 26953671 | 7086215 | 73.7 | 5148 | 59.1 | 33.6 | 56 | 0 |
| warm | 33678 | 235008 | 7312 | 96.9 | 96 | 11.6 | 4.4 | 0 | 0 |
| throughput x1 | 112492 | 787072 | 116064 | 85.3 | 320 | 11.5 | 6.9 | 0 | 0 |
| throughput x4 | 112496 | 787136 | 125264 | 84.1 | 320 | 24.8 | 18.5 | 32 | 0 |
| throughput x16 | 179993 | 1259408 | 196304 | 84.4 | 512 | 30.0 | 25.4 | 217 | 0 |
| jevbench | 606246 | 606246 | 529046 | 12.7 | 1682 | 2.2 | 0.1 | 0 | 0 |
| chat | 89991 | 629720 | 101032 | 84.0 | 1609 | 20.4 | 4.0 | 28 | 0 |
