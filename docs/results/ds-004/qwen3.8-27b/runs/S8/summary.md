# qwen3.8-27b benchmark (full, with chat)

## Provenance

- timestamp: 2026-10-07T04:19:03.585245+00:00
- repo commit: b88d7e8-dirty
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
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
- governor_duty: 0.6
- governor_wave: 8
- KV cache: 650 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 114 | 122 |
| cold | 256 | 1 | 26 | 172 | 192 |
| cold | 256 | 1 | 255 | 1196 | 1236 |
| cold | 256 | 4 | 2 | 459 | 523 |
| cold | 256 | 4 | 26 | 474 | 519 |
| cold | 256 | 4 | 255 | 2652 | 2684 |
| cold | 256 | 16 | 2 | 503 | 531 |
| cold | 256 | 16 | 26 | 866 | 918 |
| cold | 256 | 16 | 255 | 6145 | 6213 |
| cold | 256 | 64 | 2 | 1214 | 1217 |
| cold | 256 | 64 | 26 | 2615 | 2706 |
| cold | 256 | 64 | 255 | 21111 | 21165 |
| cold | 2048 | 1 | 2 | 479 | 486 |
| cold | 2048 | 1 | 26 | 583 | 627 |
| cold | 2048 | 1 | 255 | 1668 | 1723 |
| cold | 2048 | 4 | 2 | 766 | 782 |
| cold | 2048 | 4 | 26 | 824 | 853 |
| cold | 2048 | 4 | 255 | 4190 | 4254 |
| cold | 2048 | 16 | 2 | 899 | 956 |
| cold | 2048 | 16 | 26 | 1295 | 1316 |
| cold | 2048 | 16 | 255 | 7917 | 7948 |
| cold | 2048 | 64 | 2 | 1749 | 1792 |
| cold | 2048 | 64 | 26 | 3209 | 3272 |
| cold | 2048 | 64 | 255 | 22871 | 23735 |
| cold | 8192 | 1 | 2 | 1893 | 1978 |
| cold | 8192 | 1 | 26 | 1998 | 2040 |
| cold | 8192 | 1 | 255 | 3140 | 3210 |
| cold | 8192 | 4 | 2 | 2219 | 2310 |
| cold | 8192 | 4 | 26 | 2259 | 2293 |
| cold | 8192 | 4 | 255 | 8954 | 9133 |
| cold | 8192 | 16 | 2 | 2377 | 2528 |
| cold | 8192 | 16 | 26 | 2809 | 2880 |
| cold | 8192 | 16 | 255 | 12874 | 12948 |
| cold | 8192 | 64 | 2 | 3540 | 3579 |
| cold | 8192 | 64 | 26 | 4761 | 4892 |
| cold | 8192 | 64 | 255 | 29401 | 29858 |
| warm | 2048 | 16 | 26 | 784 | 839 |

| workers | requests/s |
|---|---|
| 1 | 0.8 |
| 4 | 1.0 |
| 16 | 1.0 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.7 | 92.9 | 90.4 | 0.920 | 0.140 | 108 | 267 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.063 | 0.154 | 35.0 | 42.7 | 54 | 6 |

| chat prompt | load | TTFT ms | tokens/s |
|---|---|---|---|
| short | none | 138 | 27.5 |
| long | none | 126 | 27.3 |
| short | 4 systemone | 6814 | 7.8 |
| long | 4 systemone | 275 | 16.1 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 3990369 | 29091146 | 4775386 | 83.6 | 5148 | 30.0 | 5.2 | 62 | 0 |
| warm | 33462 | 245838 | 22398 | 90.9 | 96 | 8.3 | 2.7 | 2 | 0 |
| throughput x1 | 134120 | 983352 | 136632 | 86.1 | 384 | 8.3 | 2.5 | 2 | 0 |
| throughput x4 | 178820 | 1311136 | 182176 | 86.1 | 512 | 10.6 | 6.0 | 27 | 0 |
| throughput x16 | 245887 | 1802812 | 250492 | 86.1 | 704 | 10.6 | 6.6 | 200 | 0 |
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 0.0 | 0.0 | 0 | 0 |
| chat | 111776 | 819710 | 114110 | 86.1 | 1413 | 8.5 | 1.3 | 19 | 0 |
