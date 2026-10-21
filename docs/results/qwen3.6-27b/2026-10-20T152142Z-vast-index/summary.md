# qwen3.6-27b Decision Index 0.3

## Provenance

- timestamp: 2026-10-21T064911Z
- repo commit: f97f710
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.71.05, PCIe 5x16, AMD Ryzen 9 9950X 16-Core Processor (32 thr), 188 GB, vast 56942372
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/qwen3.6-27b/2026-10-20T152142Z-vast
- shards: 4
- ids: full suite
- profile: qwen3.6-27b
- hf_model: Qwen/Qwen3.6-27B
- hf_revision: 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- prompt_layout: blurb_header
- option_orders: identity
- option_orders_images: 
- systemone_max_len: 32768
- calibration: {'blurb_header': {'T': {'choice': 1.6251477909763543, 'score': 2.061197148900324, 'noul': 1.264734324887902}, 'b': 0.0, 'source': 'qwen3.6-27b/blurb_header/calibration.json', 'orders': 'identity'}, 'decider_chat': {'T': {'choice': 1.6464561210660535, 'score': 1.9262389103053306, 'noul': 1.3881277937743584}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.627044078638005, 'score': 1.957392235350462, 'noul': 1.2806898963469258}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.4848491265570403, 'score': 8.036469832567235, 'noul': 1.146202489120627}, 'b': 0.2558914960106792, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}
- other_calibrations: {}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: qwen3.6-27b** | 56.82 | — | 0.048 | 455.9 | 1.000 |
| Decider chat · Qwen3.6-27B | 51.57 | 51.25 | 0.021 | 83.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

Parity gate vs Decider chat · Qwen3.6-27B: +5.25 (±1.5) → MISS: file a ticket before M2

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 39.7 | 53.0 | 1.000 | 11 |
| language | 64.1 | 74.5 | 1.000 | 9 |
| retrieval | 62.4 | 71.1 | 0.998 | 6 |
| tools | 74.6 | 76.9 | 0.999 | 5 |
| arts | 38.6 | 59.2 | 1.000 | 6 |

Status: {'ok': 140171, 'unsupported': 7}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 638.6 min
- vLLM during the run: KV peak 94.7%, mean 10.3%, waiting peak 174, preemptions 0
