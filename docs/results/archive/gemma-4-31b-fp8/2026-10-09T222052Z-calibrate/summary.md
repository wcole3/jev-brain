# gemma-4-31b-fp8 calibration

## Provenance

- timestamp: 2026-10-09T222052Z
- repo commit: 89f8488
- profile: gemma-4-31b-fp8
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect: .cache/collect/gemma-4-31b-fp8/{calib,eval}.jsonl.gz

## decider_chat

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 5.363 (pooled; fitted 4.148) | fitted -0.084 [-0.090, -0.074]; pooled -0.089 [-0.108, -0.068] → pooled |  | 1.882 → 0.645 | 2.094 → 0.615 | 0.126 → 0.106 | 0.166 → 0.076 | 0.828 |
| score | 259/554 | 5.363 (pooled; fitted 17.859) | fitted -0.072 [-0.148, +0.005]; pooled -0.169 [-0.189, -0.128] → pooled |  | 8.814 → 1.815 | 4.800 → 1.141 | 0.516 → 0.381 | 0.322 → 0.153 | 0.668 |
| noul | 670/666 | 7.430 | fitted -0.091 [-0.101, -0.053]; b = 0 -0.039 [-0.054, -0.022]; pooled -0.048 [-0.051, -0.038] → fitted | -0.661 | 1.309 → 0.255 | 1.351 → 0.272 | 0.101 → 0.026 | 0.115 → 0.024 | 0.886 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.363

noul offset: fitted b = -0.661; eval accuracy change +0.0015 [-0.0090, +0.0120], ECE change -0.0524 [-0.0625, -0.0224] → shipped

## header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 4.269 | fitted -0.088 [-0.092, -0.074]; pooled -0.073 [-0.091, -0.048] → fitted |  | 2.044 → 0.611 | 2.305 → 0.649 | 0.131 → 0.036 | 0.165 → 0.076 | 0.832 |
| score | 259/554 | 5.570 (pooled; fitted 19.999 (edge)) | fitted -0.080 [-0.145, +0.003]; pooled -0.144 [-0.173, -0.092] → pooled |  | 9.704 → 1.899 | 5.167 → 1.173 | 0.517 → 0.395 | 0.322 → 0.178 | 0.666 |
| noul | 670/666 | 7.571 | fitted -0.058 [-0.081, -0.035]; pooled -0.042 [-0.049, -0.036] → fitted | +0.000 | 1.222 → 0.246 | 1.467 → 0.291 | 0.082 → 0.049 | 0.111 → 0.053 | 0.886 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.570

noul offset: fitted b = -0.235; eval accuracy change +0.0015 [-0.0030, +0.0060], ECE change -0.0196 [-0.0292, +0.0008] → not shipped (b = 0)

## question_first

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 3.872 | fitted -0.097 [-0.102, -0.087]; pooled -0.090 [-0.114, -0.064] → fitted |  | 1.745 → 0.607 | 2.106 → 0.667 | 0.130 → 0.037 | 0.179 → 0.082 | 0.814 |
| score | 259/554 | 5.271 (pooled; fitted 19.999 (edge)) | fitted -0.043 [-0.111, +0.027]; pooled -0.124 [-0.165, -0.074] → pooled |  | 9.422 → 1.957 | 5.202 → 1.289 | 0.524 → 0.402 | 0.350 → 0.226 | 0.637 |
| noul | 670/666 | 7.329 | fitted -0.083 [-0.093, -0.050]; b = 0 -0.044 [-0.062, -0.023]; pooled -0.046 [-0.051, -0.038] → fitted | -0.510 | 1.251 → 0.250 | 1.388 → 0.283 | 0.097 → 0.032 | 0.113 → 0.030 | 0.892 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.271

noul offset: fitted b = -0.510; eval accuracy change +0.0045 [+0.0000, +0.0105], ECE change -0.0390 [-0.0515, -0.0122] → shipped

