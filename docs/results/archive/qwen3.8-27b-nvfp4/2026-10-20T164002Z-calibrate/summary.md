# qwen3.8-27b-nvfp4 calibration

## Provenance

- timestamp: 2026-10-20T164002Z
- repo commit: 0e16d32-dirty
- profile: qwen3.8-27b-nvfp4
- orders: min_n:4+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/qwen3.8-27b-nvfp4/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.681 | fitted -0.063 [-0.069, -0.034]; pooled -0.044 [-0.063, -0.010] → fitted |  | 0.587 → 0.477 | 0.542 → 0.479 | 0.062 → 0.024 | 0.077 → 0.014 | 0.816 |
| score | 259/554 | 1.967 (pooled; fitted 5.712) | fitted +0.141 [+0.069, +0.190]; pooled +0.036 [-0.015, +0.070] → pooled |  | 2.621 → 1.600 | 1.532 → 1.142 | 0.334 → 0.230 | 0.144 → 0.180 | 0.652 |
| noul | 670/666 | 1.139 | fitted +0.004 [-0.009, +0.013]; pooled +0.049 [+0.027, +0.065] → fitted | +0.000 | 0.230 → 0.228 | 0.233 → 0.231 | 0.038 → 0.040 | 0.031 → 0.035 | 0.889 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.967

noul offset: fitted b = -0.138; eval accuracy change -0.0015 [-0.0135, +0.0105], ECE change -0.0015 [-0.0118, +0.0123] → not shipped (b = 0)

