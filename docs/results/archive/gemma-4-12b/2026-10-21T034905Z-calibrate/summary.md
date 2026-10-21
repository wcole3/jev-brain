# gemma-4-12b calibration

## Provenance

- timestamp: 2026-10-21T034905Z
- repo commit: 06050a5
- profile: gemma-4-12b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/gemma-4-12b/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 4.035 (pooled; fitted 3.164) | fitted -0.105 [-0.116, -0.090]; pooled -0.128 [-0.151, -0.097] → pooled |  | 1.313 → 0.615 | 1.441 → 0.627 | 0.130 → 0.073 | 0.169 → 0.041 | 0.804 |
| score | 259/554 | 4.035 (pooled; fitted 16.225) | fitted -0.115 [-0.186, -0.044]; pooled -0.145 [-0.192, -0.077] → pooled |  | 7.274 → 1.990 | 4.114 → 1.462 | 0.519 → 0.383 | 0.368 → 0.223 | 0.560 |
| noul | 670/666 | 4.035 (pooled; fitted 3.594) | fitted -0.065 [-0.078, -0.046]; pooled -0.069 [-0.086, -0.040] → pooled | +0.000 | 0.501 → 0.244 | 0.664 → 0.287 | 0.076 → 0.029 | 0.116 → 0.046 | 0.862 |

pooled T (one T for every type, b = 0; the gate's fallback): 4.035

noul offset: fitted b = +0.177; eval accuracy change +0.0000 [-0.0075, +0.0075], ECE change +0.0003 [-0.0137, +0.0097] → not shipped (b = 0)

