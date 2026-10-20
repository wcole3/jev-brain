# gemma-4-31b-fp8 calibration

## Provenance

- timestamp: 2026-10-20T163846Z
- repo commit: 0e16d32-dirty
- profile: gemma-4-31b-fp8
- orders: top_p:0.9+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/gemma-4-31b-fp8/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 4.064 | fitted -0.070 [-0.076, -0.058]; pooled -0.057 [-0.077, -0.035] → fitted |  | 1.734 → 0.558 | 2.096 → 0.620 | 0.118 → 0.037 | 0.149 → 0.078 | 0.841 |
| score | 259/554 | 5.313 (pooled; fitted 19.985 (edge)) | fitted -0.017 [-0.090, +0.053]; pooled -0.088 [-0.125, -0.042] → pooled |  | 9.628 → 1.959 | 4.992 → 1.198 | 0.528 → 0.405 | 0.291 → 0.203 | 0.691 |
| noul | 670/666 | 6.658 | fitted -0.056 [-0.066, -0.031]; pooled -0.041 [-0.048, -0.021] → fitted | +0.000 | 0.897 → 0.211 | 1.063 → 0.246 | 0.065 → 0.029 | 0.079 → 0.023 | 0.916 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.313

noul offset: fitted b = -0.041; eval accuracy change +0.0000 [+0.0000, +0.0000], ECE change -0.0002 [-0.0100, +0.0102] → not shipped (b = 0)

