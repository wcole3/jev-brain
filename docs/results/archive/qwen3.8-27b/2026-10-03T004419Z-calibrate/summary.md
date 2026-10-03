# qwen3.8-27b calibration

## Provenance

- timestamp: 2026-10-03T004419Z
- repo commit: 7e5652e-dirty
- profile: qwen3.8-27b
- orders: identity
- calib split sha256: a4e492db25b2be6fb34f65689bbb715031e938a3d449e12c2677f8aa4d0e6ca8
- collect: .cache/collect/qwen3.8-27b/{calib,eval}.jsonl.gz

## decider_chat

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.496 | fitted -0.015 [-0.031, +0.013]; pooled +0.007 [-0.017, +0.034] → fitted |  | 0.554 → 0.485 | 0.507 → 0.490 | 0.042 → 0.030 | 0.042 → 0.027 | 0.807 |
| score | 259/554 | 1.664 (pooled; fitted 4.420) | fitted +0.138 [+0.069, +0.180]; pooled +0.015 [-0.027, +0.051] → pooled |  | 2.064 → 1.512 | 1.347 → 1.130 | 0.276 → 0.165 | 0.133 → 0.147 | 0.641 |
| noul | 670/666 | 0.970 | fitted -0.003 [-0.013, +0.007]; pooled +0.065 [+0.037, +0.070] → fitted | +0.000 | 0.287 → 0.287 | 0.270 → 0.269 | 0.030 → 0.034 | 0.030 → 0.027 | 0.892 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.664

noul offset: fitted b = -0.040; eval accuracy change -0.0090 [-0.0165, -0.0015], ECE change -0.0037 [-0.0131, +0.0087] → not shipped (b = 0)

## header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.536 | fitted +0.002 [-0.022, +0.022]; pooled +0.024 [-0.003, +0.046] → fitted |  | 0.567 → 0.490 | 0.494 → 0.475 | 0.051 → 0.028 | 0.038 → 0.040 | 0.823 |
| score | 259/554 | 1.775 (pooled; fitted 5.308) | fitted +0.185 [+0.116, +0.224]; pooled +0.037 [-0.007, +0.067] → pooled |  | 2.414 → 1.613 | 1.438 → 1.137 | 0.312 → 0.227 | 0.146 → 0.183 | 0.675 |
| noul | 670/666 | 0.963 | fitted -0.006 [-0.013, +0.006]; pooled +0.059 [+0.037, +0.071] → fitted | +0.000 | 0.247 → 0.247 | 0.254 → 0.254 | 0.023 → 0.019 | 0.034 → 0.028 | 0.890 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.775

noul offset: fitted b = +0.245; eval accuracy change +0.0000 [-0.0090, +0.0090], ECE change +0.0077 [-0.0093, +0.0167] → not shipped (b = 0)

## question_first

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.352 | fitted +0.021 [-0.006, +0.039]; pooled +0.067 [+0.034, +0.084] → fitted |  | 0.563 → 0.527 | 0.510 → 0.510 | 0.039 → 0.032 | 0.021 → 0.042 | 0.809 |
| score | 259/554 | 6.264 | fitted -0.067 [-0.133, -0.012]; pooled -0.036 [-0.071, -0.007] → fitted |  | 2.678 → 1.289 | 1.854 → 1.299 | 0.417 → 0.075 | 0.223 → 0.156 | 0.475 |
| noul | 670/666 | 0.825 | fitted -0.015 [-0.026, +0.010]; pooled +0.068 [+0.046, +0.073] → fitted | +0.000 | 0.279 → 0.275 | 0.283 → 0.278 | 0.037 → 0.027 | 0.035 → 0.020 | 0.878 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.703

noul offset: fitted b = +0.007; eval accuracy change +0.0000 [+0.0000, +0.0000], ECE change -0.0001 [-0.0002, +0.0001] → not shipped (b = 0)

