# qwen3.8-27b calibration

## Provenance

- timestamp: 2026-10-26T041153Z
- repo commit: e8b57ea-dirty
- profile: qwen3.8-27b
- orders: min_n:4+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: block32
- collect: .cache/collect/qwen3.8-27b/{calib,eval}-block32.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.669 | fitted -0.032 [-0.050, -0.006]; pooled +0.003 [-0.025, +0.029] → fitted |  | 0.572 → 0.467 | 0.496 → 0.450 | 0.061 → 0.025 | 0.058 → 0.026 | 0.842 |
| score | 259/554 | 1.000 (none; fitted 6.009) | fitted +0.191 [+0.127, +0.228]; pooled +0.073 [+0.028, +0.096] → none |  | 2.747 → 2.747 | 1.573 → 1.573 | 0.353 → 0.353 | 0.150 → 0.150 | 0.682 |
| noul | 670/666 | 1.344 | fitted -0.001 [-0.013, +0.014]; pooled +0.030 [+0.004, +0.050] → fitted | +0.000 | 0.254 → 0.243 | 0.248 → 0.241 | 0.040 → 0.037 | 0.044 → 0.044 | 0.884 |

pooled T (one T for every type, b = 0; the gate's fallback): 2.003

noul offset: fitted b = +0.032; eval accuracy change +0.0000 [+0.0000, +0.0000], ECE change -0.0007 [-0.0076, +0.0042] → not shipped (b = 0)

