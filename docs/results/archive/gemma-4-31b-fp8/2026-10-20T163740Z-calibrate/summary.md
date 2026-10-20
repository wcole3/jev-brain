# gemma-4-31b-fp8 calibration

## Provenance

- timestamp: 2026-10-20T163740Z
- repo commit: 0e16d32-dirty
- profile: gemma-4-31b-fp8
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/gemma-4-31b-fp8/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 4.080 | fitted -0.081 [-0.087, -0.068]; pooled -0.079 [-0.098, -0.052] → fitted |  | 1.814 → 0.576 | 2.177 → 0.635 | 0.127 → 0.052 | 0.163 → 0.082 | 0.834 |
| score | 259/554 | 5.401 (pooled; fitted 19.999 (edge)) | fitted -0.102 [-0.174, -0.025]; pooled -0.149 [-0.170, -0.101] → pooled |  | 9.844 → 1.976 | 5.333 → 1.226 | 0.537 → 0.411 | 0.333 → 0.184 | 0.653 |
| noul | 670/666 | 7.147 | fitted -0.065 [-0.080, -0.035]; pooled -0.049 [-0.053, -0.035] → fitted | +0.000 | 1.101 → 0.236 | 1.402 → 0.288 | 0.083 → 0.048 | 0.109 → 0.044 | 0.890 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.401

noul offset: fitted b = -0.156; eval accuracy change -0.0015 [-0.0045, +0.0000], ECE change -0.0045 [-0.0179, +0.0094] → not shipped (b = 0)

