# qwen3.8-27b calibration

## Provenance

- timestamp: 2026-10-08T043100Z
- repo commit: e07e2fb-dirty
- profile: qwen3.8-27b
- orders: identity
- calib split sha256: a4e492db25b2be6fb34f65689bbb715031e938a3d449e12c2677f8aa4d0e6ca8
- collect: .cache/collect/qwen3.8-27b/{calib,eval}.jsonl.gz

## decider_chat

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.496 | fitted -0.014 [-0.033, +0.013]; pooled +0.006 [-0.019, +0.034] → fitted |  | 0.554 → 0.486 | 0.507 → 0.490 | 0.046 → 0.025 | 0.044 → 0.030 | 0.808 |
| score | 259/554 | 1.665 (pooled; fitted 4.434) | fitted +0.154 [+0.079, +0.191]; pooled +0.026 [-0.020, +0.058] → pooled |  | 2.066 → 1.513 | 1.345 → 1.129 | 0.279 → 0.174 | 0.122 → 0.148 | 0.646 |
| noul | 670/666 | 0.973 | fitted -0.003 [-0.014, +0.010]; pooled +0.057 [+0.029, +0.069] → fitted | +0.000 | 0.287 → 0.287 | 0.271 → 0.270 | 0.030 → 0.039 | 0.035 → 0.032 | 0.890 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.665

noul offset: fitted b = -0.038; eval accuracy change -0.0105 [-0.0180, -0.0030], ECE change +0.0025 [-0.0097, +0.0139] → not shipped (b = 0)

## header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.536 | fitted +0.003 [-0.020, +0.024]; pooled +0.025 [-0.002, +0.046] → fitted |  | 0.567 → 0.490 | 0.494 → 0.475 | 0.046 → 0.027 | 0.041 → 0.045 | 0.824 |
| score | 259/554 | 1.775 (pooled; fitted 5.309) | fitted +0.197 [+0.128, +0.234]; pooled +0.046 [-0.001, +0.071] → pooled |  | 2.414 → 1.613 | 1.438 → 1.137 | 0.313 → 0.207 | 0.135 → 0.182 | 0.677 |
| noul | 670/666 | 0.963 | fitted -0.006 [-0.012, +0.005]; pooled +0.057 [+0.037, +0.073] → fitted | +0.000 | 0.247 → 0.247 | 0.253 → 0.253 | 0.025 → 0.019 | 0.035 → 0.029 | 0.889 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.775

noul offset: fitted b = +0.252; eval accuracy change -0.0015 [-0.0105, +0.0075], ECE change +0.0106 [-0.0072, +0.0215] → not shipped (b = 0)

## question_first

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.351 | fitted +0.017 [-0.009, +0.034]; pooled +0.064 [+0.032, +0.081] → fitted |  | 0.561 → 0.526 | 0.510 → 0.509 | 0.038 → 0.032 | 0.023 → 0.039 | 0.807 |
| score | 259/554 | 6.270 | fitted -0.064 [-0.135, -0.009]; pooled -0.047 [-0.076, -0.014] → fitted |  | 2.679 → 1.289 | 1.855 → 1.299 | 0.413 → 0.070 | 0.213 → 0.149 | 0.469 |
| noul | 670/666 | 0.831 | fitted -0.027 [-0.037, +0.002]; pooled +0.057 [+0.039, +0.072] → fitted | +0.000 | 0.280 → 0.277 | 0.283 → 0.278 | 0.042 → 0.032 | 0.048 → 0.021 | 0.880 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.703

noul offset: fitted b = +0.008; eval accuracy change +0.0000 [+0.0000, +0.0000], ECE change +0.0000 [-0.0001, +0.0001] → not shipped (b = 0)

