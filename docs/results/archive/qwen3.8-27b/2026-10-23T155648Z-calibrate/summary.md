# qwen3.8-27b calibration

## Provenance

- timestamp: 2026-10-23T155648Z
- repo commit: 166c00f-dirty
- profile: qwen3.8-27b
- orders: min_n:4+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: reread
- collect: .cache/collect/qwen3.8-27b/{calib,eval}-reread.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.676 | fitted -0.032 [-0.052, -0.006]; pooled +0.002 [-0.027, +0.028] → fitted |  | 0.578 → 0.470 | 0.494 → 0.448 | 0.062 → 0.025 | 0.060 → 0.028 | 0.840 |
| score | 259/554 | 1.000 (none; fitted 5.935) | fitted +0.178 [+0.111, +0.215]; pooled +0.070 [+0.019, +0.096] → none |  | 2.727 → 2.727 | 1.568 → 1.568 | 0.358 → 0.358 | 0.148 → 0.148 | 0.682 |
| noul | 670/666 | 1.316 | fitted -0.000 [-0.015, +0.014]; pooled +0.031 [+0.006, +0.052] → fitted | +0.000 | 0.250 → 0.241 | 0.247 → 0.241 | 0.044 → 0.036 | 0.046 → 0.046 | 0.881 |

pooled T (one T for every type, b = 0; the gate's fallback): 2.001

noul offset: fitted b = +0.001; eval accuracy change +0.0000 [+0.0000, +0.0000], ECE change +0.0000 [-0.0000, +0.0000] → not shipped (b = 0)

