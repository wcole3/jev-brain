# qwen3.8-27b-fp8 calibration

## Provenance

- timestamp: 2026-10-09T201352Z
- repo commit: 0be4c9d
- profile: qwen3.8-27b-fp8
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect: .cache/collect/qwen3.8-27b-fp8/{calib,eval}.jsonl.gz

## decider_chat

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.485 | fitted -0.014 [-0.030, +0.013]; pooled +0.004 [-0.020, +0.032] → fitted |  | 0.559 → 0.491 | 0.502 → 0.489 | 0.043 → 0.022 | 0.044 → 0.030 | 0.808 |
| score | 259/554 | 1.655 (pooled; fitted 4.426) | fitted +0.129 [+0.068, +0.179]; pooled +0.021 [-0.021, +0.057] → pooled |  | 2.072 → 1.518 | 1.356 → 1.140 | 0.291 → 0.189 | 0.138 → 0.159 | 0.644 |
| noul | 670/666 | 0.943 | fitted -0.005 [-0.008, +0.014]; pooled +0.064 [+0.045, +0.070] → fitted | +0.000 | 0.290 → 0.289 | 0.273 → 0.272 | 0.036 → 0.036 | 0.033 → 0.028 | 0.881 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.655

noul offset: fitted b = -0.056; eval accuracy change -0.0045 [-0.0120, +0.0030], ECE change +0.0052 [-0.0085, +0.0150] → not shipped (b = 0)

## header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.517 | fitted -0.003 [-0.025, +0.020]; pooled +0.018 [-0.008, +0.043] → fitted |  | 0.566 → 0.492 | 0.496 → 0.478 | 0.048 → 0.033 | 0.047 → 0.044 | 0.822 |
| score | 259/554 | 1.000 (none; fitted 5.180) | fitted +0.169 [+0.104, +0.212]; pooled +0.040 [+0.002, +0.075] → none |  | 2.383 → 2.383 | 1.427 → 1.427 | 0.322 → 0.322 | 0.149 → 0.149 | 0.681 |
| noul | 670/666 | 0.959 | fitted -0.003 [-0.011, +0.010]; pooled +0.062 [+0.038, +0.074] → fitted | +0.000 | 0.253 → 0.253 | 0.257 → 0.257 | 0.028 → 0.021 | 0.031 → 0.027 | 0.890 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.754

noul offset: fitted b = +0.220; eval accuracy change +0.0015 [-0.0060, +0.0090], ECE change +0.0097 [-0.0094, +0.0183] → not shipped (b = 0)

## question_first

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.324 | fitted +0.008 [-0.015, +0.030]; pooled +0.058 [+0.028, +0.079] → fitted |  | 0.553 → 0.522 | 0.508 → 0.508 | 0.036 → 0.025 | 0.028 → 0.036 | 0.806 |
| score | 259/554 | 6.369 | fitted -0.067 [-0.139, -0.013]; pooled -0.030 [-0.069, -0.004] → fitted |  | 2.721 → 1.290 | 1.873 → 1.301 | 0.420 → 0.079 | 0.228 → 0.161 | 0.473 |
| noul | 670/666 | 0.812 | fitted -0.019 [-0.031, +0.007]; pooled +0.063 [+0.040, +0.070] → fitted | +0.000 | 0.281 → 0.277 | 0.283 → 0.277 | 0.033 → 0.030 | 0.040 → 0.021 | 0.878 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.685

noul offset: fitted b = +0.015; eval accuracy change +0.0000 [+0.0000, +0.0000], ECE change +0.0001 [-0.0038, +0.0012] → not shipped (b = 0)

