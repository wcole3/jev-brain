# gemma-4-31b R4 pair screen: decider vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T153546Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- title: R4 pair screen
- set: decider
- control: letters
- collect letters calib-600: .cache/collect/gemma-4-31b/calib-600-letters.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-letters.jsonl.gz
- collect decider calib-600: .cache/collect/gemma-4-31b/calib-600-decider.jsonl.gz
- collect decider index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-decider.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/labels-letters/dev.jsonl.gz
- collect decider image dev: .cache/vision-collect/gemma-4-31b/r4-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered
- run time: 23 s

Reports only; the owner picks.

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| letters | 600 | 3728 | 3.947 | 19.999 | 8.007 |
| decider | 600 | 3728 | 3.875 | 16.229 | 8.499 |

## all (3728 questions)

Δ is decider − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.802 | 0.129 | 0.826 | 0.327 | baseline | baseline | baseline |
| all | decider | 3728 | 0.766 | 0.151 | 0.965 | 0.385 | -0.036 [-0.044, -0.028] | +0.0226 [+0.0133, +0.0299] | +0.1385 [+0.1124, +0.1664] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.801 | 0.129 | 0.831 | 0.328 | baseline | baseline | baseline |
| choice | decider | 3690 | 0.765 | 0.152 | 0.971 | 0.387 | -0.036 [-0.045, -0.028] | +0.0231 [+0.0136, +0.0308] | +0.1394 [+0.1130, +0.1669] |
| noul | letters | 38 | 0.868 | 0.106 | 0.351 | 0.201 | baseline | baseline | baseline |
| noul | decider | 38 | 0.868 | 0.135 | 0.405 | 0.235 | +0.000 [+0.000, +0.000] | +0.0299 [-0.0090, +0.0641] | +0.0533 [+0.0065, +0.1101] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.908 | 0.073 | 0.322 | 0.156 | baseline | baseline | baseline |
| 2 | decider | 2208 | 0.860 | 0.111 | 0.530 | 0.248 | -0.048 [-0.059, -0.038] | +0.0380 [+0.0279, +0.0493] | +0.2082 [+0.1699, +0.2496] |
| 3-5 | letters | 808 | 0.800 | 0.136 | 0.740 | 0.338 | baseline | baseline | baseline |
| 3-5 | decider | 808 | 0.782 | 0.144 | 0.811 | 0.364 | -0.017 [-0.032, -0.004] | +0.0081 [-0.0060, +0.0229] | +0.0708 [+0.0329, +0.1125] |
| 6-26 | letters | 505 | 0.410 | 0.402 | 2.730 | 0.980 | baseline | baseline | baseline |
| 6-26 | decider | 505 | 0.396 | 0.387 | 2.706 | 0.961 | -0.014 [-0.034, +0.008] | -0.0153 [-0.0421, +0.0052] | -0.0240 [-0.0888, +0.0395] |
| 27+ | letters | 207 | 0.638 | 0.105 | 1.897 | 0.510 | baseline | baseline | baseline |
| 27+ | decider | 207 | 0.609 | 0.126 | 1.952 | 0.521 | -0.029 [-0.063, +0.005] | +0.0211 [-0.0278, +0.0534] | +0.0550 [-0.0186, +0.1297] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | decider |
|---|---|---|---|
| overall | all | 0.074 | 0.085 |
| type | choice | 0.074 | 0.085 |
| options | 2 | 0.029 | 0.038 |
| options | 3-5 | 0.087 | 0.093 |
| options | 6-26 | 0.149 | 0.162 |
| options | 27+ | 0.304 | 0.353 |

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
| decider | 2 | chosen | 674 1496 |
| decider | 2 | gold | 613 1557 |
| decider | 3-5 | chosen | 236 212 220 135 5 |
| decider | 3-5 | gold | 240 230 199 137 2 |
| decider | 6-26 | chosen | 56 63 47 51 41 50 52 39 49 33 18 1 1 0 0 1 1 0 0 0 0 1 1 0 0 0 |
| decider | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| decider | 27+ | chosen | 3 8 4 4 1 7 2 3 4 1 9 2 2 3 3 3 3 2 2 0 2 4 1 2 3 1 3 |
| decider | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |

