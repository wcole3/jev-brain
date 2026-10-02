# qwen3.8-27b Decision Index 0.2.1

## Provenance

- timestamp: 2026-10-02T040847Z
- repo commit: 7a5d9b6
- host: RTX PRO 6000 Blackwell, 450/600 W, drv 580.173.02, PCIe 4x16, AMD EPYC 7742 64-Core Processor (256 thr), 504 GB, vast 53796429
- harness: 87d4650b42b377c0291a89c1f1a879f9b31082bf
- edition: 0.2.1
- run dir: .cache/index-runs/qwen3.8-27b/2026-10-02T040054Z
- shards: 4
- ids: /workspace/jev-brain/data/splits/compare-2k.json
- profile: qwen3.8-27b
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: decider_chat
- option_orders: identity
- systemone_max_len: 32768
- temperatures: {'decider_chat': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'header': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'question_first': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}}
- vllm_version: 0.30.0

| entry | Index | ECE | median ms | coverage |
|---|---|---|---|---|
| **ours: qwen3.8-27b** | 0.06 | 0.060 | 383.6 | 1.000 |
| simple-jev · Qwen3.8-27B | 55.70 | 0.113 | 373.0 | board |
| reflex 27B | 52.20 | 0.024 | 108.0 | board |
| Jevfire (Qwen3.8-27B-FP8) | 49.40 | 0.052 | 89.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.90 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 0.0 | 0.5 | 0.013 | 10 |
| language | 0.0 | 0.8 | 0.013 | 10 |
| retrieval | 0.1 | 0.8 | 0.013 | 6 |
| tools | 0.2 | 1.1 | 0.015 | 5 |
| arts | 0.1 | 0.8 | 0.013 | 7 |

Status: {'ok': 2016}; harness complete: False, completed: 2016

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 7.1 min
- vLLM during the run: KV peak 48.4%, mean 5.1%, waiting peak 112, preemptions 0
