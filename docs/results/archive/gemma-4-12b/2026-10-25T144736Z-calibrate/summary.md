# gemma-4-12b calibration

## Provenance

- timestamp: 2026-10-25T144736Z
- repo commit: dba35fb-dirty
- profile: gemma-4-12b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: h1qcap
- collect: .cache/collect/gemma-4-12b/{calib,eval}-h1qcap.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 4.018 (pooled; fitted 3.158) | fitted -0.103 [-0.108, -0.090]; pooled -0.116 [-0.136, -0.083] → pooled |  | 1.299 → 0.598 | 1.330 → 0.574 | 0.115 → 0.081 | 0.152 → 0.036 | 0.830 |
| score | 259/554 | 4.018 (pooled; fitted 15.338) | fitted -0.106 [-0.179, -0.030]; pooled -0.169 [-0.207, -0.108] → pooled |  | 7.146 → 1.946 | 4.031 → 1.382 | 0.510 → 0.379 | 0.371 → 0.202 | 0.585 |
| noul | 670/666 | 4.018 (pooled; fitted 3.804) | fitted -0.072 [-0.077, -0.046]; pooled -0.072 [-0.082, -0.042] → pooled | +0.000 | 0.517 → 0.234 | 0.630 → 0.267 | 0.080 → 0.023 | 0.096 → 0.024 | 0.883 |

pooled T (one T for every type, b = 0; the gate's fallback): 4.018

noul offset: fitted b = -0.177; eval accuracy change +0.0000 [-0.0075, +0.0075], ECE change +0.0016 [-0.0131, +0.0151] → not shipped (b = 0)

