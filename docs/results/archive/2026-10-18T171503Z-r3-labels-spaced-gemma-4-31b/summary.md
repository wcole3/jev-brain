# gemma-4-31b R3 label screen: spaced vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-18T171503Z
- repo commit: b533859
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: spaced
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-spaced calib-600: .cache/collect/gemma-4-31b/calib-600-spaced.jsonl.gz
- collect labels-spaced index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-spaced.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-spaced image dev: .cache/vision-collect/gemma-4-31b/labels-spaced/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 37 s

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
| labels-spaced | 585 | 3728 | 4.086 | 19.999 | 6.795 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.125 | 0.808 | 0.324 | baseline | baseline | baseline |
| all | labels-spaced | 3728 | 0.800 | 0.114 | 0.774 | 0.327 | -0.002 [-0.005, +0.002] | -0.0111 [-0.0155, -0.0062] | -0.0342 [-0.0463, -0.0225] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.125 | 0.813 | 0.325 | baseline | baseline | baseline |
| choice | labels-spaced | 3690 | 0.799 | 0.114 | 0.778 | 0.328 | -0.002 [-0.005, +0.002] | -0.0112 [-0.0157, -0.0065] | -0.0345 [-0.0465, -0.0224] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-spaced | 38 | 0.868 | 0.096 | 0.353 | 0.209 | +0.000 [+0.000, +0.000] | -0.0122 [-0.0369, +0.0077] | +0.0026 [-0.0237, +0.0283] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-spaced | 2208 | 0.908 | 0.062 | 0.277 | 0.151 | -0.001 [-0.004, +0.002] | -0.0087 [-0.0125, -0.0056] | -0.0351 [-0.0471, -0.0236] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-spaced | 808 | 0.793 | 0.115 | 0.700 | 0.340 | -0.004 [-0.014, +0.006] | -0.0170 [-0.0263, -0.0032] | -0.0230 [-0.0532, +0.0047] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-spaced | 505 | 0.406 | 0.400 | 2.615 | 0.991 | +0.000 [-0.014, +0.014] | +0.0048 [-0.0150, +0.0236] | -0.0452 [-0.0936, +0.0040] |
| 27+ | letters | 207 | 0.638 | 0.114 | 1.910 | 0.512 | baseline | baseline | baseline |
| 27+ | labels-spaced | 207 | 0.633 | 0.091 | 1.870 | 0.530 | -0.005 [-0.029, +0.019] | -0.0229 [-0.0610, +0.0391] | -0.0406 [-0.1213, +0.0405] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-spaced |
|---|---|---|---|
| overall | all | 0.074 | 0.076 |
| type | choice | 0.074 | 0.076 |
| options | 2 | 0.030 | 0.032 |
| options | 3-5 | 0.089 | 0.085 |
| options | 6-26 | 0.149 | 0.162 |
| options | 27+ | 0.295 | 0.300 |

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
| labels-spaced | 2 | chosen | 593 1577 |
| labels-spaced | 2 | gold | 613 1557 |
| labels-spaced | 3-5 | chosen | 238 223 213 130 4 |
| labels-spaced | 3-5 | gold | 240 230 199 137 2 |
| labels-spaced | 6-26 | chosen | 55 63 39 52 40 50 50 42 49 36 23 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| labels-spaced | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-spaced | 27+ | chosen | 6 9 2 4 0 5 4 1 3 1 7 2 3 3 5 2 3 1 2 0 3 1 1 3 3 1 3 |
| labels-spaced | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3521 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3521 | 0.811 | 0.131 | 0.743 | 0.313 | baseline | baseline | baseline |
| all | labels-spaced | 3521 | 0.810 | 0.121 | 0.709 | 0.315 | -0.001 [-0.005, +0.002] | -0.0103 [-0.0146, -0.0061] | -0.0338 [-0.0465, -0.0214] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3483 | 0.811 | 0.132 | 0.748 | 0.314 | baseline | baseline | baseline |
| choice | labels-spaced | 3483 | 0.809 | 0.122 | 0.713 | 0.316 | -0.001 [-0.005, +0.002] | -0.0104 [-0.0149, -0.0061] | -0.0342 [-0.0468, -0.0217] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-spaced | 38 | 0.868 | 0.096 | 0.353 | 0.209 | +0.000 [+0.000, +0.000] | -0.0122 [-0.0369, +0.0077] | +0.0026 [-0.0237, +0.0283] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-spaced | 2208 | 0.908 | 0.062 | 0.277 | 0.151 | -0.001 [-0.004, +0.002] | -0.0087 [-0.0125, -0.0056] | -0.0351 [-0.0471, -0.0236] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-spaced | 808 | 0.793 | 0.115 | 0.700 | 0.340 | -0.004 [-0.014, +0.006] | -0.0170 [-0.0263, -0.0032] | -0.0230 [-0.0532, +0.0047] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-spaced | 505 | 0.406 | 0.400 | 2.615 | 0.991 | +0.000 [-0.014, +0.014] | +0.0048 [-0.0150, +0.0236] | -0.0452 [-0.0936, +0.0040] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-spaced |
|---|---|---|---|
| overall | all | 0.061 | 0.063 |
| type | choice | 0.061 | 0.063 |
| options | 2 | 0.030 | 0.032 |
| options | 3-5 | 0.089 | 0.085 |
| options | 6-26 | 0.149 | 0.162 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 597 1573 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 241 216 215 131 5 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 57 56 46 52 41 50 49 44 49 34 21 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-spaced | 2 | chosen | 593 1577 |
| labels-spaced | 2 | gold | 613 1557 |
| labels-spaced | 3-5 | chosen | 238 223 213 130 4 |
| labels-spaced | 3-5 | gold | 240 230 199 137 2 |
| labels-spaced | 6-26 | chosen | 55 63 39 52 40 50 50 42 49 36 23 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| labels-spaced | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |

