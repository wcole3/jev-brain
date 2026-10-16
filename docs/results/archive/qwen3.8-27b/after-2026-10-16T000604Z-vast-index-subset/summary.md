# qwen3.8-27b Decision Index 0.3

## Provenance

- timestamp: 2026-10-16T012243Z
- repo commit: f200e45
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.99.02, PCIe 5x16, AMD Ryzen 9 9950X3D2 16-Core Processor (32 thr), 123 GB, vast 56172713
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/qwen3.8-27b/after-2026-10-16T000604Z-vast
- shards: 8
- ids: data/splits/vision-regression.json
- profile: qwen3.8-27b
- hf_model: Qwen/Qwen3.8-27B
- hf_revision: 1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
- prompt_layout: header
- option_orders: identity
- systemone_max_len: 32768
- calibration: {'decider_chat': {'T': {'choice': 1.4961189013294809, 'score': 1.6648399367497366, 'noul': 0.972520554755731}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 1.535520473719803, 'score': 1.774876073414086, 'noul': 0.9625437832558383}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 1.3508723711404127, 'score': 6.269890636485391, 'noul': 0.8313413948726119}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: qwen3.8-27b** | 0.53 | — | 0.029 | 702.9 | 1.000 |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | 373.0 | board |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | 108.3 | board |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | 89.6 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 0.0 | 1.6 | 0.031 | 11 |
| language | 0.0 | 2.3 | 0.036 | 9 |
| retrieval | 0.2 | 2.1 | 0.034 | 6 |
| tools | 2.6 | 4.2 | 0.065 | 5 |
| arts | 0.0 | 1.1 | 0.023 | 6 |

Status: {'ok': 3120}; harness complete: False, completed: 3120

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0, 0, 0, 0, 0], wall 13.0 min
- vLLM during the run: KV peak 56.1%, mean 14.5%, waiting peak 315, preemptions 0
