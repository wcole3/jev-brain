# gemma-4-31b calibration

## Provenance

- timestamp: 2026-10-20T173145Z
- repo commit: 326d316
- profile: gemma-4-31b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/gemma-4-31b/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 3.978 | fitted -0.077 [-0.082, -0.066]; pooled -0.069 [-0.091, -0.046] → fitted |  | 1.776 → 0.575 | 2.153 → 0.638 | 0.127 → 0.039 | 0.157 → 0.081 | 0.838 |
| score | 259/554 | 5.280 (pooled; fitted 19.999 (edge)) | fitted -0.101 [-0.170, -0.022]; pooled -0.161 [-0.177, -0.110] → pooled |  | 10.066 → 2.050 | 5.408 → 1.254 | 0.537 → 0.415 | 0.334 → 0.173 | 0.657 |
| noul | 670/666 | 7.104 | fitted -0.066 [-0.075, -0.041]; pooled -0.041 [-0.050, -0.027] → fitted | +0.000 | 1.053 → 0.232 | 1.365 → 0.285 | 0.081 → 0.043 | 0.108 → 0.042 | 0.890 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.280

noul offset: fitted b = -0.066; eval accuracy change +0.0015 [+0.0000, +0.0045], ECE change -0.0031 [-0.0142, +0.0065] → not shipped (b = 0)

