# qwen3.8-27b calibration

## Provenance

- timestamp: 2026-10-25T111642Z
- repo commit: 54afc85-dirty
- profile: qwen3.8-27b
- orders: min_n:4+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: h1qcap
- collect: .cache/collect/qwen3.8-27b/{calib,eval}-h1qcap.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.739 | fitted -0.024 [-0.045, +0.004]; pooled +0.013 [-0.016, +0.041] → fitted |  | 0.595 → 0.465 | 0.490 → 0.444 | 0.062 → 0.025 | 0.056 → 0.032 | 0.846 |
| score | 259/554 | 1.000 (none; fitted 6.105) | fitted +0.210 [+0.146, +0.250]; pooled +0.061 [+0.005, +0.093] → none |  | 2.809 → 2.809 | 1.567 → 1.567 | 0.356 → 0.356 | 0.136 → 0.136 | 0.700 |
| noul | 670/666 | 1.396 | fitted -0.004 [-0.018, +0.016]; pooled +0.027 [+0.002, +0.050] → fitted | +0.000 | 0.246 → 0.232 | 0.240 → 0.232 | 0.030 → 0.022 | 0.041 → 0.038 | 0.887 |

pooled T (one T for every type, b = 0; the gate's fallback): 2.056

noul offset: fitted b = +0.085; eval accuracy change +0.0000 [+0.0000, +0.0000], ECE change +0.0006 [-0.0110, +0.0079] → not shipped (b = 0)

