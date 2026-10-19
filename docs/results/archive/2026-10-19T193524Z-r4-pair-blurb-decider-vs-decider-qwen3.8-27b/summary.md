# qwen3.8-27b R4 pair screen: blurb-decider vs decider, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T193524Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- title: R4 pair screen
- set: blurb-decider
- control: decider
- collect decider calib-600: .cache/collect/qwen3.8-27b/calib-600-decider.jsonl.gz
- collect decider index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-decider.jsonl.gz
- collect blurb-decider calib-600: .cache/collect/qwen3.8-27b/calib-600-blurb-decider.jsonl.gz
- collect blurb-decider index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-blurb-decider.jsonl.gz
- collect decider image dev: .cache/vision-collect/qwen3.8-27b/r4-decider/dev.jsonl.gz
- collect blurb-decider image dev: .cache/vision-collect/qwen3.8-27b/r4-blurb-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered
- run time: 26 s

Reports only; the owner picks.

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| decider | 590 | 3728 | 1.471 | 4.550 | 0.976 |
| blurb-decider | 590 | 3728 | 1.546 | 5.078 | 1.226 |

## all (3728 questions)

Δ is blurb-decider − decider on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | decider | 3728 | 0.767 | 0.023 | 0.770 | 0.325 | baseline | baseline | baseline |
| all | blurb-decider | 3728 | 0.770 | 0.022 | 0.743 | 0.320 | +0.002 [-0.003, +0.008] | -0.0014 [-0.0128, +0.0089] | -0.0270 [-0.0338, -0.0205] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | decider | 3690 | 0.767 | 0.024 | 0.772 | 0.325 | baseline | baseline | baseline |
| choice | blurb-decider | 3690 | 0.769 | 0.022 | 0.745 | 0.320 | +0.002 [-0.004, +0.007] | -0.0023 [-0.0139, +0.0087] | -0.0269 [-0.0335, -0.0206] |
| noul | decider | 38 | 0.816 | 0.143 | 0.585 | 0.291 | baseline | baseline | baseline |
| noul | blurb-decider | 38 | 0.868 | 0.122 | 0.551 | 0.264 | +0.053 [+0.000, +0.132] | -0.0206 [-0.1080, +0.0531] | -0.0338 [-0.0951, +0.0255] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | decider | 2208 | 0.902 | 0.058 | 0.262 | 0.154 | baseline | baseline | baseline |
| 2 | blurb-decider | 2208 | 0.899 | 0.038 | 0.260 | 0.155 | -0.003 [-0.010, +0.004] | -0.0206 [-0.0272, -0.0132] | -0.0023 [-0.0073, +0.0032] |
| 3-5 | decider | 808 | 0.755 | 0.028 | 0.616 | 0.333 | baseline | baseline | baseline |
| 3-5 | blurb-decider | 808 | 0.764 | 0.032 | 0.619 | 0.332 | +0.009 [-0.005, +0.022] | +0.0033 [-0.0203, +0.0263] | +0.0036 [-0.0089, +0.0182] |
| 6-26 | decider | 505 | 0.297 | 0.284 | 2.750 | 0.970 | baseline | baseline | baseline |
| 6-26 | blurb-decider | 505 | 0.303 | 0.242 | 2.572 | 0.925 | +0.006 [-0.010, +0.022] | -0.0426 [-0.0634, -0.0243] | -0.1778 [-0.2085, -0.1471] |
| 27+ | decider | 207 | 0.531 | 0.093 | 1.963 | 0.551 | baseline | baseline | baseline |
| 27+ | blurb-decider | 207 | 0.556 | 0.073 | 1.922 | 0.545 | +0.024 [+0.005, +0.048] | -0.0196 [-0.0455, +0.0234] | -0.0408 [-0.0844, +0.0021] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | decider | blurb-decider |
|---|---|---|---|
| overall | all | 0.105 | 0.107 |
| type | choice | 0.105 | 0.107 |
| options | 2 | 0.050 | 0.057 |
| options | 3-5 | 0.119 | 0.111 |
| options | 6-26 | 0.236 | 0.244 |
| options | 27+ | 0.309 | 0.271 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| decider | 2 | chosen | 631 1539 |
| decider | 2 | gold | 613 1557 |
| decider | 3-5 | chosen | 274 227 183 121 3 |
| decider | 3-5 | gold | 240 230 199 137 2 |
| decider | 6-26 | chosen | 65 77 44 53 33 37 58 42 36 31 23 1 2 0 0 2 1 0 0 0 0 0 0 0 0 0 |
| decider | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| decider | 27+ | chosen | 4 4 4 3 4 7 8 2 3 3 5 3 3 6 2 2 4 2 2 1 3 2 1 1 3 2 2 |
| decider | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |
| blurb-decider | 2 | chosen | 610 1560 |
| blurb-decider | 2 | gold | 613 1557 |
| blurb-decider | 3-5 | chosen | 269 228 184 122 5 |
| blurb-decider | 3-5 | gold | 240 230 199 137 2 |
| blurb-decider | 6-26 | chosen | 65 80 49 47 35 41 50 41 39 32 20 1 2 0 0 2 1 0 0 0 0 0 0 0 0 0 |
| blurb-decider | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| blurb-decider | 27+ | chosen | 2 5 4 2 4 7 7 3 2 3 6 2 3 7 2 2 4 2 2 1 3 3 1 2 3 3 3 |
| blurb-decider | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |

