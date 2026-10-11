# qwen3.8-27b-fp8 Decision Index 0.3

## Provenance

- timestamp: 2026-10-11T021433Z
- repo commit: 102f9fe-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/qwen3.8-27b-fp8/2026-10-10T183800Z
- shards: 4
- ids: full suite
- profile: qwen3.8-27b-fp8
- hf_model: Qwen/Qwen3.8-27B-FP8
- hf_revision: 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a
- prompt_layout: header
- option_orders: identity
- systemone_max_len: 32768
- calibration: {'decider_chat': {'T': {'choice': 1.4847102978456486, 'score': 1.654764340913316, 'noul': 0.9427535974052343}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5169908033068626, 'score': 1.0, 'noul': 0.9589393732341274}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3239935203887572, 'score': 6.368543955447793, 'noul': 0.8118425256070971}, 'b': 0.0, 'source': 'qwen3.8-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: qwen3.8-27b-fp8** | 56.33 | — | 0.022 | 361.4 | 1.000 |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | 373.0 | board |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | 108.3 | board |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | 89.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 35.3 | 49.9 | 1.000 | 11 |
| language | 63.7 | 74.7 | 1.000 | 9 |
| retrieval | 63.5 | 72.0 | 0.998 | 6 |
| tools | 75.5 | 78.1 | 0.999 | 5 |
| arts | 42.2 | 60.8 | 1.000 | 6 |

Status: {'ok': 140171, 'unsupported': 7}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 429.1 min
- vLLM during the run: KV peak 53.1%, mean 5.5%, waiting peak 175, preemptions 0
