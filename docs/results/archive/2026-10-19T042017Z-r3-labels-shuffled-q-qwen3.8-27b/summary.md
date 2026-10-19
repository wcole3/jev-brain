# qwen3.8-27b R3 label screen: shuffled-q vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T042017Z
- repo commit: 8d38bd7-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: shuffled-q
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-shuffled-q calib-600: .cache/collect/qwen3.8-27b/calib-600-shuffled-q.jsonl.gz
- collect labels-shuffled-q index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-shuffled-q.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-shuffled-q image dev: .cache/vision-collect/qwen3.8-27b/labels-shuffled-q/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 40 s

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
| letters | 590 | 3728 | 1.491 | 5.160 | 0.934 |
| labels-shuffled-q | 590 | 3728 | 1.457 | 4.862 | 0.990 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.782 | 0.021 | 0.735 | 0.306 | baseline | baseline | baseline |
| all | labels-shuffled-q | 3728 | 0.777 | 0.034 | 0.749 | 0.312 | -0.004 [-0.010, +0.002] | +0.0125 [-0.0019, +0.0172] | +0.0144 [+0.0043, +0.0244] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.781 | 0.022 | 0.737 | 0.307 | baseline | baseline | baseline |
| choice | labels-shuffled-q | 3690 | 0.777 | 0.034 | 0.752 | 0.313 | -0.004 [-0.010, +0.002] | +0.0115 [-0.0022, +0.0167] | +0.0150 [+0.0046, +0.0249] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-shuffled-q | 38 | 0.842 | 0.165 | 0.425 | 0.212 | -0.026 [-0.079, +0.000] | +0.0520 [-0.0313, +0.1004] | -0.0487 [-0.1096, +0.0034] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-shuffled-q | 2208 | 0.912 | 0.015 | 0.215 | 0.131 | -0.003 [-0.009, +0.003] | -0.0177 [-0.0234, -0.0004] | +0.0003 [-0.0054, +0.0062] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-shuffled-q | 808 | 0.762 | 0.030 | 0.629 | 0.328 | -0.012 [-0.030, +0.005] | +0.0110 [-0.0139, +0.0301] | +0.0449 [+0.0261, +0.0646] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-shuffled-q | 505 | 0.299 | 0.275 | 2.778 | 0.979 | -0.004 [-0.022, +0.014] | -0.0008 [-0.0183, +0.0170] | +0.0454 [-0.0095, +0.0994] |
| 27+ | letters | 207 | 0.556 | 0.096 | 1.993 | 0.552 | baseline | baseline | baseline |
| 27+ | labels-shuffled-q | 207 | 0.570 | 0.096 | 1.962 | 0.556 | +0.014 [-0.010, +0.039] | +0.0004 [-0.0345, +0.0428] | -0.0304 [-0.1022, +0.0356] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled-q |
|---|---|---|---|
| overall | all | 0.096 | 0.111 |
| type | choice | 0.096 | 0.111 |
| options | 2 | 0.032 | 0.062 |
| options | 3-5 | 0.126 | 0.135 |
| options | 6-26 | 0.226 | 0.208 |
| options | 27+ | 0.333 | 0.300 |

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
| labels-shuffled-q | 2 | chosen | 702 1468 |
| labels-shuffled-q | 2 | gold | 613 1557 |
| labels-shuffled-q | 3-5 | chosen | 283 212 178 129 6 |
| labels-shuffled-q | 3-5 | gold | 240 230 199 137 2 |
| labels-shuffled-q | 6-26 | chosen | 67 66 42 48 34 38 48 48 45 36 26 1 2 0 0 2 1 0 0 0 0 1 0 0 0 0 |
| labels-shuffled-q | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-shuffled-q | 27+ | chosen | 5 5 4 3 2 6 8 2 2 3 6 3 3 5 3 1 3 3 2 2 3 1 2 1 3 2 2 |
| labels-shuffled-q | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3521 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3521 | 0.795 | 0.019 | 0.661 | 0.291 | baseline | baseline | baseline |
| all | labels-shuffled-q | 3521 | 0.790 | 0.032 | 0.678 | 0.298 | -0.005 [-0.011, +0.001] | +0.0126 [-0.0009, +0.0186] | +0.0170 [+0.0072, +0.0264] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3483 | 0.794 | 0.021 | 0.663 | 0.292 | baseline | baseline | baseline |
| choice | labels-shuffled-q | 3483 | 0.789 | 0.032 | 0.680 | 0.299 | -0.005 [-0.011, +0.001] | +0.0115 [-0.0013, +0.0182] | +0.0177 [+0.0079, +0.0274] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-shuffled-q | 38 | 0.842 | 0.165 | 0.425 | 0.212 | -0.026 [-0.079, +0.000] | +0.0520 [-0.0313, +0.1004] | -0.0487 [-0.1096, +0.0034] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-shuffled-q | 2208 | 0.912 | 0.015 | 0.215 | 0.131 | -0.003 [-0.009, +0.003] | -0.0177 [-0.0234, -0.0004] | +0.0003 [-0.0054, +0.0062] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-shuffled-q | 808 | 0.762 | 0.030 | 0.629 | 0.328 | -0.012 [-0.030, +0.005] | +0.0110 [-0.0139, +0.0301] | +0.0449 [+0.0261, +0.0646] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-shuffled-q | 505 | 0.299 | 0.275 | 2.778 | 0.979 | -0.004 [-0.022, +0.014] | -0.0008 [-0.0183, +0.0170] | +0.0454 [-0.0095, +0.0994] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled-q |
|---|---|---|---|
| overall | all | 0.082 | 0.100 |
| type | choice | 0.082 | 0.100 |
| options | 2 | 0.032 | 0.062 |
| options | 3-5 | 0.126 | 0.135 |
| options | 6-26 | 0.226 | 0.208 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 664 1506 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 261 213 206 125 3 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 59 70 49 49 33 38 52 48 40 36 25 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-shuffled-q | 2 | chosen | 702 1468 |
| labels-shuffled-q | 2 | gold | 613 1557 |
| labels-shuffled-q | 3-5 | chosen | 283 212 178 129 6 |
| labels-shuffled-q | 3-5 | gold | 240 230 199 137 2 |
| labels-shuffled-q | 6-26 | chosen | 67 66 42 48 34 38 48 48 45 36 26 1 2 0 0 2 1 0 0 0 0 1 0 0 0 0 |
| labels-shuffled-q | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |

