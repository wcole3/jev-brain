# qwen3.6-27b-fp8 calibration

## Provenance

- timestamp: 2026-10-20T164002Z
- repo commit: 0e16d32-dirty
- profile: qwen3.6-27b-fp8
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/qwen3.6-27b-fp8/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.609 | fitted -0.059 [-0.069, -0.039]; pooled -0.032 [-0.056, +0.001] → fitted |  | 0.652 → 0.538 | 0.572 → 0.501 | 0.065 → 0.028 | 0.088 → 0.028 | 0.814 |
| score | 259/554 | 2.037 (pooled; fitted 9.729) | fitted +0.164 [+0.088, +0.217]; pooled +0.009 [-0.043, +0.046] → pooled |  | 3.624 → 2.025 | 1.972 → 1.284 | 0.410 → 0.336 | 0.195 → 0.203 | 0.664 |
| noul | 670/666 | 1.259 | fitted -0.019 [-0.029, +0.006]; pooled +0.028 [-0.005, +0.058] → fitted | +0.000 | 0.245 → 0.238 | 0.258 → 0.249 | 0.040 → 0.036 | 0.036 → 0.017 | 0.896 |

pooled T (one T for every type, b = 0; the gate's fallback): 2.037

noul offset: fitted b = +0.518; eval accuracy change +0.0090 [+0.0000, +0.0180], ECE change +0.0032 [-0.0147, +0.0167] → not shipped (b = 0)

