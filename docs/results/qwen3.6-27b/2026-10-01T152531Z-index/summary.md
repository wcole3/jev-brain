# qwen3.6-27b Decision Index 0.2.1

## Provenance

- timestamp: 2026-10-02T000207Z
- repo commit: 0ea1ccd
- harness: 87d4650b42b377c0291a89c1f1a879f9b31082bf
- edition: 0.2.1
- run dir: .cache/index-runs/qwen3.6-27b/2026-10-01T152531Z
- shards: 4
- ids: full suite
- profile: qwen3.6-27b
- hf_model: Qwen/Qwen3.6-27B
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- systemone_max_len: 32768
- temperatures: {'decider_chat': {'choice': 1.943, 'score': 1.943, 'noul': 1.943}, 'header': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'question_first': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}}
- vllm_version: 0.30.0

| entry | Index | ECE | median ms | coverage |
|---|---|---|---|---|
| **ours: qwen3.6-27b** | 51.61 | 0.022 | 352.7 | 1.000 |
| Decider chat · Qwen3.6-27B | 51.35 | 0.021 | 83.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.90 | 0.074 | 524.1 | board |

Parity gate vs Decider chat · Qwen3.6-27B: +0.26 (±1.5) → pass

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 37.1 | 50.5 | 1.000 | 10 |
| language | 57.4 | 70.5 | 1.000 | 10 |
| retrieval | 52.7 | 65.6 | 1.000 | 6 |
| tools | 71.8 | 74.4 | 1.000 | 5 |
| arts | 35.0 | 52.0 | 1.000 | 7 |

Status: {'ok': 150317}; harness complete: True, completed: 150317

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 235.2 min
- vLLM during the run: KV peak 48.2%, mean 4.7%, waiting peak 112, preemptions 0
