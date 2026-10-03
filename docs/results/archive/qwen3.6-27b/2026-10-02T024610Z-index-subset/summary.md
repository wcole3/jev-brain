# qwen3.6-27b Decision Index 0.2.1

## Provenance

- timestamp: 2026-10-02T025313Z
- repo commit: 5eb50c9
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- harness: 87d4650b42b377c0291a89c1f1a879f9b31082bf
- edition: 0.2.1
- run dir: .cache/index-runs/qwen3.6-27b/2026-10-02T024610Z
- shards: 4
- ids: /workspace/jev-brain/data/splits/compare-2k.json
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
| **ours: qwen3.6-27b** | 0.06 | 0.027 | 345.7 | 1.000 |
| Decider chat · Qwen3.6-27B | 51.35 | 0.021 | 83.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.90 | 0.074 | 524.1 | board |

Parity gate vs Decider chat · Qwen3.6-27B: -51.29 (±1.5) → not judged (subset run; run incomplete: 2016 rows)

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 0.0 | 0.6 | 0.013 | 10 |
| language | 0.0 | 0.9 | 0.013 | 10 |
| retrieval | 0.1 | 0.7 | 0.013 | 6 |
| tools | 0.2 | 1.0 | 0.015 | 5 |
| arts | 0.1 | 0.8 | 0.013 | 7 |

Status: {'ok': 2016}; harness complete: False, completed: 2016

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 6.4 min
- vLLM during the run: KV peak 47.6%, mean 5.0%, waiting peak 57, preemptions 0
