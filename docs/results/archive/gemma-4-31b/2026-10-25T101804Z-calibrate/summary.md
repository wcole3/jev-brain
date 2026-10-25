# gemma-4-31b calibration

## Provenance

- timestamp: 2026-10-25T101804Z
- repo commit: 54afc85-dirty
- profile: gemma-4-31b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: h1qcap
- collect: .cache/collect/gemma-4-31b/{calib,eval}-h1qcap.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 4.040 | fitted -0.069 [-0.074, -0.056]; pooled -0.047 [-0.070, -0.025] → fitted |  | 1.787 → 0.568 | 2.069 → 0.601 | 0.123 → 0.035 | 0.146 → 0.077 | 0.851 |
| score | 259/554 | 5.451 (pooled; fitted 19.999 (edge)) | fitted -0.077 [-0.147, +0.002]; pooled -0.124 [-0.148, -0.085] → pooled |  | 10.608 → 2.066 | 5.482 → 1.209 | 0.536 → 0.434 | 0.315 → 0.191 | 0.675 |
| noul | 670/666 | 7.520 | fitted -0.061 [-0.076, -0.030]; pooled -0.037 [-0.044, -0.024] → fitted | +0.000 | 1.151 → 0.237 | 1.388 → 0.274 | 0.083 → 0.032 | 0.099 → 0.038 | 0.901 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.451

noul offset: fitted b = -0.353; eval accuracy change -0.0015 [-0.0060, +0.0030], ECE change -0.0076 [-0.0206, +0.0098] → not shipped (b = 0)

