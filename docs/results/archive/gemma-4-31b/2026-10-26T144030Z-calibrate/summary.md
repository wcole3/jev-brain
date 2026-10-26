# gemma-4-31b calibration

## Provenance

- timestamp: 2026-10-26T144030Z
- repo commit: 8876925-dirty
- profile: gemma-4-31b
- orders: top_p:0.9+reversed
- choice T(n): a candidate in the T gate (--choice-tn)
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: reread32
- collect: .cache/collect/gemma-4-31b/{calib,eval}-reread32.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 6.849 -0.792 ln n (curve; fitted 3.983) | fitted -0.067 [-0.072, -0.054]; pooled -0.046 [-0.067, -0.026]; curve -0.099 [-0.104, -0.084] → curve |  | 1.708 → 0.515 | 2.104 → 0.511 | 0.117 → 0.038 | 0.145 → 0.046 | 0.847 |
| score | 259/554 | 5.301 (pooled; fitted 19.999 (edge)) | fitted -0.048 [-0.122, +0.028]; pooled -0.105 [-0.142, -0.059] → pooled |  | 10.183 → 2.058 | 5.226 → 1.235 | 0.536 → 0.426 | 0.301 → 0.196 | 0.675 |
| noul | 670/666 | 7.149 | fitted -0.062 [-0.070, -0.028]; pooled -0.033 [-0.040, -0.018] → fitted | +0.000 | 1.006 → 0.222 | 1.106 → 0.245 | 0.076 → 0.015 | 0.080 → 0.019 | 0.916 |

choice T(n) = 6.849 -0.792 ln n (T(2) 6.30, T(4) 5.75, T(16) 4.65): eval ECE 0.078 at constant T 3.983 → 0.046 on the curve, eval NLL 0.622 → 0.511 → shipped

pooled T (one T for every type, b = 0; the gate's fallback): 5.301

noul offset: fitted b = -0.273; eval accuracy change +0.0015 [-0.0045, +0.0075], ECE change +0.0038 [-0.0142, +0.0135] → not shipped (b = 0)

