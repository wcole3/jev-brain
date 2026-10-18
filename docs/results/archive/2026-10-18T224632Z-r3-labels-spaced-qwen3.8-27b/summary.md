# qwen3.8-27b R3 label screen: spaced vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-18T224632Z
- repo commit: 6b8f34f-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: spaced
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-spaced calib-600: .cache/collect/qwen3.8-27b/calib-600-spaced.jsonl.gz
- collect labels-spaced index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-spaced.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-spaced image dev: .cache/vision-collect/qwen3.8-27b/labels-spaced/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 60 s

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
| labels-spaced | 585 | 3728 | 1.305 | 5.964 | 0.950 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.782 | 0.021 | 0.735 | 0.306 | baseline | baseline | baseline |
| all | labels-spaced | 3728 | 0.782 | 0.038 | 0.767 | 0.311 | +0.001 [-0.004, +0.005] | +0.0167 [+0.0032, +0.0219] | +0.0325 [+0.0239, +0.0408] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.781 | 0.022 | 0.737 | 0.307 | baseline | baseline | baseline |
| choice | labels-spaced | 3690 | 0.781 | 0.038 | 0.770 | 0.312 | +0.001 [-0.004, +0.005] | +0.0161 [+0.0027, +0.0217] | +0.0324 [+0.0237, +0.0405] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-spaced | 38 | 0.868 | 0.127 | 0.520 | 0.228 | +0.000 [+0.000, +0.000] | +0.0142 [-0.0460, +0.0697] | +0.0466 [-0.0094, +0.1321] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-spaced | 2208 | 0.914 | 0.017 | 0.210 | 0.129 | -0.001 [-0.006, +0.005] | -0.0149 [-0.0203, -0.0037] | -0.0051 [-0.0087, -0.0014] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-spaced | 808 | 0.781 | 0.031 | 0.594 | 0.313 | +0.006 [-0.004, +0.016] | +0.0117 [-0.0152, +0.0280] | +0.0094 [-0.0024, +0.0219] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-spaced | 505 | 0.303 | 0.309 | 2.839 | 0.985 | +0.000 [-0.014, +0.014] | +0.0337 [+0.0196, +0.0477] | +0.1071 [+0.0680, +0.1467] |
| 27+ | letters | 207 | 0.556 | 0.096 | 1.993 | 0.552 | baseline | baseline | baseline |
| 27+ | labels-spaced | 207 | 0.551 | 0.099 | 2.335 | 0.607 | -0.005 [-0.029, +0.014] | +0.0031 [-0.0339, +0.0514] | +0.3425 [+0.2527, +0.4364] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-spaced |
|---|---|---|---|
| overall | all | 0.096 | 0.117 |
| type | choice | 0.096 | 0.117 |
| options | 2 | 0.032 | 0.063 |
| options | 3-5 | 0.126 | 0.126 |
| options | 6-26 | 0.226 | 0.226 |
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
| labels-spaced | 2 | chosen | 682 1488 |
| labels-spaced | 2 | gold | 613 1557 |
| labels-spaced | 3-5 | chosen | 249 217 208 131 3 |
| labels-spaced | 3-5 | gold | 240 230 199 137 2 |
| labels-spaced | 6-26 | chosen | 68 66 52 54 31 36 48 45 38 35 26 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| labels-spaced | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-spaced | 27+ | chosen | 4 5 4 5 5 11 6 2 2 3 7 3 4 6 3 2 3 2 2 1 2 1 2 2 3 2 2 |
| labels-spaced | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3521 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3521 | 0.795 | 0.019 | 0.661 | 0.291 | baseline | baseline | baseline |
| all | labels-spaced | 3521 | 0.796 | 0.038 | 0.675 | 0.294 | +0.001 [-0.004, +0.005] | +0.0182 [+0.0051, +0.0239] | +0.0143 [+0.0074, +0.0213] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3483 | 0.794 | 0.021 | 0.663 | 0.292 | baseline | baseline | baseline |
| choice | labels-spaced | 3483 | 0.795 | 0.038 | 0.677 | 0.295 | +0.001 [-0.004, +0.005] | +0.0176 [+0.0045, +0.0240] | +0.0139 [+0.0072, +0.0206] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-spaced | 38 | 0.868 | 0.127 | 0.520 | 0.228 | +0.000 [+0.000, +0.000] | +0.0142 [-0.0460, +0.0697] | +0.0466 [-0.0094, +0.1321] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-spaced | 2208 | 0.914 | 0.017 | 0.210 | 0.129 | -0.001 [-0.006, +0.005] | -0.0149 [-0.0203, -0.0037] | -0.0051 [-0.0087, -0.0014] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-spaced | 808 | 0.781 | 0.031 | 0.594 | 0.313 | +0.006 [-0.004, +0.016] | +0.0117 [-0.0152, +0.0280] | +0.0094 [-0.0024, +0.0219] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-spaced | 505 | 0.303 | 0.309 | 2.839 | 0.985 | +0.000 [-0.014, +0.014] | +0.0337 [+0.0196, +0.0477] | +0.1071 [+0.0680, +0.1467] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-spaced |
|---|---|---|---|
| overall | all | 0.082 | 0.101 |
| type | choice | 0.082 | 0.101 |
| options | 2 | 0.032 | 0.063 |
| options | 3-5 | 0.126 | 0.126 |
| options | 6-26 | 0.226 | 0.226 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 664 1506 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 261 213 206 125 3 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 59 70 49 49 33 38 52 48 40 36 25 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-spaced | 2 | chosen | 682 1488 |
| labels-spaced | 2 | gold | 613 1557 |
| labels-spaced | 3-5 | chosen | 249 217 208 131 3 |
| labels-spaced | 3-5 | gold | 240 230 199 137 2 |
| labels-spaced | 6-26 | chosen | 68 66 52 54 31 36 48 45 38 35 26 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| labels-spaced | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |

