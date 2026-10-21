# gemma-4-31b Decision Index 0.3

## Provenance

- timestamp: 2026-10-21T072157Z
- repo commit: 18ab6ae
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.71.05, PCIe 5x16, Intel(R) Core(TM) Ultra 9 285K (24 thr), 188 GB, vast 56912441
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/gemma-4-31b/2026-10-20T154258Z-vast
- shards: 4
- ids: full suite
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: blurb_header
- option_orders: top_p:0.9+reversed
- option_orders_images: identity
- systemone_max_len: 65536
- calibration: {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.210749661448452, 'noul': 6.742793031492776}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration.json', 'orders': 'top_p:0.9+reversed'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {'identity': {'blurb_header': {'T': {'choice': 3.978299829298446, 'score': 5.279869783685001, 'noul': 7.103855559793786}, 'b': 0.0, 'source': 'gemma-4-31b/blurb_header/calibration-identity.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: gemma-4-31b** | 62.98 | — | 0.119 | 383.8 | 1.000 |
| Decider chat · Gemma-4-31B | 57.79 | 57.62 | 0.047 | 108.5 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 50.3 | 60.8 | 1.000 | 11 |
| language | 67.0 | 76.7 | 1.000 | 9 |
| retrieval | 67.3 | 74.6 | 1.000 | 6 |
| tools | 78.0 | 80.2 | 1.000 | 5 |
| arts | 49.2 | 66.3 | 1.000 | 6 |

Status: {'ok': 140178}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 812.9 min
- vLLM during the run: KV peak 100.0%, mean 26.0%, waiting peak 194, preemptions 240
