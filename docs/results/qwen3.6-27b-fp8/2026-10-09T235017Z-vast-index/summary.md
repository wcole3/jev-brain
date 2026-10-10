# qwen3.6-27b-fp8 Decision Index 0.3

## Provenance

- timestamp: 2026-10-09T235017Z
- repo commit: ee5e4be
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 615.71.09, PCIe 5x16, AMD Ryzen Threadripper PRO 9955WX 16-Cores (32 thr), 251 GB, vast 55115714
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/qwen3.6-27b-fp8/2026-10-09T235017Z-vast
- shards: 4
- ids: full suite
- profile: qwen3.6-27b-fp8
- hf_model: Qwen/Qwen3.6-27B-FP8
- hf_revision: e89b16ebf1988b3d6befa7de50abc2d76f26eb09
- prompt_layout: header
- option_orders: identity
- systemone_max_len: 32768
- calibration: {'decider_chat': {'T': {'choice': 1.6585098155596096, 'score': 1.9436420520554476, 'noul': 1.4027279458983484}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.6323603603116188, 'score': 1.9743652236518074, 'noul': 1.2859386323824527}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.475862833432394, 'score': 7.858322898611463, 'noul': 1.2234832727963472}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: qwen3.6-27b-fp8** | 56.41 | — | 0.047 | 210.8 | 1.000 |
| Decider chat · Qwen3.6-27B | 51.57 | 51.25 | 0.021 | 83.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 39.6 | 53.0 | 1.000 | 11 |
| language | 63.4 | 74.1 | 1.000 | 9 |
| retrieval | 60.8 | 70.2 | 0.998 | 6 |
| tools | 74.3 | 76.7 | 0.999 | 5 |
| arts | 40.3 | 60.1 | 1.000 | 6 |

Status: {'ok': 140171, 'unsupported': 7}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- summary written locally from the pulled run: the box's summary step raised KeyError in board.py (fixed in f6ead9c) after every row had run.
