# gemma-4-12b Decision Index 0.3

## Provenance

- timestamp: 2026-10-21T212251Z
- repo commit: 96855bb
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/gemma-4-12b/2026-10-21T163900Z-local
- shards: 4
- ids: full suite
- profile: gemma-4-12b
- hf_model: google/gemma-4-12B-it
- hf_revision: 707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7
- prompt_layout: blurb_header
- option_orders: identity
- option_orders_images: 
- systemone_max_len: 65536
- calibration: {'blurb_header': {'T': {'choice': 4.035253781242961, 'score': 4.035253781242961, 'noul': 4.035253781242961}, 'b': 0.0, 'source': 'gemma-4-12b/blurb_header/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'header': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'question_first': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: gemma-4-12b** | 53.58 | — | 0.060 | 152.6 | 1.000 |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 33.3 | 48.6 | 1.000 | 11 |
| language | 60.7 | 72.3 | 1.000 | 9 |
| retrieval | 64.0 | 72.3 | 1.000 | 6 |
| tools | 70.0 | 73.0 | 1.000 | 5 |
| arts | 36.8 | 56.5 | 1.000 | 6 |

Status: {'ok': 140178}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 262.8 min
- vLLM during the run: KV peak 12.9%, mean 3.1%, waiting peak 150, preemptions 0
