# qwen3.6-27b Decision Index 0.2.1

## Provenance

- timestamp: 2026-10-02T195225Z
- repo commit: 6990a58
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- harness: 87d4650b42b377c0291a89c1f1a879f9b31082bf
- edition: 0.2.1
- run dir: .cache/index-runs/qwen3.6-27b/2026-10-02T194432Z
- shards: 4
- ids: /home/welb/devspace/jev-brain/data/splits/compare-2k.json
- profile: qwen3.6-27b
- hf_model: Qwen/Qwen3.6-27B
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: decider_chat
- option_orders: identity
- systemone_max_len: 32768
- calibration: {'decider_chat': {'T': {'choice': 1.6479149611375679, 'score': 1.9271133600869372, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.626739845878971, 'score': 1.9577583066935726, 'noul': 1.2842455905297372}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4836733616074274, 'score': 8.054659971948029, 'noul': 1.1446681550320104}, 'b': 0.2527877422356274, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | Index | ECE | median ms | coverage |
|---|---|---|---|---|
| **ours: qwen3.6-27b** | 0.06 | 0.038 | 416.5 | 1.000 |
| Decider chat · Qwen3.6-27B | 51.35 | 0.021 | 83.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.90 | 0.074 | 524.1 | board |

Parity gate vs Decider chat · Qwen3.6-27B: -51.29 (±1.5) → not judged (subset run; run incomplete: 2016 rows)

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 0.0 | 0.6 | 0.013 | 10 |
| language | 0.0 | 0.9 | 0.013 | 10 |
| retrieval | 0.1 | 0.7 | 0.013 | 6 |
| tools | 0.2 | 1.0 | 0.015 | 5 |
| arts | 0.1 | 0.7 | 0.013 | 7 |

Status: {'ok': 2016}; harness complete: False, completed: 2016

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 6.5 min
- vLLM during the run: KV peak 46.4%, mean 4.3%, waiting peak 51, preemptions 0
