# gemma-4-31b calibration

## Provenance

- timestamp: 2026-10-24T195030Z
- repo commit: 9f88454-dirty
- profile: gemma-4-31b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: reread32
- collect: .cache/collect/gemma-4-31b/{calib,eval}-reread32.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 4.019 | fitted -0.075 [-0.080, -0.063]; pooled -0.063 [-0.083, -0.039] → fitted |  | 1.817 → 0.588 | 2.153 → 0.635 | 0.130 → 0.033 | 0.153 → 0.078 | 0.839 |
| score | 259/554 | 5.366 (pooled; fitted 19.999 (edge)) | fitted -0.097 [-0.166, -0.018]; pooled -0.141 [-0.165, -0.098] → pooled |  | 10.278 → 2.057 | 5.535 → 1.252 | 0.534 → 0.417 | 0.328 → 0.187 | 0.661 |
| noul | 670/666 | 7.327 | fitted -0.072 [-0.081, -0.042]; pooled -0.043 [-0.048, -0.031] → fitted | +0.000 | 1.100 → 0.234 | 1.333 → 0.272 | 0.086 → 0.030 | 0.101 → 0.029 | 0.898 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.366

noul offset: fitted b = -0.293; eval accuracy change +0.0000 [-0.0045, +0.0045], ECE change -0.0018 [-0.0130, +0.0161] → not shipped (b = 0)

