# qwen3.8-27b R3 label screen: symbols vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T001012Z
- repo commit: ef7d4c1-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: symbols
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-symbols calib-600: .cache/collect/qwen3.8-27b/calib-600-symbols.jsonl.gz
- collect labels-symbols index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-symbols.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-symbols image dev: .cache/vision-collect/qwen3.8-27b/labels-symbols/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 59 s

all = every question both arms answered; pure = the questions the set run showed with its own labels (fallback questions use today's letters).
Reports only; the owner picks.

### Fallback share (all questions, set run)

| grouping | bucket | share |
|---|---|---|
| overall | all | 0.052 |
| type | choice | 0.052 |
| type | noul | 0.000 |
| options | 2 | 0.000 |
| options | 3-5 | 0.000 |
| options | 6-26 | 0.000 |
| options | 27+ | 0.928 |

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| letters | 590 | 3728 | 1.491 | 5.160 | 0.934 |
| labels-symbols | 585 | 3728 | 1.119 | 4.188 | 0.690 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.782 | 0.021 | 0.735 | 0.306 | baseline | baseline | baseline |
| all | labels-symbols | 3728 | 0.702 | 0.083 | 0.998 | 0.410 | -0.079 [-0.092, -0.066] | +0.0616 [+0.0418, +0.0692] | +0.2636 [+0.2335, +0.2936] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.781 | 0.022 | 0.737 | 0.307 | baseline | baseline | baseline |
| choice | labels-symbols | 3690 | 0.702 | 0.082 | 1.001 | 0.409 | -0.078 [-0.092, -0.065] | +0.0593 [+0.0396, +0.0668] | +0.2633 [+0.2325, +0.2926] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-symbols | 38 | 0.684 | 0.219 | 0.767 | 0.441 | -0.184 [-0.316, -0.079] | +0.1069 [-0.0134, +0.2183] | +0.2936 [+0.1058, +0.5191] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-symbols | 2208 | 0.861 | 0.027 | 0.315 | 0.194 | -0.054 [-0.070, -0.038] | -0.0054 [-0.0180, +0.0121] | +0.0999 [+0.0768, +0.1247] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-symbols | 808 | 0.637 | 0.081 | 1.005 | 0.513 | -0.137 [-0.172, -0.106] | +0.0618 [+0.0167, +0.0823] | +0.4209 [+0.3557, +0.4866] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-symbols | 505 | 0.176 | 0.355 | 3.383 | 1.101 | -0.127 [-0.164, -0.093] | +0.0790 [+0.0417, +0.1143] | +0.6505 [+0.5144, +0.7866] |
| 27+ | letters | 207 | 0.556 | 0.096 | 1.993 | 0.552 | baseline | baseline | baseline |
| 27+ | labels-symbols | 207 | 0.546 | 0.133 | 2.444 | 0.614 | -0.010 [-0.034, +0.010] | +0.0375 [-0.0080, +0.0726] | +0.4514 [+0.3121, +0.5955] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-symbols |
|---|---|---|---|
| overall | all | 0.096 | 0.365 |
| type | choice | 0.096 | 0.365 |
| options | 2 | 0.032 | 0.291 |
| options | 3-5 | 0.126 | 0.470 |
| options | 6-26 | 0.226 | 0.507 |
| options | 27+ | 0.333 | 0.382 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 664 1506 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 261 213 206 125 3 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 59 70 49 49 33 38 52 48 40 36 25 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| letters | 27+ | chosen | 5 5 4 2 3 7 9 2 3 3 7 3 3 6 3 2 3 3 2 1 2 1 1 1 3 2 2 |
| letters | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |
| labels-symbols | 2 | chosen | 496 1674 |
| labels-symbols | 2 | gold | 613 1557 |
| labels-symbols | 3-5 | chosen | 230 282 79 213 4 |
| labels-symbols | 3-5 | gold | 240 230 199 137 2 |
| labels-symbols | 6-26 | chosen | 94 54 22 51 64 32 40 38 69 22 16 0 1 0 0 1 0 0 0 0 0 1 0 0 0 0 |
| labels-symbols | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-symbols | 27+ | chosen | 3 5 3 3 14 8 4 3 2 3 7 3 3 4 4 2 1 2 2 1 2 1 2 2 3 2 3 |
| labels-symbols | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3536 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3536 | 0.792 | 0.020 | 0.675 | 0.295 | baseline | baseline | baseline |
| all | labels-symbols | 3536 | 0.708 | 0.082 | 0.929 | 0.401 | -0.083 [-0.097, -0.070] | +0.0614 [+0.0426, +0.0690] | +0.2545 [+0.2256, +0.2850] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3498 | 0.791 | 0.021 | 0.677 | 0.296 | baseline | baseline | baseline |
| choice | labels-symbols | 3498 | 0.709 | 0.080 | 0.931 | 0.401 | -0.082 [-0.096, -0.069] | +0.0590 [+0.0400, +0.0676] | +0.2541 [+0.2247, +0.2842] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-symbols | 38 | 0.684 | 0.219 | 0.767 | 0.441 | -0.184 [-0.316, -0.079] | +0.1069 [-0.0134, +0.2183] | +0.2936 [+0.1058, +0.5191] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-symbols | 2208 | 0.861 | 0.027 | 0.315 | 0.194 | -0.054 [-0.070, -0.038] | -0.0054 [-0.0180, +0.0121] | +0.0999 [+0.0768, +0.1247] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-symbols | 808 | 0.637 | 0.081 | 1.005 | 0.513 | -0.137 [-0.172, -0.106] | +0.0618 [+0.0167, +0.0823] | +0.4209 [+0.3557, +0.4866] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-symbols | 505 | 0.176 | 0.355 | 3.383 | 1.101 | -0.127 [-0.164, -0.093] | +0.0790 [+0.0417, +0.1143] | +0.6505 [+0.5144, +0.7866] |
| 27+ | letters | 15 | 0.000 | 0.408 | 4.045 | 1.115 | baseline | baseline | baseline |
| 27+ | labels-symbols | 15 | 0.000 | 0.469 | 4.752 | 1.240 | +0.000 [+0.000, +0.000] | +0.0606 [-0.0425, +0.1609] | +0.7061 [+0.0809, +1.4370] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-symbols |
|---|---|---|---|
| overall | all | 0.084 | 0.365 |
| type | choice | 0.084 | 0.365 |
| options | 2 | 0.032 | 0.291 |
| options | 3-5 | 0.126 | 0.470 |
| options | 6-26 | 0.226 | 0.507 |
| options | 27+ | 0.533 | 0.667 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 664 1506 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 261 213 206 125 3 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 59 70 49 49 33 38 52 48 40 36 25 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| letters | 27+ | chosen | 0 0 2 0 0 2 1 1 2 1 1 0 0 1 0 1 1 1 0 0 0 0 0 0 1 0 0 |
| letters | 27+ | gold | 0 0 1 1 0 0 0 0 0 0 1 0 0 1 1 0 0 0 1 1 0 0 0 0 1 1 2 |
| labels-symbols | 2 | chosen | 496 1674 |
| labels-symbols | 2 | gold | 613 1557 |
| labels-symbols | 3-5 | chosen | 230 282 79 213 4 |
| labels-symbols | 3-5 | gold | 240 230 199 137 2 |
| labels-symbols | 6-26 | chosen | 94 54 22 51 64 32 40 38 69 22 16 0 1 0 0 1 0 0 0 0 0 1 0 0 0 0 |
| labels-symbols | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-symbols | 27+ | chosen | 0 0 1 0 8 0 0 1 1 1 1 0 0 0 0 0 0 1 0 0 0 0 0 0 1 0 0 |
| labels-symbols | 27+ | gold | 0 0 1 1 0 0 0 0 0 0 1 0 0 1 1 0 0 0 1 1 0 0 0 0 1 1 2 |

