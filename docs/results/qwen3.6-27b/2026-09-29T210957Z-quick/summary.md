# qwen3.6-27b benchmark (quick, systemone only)

## Provenance

- timestamp: 2026-09-29T17:09:57.154516-04:00
- repo commit: 4463738
- target: gateway
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 50
- profile: qwen3.6-27b
- hf_model: Qwen/Qwen3.6-27B
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- vllm_version: 0.30.0
- KV cache: 665 blocks × 784 tokens

| test | state tokens | questions | options | p50 ms | p95 ms |
|---|---|---|---|---|---|
| cold | 256 | 1 | 2 | 111 | 111 |
| cold | 256 | 1 | 26 | 146 | 146 |
| cold | 256 | 16 | 2 | 851 | 851 |
| cold | 256 | 16 | 26 | 1229 | 1229 |
| cold | 2048 | 1 | 2 | 406 | 406 |
| cold | 2048 | 1 | 26 | 551 | 551 |
| cold | 2048 | 16 | 2 | 1772 | 1772 |
| cold | 2048 | 16 | 26 | 2467 | 2467 |
| warm | 2048 | 16 | 26 | 1175 | 1175 |

| workers | requests/s |
|---|---|
| 1 | 0.4 |
| 4 | 0.4 |
| 16 | 0.4 |

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 50 | 0 | 68.0 | 85.7 | n/a | 0.844 | 0.389 | 93 | 146 |

| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % | generation tokens | KV peak % | KV mean % | waiting peak | preemptions |
|---|---|---|---|---|---|---|---|---|---|
| cold | 56233 | 266008 | 129592 | 51.3 | 204 | 9.2 | 3.7 | 2 | 0 |
| warm | 16185 | 108615 | 27079 | 75.1 | 48 | 12.2 | 4.5 | 2 | 0 |
| throughput x1 | 27031 | 181921 | 72161 | 60.3 | 80 | 8.9 | 4.3 | 2 | 0 |
| throughput x4 | 37844 | 254699 | 101035 | 60.3 | 112 | 10.2 | 7.3 | 47 | 0 |
| throughput x16 | 86508 | 582288 | 231056 | 60.3 | 256 | 10.2 | 8.7 | 213 | 0 |
| jevbench | 10129 | 10129 | 10129 | 0.0 | 50 | 0.0 | 0.0 | 0 | 0 |
