# qwen3.6-27b Decision Index 0.2.1

## Provenance

- timestamp: 2026-10-03T233021Z
- repo commit: 3e58290
- host: RTX PRO 6000 Blackwell, 587/600 W, drv 610.43.02, PCIe 4x16, AMD Ryzen 9 5900XT 16-Core Processor (32 thr), 121 GB, vast 54020844
- harness: 87d4650b42b377c0291a89c1f1a879f9b31082bf
- edition: 0.2.1
- run dir: .cache/index-runs/qwen3.6-27b/2026-10-03T140831Z-vast
- shards: 4
- ids: full suite
- profile: qwen3.6-27b
- hf_model: Qwen/Qwen3.6-27B
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: header
- option_orders: identity
- systemone_max_len: 32768
- calibration: {'decider_chat': {'T': {'choice': 1.6479149611375679, 'score': 1.9271133600869372, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.626739845878971, 'score': 1.9577583066935726, 'noul': 1.2842455905297372}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4836733616074274, 'score': 8.054659971948029, 'noul': 1.1446681550320104}, 'b': 0.2527877422356274, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | Index | ECE | median ms | coverage |
|---|---|---|---|---|
| **ours: qwen3.6-27b** | 55.92 | 0.042 | 364.8 | 1.000 |
| Decider chat · Qwen3.6-27B | 51.35 | 0.021 | 83.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.90 | 0.074 | 524.1 | board |

Parity gate vs Decider chat · Qwen3.6-27B: +4.57 (±1.5) → MISS: file a ticket before M2

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 38.0 | 51.1 | 1.000 | 10 |
| language | 64.6 | 75.5 | 1.000 | 10 |
| retrieval | 60.7 | 70.1 | 0.998 | 6 |
| tools | 74.5 | 76.9 | 0.999 | 5 |
| arts | 36.5 | 53.1 | 1.000 | 7 |

Status: {'ok': 150310, 'unsupported': 7}; harness complete: True, completed: 150317

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 545.7 min
- vLLM during the run: KV peak 52.0%, mean 5.9%, waiting peak 123, preemptions 0
