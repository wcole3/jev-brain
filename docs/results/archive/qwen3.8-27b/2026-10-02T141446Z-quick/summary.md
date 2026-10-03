# qwen3.8-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-10-02T14:14:46.701149+00:00
- repo commit: 7f927b0
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 595.84, PCIe 5x16, Intel(R) Core(TM) Ultra 7 265K (20 thr), 125 GB, vast 53868967
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 50
- profile: qwen3.8-27b
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: decider_chat
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: front
- prefix_block: 784
- prefix_pad_always: False
- warm_min_prefix_tokens: 784
- warm_up: row
- KV cache: 654 blocks × 784 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 784
- mamba_cache_mode: align
- enable_prefix_caching: True

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 92 | 92 |
| cold | 256 | 1 | 26 | 163 | 163 |
| cold | 256 | 16 | 2 | 427 | 427 |
| cold | 256 | 16 | 26 | 889 | 889 |
| cold | 2048 | 1 | 2 | 463 | 463 |
| cold | 2048 | 1 | 26 | 528 | 528 |
| cold | 2048 | 16 | 2 | 717 | 717 |
| cold | 2048 | 16 | 26 | 1187 | 1187 |
| warm | 2048 | 16 | 26 | 727 | 727 |

| workers | requests/s |
|---|---|
| 1 | 0.9 |
| 4 | 0.9 |
| 16 | 0.9 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 92.0 | 85.7 | n/a | 0.968 | 0.056 | 66 | 68 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.176 | 0.201 | n/a | n/a | 0 | 0 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56242 | 343309 | 61069 | 82.2 | 204 | 8.9 | 1.1 | 0 | 0 |
| warm | 16185 | 122919 | 12375 | 89.9 | 48 | 7.0 | 1.9 | 0 | 0 |
| throughput x1 | 48655 | 368757 | 51237 | 86.1 | 144 | 9.5 | 2.1 | 0 | 0 |
| throughput x4 | 64875 | 491676 | 68316 | 86.1 | 192 | 29.7 | 9.2 | 1 | 0 |
| throughput x16 | 86501 | 655568 | 91088 | 86.1 | 256 | 29.4 | 16.7 | 79 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
