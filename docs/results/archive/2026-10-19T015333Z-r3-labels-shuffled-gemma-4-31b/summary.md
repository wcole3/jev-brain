# gemma-4-31b R3 label screen: shuffled vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T015333Z
- repo commit: 111f0d1-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: shuffled
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-shuffled calib-600: .cache/collect/gemma-4-31b/calib-600-shuffled.jsonl.gz
- collect labels-shuffled index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-shuffled.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-shuffled image dev: .cache/vision-collect/gemma-4-31b/labels-shuffled/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 46 s

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
| labels-shuffled | 600 | 3728 | 3.910 | 19.999 | 6.101 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.125 | 0.808 | 0.324 | baseline | baseline | baseline |
| all | labels-shuffled | 3728 | 0.802 | 0.126 | 0.822 | 0.331 | +0.000 [-0.005, +0.005] | +0.0010 [-0.0043, +0.0060] | +0.0138 [-0.0007, +0.0270] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.125 | 0.813 | 0.325 | baseline | baseline | baseline |
| choice | labels-shuffled | 3690 | 0.801 | 0.126 | 0.826 | 0.332 | +0.000 [-0.005, +0.005] | +0.0007 [-0.0047, +0.0056] | +0.0135 [-0.0013, +0.0271] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-shuffled | 38 | 0.868 | 0.094 | 0.391 | 0.217 | +0.000 [+0.000, +0.000] | -0.0151 [-0.0413, +0.0069] | +0.0406 [-0.0190, +0.1195] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-shuffled | 2208 | 0.912 | 0.070 | 0.309 | 0.154 | +0.003 [-0.002, +0.007] | -0.0008 [-0.0054, +0.0029] | -0.0039 [-0.0142, +0.0065] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-shuffled | 808 | 0.806 | 0.126 | 0.746 | 0.339 | +0.009 [-0.001, +0.020] | -0.0066 [-0.0162, +0.0079] | +0.0229 [-0.0120, +0.0561] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-shuffled | 505 | 0.386 | 0.415 | 2.743 | 1.020 | -0.020 [-0.042, +0.000] | +0.0205 [-0.0015, +0.0425] | +0.0837 [+0.0075, +0.1581] |
| 27+ | letters | 207 | 0.638 | 0.114 | 1.910 | 0.512 | baseline | baseline | baseline |
| 27+ | labels-shuffled | 207 | 0.628 | 0.111 | 1.908 | 0.512 | -0.010 [-0.024, +0.000] | -0.0034 [-0.0440, +0.0234] | -0.0026 [-0.0222, +0.0169] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled |
|---|---|---|---|
| overall | all | 0.074 | 0.072 |
| type | choice | 0.074 | 0.072 |
| options | 2 | 0.030 | 0.028 |
| options | 3-5 | 0.089 | 0.087 |
| options | 6-26 | 0.149 | 0.147 |
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
| labels-shuffled | 2 | chosen | 611 1559 |
| labels-shuffled | 2 | gold | 613 1557 |
| labels-shuffled | 3-5 | chosen | 244 221 208 132 3 |
| labels-shuffled | 3-5 | gold | 240 230 199 137 2 |
| labels-shuffled | 6-26 | chosen | 50 56 45 53 40 48 44 41 52 45 25 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| labels-shuffled | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-shuffled | 27+ | chosen | 7 8 2 4 0 5 3 1 3 1 7 2 3 3 5 4 3 2 2 0 2 0 2 2 3 1 2 |
| labels-shuffled | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3521 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3521 | 0.811 | 0.131 | 0.743 | 0.313 | baseline | baseline | baseline |
| all | labels-shuffled | 3521 | 0.812 | 0.130 | 0.758 | 0.321 | +0.001 [-0.004, +0.006] | -0.0009 [-0.0057, +0.0044] | +0.0148 [+0.0005, +0.0298] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3483 | 0.811 | 0.132 | 0.748 | 0.314 | baseline | baseline | baseline |
| choice | labels-shuffled | 3483 | 0.811 | 0.131 | 0.762 | 0.322 | +0.001 [-0.004, +0.006] | -0.0013 [-0.0063, +0.0041] | +0.0145 [-0.0005, +0.0294] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-shuffled | 38 | 0.868 | 0.094 | 0.391 | 0.217 | +0.000 [+0.000, +0.000] | -0.0151 [-0.0413, +0.0069] | +0.0406 [-0.0190, +0.1195] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-shuffled | 2208 | 0.912 | 0.070 | 0.309 | 0.154 | +0.003 [-0.002, +0.007] | -0.0008 [-0.0054, +0.0029] | -0.0039 [-0.0142, +0.0065] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-shuffled | 808 | 0.806 | 0.126 | 0.746 | 0.339 | +0.009 [-0.001, +0.020] | -0.0066 [-0.0162, +0.0079] | +0.0229 [-0.0120, +0.0561] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-shuffled | 505 | 0.386 | 0.415 | 2.743 | 1.020 | -0.020 [-0.042, +0.000] | +0.0205 [-0.0015, +0.0425] | +0.0837 [+0.0075, +0.1581] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled |
|---|---|---|---|
| overall | all | 0.061 | 0.059 |
| type | choice | 0.061 | 0.059 |
| options | 2 | 0.030 | 0.028 |
| options | 3-5 | 0.089 | 0.087 |
| options | 6-26 | 0.149 | 0.147 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 597 1573 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 241 216 215 131 5 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 57 56 46 52 41 50 49 44 49 34 21 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-shuffled | 2 | chosen | 611 1559 |
| labels-shuffled | 2 | gold | 613 1557 |
| labels-shuffled | 3-5 | chosen | 244 221 208 132 3 |
| labels-shuffled | 3-5 | gold | 240 230 199 137 2 |
| labels-shuffled | 6-26 | chosen | 50 56 45 53 40 48 44 41 52 45 25 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| labels-shuffled | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |

