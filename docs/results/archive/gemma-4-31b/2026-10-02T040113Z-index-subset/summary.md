# gemma-4-31b Decision Index 0.2.1

## Provenance

- timestamp: 2026-10-02T040820Z
- repo commit: 7a5d9b6
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.84, PCIe 4x16, AMD Ryzen Threadripper 3960X 24-Core Processor (48 thr), 189 GB, vast 53799016
- harness: 87d4650b42b377c0291a89c1f1a879f9b31082bf
- edition: 0.2.1
- run dir: .cache/index-runs/gemma-4-31b/2026-10-02T040113Z
- shards: 4
- ids: /workspace/jev-brain/data/splits/compare-2k.json
- profile: gemma-4-31b
- hf_model: google/gemma-4-31B-it
- hf_revision: 842da3794eaa0b77d5f08bae87a17459d91ff475
- prompt_layout: decider_chat
- option_orders: identity
- systemone_max_len: 32768
- temperatures: {'decider_chat': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'header': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'question_first': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}}
- vllm_version: 0.30.0

| entry | Index | ECE | median ms | coverage |
|---|---|---|---|---|
| **ours: gemma-4-31b** | 0.10 | 0.220 | 350.9 | 1.000 |
| Decider chat · Gemma-4-31B | 57.33 | 0.047 | 108.5 | board |
| Jev (hosted API, latency over HTTPS) | 57.90 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 0.0 | 0.6 | 0.013 | 10 |
| language | 0.0 | 0.9 | 0.013 | 10 |
| retrieval | 0.1 | 0.8 | 0.013 | 6 |
| tools | 0.4 | 1.3 | 0.015 | 5 |
| arts | 0.0 | 0.8 | 0.013 | 7 |

Status: {'ok': 2016}; harness complete: False, completed: 2016

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 6.6 min
- vLLM during the run: KV peak 52.2%, mean 13.8%, waiting peak 46, preemptions 0
