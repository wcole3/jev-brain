# qwen3.8-27b benchmark (quick, with chat)

## Provenance

- timestamp: 2026-10-05T07:18:44.859700+00:00
- repo commit: 66b8531
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 50
- profile: qwen3.8-27b
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: header
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: front
- prefix_block: 784
- prefix_pad_always: False
- warm_min_prefix_tokens: 784
- warm_up: row
- systemone_priority: 1
- KV cache: 650 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 103 | 103 |
| cold | 256 | 1 | 26 | 163 | 163 |
| cold | 256 | 16 | 2 | 467 | 467 |
| cold | 256 | 16 | 26 | 826 | 826 |
| cold | 2048 | 1 | 2 | 441 | 441 |
| cold | 2048 | 1 | 26 | 558 | 558 |
| cold | 2048 | 16 | 2 | 801 | 801 |
| cold | 2048 | 16 | 26 | 1198 | 1198 |
| warm | 2048 | 16 | 26 | 710 | 710 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 90.0 | 78.6 | n/a | 0.966 | 0.056 | 88 | 111 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.286 | 0.264 | n/a | n/a | 0 | 0 |

| chat prompt | load | TTFT ms | chunks/s |
|---|---|---|---|
| short | none | 93 | 27.5 |
| long | none | 124 | 27.5 |
| short | 4 systemone | 207 | 2.3 |
| long | 4 systemone | 1349 | 3.0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 58699 | 343584 | 61344 | 82.1 | 204 | 9.6 | 2.0 | 2 | 0 |
| warm | 16731 | 122919 | 12375 | 89.9 | 48 | 8.3 | 2.4 | 2 | 0 |
| throughput x1 | 50295 | 368757 | 51237 | 86.1 | 144 | 8.3 | 2.8 | 2 | 0 |
| throughput x4 | 67058 | 491676 | 68316 | 86.1 | 192 | 10.6 | 5.8 | 27 | 0 |
| throughput x16 | 111759 | 819460 | 113860 | 86.1 | 320 | 9.9 | 6.3 | 200 | 0 |
| jevbench | 11249 | 11249 | 11249 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
| chat | 1039459 | 7621228 | 1059148 | 86.1 | 4063 | 11.2 | 6.1 | 27 | 0 |
