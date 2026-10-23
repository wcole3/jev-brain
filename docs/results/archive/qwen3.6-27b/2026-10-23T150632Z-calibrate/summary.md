# qwen3.6-27b calibration

## Provenance

- timestamp: 2026-10-23T150632Z
- repo commit: b6aac0f-dirty
- profile: qwen3.6-27b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: reread
- collect: .cache/collect/qwen3.6-27b/{calib,eval}-reread.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.590 | fitted -0.061 [-0.068, -0.035]; pooled -0.017 [-0.045, +0.012] → fitted |  | 0.638 → 0.531 | 0.546 → 0.476 | 0.060 → 0.027 | 0.081 → 0.020 | 0.837 |
| score | 259/554 | 2.030 (pooled; fitted 9.321) | fitted +0.161 [+0.087, +0.215]; pooled -0.014 [-0.065, +0.028] → pooled |  | 3.603 → 2.009 | 1.959 → 1.259 | 0.439 → 0.336 | 0.197 → 0.182 | 0.668 |
| noul | 670/666 | 1.418 | fitted -0.004 [-0.017, +0.011]; pooled +0.016 [-0.011, +0.041] → fitted | +0.000 | 0.270 → 0.252 | 0.279 → 0.259 | 0.046 → 0.038 | 0.046 → 0.042 | 0.890 |

pooled T (one T for every type, b = 0; the gate's fallback): 2.030

noul offset: fitted b = +0.507; eval accuracy change +0.0045 [-0.0075, +0.0165], ECE change -0.0091 [-0.0257, +0.0107] → not shipped (b = 0)

