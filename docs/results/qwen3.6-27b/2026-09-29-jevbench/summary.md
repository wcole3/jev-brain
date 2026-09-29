# qwen3.6-27b benchmark (full, JevBench only)

## Provenance

- timestamp: 2026-09-29T09:03:43.103207-04:00
- repo commit: 4de0f45
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: qwen3.6-27b
- hf_model: Qwen/Qwen3.6-27B
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- vllm_version: 0.30.0

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 84.4 | 91.9 | 83.7 | 0.818 | 0.377 | 89 | 257 |
