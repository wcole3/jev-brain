# gemma-4-31b benchmark (full, JevBench only)

## Provenance

- timestamp: 2026-09-29T09:23:36.044641-04:00
- repo commit: 4de0f45
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

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 87.1 | 92.1 | 87.5 | 0.936 | 0.203 | 62 | 260 |
