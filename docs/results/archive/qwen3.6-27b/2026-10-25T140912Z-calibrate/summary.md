# qwen3.6-27b calibration

## Provenance

- timestamp: 2026-10-25T140912Z
- repo commit: 6a209a4-dirty
- profile: qwen3.6-27b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: h1qcap
- collect: .cache/collect/qwen3.6-27b/{calib,eval}-h1qcap.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.660 | fitted -0.068 [-0.072, -0.043]; pooled -0.024 [-0.051, +0.006] → fitted |  | 0.648 → 0.519 | 0.544 → 0.456 | 0.067 → 0.023 | 0.083 → 0.015 | 0.843 |
| score | 259/554 | 2.131 (pooled; fitted 9.396) | fitted +0.105 [+0.027, +0.167]; pooled -0.052 [-0.096, -0.006] → pooled |  | 3.747 → 1.990 | 2.011 → 1.226 | 0.422 → 0.303 | 0.203 → 0.151 | 0.671 |
| noul | 670/666 | 1.593 | fitted -0.023 [-0.035, +0.002]; pooled -0.000 [-0.027, +0.028] → fitted | +0.000 | 0.280 → 0.249 | 0.278 → 0.249 | 0.053 → 0.030 | 0.056 → 0.033 | 0.893 |

pooled T (one T for every type, b = 0; the gate's fallback): 2.131

noul offset: fitted b = +0.332; eval accuracy change +0.0000 [-0.0060, +0.0060], ECE change -0.0048 [-0.0176, +0.0086] → not shipped (b = 0)

