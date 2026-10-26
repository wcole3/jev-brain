# qwen3.6-27b calibration

## Provenance

- timestamp: 2026-10-26T032046Z
- repo commit: e8b57ea-dirty
- profile: qwen3.6-27b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: block32
- collect: .cache/collect/qwen3.6-27b/{calib,eval}-block32.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.590 | fitted -0.054 [-0.067, -0.033]; pooled -0.008 [-0.035, +0.020] → fitted |  | 0.637 → 0.529 | 0.543 → 0.475 | 0.057 → 0.022 | 0.076 → 0.022 | 0.837 |
| score | 259/554 | 2.041 (pooled; fitted 9.398) | fitted +0.138 [+0.068, +0.200]; pooled -0.031 [-0.070, +0.023] → pooled |  | 3.655 → 2.022 | 1.970 → 1.260 | 0.435 → 0.335 | 0.212 → 0.182 | 0.664 |
| noul | 670/666 | 1.425 | fitted -0.008 [-0.025, +0.011]; pooled +0.018 [-0.012, +0.042] → fitted | +0.000 | 0.270 → 0.252 | 0.276 → 0.257 | 0.044 → 0.036 | 0.044 → 0.036 | 0.892 |

pooled T (one T for every type, b = 0; the gate's fallback): 2.041

noul offset: fitted b = +0.458; eval accuracy change -0.0030 [-0.0120, +0.0060], ECE change -0.0003 [-0.0147, +0.0133] → not shipped (b = 0)

