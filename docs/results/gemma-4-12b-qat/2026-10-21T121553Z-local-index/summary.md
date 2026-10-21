# gemma-4-12b-qat Decision Index 0.3

## Provenance

- timestamp: 2026-10-21T214719Z
- repo commit: 4457e94
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/gemma-4-12b-qat/2026-10-21T121553Z-local
- shards: 4
- ids: full suite
- profile: gemma-4-12b-qat
- hf_model: google/gemma-4-12B-it-qat-w4a16-ct
- hf_revision: 1d2c2d7f2466070e69d6fb3fd5ce9a7d75f2f6ee
- prompt_layout: blurb_header
- option_orders: identity
- option_orders_images: 
- systemone_max_len: 65536
- calibration: {'blurb_header': {'T': {'choice': 3.0074889638490045, 'score': 12.941782505400122, 'noul': 2.244027515792647}, 'b': 0.0, 'source': 'gemma-4-12b-qat/blurb_header/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'header': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}, 'question_first': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: gemma-4-12b-qat** | 51.26 | — | 0.047 | 141.5 | 1.000 |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 31.2 | 47.3 | 1.000 | 11 |
| language | 58.7 | 71.1 | 1.000 | 9 |
| retrieval | 61.8 | 71.0 | 1.000 | 6 |
| tools | 66.4 | 69.7 | 1.000 | 5 |
| arts | 35.1 | 55.1 | 1.000 | 6 |

Status: {'ok': 140178}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 0.1 min
- vLLM during the run: KV peak 0.0%, mean 0.0%, waiting peak 0, preemptions 0
