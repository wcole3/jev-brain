# gemma-4-31b R4 pair screen: blurb-decider vs decider, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T171451Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- title: R4 pair screen
- set: blurb-decider
- control: decider
- collect decider calib-600: .cache/collect/gemma-4-31b/calib-600-decider.jsonl.gz
- collect decider index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-decider.jsonl.gz
- collect blurb-decider calib-600: .cache/collect/gemma-4-31b/calib-600-blurb-decider.jsonl.gz
- collect blurb-decider index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-blurb-decider.jsonl.gz
- collect decider image dev: .cache/vision-collect/gemma-4-31b/r4-decider/dev.jsonl.gz
- collect blurb-decider image dev: .cache/vision-collect/gemma-4-31b/r4-blurb-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered
- run time: 26 s

Reports only; the owner picks.

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| decider | 600 | 3728 | 3.875 | 16.229 | 8.499 |
| blurb-decider | 600 | 3728 | 3.842 | 18.870 | 7.813 |

## all (3728 questions)

Δ is blurb-decider − decider on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | decider | 3728 | 0.766 | 0.151 | 0.965 | 0.385 | baseline | baseline | baseline |
| all | blurb-decider | 3728 | 0.776 | 0.139 | 0.913 | 0.363 | +0.010 [+0.004, +0.016] | -0.0121 [-0.0184, -0.0057] | -0.0516 [-0.0658, -0.0380] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | decider | 3690 | 0.765 | 0.152 | 0.971 | 0.387 | baseline | baseline | baseline |
| choice | blurb-decider | 3690 | 0.775 | 0.140 | 0.919 | 0.365 | +0.010 [+0.005, +0.016] | -0.0123 [-0.0185, -0.0059] | -0.0517 [-0.0662, -0.0372] |
| noul | decider | 38 | 0.868 | 0.135 | 0.405 | 0.235 | baseline | baseline | baseline |
| noul | blurb-decider | 38 | 0.868 | 0.098 | 0.360 | 0.212 | +0.000 [+0.000, +0.000] | -0.0379 [-0.0673, +0.0066] | -0.0445 [-0.0938, -0.0028] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | decider | 2208 | 0.860 | 0.111 | 0.530 | 0.248 | baseline | baseline | baseline |
| 2 | blurb-decider | 2208 | 0.872 | 0.101 | 0.485 | 0.226 | +0.012 [+0.005, +0.019] | -0.0104 [-0.0173, -0.0031] | -0.0457 [-0.0627, -0.0286] |
| 3-5 | decider | 808 | 0.782 | 0.144 | 0.811 | 0.364 | baseline | baseline | baseline |
| 3-5 | blurb-decider | 808 | 0.793 | 0.123 | 0.736 | 0.335 | +0.011 [-0.004, +0.026] | -0.0206 [-0.0338, -0.0035] | -0.0755 [-0.1147, -0.0389] |
| 6-26 | decider | 505 | 0.396 | 0.387 | 2.706 | 0.961 | baseline | baseline | baseline |
| 6-26 | blurb-decider | 505 | 0.400 | 0.378 | 2.630 | 0.941 | +0.004 [-0.012, +0.020] | -0.0082 [-0.0257, +0.0089] | -0.0759 [-0.1137, -0.0366] |
| 27+ | decider | 207 | 0.609 | 0.126 | 1.952 | 0.521 | baseline | baseline | baseline |
| 27+ | blurb-decider | 207 | 0.609 | 0.100 | 1.989 | 0.531 | +0.000 [-0.024, +0.024] | -0.0253 [-0.0529, +0.0245] | +0.0378 [-0.0110, +0.0922] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | decider | blurb-decider |
|---|---|---|---|
| overall | all | 0.085 | 0.082 |
| type | choice | 0.085 | 0.082 |
| options | 2 | 0.038 | 0.035 |
| options | 3-5 | 0.093 | 0.089 |
| options | 6-26 | 0.162 | 0.172 |
| options | 27+ | 0.353 | 0.329 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| decider | 2 | chosen | 674 1496 |
| decider | 2 | gold | 613 1557 |
| decider | 3-5 | chosen | 236 212 220 135 5 |
| decider | 3-5 | gold | 240 230 199 137 2 |
| decider | 6-26 | chosen | 56 63 47 51 41 50 52 39 49 33 18 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| decider | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| decider | 27+ | chosen | 3 8 4 4 1 7 2 3 4 1 9 2 2 3 3 3 3 2 2 0 2 4 1 2 3 1 3 |
| decider | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |
| blurb-decider | 2 | chosen | 685 1485 |
| blurb-decider | 2 | gold | 613 1557 |
| blurb-decider | 3-5 | chosen | 250 216 208 128 6 |
| blurb-decider | 3-5 | gold | 240 230 199 137 2 |
| blurb-decider | 6-26 | chosen | 60 62 46 51 37 50 51 41 46 36 19 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| blurb-decider | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| blurb-decider | 27+ | chosen | 6 7 3 3 2 5 3 3 3 1 9 2 3 3 3 4 3 2 3 0 2 6 1 1 3 1 3 |
| blurb-decider | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |

