# qwen3.8-27b benchmark (full, JevBench only)

## Provenance

- timestamp: 2026-09-29T09:14:30.113372-04:00
- repo commit: 4de0f45
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- profile: qwen3.8-27b
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: decider_chat
- option_orders: identity
- vllm_version: 0.30.0

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 86.3 | 90.3 | 86.2 | 0.878 | 0.213 | 88 | 246 |
