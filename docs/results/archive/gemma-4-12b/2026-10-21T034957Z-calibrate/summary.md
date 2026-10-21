# gemma-4-12b calibration

## Provenance

- timestamp: 2026-10-21T034957Z
- repo commit: 06050a5-dirty
- profile: gemma-4-12b
- orders: top_p:0.9+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/gemma-4-12b/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 3.985 (pooled; fitted 3.112) | fitted -0.089 [-0.100, -0.075]; pooled -0.116 [-0.134, -0.086] → pooled |  | 1.182 → 0.564 | 1.316 → 0.588 | 0.115 → 0.071 | 0.154 → 0.038 | 0.815 |
| score | 259/554 | 3.985 (pooled; fitted 15.641) | fitted -0.026 [-0.099, +0.043]; pooled -0.046 [-0.105, +0.009] → pooled |  | 7.010 → 1.965 | 3.937 → 1.446 | 0.480 → 0.352 | 0.311 → 0.266 | 0.590 |
| noul | 670/666 | 3.985 (pooled; fitted 3.590) | fitted -0.067 [-0.078, -0.047]; pooled -0.074 [-0.086, -0.041] → pooled | +0.000 | 0.492 → 0.240 | 0.649 → 0.282 | 0.071 → 0.030 | 0.105 → 0.031 | 0.878 |

pooled T (one T for every type, b = 0; the gate's fallback): 3.985

noul offset: fitted b = +0.093; eval accuracy change -0.0045 [-0.0120, +0.0015], ECE change -0.0031 [-0.0128, +0.0085] → not shipped (b = 0)

