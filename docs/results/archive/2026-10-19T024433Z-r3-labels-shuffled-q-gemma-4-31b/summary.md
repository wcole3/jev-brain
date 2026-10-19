# gemma-4-31b R3 label screen: shuffled-q vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T024433Z
- repo commit: b6662bc-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: shuffled-q
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-shuffled-q calib-600: .cache/collect/gemma-4-31b/calib-600-shuffled-q.jsonl.gz
- collect labels-shuffled-q index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-shuffled-q.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-shuffled-q image dev: .cache/vision-collect/gemma-4-31b/labels-shuffled-q/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 42 s

all = every question both arms answered; pure = the questions the set run showed with its own labels (fallback questions use today's letters).
Reports only; the owner picks.

### Fallback share (all questions, set run)

| grouping | bucket | share |
|---|---|---|
| overall | all | 0.056 |
| type | choice | 0.056 |
| type | noul | 0.000 |
| options | 2 | 0.000 |
| options | 3-5 | 0.000 |
| options | 6-26 | 0.000 |
| options | 27+ | 1.000 |

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| letters | 590 | 3728 | 4.092 | 19.999 | 8.022 |
| labels-shuffled-q | 600 | 3728 | 3.940 | 19.999 | 6.720 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.125 | 0.808 | 0.324 | baseline | baseline | baseline |
| all | labels-shuffled-q | 3728 | 0.799 | 0.124 | 0.798 | 0.330 | -0.003 [-0.007, +0.002] | -0.0007 [-0.0056, +0.0044] | -0.0100 [-0.0248, +0.0047] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.125 | 0.813 | 0.325 | baseline | baseline | baseline |
| choice | labels-shuffled-q | 3690 | 0.798 | 0.125 | 0.803 | 0.332 | -0.003 [-0.008, +0.002] | -0.0007 [-0.0056, +0.0046] | -0.0101 [-0.0249, +0.0051] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-shuffled-q | 38 | 0.868 | 0.100 | 0.343 | 0.202 | +0.000 [+0.000, +0.000] | -0.0090 [-0.0358, +0.0144] | -0.0077 [-0.0306, +0.0132] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-shuffled-q | 2208 | 0.909 | 0.070 | 0.304 | 0.156 | +0.000 [-0.004, +0.005] | -0.0009 [-0.0052, +0.0033] | -0.0085 [-0.0194, +0.0024] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-shuffled-q | 808 | 0.798 | 0.128 | 0.719 | 0.343 | +0.001 [-0.011, +0.012] | -0.0043 [-0.0134, +0.0108] | -0.0035 [-0.0381, +0.0313] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-shuffled-q | 505 | 0.386 | 0.408 | 2.629 | 0.998 | -0.020 [-0.040, +0.000] | +0.0127 [-0.0089, +0.0318] | -0.0304 [-0.1072, +0.0441] |
| 27+ | letters | 207 | 0.638 | 0.114 | 1.910 | 0.512 | baseline | baseline | baseline |
| 27+ | labels-shuffled-q | 207 | 0.628 | 0.103 | 1.907 | 0.513 | -0.010 [-0.024, +0.000] | -0.0114 [-0.0436, +0.0296] | -0.0027 [-0.0184, +0.0133] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled-q |
|---|---|---|---|
| overall | all | 0.074 | 0.072 |
| type | choice | 0.074 | 0.072 |
| options | 2 | 0.030 | 0.028 |
| options | 3-5 | 0.089 | 0.090 |
| options | 6-26 | 0.149 | 0.145 |
| options | 27+ | 0.295 | 0.290 |

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
| labels-shuffled-q | 2 | chosen | 604 1566 |
| labels-shuffled-q | 2 | gold | 613 1557 |
| labels-shuffled-q | 3-5 | chosen | 240 225 213 127 3 |
| labels-shuffled-q | 3-5 | gold | 240 230 199 137 2 |
| labels-shuffled-q | 6-26 | chosen | 50 56 42 53 43 54 47 41 49 40 24 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| labels-shuffled-q | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-shuffled-q | 27+ | chosen | 6 8 3 3 0 5 3 1 3 1 7 2 3 4 4 4 3 2 2 0 2 0 2 2 4 1 2 |
| labels-shuffled-q | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3521 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3521 | 0.811 | 0.131 | 0.743 | 0.313 | baseline | baseline | baseline |
| all | labels-shuffled-q | 3521 | 0.809 | 0.129 | 0.733 | 0.320 | -0.002 [-0.007, +0.003] | -0.0018 [-0.0068, +0.0032] | -0.0105 [-0.0258, +0.0049] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3483 | 0.811 | 0.132 | 0.748 | 0.314 | baseline | baseline | baseline |
| choice | labels-shuffled-q | 3483 | 0.808 | 0.130 | 0.737 | 0.321 | -0.002 [-0.007, +0.003] | -0.0019 [-0.0070, +0.0033] | -0.0105 [-0.0257, +0.0050] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-shuffled-q | 38 | 0.868 | 0.100 | 0.343 | 0.202 | +0.000 [+0.000, +0.000] | -0.0090 [-0.0358, +0.0144] | -0.0077 [-0.0306, +0.0132] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-shuffled-q | 2208 | 0.909 | 0.070 | 0.304 | 0.156 | +0.000 [-0.004, +0.005] | -0.0009 [-0.0052, +0.0033] | -0.0085 [-0.0194, +0.0024] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-shuffled-q | 808 | 0.798 | 0.128 | 0.719 | 0.343 | +0.001 [-0.011, +0.012] | -0.0043 [-0.0134, +0.0108] | -0.0035 [-0.0381, +0.0313] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-shuffled-q | 505 | 0.386 | 0.408 | 2.629 | 0.998 | -0.020 [-0.040, +0.000] | +0.0127 [-0.0089, +0.0318] | -0.0304 [-0.1072, +0.0441] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled-q |
|---|---|---|---|
| overall | all | 0.061 | 0.059 |
| type | choice | 0.061 | 0.059 |
| options | 2 | 0.030 | 0.028 |
| options | 3-5 | 0.089 | 0.090 |
| options | 6-26 | 0.149 | 0.145 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 597 1573 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 241 216 215 131 5 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 57 56 46 52 41 50 49 44 49 34 21 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-shuffled-q | 2 | chosen | 604 1566 |
| labels-shuffled-q | 2 | gold | 613 1557 |
| labels-shuffled-q | 3-5 | chosen | 240 225 213 127 3 |
| labels-shuffled-q | 3-5 | gold | 240 230 199 137 2 |
| labels-shuffled-q | 6-26 | chosen | 50 56 42 53 43 54 47 41 49 40 24 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| labels-shuffled-q | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |

