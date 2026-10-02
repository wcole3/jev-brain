# qwen3.6-27b calibration

## Provenance

- timestamp: 2026-10-02T154740Z
- repo commit: 72ef31e-dirty
- profile: qwen3.6-27b
- orders: identity
- calib split sha256: a4e492db25b2be6fb34f65689bbb715031e938a3d449e12c2677f8aa4d0e6ca8
- collect: .cache/collect/qwen3.6-27b/{calib,eval}.jsonl.gz
- written: True

## decider_chat

| type | n calib/eval | T | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.648 |  | 0.668 → 0.543 | 0.545 → 0.501 | 0.070 → 0.027 | 0.067 → 0.041 | 0.811 |
| score | 259/554 | 6.323 |  | 2.725 → 1.292 | 1.602 → 1.179 | 0.439 → 0.080 | 0.197 → 0.236 | 0.616 |
| noul | 670/666 | 1.386 | +0.000 | 0.318 → 0.299 | 0.296 → 0.286 | 0.055 → 0.032 | 0.045 → 0.038 | 0.880 |

noul offset: fitted b = +0.170; eval accuracy change +0.0000 [-0.0045, +0.0045], ECE change -0.0002 [-0.0148, +0.0116] → not shipped (b = 0)

## header

| type | n calib/eval | T | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.627 |  | 0.664 → 0.542 | 0.553 → 0.496 | 0.068 → 0.034 | 0.079 → 0.029 | 0.817 |
| score | 259/554 | 7.195 |  | 3.085 → 1.294 | 1.703 → 1.179 | 0.412 → 0.105 | 0.178 → 0.304 | 0.664 |
| noul | 670/666 | 1.284 | +0.000 | 0.257 → 0.248 | 0.278 → 0.266 | 0.035 → 0.025 | 0.040 → 0.023 | 0.895 |

noul offset: fitted b = +0.302; eval accuracy change +0.0000 [-0.0045, +0.0045], ECE change +0.0076 [-0.0091, +0.0197] → not shipped (b = 0)

## question_first

| type | n calib/eval | T | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.484 |  | 0.604 → 0.530 | 0.576 → 0.529 | 0.058 → 0.048 | 0.068 → 0.025 | 0.811 |
| score | 259/554 | 8.055 |  | 3.291 → 1.306 | 2.181 → 1.318 | 0.407 → 0.138 | 0.253 → 0.167 | 0.448 |
| noul | 670/666 | 1.145 | +0.253 | 0.270 → 0.263 | 0.287 → 0.277 | 0.028 → 0.039 | 0.037 → 0.026 | 0.877 |

noul offset: fitted b = +0.253; eval accuracy change +0.0165 [+0.0030, +0.0300], ECE change -0.0165 [-0.0265, +0.0092] → shipped

