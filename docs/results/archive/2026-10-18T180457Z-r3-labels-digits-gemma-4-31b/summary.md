# gemma-4-31b R3 label screen: digits vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-18T180457Z
- repo commit: 37a70a9
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: digits
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-digits calib-600: .cache/collect/gemma-4-31b/calib-600-digits.jsonl.gz
- collect labels-digits index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-digits.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-digits image dev: .cache/vision-collect/gemma-4-31b/labels-digits/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 37 s

all = every question both arms answered; pure = the questions the set run showed with its own labels (fallback questions use today's letters).
Reports only; the owner picks.

### Fallback share (all questions, set run)

| grouping | bucket | share |
|---|---|---|
| overall | all | 0.179 |
| type | choice | 0.181 |
| type | noul | 0.000 |
| options | 2 | 0.000 |
| options | 3-5 | 0.000 |
| options | 6-26 | 0.911 |
| options | 27+ | 1.000 |

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| letters | 590 | 3728 | 4.092 | 19.999 | 8.022 |
| labels-digits | 600 | 3728 | 3.876 | 19.999 | 6.031 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.125 | 0.808 | 0.324 | baseline | baseline | baseline |
| all | labels-digits | 3728 | 0.801 | 0.122 | 0.805 | 0.324 | -0.001 [-0.004, +0.002] | -0.0023 [-0.0056, +0.0017] | -0.0031 [-0.0106, +0.0045] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.125 | 0.813 | 0.325 | baseline | baseline | baseline |
| choice | labels-digits | 3690 | 0.800 | 0.123 | 0.810 | 0.325 | -0.001 [-0.004, +0.002] | -0.0024 [-0.0057, +0.0016] | -0.0030 [-0.0106, +0.0045] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-digits | 38 | 0.868 | 0.110 | 0.344 | 0.199 | +0.000 [+0.000, +0.000] | +0.0009 [-0.0166, +0.0164] | -0.0071 [-0.0278, +0.0105] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-digits | 2208 | 0.909 | 0.062 | 0.283 | 0.148 | +0.000 [-0.003, +0.003] | -0.0085 [-0.0120, -0.0058] | -0.0291 [-0.0379, -0.0200] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-digits | 808 | 0.793 | 0.133 | 0.722 | 0.343 | -0.004 [-0.012, +0.004] | +0.0006 [-0.0064, +0.0124] | -0.0006 [-0.0224, +0.0203] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-digits | 505 | 0.410 | 0.405 | 2.770 | 0.987 | +0.004 [+0.000, +0.010] | +0.0104 [-0.0028, +0.0203] | +0.1101 [+0.0966, +0.1246] |
| 27+ | letters | 207 | 0.638 | 0.114 | 1.910 | 0.512 | baseline | baseline | baseline |
| 27+ | labels-digits | 207 | 0.628 | 0.101 | 1.899 | 0.509 | -0.010 [-0.024, +0.000] | -0.0129 [-0.0457, +0.0299] | -0.0116 [-0.0357, +0.0125] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-digits |
|---|---|---|---|
| overall | all | 0.074 | 0.073 |
| type | choice | 0.074 | 0.073 |
| options | 2 | 0.030 | 0.025 |
| options | 3-5 | 0.089 | 0.094 |
| options | 6-26 | 0.149 | 0.152 |
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
| labels-digits | 2 | chosen | 603 1567 |
| labels-digits | 2 | gold | 613 1557 |
| labels-digits | 3-5 | chosen | 246 214 211 133 4 |
| labels-digits | 3-5 | gold | 240 230 199 137 2 |
| labels-digits | 6-26 | chosen | 57 56 46 50 39 54 49 43 49 35 21 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| labels-digits | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-digits | 27+ | chosen | 6 8 2 4 0 5 3 1 3 1 7 2 3 4 5 4 4 2 2 0 2 0 2 2 3 1 2 |
| labels-digits | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3061 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3061 | 0.878 | 0.087 | 0.424 | 0.204 | baseline | baseline | baseline |
| all | labels-digits | 3061 | 0.877 | 0.081 | 0.404 | 0.201 | -0.001 [-0.004, +0.002] | -0.0061 [-0.0094, -0.0027] | -0.0200 [-0.0292, -0.0118] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3023 | 0.878 | 0.087 | 0.425 | 0.204 | baseline | baseline | baseline |
| choice | labels-digits | 3023 | 0.877 | 0.081 | 0.405 | 0.201 | -0.001 [-0.004, +0.002] | -0.0063 [-0.0096, -0.0030] | -0.0202 [-0.0294, -0.0117] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-digits | 38 | 0.868 | 0.110 | 0.344 | 0.199 | +0.000 [+0.000, +0.000] | +0.0009 [-0.0166, +0.0164] | -0.0071 [-0.0278, +0.0105] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-digits | 2208 | 0.909 | 0.062 | 0.283 | 0.148 | +0.000 [-0.003, +0.003] | -0.0085 [-0.0120, -0.0058] | -0.0291 [-0.0379, -0.0200] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-digits | 808 | 0.793 | 0.133 | 0.722 | 0.343 | -0.004 [-0.012, +0.004] | +0.0006 [-0.0064, +0.0124] | -0.0006 [-0.0224, +0.0203] |
| 6-26 | letters | 45 | 0.822 | 0.126 | 0.557 | 0.256 | baseline | baseline | baseline |
| 6-26 | labels-digits | 45 | 0.822 | 0.098 | 0.632 | 0.271 | +0.000 [+0.000, +0.000] | -0.0280 [-0.0601, +0.0224] | +0.0748 [+0.0192, +0.1474] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-digits |
|---|---|---|---|
| overall | all | 0.047 | 0.045 |
| type | choice | 0.047 | 0.045 |
| options | 2 | 0.030 | 0.025 |
| options | 3-5 | 0.089 | 0.094 |
| options | 6-26 | 0.089 | 0.089 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 597 1573 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 241 216 215 131 5 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 3 7 8 6 5 8 4 1 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 6 8 7 4 4 8 5 1 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 2 | chosen | 603 1567 |
| labels-digits | 2 | gold | 613 1557 |
| labels-digits | 3-5 | chosen | 246 214 211 133 4 |
| labels-digits | 3-5 | gold | 240 230 199 137 2 |
| labels-digits | 6-26 | chosen | 3 7 8 6 4 9 4 1 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 6-26 | gold | 6 8 7 4 4 8 5 1 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

