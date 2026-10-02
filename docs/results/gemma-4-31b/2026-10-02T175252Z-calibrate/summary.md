# gemma-4-31b calibration

## Provenance

- timestamp: 2026-10-02T175252Z
- repo commit: b7331e4
- profile: gemma-4-31b
- orders: identity
- calib split sha256: a4e492db25b2be6fb34f65689bbb715031e938a3d449e12c2677f8aa4d0e6ca8
- collect: .cache/collect/gemma-4-31b/{calib,eval}.jsonl.gz

## decider_chat

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 4.123 | fitted -0.086 [-0.090, -0.074]; pooled -0.075 [-0.093, -0.051] → fitted |  | 1.839 → 0.572 | 2.074 → 0.608 | 0.124 → 0.044 | 0.159 → 0.073 | 0.837 |
| score | 259/554 | 5.378 (pooled; fitted 18.187) | fitted -0.072 [-0.148, +0.005]; pooled -0.160 [-0.181, -0.117] → pooled |  | 8.977 → 1.835 | 4.912 → 1.156 | 0.518 → 0.377 | 0.320 → 0.159 | 0.668 |
| noul | 670/666 | 7.528 | fitted -0.091 [-0.103, -0.057]; b = 0 -0.043 [-0.063, -0.024]; pooled -0.045 [-0.051, -0.036] → fitted | -0.636 | 1.334 → 0.256 | 1.384 → 0.275 | 0.104 → 0.027 | 0.118 → 0.028 | 0.889 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.378

noul offset: fitted b = -0.636; eval accuracy change +0.0075 [-0.0030, +0.0180], ECE change -0.0473 [-0.0600, -0.0191] → shipped

## header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 4.263 | fitted -0.088 [-0.093, -0.077]; pooled -0.078 [-0.094, -0.050] → fitted |  | 2.009 → 0.604 | 2.316 → 0.650 | 0.125 → 0.041 | 0.167 → 0.079 | 0.830 |
| score | 259/554 | 5.603 (pooled; fitted 19.999 (edge)) | fitted -0.084 [-0.140, -0.004]; pooled -0.154 [-0.176, -0.099] → pooled |  | 9.996 → 1.932 | 5.366 → 1.197 | 0.534 → 0.409 | 0.324 → 0.170 | 0.666 |
| noul | 670/666 | 7.609 | fitted -0.064 [-0.083, -0.037]; pooled -0.043 [-0.049, -0.032] → fitted | +0.000 | 1.215 → 0.243 | 1.508 → 0.291 | 0.083 → 0.034 | 0.115 → 0.051 | 0.884 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.603

noul offset: fitted b = -0.211; eval accuracy change +0.0015 [+0.0000, +0.0045], ECE change -0.0188 [-0.0309, +0.0042] → not shipped (b = 0)

## question_first

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 3.839 | fitted -0.093 [-0.099, -0.085]; pooled -0.084 [-0.107, -0.059] → fitted |  | 1.683 → 0.587 | 2.103 → 0.668 | 0.130 → 0.032 | 0.175 → 0.082 | 0.816 |
| score | 259/554 | 5.278 (pooled; fitted 19.999 (edge)) | fitted -0.056 [-0.125, +0.011]; pooled -0.142 [-0.174, -0.089] → pooled |  | 9.695 → 1.998 | 5.377 → 1.318 | 0.542 → 0.414 | 0.357 → 0.216 | 0.628 |
| noul | 670/666 | 7.266 | fitted -0.085 [-0.092, -0.054]; b = 0 -0.047 [-0.067, -0.026]; pooled -0.044 [-0.048, -0.036] → fitted | -0.460 | 1.211 → 0.245 | 1.440 → 0.289 | 0.094 → 0.036 | 0.118 → 0.033 | 0.878 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.278

noul offset: fitted b = -0.460; eval accuracy change -0.0015 [-0.0060, +0.0030], ECE change -0.0382 [-0.0485, -0.0082] → shipped

