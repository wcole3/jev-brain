# qwen3.8-27b R3 label screen: lower vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-18T220610Z
- repo commit: e4d2608-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: lower
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-lower calib-600: .cache/collect/qwen3.8-27b/calib-600-lower.jsonl.gz
- collect labels-lower index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-lower.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-lower image dev: .cache/vision-collect/qwen3.8-27b/labels-lower/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 50 s

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
| labels-lower | 590 | 3728 | 1.490 | 4.609 | 1.022 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.782 | 0.021 | 0.735 | 0.306 | baseline | baseline | baseline |
| all | labels-lower | 3728 | 0.782 | 0.024 | 0.729 | 0.307 | +0.001 [-0.003, +0.005] | +0.0027 [-0.0071, +0.0087] | -0.0051 [-0.0110, +0.0002] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.781 | 0.022 | 0.737 | 0.307 | baseline | baseline | baseline |
| choice | labels-lower | 3690 | 0.782 | 0.024 | 0.732 | 0.307 | +0.001 [-0.003, +0.004] | +0.0017 [-0.0078, +0.0081] | -0.0049 [-0.0108, +0.0005] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-lower | 38 | 0.868 | 0.101 | 0.451 | 0.227 | +0.000 [+0.000, +0.000] | -0.0113 [-0.0694, +0.0455] | -0.0226 [-0.0684, +0.0078] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-lower | 2208 | 0.915 | 0.032 | 0.213 | 0.128 | +0.000 [-0.004, +0.004] | -0.0006 [-0.0061, +0.0046] | -0.0020 [-0.0042, +0.0001] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-lower | 808 | 0.772 | 0.029 | 0.592 | 0.317 | -0.002 [-0.012, +0.006] | +0.0102 [-0.0133, +0.0243] | +0.0082 [+0.0021, +0.0141] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-lower | 505 | 0.309 | 0.287 | 2.704 | 0.967 | +0.006 [-0.006, +0.018] | +0.0112 [-0.0000, +0.0233] | -0.0285 [-0.0558, -0.0013] |
| 27+ | letters | 207 | 0.556 | 0.096 | 1.993 | 0.552 | baseline | baseline | baseline |
| 27+ | labels-lower | 207 | 0.565 | 0.093 | 1.960 | 0.554 | +0.010 [-0.010, +0.029] | -0.0026 [-0.0351, +0.0389] | -0.0329 [-0.1064, +0.0320] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-lower |
|---|---|---|---|
| overall | all | 0.096 | 0.104 |
| type | choice | 0.096 | 0.104 |
| options | 2 | 0.032 | 0.047 |
| options | 3-5 | 0.126 | 0.129 |
| options | 6-26 | 0.226 | 0.230 |
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
| labels-lower | 2 | chosen | 686 1484 |
| labels-lower | 2 | gold | 613 1557 |
| labels-lower | 3-5 | chosen | 267 214 194 129 4 |
| labels-lower | 3-5 | gold | 240 230 199 137 2 |
| labels-lower | 6-26 | chosen | 66 69 49 48 33 39 49 45 41 35 24 1 2 0 0 1 1 1 0 0 0 1 0 0 0 0 |
| labels-lower | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-lower | 27+ | chosen | 3 5 4 3 3 6 8 2 4 3 6 3 3 5 3 1 3 3 2 1 3 1 1 2 3 2 2 |
| labels-lower | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3521 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3521 | 0.795 | 0.019 | 0.661 | 0.291 | baseline | baseline | baseline |
| all | labels-lower | 3521 | 0.795 | 0.022 | 0.657 | 0.292 | +0.000 [-0.004, +0.004] | +0.0027 [-0.0061, +0.0098] | -0.0035 [-0.0078, +0.0007] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3483 | 0.794 | 0.021 | 0.663 | 0.292 | baseline | baseline | baseline |
| choice | labels-lower | 3483 | 0.794 | 0.022 | 0.659 | 0.293 | +0.000 [-0.003, +0.004] | +0.0017 [-0.0065, +0.0099] | -0.0033 [-0.0077, +0.0008] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-lower | 38 | 0.868 | 0.101 | 0.451 | 0.227 | +0.000 [+0.000, +0.000] | -0.0113 [-0.0694, +0.0455] | -0.0226 [-0.0684, +0.0078] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-lower | 2208 | 0.915 | 0.032 | 0.213 | 0.128 | +0.000 [-0.004, +0.004] | -0.0006 [-0.0061, +0.0046] | -0.0020 [-0.0042, +0.0001] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-lower | 808 | 0.772 | 0.029 | 0.592 | 0.317 | -0.002 [-0.012, +0.006] | +0.0102 [-0.0133, +0.0243] | +0.0082 [+0.0021, +0.0141] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-lower | 505 | 0.309 | 0.287 | 2.704 | 0.967 | +0.006 [-0.006, +0.018] | +0.0112 [-0.0000, +0.0233] | -0.0285 [-0.0558, -0.0013] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-lower |
|---|---|---|---|
| overall | all | 0.082 | 0.093 |
| type | choice | 0.082 | 0.093 |
| options | 2 | 0.032 | 0.047 |
| options | 3-5 | 0.126 | 0.129 |
| options | 6-26 | 0.226 | 0.230 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 664 1506 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 261 213 206 125 3 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 59 70 49 49 33 38 52 48 40 36 25 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-lower | 2 | chosen | 686 1484 |
| labels-lower | 2 | gold | 613 1557 |
| labels-lower | 3-5 | chosen | 267 214 194 129 4 |
| labels-lower | 3-5 | gold | 240 230 199 137 2 |
| labels-lower | 6-26 | chosen | 66 69 49 48 33 39 49 45 41 35 24 1 2 0 0 1 1 1 0 0 0 1 0 0 0 0 |
| labels-lower | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |

