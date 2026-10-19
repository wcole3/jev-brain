# qwen3.8-27b R3 label screen: content vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T004859Z
- repo commit: 76fcba1-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: content
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-content calib-600: .cache/collect/qwen3.8-27b/calib-600-content.jsonl.gz
- collect labels-content index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-content.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-content image dev: .cache/vision-collect/qwen3.8-27b/labels-content/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 39 s

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
| letters | 590 | 3728 | 1.491 | 5.160 | 0.934 |
| labels-content | 585 | 3728 | 1.352 | 5.966 | 1.085 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.782 | 0.021 | 0.735 | 0.306 | baseline | baseline | baseline |
| all | labels-content | 3728 | 0.781 | 0.047 | 0.761 | 0.310 | -0.001 [-0.006, +0.005] | +0.0261 [+0.0103, +0.0307] | +0.0263 [+0.0161, +0.0360] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.781 | 0.022 | 0.737 | 0.307 | baseline | baseline | baseline |
| choice | labels-content | 3690 | 0.780 | 0.048 | 0.765 | 0.312 | -0.001 [-0.006, +0.005] | +0.0258 [+0.0099, +0.0306] | +0.0278 [+0.0177, +0.0375] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-content | 38 | 0.895 | 0.106 | 0.349 | 0.194 | +0.026 [-0.053, +0.132] | -0.0067 [-0.0771, +0.0531] | -0.1252 [-0.2971, +0.0004] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-content | 2208 | 0.914 | 0.009 | 0.210 | 0.128 | -0.001 [-0.008, +0.006] | -0.0231 [-0.0290, -0.0045] | -0.0052 [-0.0136, +0.0045] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-content | 808 | 0.774 | 0.031 | 0.608 | 0.317 | -0.001 [-0.016, +0.014] | +0.0119 [-0.0194, +0.0300] | +0.0239 [+0.0062, +0.0431] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-content | 505 | 0.305 | 0.302 | 2.780 | 0.976 | +0.002 [-0.010, +0.014] | +0.0260 [+0.0131, +0.0391] | +0.0477 [+0.0089, +0.0853] |
| 27+ | letters | 207 | 0.556 | 0.096 | 1.993 | 0.552 | baseline | baseline | baseline |
| 27+ | labels-content | 207 | 0.551 | 0.092 | 2.311 | 0.604 | -0.005 [-0.029, +0.014] | -0.0041 [-0.0432, +0.0464] | +0.3185 [+0.2342, +0.4052] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-content |
|---|---|---|---|
| overall | all | 0.096 | 0.100 |
| type | choice | 0.096 | 0.100 |
| options | 2 | 0.032 | 0.039 |
| options | 3-5 | 0.126 | 0.129 |
| options | 6-26 | 0.226 | 0.200 |
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
| labels-content | 2 | chosen | 677 1493 |
| labels-content | 2 | gold | 613 1557 |
| labels-content | 3-5 | chosen | 238 217 220 130 3 |
| labels-content | 3-5 | gold | 240 230 199 137 2 |
| labels-content | 6-26 | chosen | 61 66 52 52 34 38 50 46 40 35 25 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| labels-content | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-content | 27+ | chosen | 4 5 4 5 5 11 6 2 2 3 7 3 4 6 3 2 3 2 2 1 2 1 2 2 3 2 2 |
| labels-content | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (2944 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 2944 | 0.871 | 0.028 | 0.338 | 0.185 | baseline | baseline | baseline |
| all | labels-content | 2944 | 0.871 | 0.013 | 0.342 | 0.184 | -0.000 [-0.006, +0.005] | -0.0158 [-0.0241, +0.0038] | +0.0034 [-0.0051, +0.0122] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 2906 | 0.871 | 0.029 | 0.336 | 0.184 | baseline | baseline | baseline |
| choice | labels-content | 2906 | 0.871 | 0.013 | 0.341 | 0.184 | -0.001 [-0.007, +0.006] | -0.0160 [-0.0246, +0.0033] | +0.0051 [-0.0033, +0.0139] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-content | 38 | 0.895 | 0.106 | 0.349 | 0.194 | +0.026 [-0.053, +0.132] | -0.0067 [-0.0771, +0.0531] | -0.1252 [-0.2971, +0.0004] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2052 | 0.918 | 0.030 | 0.204 | 0.125 | baseline | baseline | baseline |
| 2 | labels-content | 2052 | 0.918 | 0.012 | 0.199 | 0.123 | +0.000 [-0.006, +0.007] | -0.0176 [-0.0276, +0.0000] | -0.0046 [-0.0144, +0.0051] |
| 3-5 | letters | 728 | 0.801 | 0.022 | 0.529 | 0.283 | baseline | baseline | baseline |
| 3-5 | labels-content | 728 | 0.798 | 0.029 | 0.553 | 0.287 | -0.003 [-0.018, +0.012] | +0.0077 [-0.0222, +0.0267] | +0.0245 [+0.0058, +0.0452] |
| 6-26 | letters | 164 | 0.604 | 0.076 | 1.168 | 0.505 | baseline | baseline | baseline |
| 6-26 | labels-content | 164 | 0.604 | 0.066 | 1.180 | 0.503 | +0.000 [-0.030, +0.037] | -0.0098 [-0.0523, +0.0506] | +0.0112 [-0.0339, +0.0597] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-content |
|---|---|---|---|
| overall | all | 0.064 | 0.064 |
| type | choice | 0.064 | 0.064 |
| options | 2 | 0.021 | 0.028 |
| options | 3-5 | 0.109 | 0.109 |
| options | 6-26 | 0.390 | 0.305 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 584 1430 |
| letters | 2 | gold | 528 1486 |
| letters | 3-5 | chosen | 232 187 191 117 1 |
| letters | 3-5 | gold | 227 206 174 121 0 |
| letters | 6-26 | chosen | 27 21 18 20 13 15 14 16 10 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 19 15 18 18 11 24 17 18 13 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 2 | chosen | 590 1424 |
| labels-content | 2 | gold | 528 1486 |
| labels-content | 3-5 | chosen | 213 191 203 120 1 |
| labels-content | 3-5 | gold | 227 206 174 121 0 |
| labels-content | 6-26 | chosen | 29 19 22 19 13 14 13 14 11 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 6-26 | gold | 19 15 18 18 11 24 17 18 13 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

