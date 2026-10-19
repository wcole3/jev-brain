# qwen3.8-27b R3 label screen: shuffled vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T034257Z
- repo commit: 8d38bd7-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: shuffled
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-shuffled calib-600: .cache/collect/qwen3.8-27b/calib-600-shuffled.jsonl.gz
- collect labels-shuffled index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-shuffled.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-shuffled image dev: .cache/vision-collect/qwen3.8-27b/labels-shuffled/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`
- run time: 42 s

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
| labels-shuffled | 590 | 3728 | 1.440 | 5.238 | 0.897 |

## all (3728 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.782 | 0.021 | 0.735 | 0.306 | baseline | baseline | baseline |
| all | labels-shuffled | 3728 | 0.777 | 0.025 | 0.759 | 0.316 | -0.005 [-0.010, +0.002] | +0.0038 [-0.0085, +0.0115] | +0.0247 [+0.0147, +0.0349] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.781 | 0.022 | 0.737 | 0.307 | baseline | baseline | baseline |
| choice | labels-shuffled | 3690 | 0.776 | 0.026 | 0.763 | 0.317 | -0.005 [-0.011, +0.001] | +0.0038 [-0.0090, +0.0117] | +0.0252 [+0.0148, +0.0355] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-shuffled | 38 | 0.868 | 0.087 | 0.450 | 0.226 | +0.000 [+0.000, +0.000] | -0.0254 [-0.0823, +0.0033] | -0.0239 [-0.0534, +0.0005] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-shuffled | 2208 | 0.909 | 0.029 | 0.232 | 0.138 | -0.005 [-0.012, +0.001] | -0.0031 [-0.0091, +0.0054] | +0.0176 [+0.0116, +0.0235] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-shuffled | 808 | 0.769 | 0.033 | 0.599 | 0.318 | -0.006 [-0.022, +0.010] | +0.0140 [-0.0135, +0.0322] | +0.0143 [-0.0035, +0.0313] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-shuffled | 505 | 0.295 | 0.276 | 2.826 | 0.990 | -0.008 [-0.028, +0.012] | +0.0004 [-0.0187, +0.0203] | +0.0934 [+0.0359, +0.1505] |
| 27+ | letters | 207 | 0.556 | 0.096 | 1.993 | 0.552 | baseline | baseline | baseline |
| 27+ | labels-shuffled | 207 | 0.575 | 0.105 | 1.967 | 0.557 | +0.019 [-0.005, +0.048] | +0.0095 [-0.0244, +0.0548] | -0.0257 [-0.0957, +0.0403] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled |
|---|---|---|---|
| overall | all | 0.096 | 0.106 |
| type | choice | 0.096 | 0.106 |
| options | 2 | 0.032 | 0.058 |
| options | 3-5 | 0.126 | 0.125 |
| options | 6-26 | 0.226 | 0.200 |
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
| labels-shuffled | 2 | chosen | 698 1472 |
| labels-shuffled | 2 | gold | 613 1557 |
| labels-shuffled | 3-5 | chosen | 283 220 173 128 4 |
| labels-shuffled | 3-5 | gold | 240 230 199 137 2 |
| labels-shuffled | 6-26 | chosen | 74 59 33 46 28 53 52 43 42 39 29 1 2 0 0 2 1 0 0 0 0 1 0 0 0 0 |
| labels-shuffled | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-shuffled | 27+ | chosen | 4 5 4 3 2 6 8 2 2 3 6 3 3 5 3 1 3 3 2 2 3 1 2 1 3 2 2 |
| labels-shuffled | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |


## pure (3521 questions)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3521 | 0.795 | 0.019 | 0.661 | 0.291 | baseline | baseline | baseline |
| all | labels-shuffled | 3521 | 0.789 | 0.023 | 0.688 | 0.301 | -0.006 [-0.012, +0.000] | +0.0034 [-0.0077, +0.0122] | +0.0277 [+0.0175, +0.0378] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3483 | 0.794 | 0.021 | 0.663 | 0.292 | baseline | baseline | baseline |
| choice | labels-shuffled | 3483 | 0.788 | 0.024 | 0.691 | 0.302 | -0.006 [-0.012, +0.000] | +0.0035 [-0.0079, +0.0128] | +0.0283 [+0.0180, +0.0384] |
| noul | letters | 38 | 0.868 | 0.113 | 0.474 | 0.228 | baseline | baseline | baseline |
| noul | labels-shuffled | 38 | 0.868 | 0.087 | 0.450 | 0.226 | +0.000 [+0.000, +0.000] | -0.0254 [-0.0823, +0.0033] | -0.0239 [-0.0534, +0.0005] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.215 | 0.131 | baseline | baseline | baseline |
| 2 | labels-shuffled | 2208 | 0.909 | 0.029 | 0.232 | 0.138 | -0.005 [-0.012, +0.001] | -0.0031 [-0.0091, +0.0054] | +0.0176 [+0.0116, +0.0235] |
| 3-5 | letters | 808 | 0.775 | 0.019 | 0.584 | 0.312 | baseline | baseline | baseline |
| 3-5 | labels-shuffled | 808 | 0.769 | 0.033 | 0.599 | 0.318 | -0.006 [-0.022, +0.010] | +0.0140 [-0.0135, +0.0322] | +0.0143 [-0.0035, +0.0313] |
| 6-26 | letters | 505 | 0.303 | 0.276 | 2.732 | 0.960 | baseline | baseline | baseline |
| 6-26 | labels-shuffled | 505 | 0.295 | 0.276 | 2.826 | 0.990 | -0.008 [-0.028, +0.012] | +0.0004 [-0.0187, +0.0203] | +0.0934 [+0.0359, +0.1505] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled |
|---|---|---|---|
| overall | all | 0.082 | 0.094 |
| type | choice | 0.082 | 0.094 |
| options | 2 | 0.032 | 0.058 |
| options | 3-5 | 0.126 | 0.125 |
| options | 6-26 | 0.226 | 0.200 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 664 1506 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 261 213 206 125 3 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 59 70 49 49 33 38 52 48 40 36 25 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| labels-shuffled | 2 | chosen | 698 1472 |
| labels-shuffled | 2 | gold | 613 1557 |
| labels-shuffled | 3-5 | chosen | 283 220 173 128 4 |
| labels-shuffled | 3-5 | gold | 240 230 199 137 2 |
| labels-shuffled | 6-26 | chosen | 74 59 33 46 28 53 52 43 42 39 29 1 2 0 0 2 1 0 0 0 0 1 0 0 0 0 |
| labels-shuffled | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |

