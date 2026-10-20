# qwen3.6-27b calibration

## Provenance

- timestamp: 2026-10-20T173146Z
- repo commit: 326d316
- profile: qwen3.6-27b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/qwen3.6-27b/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.625 | fitted -0.056 [-0.068, -0.032]; pooled -0.014 [-0.044, +0.016] → fitted |  | 0.663 → 0.543 | 0.561 → 0.496 | 0.066 → 0.022 | 0.081 → 0.025 | 0.820 |
| score | 259/554 | 2.061 (pooled; fitted 9.973) | fitted +0.191 [+0.115, +0.239]; pooled +0.048 [-0.007, +0.072] → pooled |  | 3.701 → 2.041 | 1.998 → 1.291 | 0.415 → 0.308 | 0.177 → 0.225 | 0.673 |
| noul | 670/666 | 1.265 | fitted -0.011 [-0.025, +0.009]; pooled +0.035 [-0.000, +0.059] → fitted | +0.000 | 0.245 → 0.238 | 0.253 → 0.245 | 0.035 → 0.030 | 0.035 → 0.025 | 0.898 |

pooled T (one T for every type, b = 0; the gate's fallback): 2.061

noul offset: fitted b = +0.446; eval accuracy change +0.0060 [-0.0075, +0.0195], ECE change -0.0073 [-0.0207, +0.0105] → not shipped (b = 0)

