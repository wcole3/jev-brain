# gemma-4-31b benchmark (full, systemone only)

## Provenance

- timestamp: 2026-09-30T14:36:38.772168+00:00
- repo commit: 4d80cd5
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
- warm_up: off
- KV cache: 9965 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 91 | 105 |
| cold | 256 | 1 | 26 | 166 | 169 |
| cold | 256 | 1 | 255 | 1215 | 1219 |
| cold | 256 | 4 | 2 | 157 | 169 |
| cold | 256 | 4 | 26 | 305 | 320 |
| cold | 256 | 4 | 255 | 2389 | 2396 |
| cold | 256 | 16 | 2 | 289 | 311 |
| cold | 256 | 16 | 26 | 769 | 782 |
| cold | 256 | 16 | 255 | 13643 | 13696 |
| cold | 256 | 64 | 2 | 813 | 826 |
| cold | 256 | 64 | 26 | 2731 | 2803 |
| cold | 256 | 64 | 255 | 52847 | 53505 |
| cold | 2048 | 1 | 2 | 513 | 531 |
| cold | 2048 | 1 | 26 | 605 | 618 |
| cold | 2048 | 1 | 255 | 1845 | 1873 |
| cold | 2048 | 4 | 2 | 603 | 614 |
| cold | 2048 | 4 | 26 | 798 | 814 |
| cold | 2048 | 4 | 255 | 3178 | 3196 |
| cold | 2048 | 16 | 2 | 795 | 797 |
| cold | 2048 | 16 | 26 | 1377 | 1388 |
| cold | 2048 | 16 | 255 | 16056 | 16252 |
| cold | 2048 | 64 | 2 | 1616 | 1650 |
| cold | 2048 | 64 | 26 | 3641 | 3699 |
| cold | 2048 | 64 | 255 | 57574 | 58268 |
| cold | 8192 | 1 | 2 | 2181 | 2201 |
| cold | 8192 | 1 | 26 | 2273 | 2290 |
| cold | 8192 | 1 | 255 | 3720 | 3747 |
| cold | 8192 | 4 | 2 | 2271 | 2308 |
| cold | 8192 | 4 | 26 | 2514 | 2525 |
| cold | 8192 | 4 | 255 | 5354 | 5410 |
| cold | 8192 | 16 | 2 | 2580 | 2601 |
| cold | 8192 | 16 | 26 | 3287 | 3343 |
| cold | 8192 | 16 | 255 | 20626 | 20679 |
| cold | 8192 | 64 | 2 | 3826 | 4082 |
| cold | 8192 | 64 | 26 | 6078 | 6110 |
| cold | 8192 | 64 | 255 | 69802 | 70514 |
| warm | 2048 | 16 | 26 | 215 | 229 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 87.0 | 91.9 | 87.5 | 0.936 | 0.203 | 63 | 278 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.126 | 0.252 | 53.3 | 42.7 | 6 | 72 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3949605 | 24026344 | 6418056 | 73.3 | 5148 | 58.1 | 31.9 | 57 | 0 |
| warm | 32586 | 217536 | 5920 | 97.3 | 96 | 13.7 | 4.6 | 0 | 0 |
| throughput x1 | 119746 | 801856 | 120384 | 85.0 | 352 | 14.6 | 6.1 | 0 | 0 |
| throughput x4 | 141507 | 947472 | 142096 | 85.0 | 416 | 34.2 | 26.1 | 32 | 0 |
| throughput x16 | 201373 | 1348288 | 202176 | 85.0 | 592 | 38.2 | 33.7 | 206 | 0 |
| jevbench | 568955 | 568955 | 501563 | 11.8 | 1682 | 0.0 | 0.0 | 0 | 0 |
