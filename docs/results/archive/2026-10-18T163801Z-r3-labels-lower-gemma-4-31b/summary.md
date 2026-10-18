# gemma-4-31b R3 label screen: lower vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-18T163801Z
- repo commit: b784d38
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: lower
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-lower calib-600: .cache/collect/gemma-4-31b/calib-600-lower.jsonl.gz
- collect labels-lower index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-lower.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-lower image dev: .cache/vision-collect/gemma-4-31b/labels-lower/dev.jsonl.gz
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
| labels-lower | 600 | 3728 | 3.862 | 19.999 | 6.627 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.125 | 0.808 | 0.324 | baseline | baseline | baseline |
| all | labels-lower | 3728 | 0.799 | 0.132 | 0.806 | 0.330 | -0.003 [-0.006, +0.000] | +0.0070 [+0.0035, +0.0103] | -0.0017 [-0.0106, +0.0064] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.125 | 0.813 | 0.325 | baseline | baseline | baseline |
| choice | labels-lower | 3690 | 0.798 | 0.132 | 0.811 | 0.331 | -0.003 [-0.006, +0.000] | +0.0071 [+0.0036, +0.0105] | -0.0016 [-0.0103, +0.0070] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-lower | 38 | 0.868 | 0.105 | 0.334 | 0.198 | +0.000 [+0.000, +0.000] | -0.0036 [-0.0212, +0.0182] | -0.0162 [-0.0401, +0.0019] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-lower | 2208 | 0.907 | 0.069 | 0.297 | 0.155 | -0.002 [-0.005, +0.001] | -0.0017 [-0.0048, -0.0000] | -0.0153 [-0.0216, -0.0091] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-lower | 808 | 0.792 | 0.147 | 0.748 | 0.348 | -0.005 [-0.011, +0.000] | +0.0143 [+0.0072, +0.0214] | +0.0249 [+0.0073, +0.0415] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-lower | 505 | 0.404 | 0.415 | 2.677 | 0.991 | -0.002 [-0.016, +0.012] | +0.0198 [+0.0051, +0.0360] | +0.0172 [-0.0324, +0.0682] |
| 27+ | letters | 207 | 0.638 | 0.114 | 1.910 | 0.512 | baseline | baseline | baseline |
| 27+ | labels-lower | 207 | 0.633 | 0.109 | 1.904 | 0.510 | -0.005 [-0.024, +0.014] | -0.0055 [-0.0354, +0.0325] | -0.0063 [-0.0305, +0.0189] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-lower |
|---|---|---|---|
| overall | all | 0.074 | 0.076 |
| type | choice | 0.074 | 0.076 |
| options | 2 | 0.030 | 0.029 |
| options | 3-5 | 0.089 | 0.089 |
| options | 6-26 | 0.149 | 0.168 |
| options | 27+ | 0.295 | 0.304 |

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
| labels-lower | 2 | chosen | 601 1569 |
| labels-lower | 2 | gold | 613 1557 |
| labels-lower | 3-5 | chosen | 243 216 213 132 4 |
| labels-lower | 3-5 | gold | 240 230 199 137 2 |
| labels-lower | 6-26 | chosen | 56 59 41 51 44 52 50 40 47 39 20 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| labels-lower | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-lower | 27+ | chosen | 7 8 2 3 0 5 3 1 2 1 7 2 3 4 4 4 4 2 2 0 2 0 2 2 3 1 2 |
| labels-lower | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3521 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3521 | 0.811 | 0.131 | 0.743 | 0.313 | baseline | baseline | baseline |
| all | labels-lower | 3521 | 0.809 | 0.136 | 0.742 | 0.319 | -0.003 [-0.006, +0.000] | +0.0046 [+0.0016, +0.0081] | -0.0014 [-0.0104, +0.0077] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3483 | 0.811 | 0.132 | 0.748 | 0.314 | baseline | baseline | baseline |
| choice | labels-lower | 3483 | 0.808 | 0.137 | 0.746 | 0.320 | -0.003 [-0.005, +0.000] | +0.0046 [+0.0017, +0.0081] | -0.0013 [-0.0101, +0.0075] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-lower | 38 | 0.868 | 0.105 | 0.334 | 0.198 | +0.000 [+0.000, +0.000] | -0.0036 [-0.0212, +0.0182] | -0.0162 [-0.0401, +0.0019] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-lower | 2208 | 0.907 | 0.069 | 0.297 | 0.155 | -0.002 [-0.005, +0.001] | -0.0017 [-0.0048, -0.0000] | -0.0153 [-0.0216, -0.0091] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-lower | 808 | 0.792 | 0.147 | 0.748 | 0.348 | -0.005 [-0.011, +0.000] | +0.0143 [+0.0072, +0.0214] | +0.0249 [+0.0073, +0.0415] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-lower | 505 | 0.404 | 0.415 | 2.677 | 0.991 | -0.002 [-0.016, +0.012] | +0.0198 [+0.0051, +0.0360] | +0.0172 [-0.0324, +0.0682] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-lower |
|---|---|---|---|
| overall | all | 0.061 | 0.063 |
| type | choice | 0.061 | 0.063 |
| options | 2 | 0.030 | 0.029 |
| options | 3-5 | 0.089 | 0.089 |
| options | 6-26 | 0.149 | 0.168 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 597 1573 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 241 216 215 131 5 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 57 56 46 52 41 50 49 44 49 34 21 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-lower | 2 | chosen | 601 1569 |
| labels-lower | 2 | gold | 613 1557 |
| labels-lower | 3-5 | chosen | 243 216 213 132 4 |
| labels-lower | 3-5 | gold | 240 230 199 137 2 |
| labels-lower | 6-26 | chosen | 56 59 41 51 44 52 50 40 47 39 20 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| labels-lower | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |

