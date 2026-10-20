# qwen3.8-27b-nvfp4 Decision Index 0.3

## Provenance

- timestamp: 2026-10-20T222510Z
- repo commit: 326d316
- host: RTX PRO 6000 Blackwell, 500/600 W, drv 580.178.04, PCIe 5x16, AMD Ryzen Threadripper PRO 7995WX 96-Cores (192 thr), 251 GB, vast 56910924
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/qwen3.8-27b-nvfp4/2026-10-20T152132Z-vast
- shards: 4
- ids: full suite
- profile: qwen3.8-27b-nvfp4
- hf_model: RadixArk/Qwen3.8-27B-NVFP4
- hf_revision: 319f741cce68d7914884900c138a1fbb70a42f30
- prompt_layout: blurb_header
- option_orders: min_n:4+reversed
- option_orders_images: 
- systemone_max_len: 32768
- calibration: {'blurb_header': {'T': {'choice': 1.6807640584736696, 'score': 1.9672694770276271, 'noul': 1.1388145341309106}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/blurb_header/calibration.json', 'orders': 'min_n:4+reversed'}, 'decider_chat': {'T': {'choice': 1.534912409014274, 'score': 1.6956928316925777, 'noul': 0.9175902098440983}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.5971415409111187, 'score': 1.829572794304793, 'noul': 0.9633966437867898}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3876276536831984, 'score': 1.7744416557968425, 'noul': 0.9417765210190306}, 'b': 0.0, 'source': 'qwen3.8-27b-nvfp4/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: qwen3.8-27b-nvfp4** | 56.63 | — | 0.025 | 247.2 | 1.000 |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | 373.0 | board |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | 108.3 | board |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | 89.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 37.3 | 51.2 | 1.000 | 11 |
| language | 61.9 | 73.5 | 1.000 | 9 |
| retrieval | 64.5 | 72.7 | 0.998 | 6 |
| tools | 76.6 | 79.1 | 0.999 | 5 |
| arts | 40.6 | 59.4 | 1.000 | 6 |

Status: {'ok': 140171, 'unsupported': 7}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 328.5 min
- vLLM during the run: KV peak 49.0%, mean 5.6%, waiting peak 229, preemptions 0
