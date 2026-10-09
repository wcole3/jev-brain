# gemma-4-31b Decision Index 0.3 (rescore)

## Provenance

- timestamp: 2026-10-04T105814Z
- repo commit: 0aeee17
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.84, PCIe 5x16, AMD Ryzen 9 9950X3D 16-Core Processor (32 thr), 92 GB, vast 54088302
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/gemma-4-31b/2026-10-04T013002Z-vast-0.3
- shards: 4
- ids: full suite
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- systemone_max_len: 32768
- calibration: {'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0
- rescored: 2026-10-09T164331Z at 0583abf: 2026-10-04T013002Z-vast-index plus the 2,638 rebuilt GSM8K rows run under this run's settings

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: gemma-4-31b** | 61.60 | — | 0.119 | 329.5 | 1.000 |
| Decider chat · Gemma-4-31B | 57.79 | 57.62 | 0.047 | 108.5 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 48.6 | 59.6 | 1.000 | 11 |
| language | 65.8 | 75.9 | 1.000 | 9 |
| retrieval | 67.2 | 74.2 | 0.995 | 6 |
| tools | 76.6 | 79.1 | 0.999 | 5 |
| arts | 45.7 | 64.0 | 1.000 | 6 |

Status: {'ok': 152944, 'unsupported': 11}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- 0.2.1 index of the same run: see 2026-10-04T013002Z-vast-index
