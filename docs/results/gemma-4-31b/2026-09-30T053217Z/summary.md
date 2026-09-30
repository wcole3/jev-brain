# gemma-4-31b benchmark (full, systemone only)

## Provenance

- timestamp: 2026-09-30T05:32:17.590716+00:00
- repo commit: 5bab2e8
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: decider_chat
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: off
- prefix_block: 0
- prefix_pad_always: False
- warm_min_prefix_tokens: 512
- KV cache: 9965 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 85 | 86 |
| cold | 256 | 1 | 26 | 155 | 157 |
| cold | 256 | 1 | 255 | 1147 | 1151 |
| cold | 256 | 4 | 2 | 144 | 154 |
| cold | 256 | 4 | 26 | 288 | 305 |
| cold | 256 | 4 | 255 | 2260 | 2302 |
| cold | 256 | 16 | 2 | 264 | 277 |
| cold | 256 | 16 | 26 | 728 | 736 |
| cold | 256 | 16 | 255 | 6746 | 6804 |
| cold | 256 | 64 | 2 | 774 | 784 |
| cold | 256 | 64 | 26 | 2557 | 2576 |
| cold | 256 | 64 | 255 | 50310 | 51012 |
| cold | 2048 | 1 | 2 | 479 | 497 |
| cold | 2048 | 1 | 26 | 575 | 601 |
| cold | 2048 | 1 | 255 | 1748 | 1756 |
| cold | 2048 | 4 | 2 | 980 | 999 |
| cold | 2048 | 4 | 26 | 1201 | 1207 |
| cold | 2048 | 4 | 255 | 3541 | 3575 |
| cold | 2048 | 16 | 2 | 1188 | 1215 |
| cold | 2048 | 16 | 26 | 1765 | 1795 |
| cold | 2048 | 16 | 255 | 8547 | 8702 |
| cold | 2048 | 64 | 2 | 1945 | 1986 |
| cold | 2048 | 64 | 26 | 3920 | 3933 |
| cold | 2048 | 64 | 255 | 54640 | 54756 |
| cold | 8192 | 1 | 2 | 2118 | 2122 |
| cold | 8192 | 1 | 26 | 2155 | 2205 |
| cold | 8192 | 1 | 255 | 3566 | 3570 |
| cold | 8192 | 4 | 2 | 4190 | 4241 |
| cold | 8192 | 4 | 26 | 4404 | 4414 |
| cold | 8192 | 4 | 255 | 7151 | 7290 |
| cold | 8192 | 16 | 2 | 4553 | 4591 |
| cold | 8192 | 16 | 26 | 5186 | 5208 |
| cold | 8192 | 16 | 255 | 13361 | 13475 |
| cold | 8192 | 64 | 2 | 5755 | 5884 |
| cold | 8192 | 64 | 26 | 7705 | 7885 |
| cold | 8192 | 64 | 255 | 67885 | 68048 |
| warm | 2048 | 16 | 26 | 251 | 258 |

| workers | requests/s |
|---|---|
| 1 | 0.6 |
| 4 | 0.6 |
| 16 | 0.5 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 87.2 | 92.3 | 87.5 | 0.936 | 0.203 | 58 | 266 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.126 | 0.251 | 53.3 | 42.7 | 6 | 72 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3949636 | 24027525 | 6392293 | 73.4 | 5148 | 62.5 | 29.3 | 57 | 0 |
| warm | 32586 | 217536 | 7968 | 96.3 | 96 | 13.7 | 2.1 | 0 | 0 |
| throughput x1 | 92515 | 619360 | 127584 | 79.4 | 272 | 14.5 | 4.3 | 0 | 0 |
| throughput x4 | 108851 | 728816 | 150256 | 79.4 | 320 | 33.8 | 22.3 | 24 | 0 |
| throughput x16 | 152402 | 1020512 | 255584 | 75.0 | 448 | 39.2 | 33.3 | 178 | 0 |
| jevbench | 568955 | 568955 | 501563 | 11.8 | 1682 | 0.0 | 0.0 | 0 | 0 |
