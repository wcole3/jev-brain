# qwen3.8-27b Decision Index 0.2.1

## Provenance

- timestamp: 2026-10-03T203247Z
- repo commit: 3e58290
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.84, PCIe 5x16, AMD Ryzen 7 9800X3D 8-Core Processor (16 thr), 92 GB, vast 54017287
- harness: 87d4650b42b377c0291a89c1f1a879f9b31082bf
- edition: 0.2.1
- run dir: .cache/index-runs/qwen3.8-27b/2026-10-03T133219Z-vast
- shards: 4
- ids: full suite
- profile: qwen3.8-27b
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: decider_chat
- option_orders: identity
- systemone_max_len: 32768
- calibration: {'decider_chat': {'T': {'choice': 1.4958925733915396, 'score': 1.6641806616549275, 'noul': 0.9701214258536706}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5360739185489443, 'score': 1.7751446114421117, 'noul': 0.9629807468103339}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3522738771932372, 'score': 6.26411640450269, 'noul': 0.8245982249217311}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | Index | ECE | median ms | coverage |
|---|---|---|---|---|
| **ours: qwen3.8-27b** | 51.47 | 0.026 | 274.5 | 1.000 |
| simple-jev · Qwen3.8-27B | 55.70 | 0.113 | 373.0 | board |
| reflex 27B | 52.20 | 0.024 | 108.0 | board |
| Jevfire (Qwen3.8-27B-FP8) | 49.40 | 0.052 | 89.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.90 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 33.3 | 47.9 | 1.000 | 10 |
| language | 54.4 | 68.8 | 1.000 | 10 |
| retrieval | 57.6 | 68.9 | 1.000 | 6 |
| tools | 74.2 | 77.0 | 1.000 | 5 |
| arts | 37.0 | 52.7 | 1.000 | 7 |

Status: {'ok': 150317}; harness complete: True, completed: 150317

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 407.2 min
- vLLM during the run: KV peak 49.0%, mean 5.6%, waiting peak 93, preemptions 0
