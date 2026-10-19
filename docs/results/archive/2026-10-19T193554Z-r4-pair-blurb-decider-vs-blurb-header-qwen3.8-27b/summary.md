# qwen3.8-27b R4 pair screen: blurb-decider vs blurb-header, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T193554Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- title: R4 pair screen
- set: blurb-decider
- control: blurb-header
- collect blurb-header calib-600: .cache/collect/qwen3.8-27b/calib-600-blurb-header.jsonl.gz
- collect blurb-header index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-blurb-header.jsonl.gz
- collect blurb-decider calib-600: .cache/collect/qwen3.8-27b/calib-600-blurb-decider.jsonl.gz
- collect blurb-decider index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-blurb-decider.jsonl.gz
- collect blurb-header image dev: .cache/vision-collect/qwen3.8-27b/r4-blurb-header/dev.jsonl.gz
- collect blurb-decider image dev: .cache/vision-collect/qwen3.8-27b/r4-blurb-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered
- run time: 23 s

Reports only; the owner picks.

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| blurb-header | 590 | 3728 | 1.567 | 6.022 | 1.189 |
| blurb-decider | 590 | 3728 | 1.546 | 5.078 | 1.226 |

## all (3728 questions)

Δ is blurb-decider − blurb-header on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | blurb-header | 3728 | 0.786 | 0.035 | 0.715 | 0.300 | baseline | baseline | baseline |
| all | blurb-decider | 3728 | 0.770 | 0.022 | 0.743 | 0.320 | -0.017 [-0.024, -0.009] | -0.0128 [-0.0207, +0.0011] | +0.0287 [+0.0182, +0.0388] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | blurb-header | 3690 | 0.785 | 0.035 | 0.717 | 0.301 | baseline | baseline | baseline |
| choice | blurb-decider | 3690 | 0.769 | 0.022 | 0.745 | 0.320 | -0.017 [-0.024, -0.009] | -0.0129 [-0.0210, +0.0008] | +0.0284 [+0.0179, +0.0386] |
| noul | blurb-header | 38 | 0.895 | 0.172 | 0.496 | 0.216 | baseline | baseline | baseline |
| noul | blurb-decider | 38 | 0.868 | 0.122 | 0.551 | 0.264 | -0.026 [-0.079, +0.000] | -0.0500 [-0.1066, +0.0493] | +0.0553 [+0.0168, +0.0942] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | blurb-header | 2208 | 0.916 | 0.017 | 0.208 | 0.127 | baseline | baseline | baseline |
| 2 | blurb-decider | 2208 | 0.899 | 0.038 | 0.260 | 0.155 | -0.018 [-0.027, -0.009] | +0.0208 [+0.0040, +0.0271] | +0.0519 [+0.0430, +0.0612] |
| 3-5 | blurb-header | 808 | 0.781 | 0.028 | 0.581 | 0.308 | baseline | baseline | baseline |
| 3-5 | blurb-decider | 808 | 0.764 | 0.032 | 0.619 | 0.332 | -0.017 [-0.037, +0.001] | +0.0032 [-0.0184, +0.0257] | +0.0383 [+0.0159, +0.0607] |
| 6-26 | blurb-header | 505 | 0.313 | 0.261 | 2.655 | 0.942 | baseline | baseline | baseline |
| 6-26 | blurb-decider | 505 | 0.303 | 0.242 | 2.572 | 0.925 | -0.010 [-0.024, +0.004] | -0.0196 [-0.0368, -0.0037] | -0.0835 [-0.1258, -0.0447] |
| 27+ | blurb-header | 207 | 0.575 | 0.093 | 1.905 | 0.544 | baseline | baseline | baseline |
| 27+ | blurb-decider | 207 | 0.556 | 0.073 | 1.922 | 0.545 | -0.019 [-0.048, +0.005] | -0.0198 [-0.0603, +0.0329] | +0.0170 [-0.0610, +0.0834] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | blurb-header | blurb-decider |
|---|---|---|---|
| overall | all | 0.094 | 0.107 |
| type | choice | 0.094 | 0.107 |
| options | 2 | 0.033 | 0.057 |
| options | 3-5 | 0.119 | 0.111 |
| options | 6-26 | 0.232 | 0.244 |
| options | 27+ | 0.304 | 0.271 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| blurb-header | 2 | chosen | 650 1520 |
| blurb-header | 2 | gold | 613 1557 |
| blurb-header | 3-5 | chosen | 255 217 209 123 4 |
| blurb-header | 3-5 | gold | 240 230 199 137 2 |
| blurb-header | 6-26 | chosen | 64 70 51 47 36 41 49 40 40 37 24 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| blurb-header | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| blurb-header | 27+ | chosen | 6 5 4 2 3 8 8 2 3 3 5 2 3 5 3 3 2 2 2 1 3 2 1 1 3 2 3 |
| blurb-header | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |
| blurb-decider | 2 | chosen | 610 1560 |
| blurb-decider | 2 | gold | 613 1557 |
| blurb-decider | 3-5 | chosen | 269 228 184 122 5 |
| blurb-decider | 3-5 | gold | 240 230 199 137 2 |
| blurb-decider | 6-26 | chosen | 65 80 49 47 35 41 50 41 39 32 20 1 2 0 0 2 1 0 0 0 0 0 0 0 0 0 |
| blurb-decider | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| blurb-decider | 27+ | chosen | 2 5 4 2 4 7 7 3 2 3 6 2 3 7 2 2 4 2 2 1 3 3 1 2 3 3 3 |
| blurb-decider | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |

