# gemma-4-31b Decision Index 0.2.1

## Provenance

- timestamp: 2026-10-03T214648Z
- repo commit: 3e58290
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 615.71.09, PCIe 4x16, AMD EPYC 7532 32-Core Processor (128 thr), 1008 GB, vast 54017289
- harness: 87d4650b42b377c0291a89c1f1a879f9b31082bf
- edition: 0.2.1
- run dir: .cache/index-runs/gemma-4-31b/2026-10-03T133229Z-vast
- shards: 4
- ids: full suite
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: decider_chat
- option_orders: identity
- systemone_max_len: 32768
- calibration: {'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | Index | ECE | median ms | coverage |
|---|---|---|---|---|
| **ours: gemma-4-31b** | 57.16 | 0.150 | 276.1 | 1.000 |
| Decider chat · Gemma-4-31B | 57.33 | 0.047 | 108.5 | board |
| Jev (hosted API, latency over HTTPS) | 57.90 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 44.3 | 55.8 | 1.000 | 10 |
| language | 60.7 | 72.4 | 1.000 | 10 |
| retrieval | 62.9 | 71.6 | 1.000 | 6 |
| tools | 75.5 | 78.2 | 1.000 | 5 |
| arts | 36.3 | 52.1 | 1.000 | 7 |

Status: {'ok': 150317}; harness complete: True, completed: 150317

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 476.5 min
- vLLM during the run: KV peak 65.6%, mean 15.1%, waiting peak 103, preemptions 0
