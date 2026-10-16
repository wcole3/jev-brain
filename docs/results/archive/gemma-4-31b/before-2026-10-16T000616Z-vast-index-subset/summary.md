# gemma-4-31b Decision Index 0.3

## Provenance

- timestamp: 2026-10-16T005043Z
- repo commit: d674515
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.104.02, PCIe 5x16, AMD EPYC 9554 64-Core Processor (256 thr), 1385 GB, vast 56172708
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/gemma-4-31b/before-2026-10-16T000616Z-vast
- shards: 8
- ids: data/splits/vision-regression.json
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: header
- option_orders: identity
- systemone_max_len: 65536
- calibration: {'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: gemma-4-31b** | 0.61 | — | 0.110 | 845.3 | 1.000 |
| Decider chat · Gemma-4-31B | 57.79 | 57.62 | 0.047 | 108.5 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 0.0 | 1.7 | 0.031 | 11 |
| language | 0.0 | 2.4 | 0.036 | 9 |
| retrieval | 0.3 | 2.1 | 0.034 | 6 |
| tools | 3.0 | 4.6 | 0.065 | 5 |
| arts | 0.0 | 1.3 | 0.023 | 6 |

Status: {'ok': 3120}; harness complete: False, completed: 3120

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0, 0, 0, 0, 0], wall 24.2 min
- vLLM during the run: KV peak 99.5%, mean 53.1%, waiting peak 186, preemptions 21
