# qwen3.8-27b Decision Index 0.3 (rescore)

## Provenance

- timestamp: 2026-10-04T104559Z
- repo commit: 8a14b18
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.84, PCIe 4x16, AMD Ryzen Threadripper 3960X 24-Core Processor (48 thr), 189 GB, vast 54093767
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/qwen3.8-27b/2026-10-04T022907Z-vast-0.3
- shards: 4
- ids: full suite
- profile: qwen3.8-27b
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: header
- option_orders: identity
- systemone_max_len: 32768
- calibration: {'decider_chat': {'T': {'choice': 1.4958925733915396, 'score': 1.6641806616549275, 'noul': 0.9701214258536706}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5360739185489443, 'score': 1.7751446114421117, 'noul': 0.9629807468103339}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3522738771932372, 'score': 6.26411640450269, 'noul': 0.8245982249217311}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0
- rescored: 2026-10-09T164331Z at 0583abf: 2026-10-04T022907Z-vast-index plus the 2,638 rebuilt GSM8K rows run under this run's settings

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: qwen3.8-27b** | 56.60 | — | 0.024 | 321.0 | 1.000 |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | 373.0 | board |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | 108.3 | board |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | 89.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 35.7 | 50.2 | 1.000 | 11 |
| language | 63.6 | 74.6 | 1.000 | 9 |
| retrieval | 63.7 | 72.1 | 0.998 | 6 |
| tools | 76.3 | 78.9 | 0.999 | 5 |
| arts | 42.2 | 60.8 | 1.000 | 6 |

Status: {'ok': 152948, 'unsupported': 7}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- 0.2.1 index of the same run: see 2026-10-04T022907Z-vast-index
