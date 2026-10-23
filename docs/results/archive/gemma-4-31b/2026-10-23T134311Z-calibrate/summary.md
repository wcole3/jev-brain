# gemma-4-31b calibration

## Provenance

- timestamp: 2026-10-23T134311Z
- repo commit: 8eeab99-dirty
- profile: gemma-4-31b
- orders: top_p:0.9+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: reread
- collect: .cache/collect/gemma-4-31b/{calib,eval}-reread.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 3.993 | fitted -0.064 [-0.071, -0.052]; pooled -0.045 [-0.066, -0.024] → fitted |  | 1.717 → 0.561 | 2.039 → 0.607 | 0.119 → 0.036 | 0.140 → 0.076 | 0.850 |
| score | 259/554 | 5.306 (pooled; fitted 19.999 (edge)) | fitted -0.046 [-0.121, +0.029]; pooled -0.102 [-0.139, -0.053] → pooled |  | 10.214 → 2.061 | 5.262 → 1.238 | 0.535 → 0.434 | 0.300 → 0.199 | 0.679 |
| noul | 670/666 | 7.121 | fitted -0.056 [-0.066, -0.026]; pooled -0.033 [-0.039, -0.016] → fitted | +0.000 | 0.998 → 0.220 | 1.083 → 0.243 | 0.073 → 0.020 | 0.077 → 0.021 | 0.917 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.306

noul offset: fitted b = -0.253; eval accuracy change +0.0000 [-0.0075, +0.0075], ECE change +0.0044 [-0.0104, +0.0144] → not shipped (b = 0)

