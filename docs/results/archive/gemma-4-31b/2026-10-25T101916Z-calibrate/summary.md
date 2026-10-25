# gemma-4-31b calibration

## Provenance

- timestamp: 2026-10-25T101916Z
- repo commit: 54afc85-dirty
- profile: gemma-4-31b
- orders: top_p:0.9+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: h1qcap
- collect: .cache/collect/gemma-4-31b/{calib,eval}-h1qcap.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 4.020 | fitted -0.064 [-0.068, -0.051]; pooled -0.042 [-0.063, -0.022] → fitted |  | 1.701 → 0.548 | 2.034 → 0.593 | 0.112 → 0.036 | 0.140 → 0.076 | 0.853 |
| score | 259/554 | 5.385 (pooled; fitted 19.999 (edge)) | fitted -0.042 [-0.118, +0.034]; pooled -0.117 [-0.139, -0.071] → pooled |  | 10.552 → 2.075 | 5.297 → 1.196 | 0.540 → 0.439 | 0.295 → 0.177 | 0.688 |
| noul | 670/666 | 7.215 | fitted -0.045 [-0.060, -0.017]; pooled -0.030 [-0.037, -0.014] → fitted | +0.000 | 1.020 → 0.221 | 1.109 → 0.242 | 0.074 → 0.021 | 0.074 → 0.029 | 0.919 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.385

noul offset: fitted b = -0.322; eval accuracy change +0.0000 [-0.0060, +0.0060], ECE change -0.0046 [-0.0203, +0.0094] → not shipped (b = 0)

