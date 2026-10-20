# qwen3.8-27b calibration

## Provenance

- timestamp: 2026-10-20T164002Z
- repo commit: 0e16d32-dirty
- profile: qwen3.8-27b
- orders: min_n:4+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/qwen3.8-27b/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.641 | fitted -0.039 [-0.050, -0.006]; pooled -0.002 [-0.028, +0.027] → fitted |  | 0.564 → 0.466 | 0.503 → 0.469 | 0.055 → 0.022 | 0.056 → 0.018 | 0.819 |
| score | 259/554 | 1.000 (none; fitted 5.683) | fitted +0.193 [+0.121, +0.224]; pooled +0.077 [+0.019, +0.094] → none |  | 2.625 → 2.625 | 1.523 → 1.523 | 0.363 → 0.363 | 0.130 → 0.130 | 0.666 |
| noul | 670/666 | 1.212 | fitted +0.002 [-0.013, +0.014]; pooled +0.039 [+0.011, +0.059] → fitted | +0.000 | 0.241 → 0.237 | 0.242 → 0.239 | 0.024 → 0.032 | 0.039 → 0.040 | 0.881 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.945

noul offset: fitted b = +0.084; eval accuracy change +0.0000 [+0.0000, +0.0000], ECE change -0.0023 [-0.0138, +0.0064] → not shipped (b = 0)

