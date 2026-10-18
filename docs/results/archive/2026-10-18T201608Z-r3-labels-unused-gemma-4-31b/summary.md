# gemma-4-31b R3 label screen: unused vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-18T201608Z
- repo commit: 0ec2db9-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: unused
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-unused calib-600: .cache/collect/gemma-4-31b/calib-600-unused.jsonl.gz
- collect labels-unused index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-unused.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-unused image dev: .cache/vision-collect/gemma-4-31b/labels-unused/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 54 s

all = every question both arms answered; pure = the questions the set run showed with its own labels (fallback questions use today's letters).
Reports only; the owner picks.

### Fallback share (all questions, set run)

| grouping | bucket | share |
|---|---|---|
| overall | all | 0.000 |
| type | choice | 0.000 |
| type | noul | 0.000 |
| options | 2 | 0.000 |
| options | 3-5 | 0.000 |
| options | 6-26 | 0.000 |
| options | 27+ | 0.000 |

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| letters | 590 | 3728 | 4.092 | 19.999 | 8.022 |
| labels-unused | 600 | 3728 | 2.563 | 19.999 | 4.416 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.125 | 0.808 | 0.324 | baseline | baseline | baseline |
| all | labels-unused | 3728 | 0.700 | 0.092 | 1.006 | 0.404 | -0.102 [-0.115, -0.088] | -0.0328 [-0.0453, -0.0200] | +0.1977 [+0.1494, +0.2433] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.125 | 0.813 | 0.325 | baseline | baseline | baseline |
| choice | labels-unused | 3690 | 0.698 | 0.093 | 1.013 | 0.406 | -0.103 [-0.116, -0.090] | -0.0328 [-0.0449, -0.0199] | +0.2000 [+0.1531, +0.2472] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-unused | 38 | 0.895 | 0.063 | 0.326 | 0.188 | +0.026 [+0.000, +0.079] | -0.0459 [-0.0626, +0.0116] | -0.0244 [-0.1134, +0.0735] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-unused | 2208 | 0.899 | 0.057 | 0.355 | 0.172 | -0.010 [-0.018, -0.002] | -0.0138 [-0.0221, -0.0067] | +0.0422 [+0.0167, +0.0673] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-unused | 808 | 0.553 | 0.196 | 1.231 | 0.618 | -0.244 [-0.278, -0.210] | +0.0632 [+0.0316, +0.0934] | +0.5083 [+0.4134, +0.6041] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-unused | 505 | 0.305 | 0.103 | 2.132 | 0.833 | -0.101 [-0.156, -0.048] | -0.2921 [-0.3394, -0.2331] | -0.5277 [-0.7258, -0.3273] |
| 27+ | letters | 207 | 0.638 | 0.114 | 1.910 | 0.512 | baseline | baseline | baseline |
| 27+ | labels-unused | 207 | 0.106 | 0.080 | 4.324 | 0.989 | -0.531 [-0.604, -0.464] | -0.0340 [-0.1014, +0.0159] | +2.4136 [+2.0932, +2.7161] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-unused |
|---|---|---|---|
| overall | all | 0.074 | 0.347 |
| type | choice | 0.074 | 0.347 |
| options | 2 | 0.030 | 0.068 |
| options | 3-5 | 0.089 | 0.649 |
| options | 6-26 | 0.149 | 0.814 |
| options | 27+ | 0.295 | 0.952 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 597 1573 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 241 216 215 131 5 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 57 56 46 52 41 50 49 44 49 34 21 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| letters | 27+ | chosen | 7 8 2 4 0 5 2 1 3 1 7 2 3 3 5 4 3 2 2 0 2 0 2 2 3 1 2 |
| letters | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |
| labels-unused | 2 | chosen | 660 1510 |
| labels-unused | 2 | gold | 613 1557 |
| labels-unused | 3-5 | chosen | 296 401 12 98 1 |
| labels-unused | 3-5 | gold | 240 230 199 137 2 |
| labels-unused | 6-26 | chosen | 209 42 0 6 1 175 9 21 27 2 10 0 0 0 0 0 0 0 2 0 0 0 1 0 0 0 |
| labels-unused | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-unused | 27+ | chosen | 8 10 1 1 0 4 0 1 1 0 5 0 1 0 0 0 2 0 4 0 0 1 0 0 1 0 1 |
| labels-unused | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.125 | 0.808 | 0.324 | baseline | baseline | baseline |
| all | labels-unused | 3728 | 0.700 | 0.092 | 1.006 | 0.404 | -0.102 [-0.115, -0.088] | -0.0328 [-0.0453, -0.0200] | +0.1977 [+0.1494, +0.2433] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.125 | 0.813 | 0.325 | baseline | baseline | baseline |
| choice | labels-unused | 3690 | 0.698 | 0.093 | 1.013 | 0.406 | -0.103 [-0.116, -0.090] | -0.0328 [-0.0449, -0.0199] | +0.2000 [+0.1531, +0.2472] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-unused | 38 | 0.895 | 0.063 | 0.326 | 0.188 | +0.026 [+0.000, +0.079] | -0.0459 [-0.0626, +0.0116] | -0.0244 [-0.1134, +0.0735] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-unused | 2208 | 0.899 | 0.057 | 0.355 | 0.172 | -0.010 [-0.018, -0.002] | -0.0138 [-0.0221, -0.0067] | +0.0422 [+0.0167, +0.0673] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-unused | 808 | 0.553 | 0.196 | 1.231 | 0.618 | -0.244 [-0.278, -0.210] | +0.0632 [+0.0316, +0.0934] | +0.5083 [+0.4134, +0.6041] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-unused | 505 | 0.305 | 0.103 | 2.132 | 0.833 | -0.101 [-0.156, -0.048] | -0.2921 [-0.3394, -0.2331] | -0.5277 [-0.7258, -0.3273] |
| 27+ | letters | 207 | 0.638 | 0.114 | 1.910 | 0.512 | baseline | baseline | baseline |
| 27+ | labels-unused | 207 | 0.106 | 0.080 | 4.324 | 0.989 | -0.531 [-0.604, -0.464] | -0.0340 [-0.1014, +0.0159] | +2.4136 [+2.0932, +2.7161] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-unused |
|---|---|---|---|
| overall | all | 0.074 | 0.347 |
| type | choice | 0.074 | 0.347 |
| options | 2 | 0.030 | 0.068 |
| options | 3-5 | 0.089 | 0.649 |
| options | 6-26 | 0.149 | 0.814 |
| options | 27+ | 0.295 | 0.952 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 597 1573 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 241 216 215 131 5 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 57 56 46 52 41 50 49 44 49 34 21 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| letters | 27+ | chosen | 7 8 2 4 0 5 2 1 3 1 7 2 3 3 5 4 3 2 2 0 2 0 2 2 3 1 2 |
| letters | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |
| labels-unused | 2 | chosen | 660 1510 |
| labels-unused | 2 | gold | 613 1557 |
| labels-unused | 3-5 | chosen | 296 401 12 98 1 |
| labels-unused | 3-5 | gold | 240 230 199 137 2 |
| labels-unused | 6-26 | chosen | 209 42 0 6 1 175 9 21 27 2 10 0 0 0 0 0 0 0 2 0 0 0 1 0 0 0 |
| labels-unused | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-unused | 27+ | chosen | 8 10 1 1 0 4 0 1 1 0 5 0 1 0 0 0 2 0 4 0 0 1 0 0 1 0 1 |
| labels-unused | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |

