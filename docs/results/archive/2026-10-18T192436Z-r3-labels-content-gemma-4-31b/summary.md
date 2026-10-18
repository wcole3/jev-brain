# gemma-4-31b R3 label screen: content vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-18T192436Z
- repo commit: 1c9af21-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: content
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-content calib-600: .cache/collect/gemma-4-31b/calib-600-content.jsonl.gz
- collect labels-content index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-content.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-content image dev: .cache/vision-collect/gemma-4-31b/labels-content/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 40 s

all = every question both arms answered; pure = the questions the set run showed with its own labels (fallback questions use today's letters).
Reports only; the owner picks.

### Fallback share (all questions, set run)

| grouping | bucket | share |
|---|---|---|
| overall | all | 0.210 |
| type | choice | 0.212 |
| type | noul | 0.000 |
| options | 2 | 0.071 |
| options | 3-5 | 0.099 |
| options | 6-26 | 0.675 |
| options | 27+ | 1.000 |

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| letters | 590 | 3728 | 4.092 | 19.999 | 8.022 |
| labels-content | 585 | 3728 | 3.971 | 19.999 | 7.536 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.125 | 0.808 | 0.324 | baseline | baseline | baseline |
| all | labels-content | 3728 | 0.802 | 0.114 | 0.804 | 0.329 | +0.000 [-0.004, +0.005] | -0.0107 [-0.0155, -0.0054] | -0.0043 [-0.0176, +0.0077] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.125 | 0.813 | 0.325 | baseline | baseline | baseline |
| choice | labels-content | 3690 | 0.801 | 0.114 | 0.808 | 0.330 | +0.000 [-0.004, +0.005] | -0.0110 [-0.0159, -0.0058] | -0.0045 [-0.0174, +0.0076] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-content | 38 | 0.868 | 0.084 | 0.365 | 0.213 | +0.000 [+0.000, +0.000] | -0.0245 [-0.0509, +0.0054] | +0.0149 [-0.0157, +0.0549] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.909 | 0.071 | 0.313 | 0.154 | baseline | baseline | baseline |
| 2 | labels-content | 2208 | 0.912 | 0.067 | 0.306 | 0.151 | +0.003 [-0.002, +0.008] | -0.0035 [-0.0073, +0.0009] | -0.0069 [-0.0186, +0.0041] |
| 3-5 | letters | 808 | 0.797 | 0.132 | 0.723 | 0.335 | baseline | baseline | baseline |
| 3-5 | labels-content | 808 | 0.795 | 0.111 | 0.722 | 0.342 | -0.002 [-0.012, +0.007] | -0.0212 [-0.0317, -0.0028] | -0.0010 [-0.0349, +0.0299] |
| 6-26 | letters | 505 | 0.406 | 0.395 | 2.660 | 0.968 | baseline | baseline | baseline |
| 6-26 | labels-content | 505 | 0.406 | 0.394 | 2.680 | 1.006 | +0.000 [-0.016, +0.016] | -0.0010 [-0.0186, +0.0275] | +0.0197 [-0.0289, +0.0679] |
| 27+ | letters | 207 | 0.638 | 0.114 | 1.910 | 0.512 | baseline | baseline | baseline |
| 27+ | labels-content | 207 | 0.618 | 0.097 | 1.862 | 0.528 | -0.019 [-0.048, +0.005] | -0.0168 [-0.0575, +0.0419] | -0.0483 [-0.1297, +0.0291] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-content |
|---|---|---|---|
| overall | all | 0.074 | 0.071 |
| type | choice | 0.074 | 0.071 |
| options | 2 | 0.030 | 0.024 |
| options | 3-5 | 0.089 | 0.082 |
| options | 6-26 | 0.149 | 0.168 |
| options | 27+ | 0.295 | 0.295 |

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
| labels-content | 2 | chosen | 615 1555 |
| labels-content | 2 | gold | 613 1557 |
| labels-content | 3-5 | chosen | 234 226 213 131 4 |
| labels-content | 3-5 | gold | 240 230 199 137 2 |
| labels-content | 6-26 | chosen | 57 63 38 52 39 50 50 42 50 34 24 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| labels-content | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-content | 27+ | chosen | 6 9 2 3 0 4 5 1 3 1 8 2 3 4 4 2 3 2 2 0 3 2 2 3 3 1 3 |
| labels-content | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (2944 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 2944 | 0.880 | 0.081 | 0.422 | 0.200 | baseline | baseline | baseline |
| all | labels-content | 2944 | 0.882 | 0.071 | 0.425 | 0.201 | +0.002 [-0.003, +0.007] | -0.0097 [-0.0150, -0.0029] | +0.0033 [-0.0090, +0.0157] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 2906 | 0.880 | 0.081 | 0.423 | 0.200 | baseline | baseline | baseline |
| choice | labels-content | 2906 | 0.882 | 0.071 | 0.426 | 0.201 | +0.002 [-0.003, +0.007] | -0.0101 [-0.0155, -0.0031] | +0.0031 [-0.0093, +0.0155] |
| noul | letters | 38 | 0.868 | 0.109 | 0.351 | 0.200 | baseline | baseline | baseline |
| noul | labels-content | 38 | 0.868 | 0.084 | 0.365 | 0.213 | +0.000 [+0.000, +0.000] | -0.0245 [-0.0509, +0.0054] | +0.0149 [-0.0157, +0.0549] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2052 | 0.912 | 0.069 | 0.306 | 0.150 | baseline | baseline | baseline |
| 2 | labels-content | 2052 | 0.916 | 0.066 | 0.301 | 0.146 | +0.003 [-0.002, +0.008] | -0.0033 [-0.0073, +0.0014] | -0.0043 [-0.0160, +0.0076] |
| 3-5 | letters | 728 | 0.810 | 0.127 | 0.679 | 0.314 | baseline | baseline | baseline |
| 3-5 | labels-content | 728 | 0.810 | 0.103 | 0.672 | 0.319 | +0.000 [-0.010, +0.010] | -0.0246 [-0.0353, -0.0040] | -0.0066 [-0.0417, +0.0287] |
| 6-26 | letters | 164 | 0.787 | 0.071 | 0.736 | 0.310 | baseline | baseline | baseline |
| 6-26 | labels-content | 164 | 0.780 | 0.113 | 0.878 | 0.360 | -0.006 [-0.043, +0.030] | +0.0419 [-0.0172, +0.0974] | +0.1418 [+0.0729, +0.2095] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-content |
|---|---|---|---|
| overall | all | 0.042 | 0.039 |
| type | choice | 0.042 | 0.039 |
| options | 2 | 0.018 | 0.011 |
| options | 3-5 | 0.076 | 0.070 |
| options | 6-26 | 0.189 | 0.244 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 515 1499 |
| letters | 2 | gold | 528 1486 |
| letters | 3-5 | chosen | 222 192 194 118 2 |
| letters | 3-5 | gold | 227 206 174 121 0 |
| letters | 6-26 | chosen | 22 15 14 23 13 20 17 14 15 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 19 15 18 18 11 24 17 18 13 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 2 | chosen | 534 1480 |
| labels-content | 2 | gold | 528 1486 |
| labels-content | 3-5 | chosen | 214 200 194 119 1 |
| labels-content | 3-5 | gold | 227 206 174 121 0 |
| labels-content | 6-26 | chosen | 23 18 11 25 12 20 16 14 17 8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 6-26 | gold | 19 15 18 18 11 24 17 18 13 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

