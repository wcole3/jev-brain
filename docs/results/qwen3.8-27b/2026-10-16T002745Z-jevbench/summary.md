# qwen3.8-27b benchmark (full, JevBench only)

## Provenance

- timestamp: 2026-10-16T00:27:45.981476+00:00
- repo commit: d674515
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.99.02, PCIe 5x16, AMD Ryzen 9 9950X3D2 16-Core Processor (32 thr), 123 GB, vast 56172713
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
- prefix_block: 800
- prefix_pad_always: False
- warm_min_prefix_tokens: 800
- warm_up: row
- systemone_priority: 1
- governor_duty: 0.6
- governor_wave: 8
- KV cache: 577 blocks × 800 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: float32
- mamba_block_size: 800
- mamba_cache_mode: align
- enable_prefix_caching: True

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 89.7 | 93.1 | 90.4 | 0.919 | 0.145 | 53 | 220 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.054 | 0.154 | 35.0 | 42.7 | 54 | 6 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| jevbench | 552075 | 552075 | 552075 | 0.0 | 1682 | 3.0 | 0.2 | 0 | 0 |
