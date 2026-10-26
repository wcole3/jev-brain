# gemma-4-12b calibration

## Provenance

- timestamp: 2026-10-26T023406Z
- repo commit: e8b57ea-dirty
- profile: gemma-4-12b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: block32
- collect: .cache/collect/gemma-4-12b/{calib,eval}-block32.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 4.030 (pooled; fitted 3.162) | fitted -0.102 [-0.111, -0.086]; pooled -0.110 [-0.133, -0.078] → pooled |  | 1.341 → 0.626 | 1.356 → 0.600 | 0.128 → 0.075 | 0.153 → 0.042 | 0.822 |
| score | 259/554 | 4.030 (pooled; fitted 15.794) | fitted -0.059 [-0.128, +0.010]; pooled -0.092 [-0.143, -0.033] → pooled |  | 7.203 → 1.966 | 3.934 → 1.389 | 0.526 → 0.388 | 0.335 → 0.244 | 0.603 |
| noul | 670/666 | 3.760 | fitted -0.069 [-0.077, -0.043]; pooled -0.069 [-0.082, -0.038] → fitted | +0.000 | 0.507 → 0.238 | 0.612 → 0.268 | 0.072 → 0.027 | 0.094 → 0.025 | 0.884 |

pooled T (one T for every type, b = 0; the gate's fallback): 4.030

noul offset: fitted b = -0.104; eval accuracy change +0.0000 [-0.0090, +0.0075], ECE change -0.0051 [-0.0166, +0.0092] → not shipped (b = 0)

