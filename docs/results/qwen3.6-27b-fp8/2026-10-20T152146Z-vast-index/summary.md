# qwen3.6-27b-fp8 Decision Index 0.3

## Provenance

- timestamp: 2026-10-21T003601Z
- repo commit: f97f710
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 615.71.09, PCIe 5x16, AMD EPYC 9334 32-Core Processor (64 thr), 188 GB, vast 56942374
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/qwen3.6-27b-fp8/2026-10-20T152146Z-vast
- shards: 4
- ids: full suite
- profile: qwen3.6-27b-fp8
- hf_model: Qwen/Qwen3.6-27B-FP8
- hf_revision: e89b16ebf1988b3d6befa7de50abc2d76f26eb09
- prompt_layout: blurb_header
- option_orders: identity
- option_orders_images: 
- systemone_max_len: 32768
- calibration: {'blurb_header': {'T': {'choice': 1.6087767463450138, 'score': 2.0371306533981115, 'noul': 1.2594265719567521}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/blurb_header/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.6585098155596096, 'score': 1.9436420520554476, 'noul': 1.4027279458983484}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.6323603603116188, 'score': 1.9743652236518074, 'noul': 1.2859386323824527}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.475862833432394, 'score': 7.858322898611463, 'noul': 1.2234832727963472}, 'b': 0.0, 'source': 'qwen3.6-27b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: qwen3.6-27b-fp8** | 56.78 | — | 0.049 | 207.4 | 1.000 |
| Decider chat · Qwen3.6-27B | 51.57 | 51.25 | 0.021 | 83.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 39.6 | 52.9 | 1.000 | 11 |
| language | 64.0 | 74.5 | 1.000 | 9 |
| retrieval | 62.8 | 71.2 | 0.998 | 6 |
| tools | 74.3 | 76.6 | 0.999 | 5 |
| arts | 38.5 | 59.2 | 1.000 | 6 |

Status: {'ok': 140171, 'unsupported': 7}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 273.5 min
- vLLM during the run: KV peak 51.6%, mean 5.8%, waiting peak 208, preemptions 0
