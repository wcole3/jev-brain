# gemma-4-31b-fp8 Decision Index 0.3

## Provenance

- timestamp: 2026-10-10T084159Z
- repo commit: 53b6615
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 595.71.05, PCIe 5x16, Intel(R) Core(TM) Ultra 9 285K (24 thr), 188 GB, vast 55115712
- harness: 9eb2dbe2a358004c8782c66e40a83ac07b953fec
- edition: 0.3
- run dir: .cache/index-runs/gemma-4-31b-fp8/2026-10-09T234758Z-vast
- shards: 4
- ids: full suite
- profile: gemma-4-31b-fp8
- hf_model: RedHatAI/gemma-4-31B-it-FP8-block
- hf_revision: d7242548c457ab4b45bd3adb8937f2659af4739d
- prompt_layout: header
- option_orders: identity
- systemone_max_len: 32768
- calibration: {'decider_chat': {'T': {'choice': 5.363447128397169, 'score': 5.363447128397169, 'noul': 7.429858290799572}, 'b': -0.6607285712296436, 'source': 'gemma-4-31b-fp8/decider_chat/calibration.json', 'orders': 'identity'}, 'header': {'T': {'choice': 4.26925012489692, 'score': 5.57005202284913, 'noul': 7.570546716767989}, 'b': 0.0, 'source': 'gemma-4-31b-fp8/header/calibration.json', 'orders': 'identity'}, 'question_first': {'T': {'choice': 3.871975258837799, 'score': 5.270830338695965, 'noul': 7.328579609654185}, 'b': -0.5101802033029419, 'source': 'gemma-4-31b-fp8/question_first/calibration.json', 'orders': 'identity'}}
- vllm_version: 0.30.0

| entry | Index | Full | ECE | median ms | coverage |
|---|---|---|---|---|---|
| **ours: gemma-4-31b-fp8** | 61.56 | — | 0.118 | 201.4 | 1.000 |
| Decider chat · Gemma-4-31B | 57.79 | 57.62 | 0.047 | 108.5 | board |
| Jev (hosted API, latency over HTTPS) | 57.96 | 60.11 | 0.074 | 524.1 | board |

| area | skill | raw | coverage | n |
|---|---|---|---|---|
| knowledge | 48.6 | 59.6 | 1.000 | 11 |
| language | 65.6 | 75.8 | 1.000 | 9 |
| retrieval | 67.2 | 74.2 | 0.995 | 6 |
| tools | 76.5 | 79.0 | 0.999 | 5 |
| arts | 45.8 | 64.0 | 1.000 | 6 |

Status: {'ok': 140167, 'unsupported': 11}; harness complete: True, completed: 140178

- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals); the board's ECE uses its own row set, so compare loosely.
- median ms: the harness's per-request wall time with all shards running at once, not latency-v1; see the latency report for the comparable figure.
- shard exit codes: [0, 0, 0, 0], wall 0.0 min
- vLLM during the run: KV peak 0.0%, mean 0.0%, waiting peak 0, preemptions 0
