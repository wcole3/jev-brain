# qwen3.8-27b R3 label screen: digits vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-18T232927Z
- repo commit: 2e72beb-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: digits
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-digits calib-600: .cache/collect/qwen3.8-27b/calib-600-digits.jsonl.gz
- collect labels-digits index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-digits.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-digits image dev: .cache/vision-collect/qwen3.8-27b/labels-digits/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 56 s

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
| letters | 590 | 3728 | 1.491 | 5.160 | 0.934 |
| labels-digits | 590 | 3728 | 1.531 | 4.820 | 1.009 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.782 | 0.021 | 0.735 | 0.306 | baseline | baseline | baseline |
| all | labels-digits | 3728 | 0.782 | 0.021 | 0.731 | 0.306 | +0.000 [-0.005, +0.005] | -0.0007 [-0.0107, +0.0074] | -0.0038 [-0.0096, +0.0022] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.781 | 0.022 | 0.737 | 0.307 | baseline | baseline | baseline |
| choice | labels-digits | 3690 | 0.781 | 0.022 | 0.734 | 0.307 | +0.000 [-0.005, +0.005] | -0.0008 [-0.0108, +0.0077] | -0.0033 [-0.0095, +0.0028] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-digits | 38 | 0.868 | 0.122 | 0.421 | 0.216 | +0.000 [+0.000, +0.000] | +0.0090 [-0.0607, +0.0675] | -0.0530 [-0.1294, +0.0085] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-digits | 2208 | 0.917 | 0.033 | 0.209 | 0.129 | +0.002 [-0.004, +0.008] | +0.0004 [-0.0065, +0.0062] | -0.0054 [-0.0090, -0.0017] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-digits | 808 | 0.762 | 0.032 | 0.606 | 0.321 | -0.012 [-0.026, +0.001] | +0.0126 [-0.0150, +0.0311] | +0.0215 [+0.0070, +0.0349] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-digits | 505 | 0.309 | 0.263 | 2.710 | 0.954 | +0.006 [-0.002, +0.016] | -0.0127 [-0.0222, -0.0018] | -0.0225 [-0.0416, -0.0039] |
| 27+ | letters | 207 | 0.556 | 0.096 | 1.993 | 0.552 | baseline | baseline | baseline |
| 27+ | labels-digits | 207 | 0.570 | 0.086 | 1.953 | 0.554 | +0.014 [-0.005, +0.039] | -0.0095 [-0.0455, +0.0325] | -0.0400 [-0.1149, +0.0255] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-digits |
|---|---|---|---|
| overall | all | 0.096 | 0.111 |
| type | choice | 0.096 | 0.111 |
| options | 2 | 0.032 | 0.058 |
| options | 3-5 | 0.126 | 0.134 |
| options | 6-26 | 0.226 | 0.224 |
| options | 27+ | 0.333 | 0.295 |

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
| labels-digits | 2 | chosen | 697 1473 |
| labels-digits | 2 | gold | 613 1557 |
| labels-digits | 3-5 | chosen | 274 211 192 124 7 |
| labels-digits | 3-5 | gold | 240 230 199 137 2 |
| labels-digits | 6-26 | chosen | 62 66 49 49 34 39 55 46 38 37 23 1 2 0 0 1 1 1 0 0 0 1 0 0 0 0 |
| labels-digits | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-digits | 27+ | chosen | 2 5 4 3 3 6 8 2 4 3 6 3 3 5 3 1 3 3 2 1 3 1 1 2 3 2 2 |
| labels-digits | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3061 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3061 | 0.874 | 0.027 | 0.323 | 0.183 | baseline | baseline | baseline |
| all | labels-digits | 3061 | 0.873 | 0.032 | 0.325 | 0.184 | -0.001 [-0.007, +0.005] | +0.0045 [-0.0028, +0.0111] | +0.0014 [-0.0034, +0.0061] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3023 | 0.874 | 0.028 | 0.322 | 0.183 | baseline | baseline | baseline |
| choice | labels-digits | 3023 | 0.873 | 0.032 | 0.324 | 0.184 | -0.001 [-0.007, +0.005] | +0.0045 [-0.0029, +0.0110] | +0.0021 [-0.0026, +0.0067] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-digits | 38 | 0.868 | 0.122 | 0.421 | 0.216 | +0.000 [+0.000, +0.000] | +0.0090 [-0.0607, +0.0675] | -0.0530 [-0.1294, +0.0085] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-digits | 2208 | 0.917 | 0.033 | 0.209 | 0.129 | +0.002 [-0.004, +0.008] | +0.0004 [-0.0065, +0.0062] | -0.0054 [-0.0090, -0.0017] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-digits | 808 | 0.762 | 0.032 | 0.606 | 0.321 | -0.012 [-0.026, +0.001] | +0.0126 [-0.0150, +0.0311] | +0.0215 [+0.0070, +0.0349] |
| 6-26 | letters | 45 | 0.644 | 0.093 | 0.977 | 0.448 | baseline | baseline | baseline |
| 6-26 | labels-digits | 45 | 0.689 | 0.215 | 0.955 | 0.432 | +0.044 [+0.000, +0.111] | +0.1223 [-0.0134, +0.1699] | -0.0219 [-0.1089, +0.0506] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-digits |
|---|---|---|---|
| overall | all | 0.060 | 0.080 |
| type | choice | 0.060 | 0.080 |
| options | 2 | 0.032 | 0.058 |
| options | 3-5 | 0.126 | 0.134 |
| options | 6-26 | 0.222 | 0.156 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 664 1506 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 261 213 206 125 3 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 4 10 7 6 3 6 3 2 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 6 8 7 4 4 8 5 1 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 2 | chosen | 697 1473 |
| labels-digits | 2 | gold | 613 1557 |
| labels-digits | 3-5 | chosen | 274 211 192 124 7 |
| labels-digits | 3-5 | gold | 240 230 199 137 2 |
| labels-digits | 6-26 | chosen | 5 9 7 4 4 7 4 2 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 6-26 | gold | 6 8 7 4 4 8 5 1 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

