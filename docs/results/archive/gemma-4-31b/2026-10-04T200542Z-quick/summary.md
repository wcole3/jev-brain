# gemma-4-31b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-10-04T20:05:42.413619+00:00
- repo commit: f0e5b9c
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 50
- profile: gemma-4-31b
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
- KV cache: 9947 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 103 | 103 |
| cold | 256 | 1 | 26 | 192 | 192 |
| cold | 256 | 16 | 2 | 306 | 306 |
| cold | 256 | 16 | 26 | 841 | 841 |
| cold | 2048 | 1 | 2 | 502 | 502 |
| cold | 2048 | 1 | 26 | 605 | 605 |
| cold | 2048 | 16 | 2 | 793 | 793 |
| cold | 2048 | 16 | 26 | 1395 | 1395 |
| warm | 2048 | 16 | 26 | 274 | 274 |

| workers | requests/s |
|---|---|
| 1 | 0.7 |
| 4 | 0.8 |
| 16 | 0.8 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 72.0 | 100.0 | n/a | 0.848 | 0.389 | 84 | 98 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.230 | 0.456 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 59224 | 301969 | 55377 | 81.7 | 204 | 13.8 | 2.8 | 0 | 0 |
| warm | 16839 | 117504 | 5920 | 95.0 | 48 | 13.5 | 7.5 | 0 | 0 |
| throughput x1 | 45001 | 314896 | 42512 | 86.5 | 128 | 13.9 | 5.9 | 0 | 0 |
| throughput x4 | 61876 | 432976 | 58512 | 86.5 | 176 | 34.0 | 25.7 | 31 | 0 |
| throughput x16 | 129361 | 905056 | 122240 | 86.5 | 368 | 37.4 | 31.7 | 220 | 0 |
| jevbench | 11846 | 11846 | 10118 | 14.6 | 50 | 0.0 | 0.0 | 0 | 0 |
