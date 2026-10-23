# gemma-4-12b calibration

## Provenance

- timestamp: 2026-10-23T142452Z
- repo commit: 37d82f5-dirty
- profile: gemma-4-12b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: reread
- collect: .cache/collect/gemma-4-12b/{calib,eval}-reread.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 4.047 (pooled; fitted 3.186) | fitted -0.112 [-0.116, -0.093]; pooled -0.115 [-0.137, -0.083] → pooled |  | 1.355 → 0.629 | 1.369 → 0.605 | 0.126 → 0.078 | 0.160 → 0.045 | 0.815 |
| score | 259/554 | 4.047 (pooled; fitted 15.816) | fitted -0.047 [-0.118, +0.025]; pooled -0.093 [-0.140, -0.032] → pooled |  | 7.228 → 1.963 | 3.917 → 1.381 | 0.526 → 0.384 | 0.332 → 0.240 | 0.605 |
| noul | 670/666 | 3.741 | fitted -0.069 [-0.077, -0.042]; pooled -0.069 [-0.081, -0.038] → fitted | +0.000 | 0.503 → 0.236 | 0.603 → 0.267 | 0.073 → 0.029 | 0.098 → 0.029 | 0.878 |

pooled T (one T for every type, b = 0; the gate's fallback): 4.047

noul offset: fitted b = -0.090; eval accuracy change +0.0045 [-0.0015, +0.0105], ECE change -0.0071 [-0.0122, +0.0072] → not shipped (b = 0)

