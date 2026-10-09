# qwen3.6-27b-fp8 calibration

## Provenance

- timestamp: 2026-10-09T204542Z
- repo commit: fdb758b
- profile: qwen3.6-27b-fp8
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect: .cache/collect/qwen3.6-27b-fp8/{calib,eval}.jsonl.gz

## decider_chat

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.659 | fitted -0.039 [-0.054, -0.012]; pooled -0.017 [-0.038, +0.015] → fitted |  | 0.674 → 0.545 | 0.550 → 0.501 | 0.069 → 0.029 | 0.074 → 0.035 | 0.806 |
| score | 259/554 | 1.944 (pooled; fitted 6.442) | fitted +0.041 [-0.037, +0.106]; pooled -0.073 [-0.107, -0.016] → pooled |  | 2.775 → 1.689 | 1.622 → 1.167 | 0.446 → 0.313 | 0.202 → 0.129 | 0.616 |
| noul | 670/666 | 1.403 | fitted -0.005 [-0.031, +0.021]; pooled +0.027 [-0.005, +0.056] → fitted | +0.000 | 0.319 → 0.299 | 0.301 → 0.289 | 0.059 → 0.036 | 0.051 → 0.046 | 0.883 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.944

noul offset: fitted b = +0.226; eval accuracy change -0.0075 [-0.0165, +0.0000], ECE change -0.0026 [-0.0215, +0.0173] → not shipped (b = 0)

## header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.632 | fitted -0.053 [-0.064, -0.030]; pooled -0.031 [-0.050, +0.002] → fitted |  | 0.667 → 0.544 | 0.558 → 0.497 | 0.068 → 0.023 | 0.087 → 0.034 | 0.812 |
| score | 259/554 | 1.974 (pooled; fitted 7.467) | fitted +0.129 [+0.053, +0.186]; pooled +0.020 [-0.032, +0.058] → pooled |  | 3.157 → 1.829 | 1.744 → 1.197 | 0.413 → 0.296 | 0.189 → 0.209 | 0.661 |
| noul | 670/666 | 1.286 | fitted -0.012 [-0.027, +0.008]; pooled +0.026 [-0.005, +0.057] → fitted | +0.000 | 0.259 → 0.250 | 0.283 → 0.269 | 0.035 → 0.022 | 0.039 → 0.027 | 0.892 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.974

noul offset: fitted b = +0.389; eval accuracy change +0.0045 [-0.0030, +0.0120], ECE change -0.0068 [-0.0176, +0.0100] → not shipped (b = 0)

## question_first

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.476 | fitted -0.042 [-0.057, -0.020]; pooled +0.000 [-0.031, +0.029] → fitted |  | 0.605 → 0.532 | 0.578 → 0.530 | 0.063 → 0.034 | 0.069 → 0.027 | 0.813 |
| score | 259/554 | 7.858 | fitted -0.145 [-0.214, -0.082]; pooled -0.080 [-0.109, -0.043] → fitted |  | 3.269 → 1.301 | 2.186 → 1.316 | 0.428 → 0.120 | 0.275 → 0.130 | 0.430 |
| noul | 670/666 | 1.223 | fitted +0.002 [-0.014, +0.018]; pooled +0.039 [+0.006, +0.060] → fitted | +0.000 | 0.279 → 0.274 | 0.301 → 0.295 | 0.040 → 0.042 | 0.036 → 0.038 | 0.856 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.888

noul offset: fitted b = +0.344; eval accuracy change +0.0150 [+0.0000, +0.0315], ECE change -0.0124 [-0.0285, +0.0084] → not shipped (b = 0)

