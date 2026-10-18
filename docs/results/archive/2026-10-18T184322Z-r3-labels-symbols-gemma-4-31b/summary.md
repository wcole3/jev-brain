# gemma-4-31b R3 label screen: symbols vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-18T184322Z
- repo commit: f623b0c-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: symbols
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-symbols calib-600: .cache/collect/gemma-4-31b/calib-600-symbols.jsonl.gz
- collect labels-symbols index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-symbols.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-symbols image dev: .cache/vision-collect/gemma-4-31b/labels-symbols/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 45 s

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
| letters | 590 | 3728 | 4.092 | 19.999 | 8.022 |
| labels-symbols | 585 | 3728 | 3.834 | 11.044 | 4.457 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.125 | 0.808 | 0.324 | baseline | baseline | baseline |
| all | labels-symbols | 3728 | 0.743 | 0.110 | 0.817 | 0.365 | -0.058 [-0.068, -0.049] | -0.0148 [-0.0248, -0.0058] | +0.0093 [-0.0211, +0.0379] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.125 | 0.813 | 0.325 | baseline | baseline | baseline |
| choice | labels-symbols | 3690 | 0.742 | 0.110 | 0.822 | 0.367 | -0.059 [-0.069, -0.049] | -0.0152 [-0.0254, -0.0062] | +0.0091 [-0.0203, +0.0378] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-symbols | 38 | 0.868 | 0.083 | 0.381 | 0.229 | +0.000 [+0.000, +0.000] | -0.0257 [-0.0772, +0.0087] | +0.0304 [-0.0588, +0.1388] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-symbols | 2208 | 0.837 | 0.093 | 0.355 | 0.217 | -0.072 [-0.086, -0.060] | +0.0222 [+0.0104, +0.0329] | +0.0421 [+0.0092, +0.0758] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-symbols | 808 | 0.762 | 0.074 | 0.804 | 0.386 | -0.035 [-0.052, -0.017] | -0.0588 [-0.0650, -0.0223] | +0.0813 [+0.0222, +0.1388] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-symbols | 505 | 0.354 | 0.297 | 2.410 | 0.910 | -0.051 [-0.075, -0.028] | -0.0982 [-0.1300, -0.0724] | -0.2502 [-0.3729, -0.1255] |
| 27+ | letters | 207 | 0.638 | 0.114 | 1.910 | 0.512 | baseline | baseline | baseline |
| 27+ | labels-symbols | 207 | 0.623 | 0.096 | 1.921 | 0.538 | -0.014 [-0.043, +0.014] | -0.0181 [-0.0686, +0.0513] | +0.0111 [-0.0878, +0.1191] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-symbols |
|---|---|---|---|
| overall | all | 0.074 | 0.180 |
| type | choice | 0.074 | 0.180 |
| options | 2 | 0.030 | 0.168 |
| options | 3-5 | 0.089 | 0.146 |
| options | 6-26 | 0.149 | 0.230 |
| options | 27+ | 0.295 | 0.319 |

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
| labels-symbols | 2 | chosen | 457 1713 |
| labels-symbols | 2 | gold | 613 1557 |
| labels-symbols | 3-5 | chosen | 243 212 194 153 6 |
| labels-symbols | 3-5 | gold | 240 230 199 137 2 |
| labels-symbols | 6-26 | chosen | 40 60 38 53 63 55 47 44 46 33 23 0 0 0 0 0 1 0 0 0 0 1 1 0 0 0 |
| labels-symbols | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-symbols | 27+ | chosen | 8 11 1 5 0 4 6 2 3 1 6 2 3 4 4 2 4 1 2 0 2 2 2 1 3 1 3 |
| labels-symbols | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3536 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3536 | 0.808 | 0.132 | 0.757 | 0.316 | baseline | baseline | baseline |
| all | labels-symbols | 3536 | 0.748 | 0.117 | 0.766 | 0.359 | -0.060 [-0.070, -0.051] | -0.0150 [-0.0251, -0.0056] | +0.0100 [-0.0209, +0.0407] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3498 | 0.808 | 0.133 | 0.761 | 0.317 | baseline | baseline | baseline |
| choice | labels-symbols | 3498 | 0.747 | 0.117 | 0.771 | 0.360 | -0.061 [-0.072, -0.051] | -0.0155 [-0.0254, -0.0061] | +0.0097 [-0.0213, +0.0415] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-symbols | 38 | 0.868 | 0.083 | 0.381 | 0.229 | +0.000 [+0.000, +0.000] | -0.0257 [-0.0772, +0.0087] | +0.0304 [-0.0588, +0.1388] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-symbols | 2208 | 0.837 | 0.093 | 0.355 | 0.217 | -0.072 [-0.086, -0.060] | +0.0222 [+0.0104, +0.0329] | +0.0421 [+0.0092, +0.0758] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-symbols | 808 | 0.762 | 0.074 | 0.804 | 0.386 | -0.035 [-0.052, -0.017] | -0.0588 [-0.0650, -0.0223] | +0.0813 [+0.0222, +0.1388] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-symbols | 505 | 0.354 | 0.297 | 2.410 | 0.910 | -0.051 [-0.075, -0.028] | -0.0982 [-0.1300, -0.0724] | -0.2502 [-0.3729, -0.1255] |
| 27+ | letters | 15 | 0.133 | 0.329 | 3.863 | 1.066 | baseline | baseline | baseline |
| 27+ | labels-symbols | 15 | 0.200 | 0.547 | 4.058 | 1.217 | +0.067 [-0.133, +0.333] | +0.2180 [-0.0266, +0.4187] | +0.1942 [-0.6424, +0.9677] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-symbols |
|---|---|---|---|
| overall | all | 0.063 | 0.173 |
| type | choice | 0.063 | 0.173 |
| options | 2 | 0.030 | 0.168 |
| options | 3-5 | 0.089 | 0.146 |
| options | 6-26 | 0.149 | 0.230 |
| options | 27+ | 0.533 | 0.533 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 597 1573 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 241 216 215 131 5 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 57 56 46 52 41 50 49 44 49 34 21 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| letters | 27+ | chosen | 1 1 1 1 0 2 0 1 1 0 3 0 1 0 0 1 1 0 0 0 0 0 0 0 1 0 0 |
| letters | 27+ | gold | 0 0 1 1 0 0 0 0 0 0 1 0 0 1 1 0 0 0 1 1 0 0 0 0 1 1 2 |
| labels-symbols | 2 | chosen | 457 1713 |
| labels-symbols | 2 | gold | 613 1557 |
| labels-symbols | 3-5 | chosen | 243 212 194 153 6 |
| labels-symbols | 3-5 | gold | 240 230 199 137 2 |
| labels-symbols | 6-26 | chosen | 40 60 38 53 63 55 47 44 46 33 23 0 0 0 0 0 1 0 0 0 0 1 1 0 0 0 |
| labels-symbols | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-symbols | 27+ | chosen | 0 5 0 2 0 1 0 1 1 0 1 0 1 0 0 0 1 0 0 0 0 0 0 0 1 0 0 |
| labels-symbols | 27+ | gold | 0 0 1 1 0 0 0 0 0 0 1 0 0 1 1 0 0 0 1 1 0 0 0 0 1 1 2 |

