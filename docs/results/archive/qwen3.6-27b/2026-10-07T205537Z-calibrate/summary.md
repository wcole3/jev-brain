# qwen3.6-27b calibration

## Provenance

- timestamp: 2026-10-07T205537Z
- repo commit: e07e2fb
- profile: qwen3.6-27b
- orders: identity
- calib split sha256: a4e492db25b2be6fb34f65689bbb715031e938a3d449e12c2677f8aa4d0e6ca8
- collect: .cache/collect/qwen3.6-27b/{calib,eval}.jsonl.gz

## decider_chat

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.646 | fitted -0.035 [-0.049, -0.008]; pooled -0.009 [-0.033, +0.021] → fitted |  | 0.667 → 0.543 | 0.546 → 0.501 | 0.071 → 0.030 | 0.071 → 0.036 | 0.812 |
| score | 259/554 | 1.926 (pooled; fitted 6.303) | fitted +0.030 [-0.045, +0.097]; pooled -0.086 [-0.116, -0.026] → pooled |  | 2.723 → 1.677 | 1.602 → 1.163 | 0.436 → 0.301 | 0.207 → 0.121 | 0.614 |
| noul | 670/666 | 1.388 | fitted -0.009 [-0.031, +0.016]; pooled +0.025 [-0.005, +0.056] → fitted | +0.000 | 0.318 → 0.299 | 0.297 → 0.287 | 0.055 → 0.030 | 0.047 → 0.038 | 0.881 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.926

noul offset: fitted b = +0.172; eval accuracy change -0.0015 [-0.0075, +0.0030], ECE change +0.0036 [-0.0134, +0.0165] → not shipped (b = 0)

## header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.627 | fitted -0.046 [-0.061, -0.022]; pooled -0.020 [-0.044, +0.011] → fitted |  | 0.664 → 0.542 | 0.553 → 0.496 | 0.068 → 0.037 | 0.079 → 0.033 | 0.817 |
| score | 259/554 | 1.957 (pooled; fitted 7.181) | fitted +0.114 [+0.035, +0.163]; pooled +0.017 [-0.033, +0.049] → pooled |  | 3.082 → 1.804 | 1.709 → 1.183 | 0.413 → 0.293 | 0.181 → 0.199 | 0.657 |
| noul | 670/666 | 1.281 | fitted -0.016 [-0.029, +0.007]; pooled +0.028 [-0.008, +0.060] → fitted | +0.000 | 0.256 → 0.247 | 0.279 → 0.266 | 0.034 → 0.027 | 0.040 → 0.024 | 0.895 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.957

noul offset: fitted b = +0.306; eval accuracy change -0.0015 [-0.0045, +0.0000], ECE change +0.0086 [-0.0077, +0.0195] → not shipped (b = 0)

## question_first

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.485 | fitted -0.043 [-0.055, -0.016]; pooled +0.001 [-0.032, +0.030] → fitted |  | 0.605 → 0.531 | 0.576 → 0.529 | 0.062 → 0.041 | 0.069 → 0.026 | 0.810 |
| score | 259/554 | 8.036 | fitted -0.092 [-0.168, -0.031]; pooled -0.053 [-0.099, -0.007] → fitted |  | 3.289 → 1.306 | 2.182 → 1.317 | 0.410 → 0.138 | 0.256 → 0.164 | 0.448 |
| noul | 670/666 | 1.146 | fitted -0.001 [-0.019, +0.022]; b = 0 +0.004 [-0.010, +0.020]; pooled +0.040 [+0.010, +0.062] → fitted | +0.256 | 0.270 → 0.264 | 0.286 → 0.277 | 0.035 → 0.035 | 0.037 → 0.036 | 0.877 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.903

noul offset: fitted b = +0.256; eval accuracy change +0.0150 [+0.0015, +0.0285], ECE change -0.0045 [-0.0237, +0.0154] → shipped

