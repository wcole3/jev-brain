# gemma-4-31b R4 pair screen: blurb-header vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T162701Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- title: R4 pair screen
- set: blurb-header
- control: letters
- collect letters calib-600: .cache/collect/gemma-4-31b/calib-600-letters.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-letters.jsonl.gz
- collect blurb-header calib-600: .cache/collect/gemma-4-31b/calib-600-blurb-header.jsonl.gz
- collect blurb-header index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-blurb-header.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/labels-letters/dev.jsonl.gz
- collect blurb-header image dev: .cache/vision-collect/gemma-4-31b/r4-blurb-header/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered
- run time: 28 s

Reports only; the owner picks.

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| letters | 600 | 3728 | 3.947 | 19.999 | 8.007 |
| blurb-header | 600 | 3728 | 3.783 | 19.999 | 7.299 |

## all (3728 questions)

Δ is blurb-header − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.129 | 0.826 | 0.327 | baseline | baseline | baseline |
| all | blurb-header | 3728 | 0.806 | 0.128 | 0.838 | 0.320 | +0.004 [-0.000, +0.009] | -0.0004 [-0.0055, +0.0040] | +0.0112 [+0.0003, +0.0217] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.129 | 0.831 | 0.328 | baseline | baseline | baseline |
| choice | blurb-header | 3690 | 0.806 | 0.129 | 0.843 | 0.322 | +0.004 [-0.000, +0.009] | -0.0004 [-0.0056, +0.0042] | +0.0114 [+0.0002, +0.0221] |
| noul | letters | 38 | 0.868 | 0.106 | 0.351 | 0.201 | baseline | baseline | baseline |
| noul | blurb-header | 38 | 0.868 | 0.084 | 0.342 | 0.189 | +0.000 [+0.000, +0.000] | -0.0212 [-0.0457, +0.0072] | -0.0099 [-0.0422, +0.0188] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.908 | 0.073 | 0.322 | 0.156 | baseline | baseline | baseline |
| 2 | blurb-header | 2208 | 0.915 | 0.067 | 0.317 | 0.145 | +0.007 [+0.001, +0.013] | -0.0061 [-0.0117, -0.0005] | -0.0052 [-0.0183, +0.0086] |
| 3-5 | letters | 808 | 0.800 | 0.136 | 0.740 | 0.338 | baseline | baseline | baseline |
| 3-5 | blurb-header | 808 | 0.802 | 0.131 | 0.716 | 0.324 | +0.002 [-0.007, +0.012] | -0.0050 [-0.0149, +0.0057] | -0.0244 [-0.0456, -0.0049] |
| 6-26 | letters | 505 | 0.410 | 0.402 | 2.730 | 0.980 | baseline | baseline | baseline |
| 6-26 | blurb-header | 505 | 0.418 | 0.433 | 2.861 | 0.998 | +0.008 [-0.006, +0.022] | +0.0315 [+0.0138, +0.0470] | +0.1312 [+0.0954, +0.1649] |
| 27+ | letters | 207 | 0.638 | 0.105 | 1.897 | 0.510 | baseline | baseline | baseline |
| 27+ | blurb-header | 207 | 0.614 | 0.114 | 1.928 | 0.523 | -0.024 [-0.048, -0.005] | +0.0095 [-0.0324, +0.0533] | +0.0318 [-0.0118, +0.0798] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | blurb-header |
|---|---|---|---|
| overall | all | 0.074 | 0.070 |
| type | choice | 0.074 | 0.070 |
| options | 2 | 0.029 | 0.024 |
| options | 3-5 | 0.087 | 0.078 |
| options | 6-26 | 0.149 | 0.150 |
| options | 27+ | 0.304 | 0.314 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 595 1575 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 240 216 217 130 5 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 57 56 46 50 40 53 49 43 49 35 21 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| letters | 27+ | chosen | 7 8 2 4 0 5 3 1 3 1 7 2 3 3 5 4 3 2 2 0 2 0 2 2 3 1 2 |
| letters | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |
| blurb-header | 2 | chosen | 620 1550 |
| blurb-header | 2 | gold | 613 1557 |
| blurb-header | 3-5 | chosen | 245 219 213 126 5 |
| blurb-header | 3-5 | gold | 240 230 199 137 2 |
| blurb-header | 6-26 | chosen | 59 56 46 48 38 54 47 44 48 35 24 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| blurb-header | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| blurb-header | 27+ | chosen | 7 7 2 4 0 6 3 3 3 1 7 2 3 3 4 4 3 2 2 0 2 2 1 2 3 1 2 |
| blurb-header | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |

