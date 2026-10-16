# gemma-4-31b benchmark (full, JevBench only)

## Provenance

- timestamp: 2026-10-16T00:22:51.970910+00:00
- repo commit: d674515
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.104.02, PCIe 5x16, AMD EPYC 9554 64-Core Processor (256 thr), 1385 GB, vast 56172708
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- vllm_version: 0.30.0
- prefix_pad: off
- prefix_block: 0
- prefix_pad_always: False
- warm_min_prefix_tokens: 4096
- warm_up: prefix
- systemone_priority: 0
- governor_duty: 0.5
- governor_wave: 8
- KV cache: 9712 blocks × 16 tokens
- cache_dtype: auto
- mamba_cache_dtype: auto
- mamba_ssm_cache_dtype: auto
- mamba_block_size: None
- mamba_cache_mode: none
- enable_prefix_caching: True

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 88.2 | 92.0 | 91.7 | 0.932 | 0.227 | 64 | 280 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.041 | 0.170 | 49.4 | 42.7 | 5 | 47 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| jevbench | 606246 | 606246 | 545702 | 10.0 | 1682 | 4.3 | 0.4 | 0 | 0 |
