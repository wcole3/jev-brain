# qwen3.6-27b Decision Index 0.3 (rescore)

## Provenance

- timestamp: 2026-10-03T233021Z
- repo commit: 3e58290
- host: RTX PRO 6000 Blackwell, 587/600 W, drv 610.43.02, PCIe 4x16, AMD Ryzen 9 5900XT 16-Core Processor (32 thr), 121 GB, vast 54020844
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/qwen3.6-27b/2026-10-03T140831Z-vast-0.3
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
- rescored: 2026-10-09T164331Z at 0583abf: 2026-10-03T140831Z-vast-index plus the 2,638 rebuilt GSM8K rows run under this run's settings

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: qwen3.6-27b** | 56.51 | — | 0.047 | 358.2 | 1.000 |
| Decider chat · Qwen3.6-27B | 51.57 | 51.25 | 0.021 | 83.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

Parity gate vs Decider chat · Qwen3.6-27B: +4.94 (±1.5) → MISS: file a ticket before M2

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 39.8 | 53.2 | 1.000 | 11 |
| language | 63.6 | 74.2 | 1.000 | 9 |
| retrieval | 60.7 | 70.1 | 0.998 | 6 |
| tools | 74.5 | 76.9 | 0.999 | 5 |
| arts | 40.2 | 60.2 | 1.000 | 6 |

Status: {'ok': 152948, 'unsupported': 7}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- 0.2.1 index of the same run: see 2026-10-03T140831Z-vast-index
