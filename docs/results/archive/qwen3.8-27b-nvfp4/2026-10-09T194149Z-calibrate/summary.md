# qwen3.8-27b-nvfp4 calibration

## Provenance

- timestamp: 2026-10-09T194149Z
- repo commit: ec2a235
- profile: qwen3.8-27b-nvfp4
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect: .cache/collect/qwen3.8-27b-nvfp4/{calib,eval}.jsonl.gz

## decider_chat

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.535 | fitted -0.028 [-0.042, +0.003]; pooled -0.008 [-0.034, +0.019] → fitted |  | 0.562 → 0.484 | 0.527 → 0.497 | 0.059 → 0.021 | 0.052 → 0.024 | 0.808 |
| score | 259/554 | 1.696 (pooled; fitted 4.470) | fitted +0.133 [+0.060, +0.182]; pooled +0.008 [-0.031, +0.050] → pooled |  | 2.081 → 1.505 | 1.366 → 1.126 | 0.269 → 0.173 | 0.124 → 0.132 | 0.646 |
| noul | 670/666 | 0.918 | fitted -0.010 [-0.024, +0.007]; pooled +0.075 [+0.043, +0.076] → fitted | +0.000 | 0.284 → 0.283 | 0.276 → 0.274 | 0.028 → 0.024 | 0.025 → 0.016 | 0.889 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.696

noul offset: fitted b = -0.292; eval accuracy change -0.0045 [-0.0180, +0.0090], ECE change -0.0021 [-0.0170, +0.0176] → not shipped (b = 0)

## header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.597 | fitted -0.038 [-0.052, -0.010]; pooled -0.020 [-0.043, +0.011] → fitted |  | 0.595 → 0.501 | 0.533 → 0.489 | 0.050 → 0.024 | 0.063 → 0.026 | 0.816 |
| score | 259/554 | 1.830 (pooled; fitted 5.474) | fitted +0.186 [+0.114, +0.229]; pooled +0.031 [-0.021, +0.065] → pooled |  | 2.475 → 1.613 | 1.475 → 1.129 | 0.328 → 0.206 | 0.133 → 0.163 | 0.675 |
| noul | 670/666 | 0.963 | fitted -0.004 [-0.009, +0.006]; pooled +0.071 [+0.046, +0.079] → fitted | +0.000 | 0.249 → 0.249 | 0.244 → 0.243 | 0.028 → 0.028 | 0.036 → 0.033 | 0.892 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.830

noul offset: fitted b = -0.002; eval accuracy change +0.0030 [-0.0060, +0.0120], ECE change +0.0016 [-0.0060, +0.0076] → not shipped (b = 0)

## question_first

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.388 | fitted -0.021 [-0.036, +0.004]; pooled +0.026 [-0.006, +0.048] → fitted |  | 0.567 → 0.526 | 0.547 → 0.528 | 0.046 → 0.028 | 0.046 → 0.025 | 0.805 |
| score | 259/554 | 1.774 (pooled; fitted 6.613) | fitted -0.007 [-0.075, +0.045]; pooled -0.026 [-0.057, +0.014] → pooled |  | 2.815 → 1.808 | 1.882 → 1.437 | 0.387 → 0.283 | 0.207 → 0.181 | 0.523 |
| noul | 670/666 | 0.942 | fitted -0.005 [-0.011, +0.007]; pooled +0.065 [+0.037, +0.072] → fitted | +0.000 | 0.295 → 0.294 | 0.289 → 0.288 | 0.032 → 0.025 | 0.019 → 0.014 | 0.859 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.774

noul offset: fitted b = -0.205; eval accuracy change +0.0075 [-0.0090, +0.0240], ECE change +0.0112 [-0.0116, +0.0255] → not shipped (b = 0)

