# gemma-4-31b R4 pair screen: blurb-decider vs blurb-header, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T171521Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- title: R4 pair screen
- set: blurb-decider
- control: blurb-header
- collect blurb-header calib-600: .cache/collect/gemma-4-31b/calib-600-blurb-header.jsonl.gz
- collect blurb-header index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-blurb-header.jsonl.gz
- collect blurb-decider calib-600: .cache/collect/gemma-4-31b/calib-600-blurb-decider.jsonl.gz
- collect blurb-decider index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-blurb-decider.jsonl.gz
- collect blurb-header image dev: .cache/vision-collect/gemma-4-31b/r4-blurb-header/dev.jsonl.gz
- collect blurb-decider image dev: .cache/vision-collect/gemma-4-31b/r4-blurb-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered
- run time: 25 s

Reports only; the owner picks.

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| blurb-header | 600 | 3728 | 3.783 | 19.999 | 7.299 |
| blurb-decider | 600 | 3728 | 3.842 | 18.870 | 7.813 |

## all (3728 questions)

Δ is blurb-decider − blurb-header on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | blurb-header | 3728 | 0.806 | 0.128 | 0.838 | 0.320 | baseline | baseline | baseline |
| all | blurb-decider | 3728 | 0.776 | 0.139 | 0.913 | 0.363 | -0.030 [-0.038, -0.022] | +0.0109 [+0.0029, +0.0188] | +0.0757 [+0.0498, +0.1028] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | blurb-header | 3690 | 0.806 | 0.129 | 0.843 | 0.322 | baseline | baseline | baseline |
| choice | blurb-decider | 3690 | 0.775 | 0.140 | 0.919 | 0.365 | -0.030 [-0.038, -0.022] | +0.0112 [+0.0028, +0.0192] | +0.0763 [+0.0495, +0.1046] |
| noul | blurb-header | 38 | 0.868 | 0.084 | 0.342 | 0.189 | baseline | baseline | baseline |
| noul | blurb-decider | 38 | 0.868 | 0.098 | 0.360 | 0.212 | +0.000 [+0.000, +0.000] | +0.0132 [-0.0169, +0.0417] | +0.0187 [-0.0257, +0.0611] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | blurb-header | 2208 | 0.915 | 0.067 | 0.317 | 0.145 | baseline | baseline | baseline |
| 2 | blurb-decider | 2208 | 0.872 | 0.101 | 0.485 | 0.226 | -0.043 [-0.054, -0.033] | +0.0337 [+0.0243, +0.0450] | +0.1678 [+0.1306, +0.2076] |
| 3-5 | blurb-header | 808 | 0.802 | 0.131 | 0.716 | 0.324 | baseline | baseline | baseline |
| 3-5 | blurb-decider | 808 | 0.793 | 0.123 | 0.736 | 0.335 | -0.009 [-0.026, +0.007] | -0.0076 [-0.0224, +0.0095] | +0.0197 [-0.0195, +0.0597] |
| 6-26 | blurb-header | 505 | 0.418 | 0.433 | 2.861 | 0.998 | baseline | baseline | baseline |
| 6-26 | blurb-decider | 505 | 0.400 | 0.378 | 2.630 | 0.941 | -0.018 [-0.036, -0.002] | -0.0550 [-0.0786, -0.0357] | -0.2311 [-0.3016, -0.1645] |
| 27+ | blurb-header | 207 | 0.614 | 0.114 | 1.928 | 0.523 | baseline | baseline | baseline |
| 27+ | blurb-decider | 207 | 0.609 | 0.100 | 1.989 | 0.531 | -0.005 [-0.039, +0.029] | -0.0137 [-0.0579, +0.0348] | +0.0611 [-0.0325, +0.1497] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | blurb-header | blurb-decider |
|---|---|---|---|
| overall | all | 0.070 | 0.082 |
| type | choice | 0.070 | 0.082 |
| options | 2 | 0.024 | 0.035 |
| options | 3-5 | 0.078 | 0.089 |
| options | 6-26 | 0.150 | 0.172 |
| options | 27+ | 0.314 | 0.329 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| blurb-header | 2 | chosen | 620 1550 |
| blurb-header | 2 | gold | 613 1557 |
| blurb-header | 3-5 | chosen | 245 219 213 126 5 |
| blurb-header | 3-5 | gold | 240 230 199 137 2 |
| blurb-header | 6-26 | chosen | 59 56 46 48 38 54 47 44 48 35 24 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| blurb-header | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| blurb-header | 27+ | chosen | 7 7 2 4 0 6 3 3 3 1 7 2 3 3 4 4 3 2 2 0 2 2 1 2 3 1 2 |
| blurb-header | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |
| blurb-decider | 2 | chosen | 685 1485 |
| blurb-decider | 2 | gold | 613 1557 |
| blurb-decider | 3-5 | chosen | 250 216 208 128 6 |
| blurb-decider | 3-5 | gold | 240 230 199 137 2 |
| blurb-decider | 6-26 | chosen | 60 62 46 51 37 50 51 41 46 36 19 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| blurb-decider | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| blurb-decider | 27+ | chosen | 6 7 3 3 2 5 3 3 3 1 9 2 3 3 3 4 3 2 3 0 2 6 1 1 3 1 3 |
| blurb-decider | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |

