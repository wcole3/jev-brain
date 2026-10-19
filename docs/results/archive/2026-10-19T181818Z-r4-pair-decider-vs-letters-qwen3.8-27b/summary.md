# qwen3.8-27b R4 pair screen: decider vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T181818Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- title: R4 pair screen
- set: decider
- control: letters
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib-600-letters.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-letters.jsonl.gz
- collect decider calib-600: .cache/collect/qwen3.8-27b/calib-600-decider.jsonl.gz
- collect decider index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-decider.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/labels-letters/dev.jsonl.gz
- collect decider image dev: .cache/vision-collect/qwen3.8-27b/r4-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered
- run time: 24 s

Reports only; the owner picks.

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| letters | 590 | 3728 | 1.492 | 5.187 | 0.934 |
| decider | 590 | 3728 | 1.471 | 4.550 | 0.976 |

## all (3728 questions)

Δ is decider − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.782 | 0.022 | 0.734 | 0.305 | baseline | baseline | baseline |
| all | decider | 3728 | 0.767 | 0.023 | 0.770 | 0.325 | -0.015 [-0.022, -0.008] | +0.0014 [-0.0098, +0.0120] | +0.0360 [+0.0266, +0.0447] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.781 | 0.023 | 0.737 | 0.306 | baseline | baseline | baseline |
| choice | decider | 3690 | 0.767 | 0.024 | 0.772 | 0.325 | -0.014 [-0.021, -0.007] | +0.0014 [-0.0098, +0.0122] | +0.0352 [+0.0256, +0.0442] |
| noul | letters | 38 | 0.868 | 0.112 | 0.474 | 0.229 | baseline | baseline | baseline |
| noul | decider | 38 | 0.816 | 0.143 | 0.585 | 0.291 | -0.053 [-0.132, +0.000] | +0.0313 [-0.0388, +0.1072] | +0.1108 [+0.0496, +0.1846] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.214 | 0.130 | baseline | baseline | baseline |
| 2 | decider | 2208 | 0.902 | 0.058 | 0.262 | 0.154 | -0.013 [-0.023, -0.004] | +0.0258 [+0.0159, +0.0342] | +0.0480 [+0.0406, +0.0559] |
| 3-5 | letters | 808 | 0.777 | 0.022 | 0.583 | 0.311 | baseline | baseline | baseline |
| 3-5 | decider | 808 | 0.755 | 0.028 | 0.616 | 0.333 | -0.022 [-0.041, -0.004] | +0.0068 [-0.0190, +0.0286] | +0.0333 [+0.0141, +0.0516] |
| 6-26 | letters | 505 | 0.303 | 0.275 | 2.732 | 0.959 | baseline | baseline | baseline |
| 6-26 | decider | 505 | 0.297 | 0.284 | 2.750 | 0.970 | -0.006 [-0.018, +0.006] | +0.0091 [-0.0093, +0.0279] | +0.0178 [-0.0202, +0.0554] |
| 27+ | letters | 207 | 0.556 | 0.088 | 2.000 | 0.553 | baseline | baseline | baseline |
| 27+ | decider | 207 | 0.531 | 0.093 | 1.963 | 0.551 | -0.024 [-0.048, -0.005] | +0.0041 [-0.0359, +0.0353] | -0.0369 [-0.1165, +0.0359] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | decider |
|---|---|---|---|
| overall | all | 0.098 | 0.105 |
| type | choice | 0.098 | 0.105 |
| options | 2 | 0.033 | 0.050 |
| options | 3-5 | 0.134 | 0.119 |
| options | 6-26 | 0.232 | 0.236 |
| options | 27+ | 0.319 | 0.309 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 664 1506 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 256 213 207 129 3 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 61 70 49 48 32 40 52 46 40 37 24 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| letters | 27+ | chosen | 4 5 4 2 3 7 9 2 3 3 7 3 3 6 3 2 3 3 2 1 2 1 1 2 3 2 2 |
| letters | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |
| decider | 2 | chosen | 631 1539 |
| decider | 2 | gold | 613 1557 |
| decider | 3-5 | chosen | 274 227 183 121 3 |
| decider | 3-5 | gold | 240 230 199 137 2 |
| decider | 6-26 | chosen | 65 77 44 53 33 37 58 42 36 31 23 1 2 0 0 2 1 0 0 0 0 0 0 0 0 0 |
| decider | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| decider | 27+ | chosen | 4 4 4 3 4 7 8 2 3 3 5 3 3 6 2 2 4 2 2 1 3 2 1 1 3 2 2 |
| decider | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |

