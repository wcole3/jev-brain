# qwen3.8-27b R4 pair screen: blurb-header vs letters, text index-dev-2k

## Provenance

- timestamp: 2026-10-19T185753Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- title: R4 pair screen
- set: blurb-header
- control: letters
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib-600-letters.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-letters.jsonl.gz
- collect blurb-header calib-600: .cache/collect/qwen3.8-27b/calib-600-blurb-header.jsonl.gz
- collect blurb-header index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-blurb-header.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/labels-letters/dev.jsonl.gz
- collect blurb-header image dev: .cache/vision-collect/qwen3.8-27b/r4-blurb-header/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered
- run time: 25 s

Reports only; the owner picks.

## Fits (calib-600)

| arm | calib questions | index-dev-2k questions | choice | score | noul |
|---|---|---|---|---|---|
| letters | 590 | 3728 | 1.492 | 5.187 | 0.934 |
| blurb-header | 590 | 3728 | 1.567 | 6.022 | 1.189 |

## all (3728 questions)

Δ is blurb-header − letters on the same questions, with a 95% paired-bootstrap CI.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | letters | 3728 | 0.782 | 0.022 | 0.734 | 0.305 | baseline | baseline | baseline |
| all | blurb-header | 3728 | 0.786 | 0.035 | 0.715 | 0.300 | +0.004 [-0.001, +0.009] | +0.0128 [-0.0007, +0.0185] | -0.0197 [-0.0260, -0.0132] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | letters | 3690 | 0.781 | 0.023 | 0.737 | 0.306 | baseline | baseline | baseline |
| choice | blurb-header | 3690 | 0.785 | 0.035 | 0.717 | 0.301 | +0.004 [-0.001, +0.009] | +0.0120 [-0.0014, +0.0182] | -0.0201 [-0.0265, -0.0137] |
| noul | letters | 38 | 0.868 | 0.112 | 0.474 | 0.229 | baseline | baseline | baseline |
| noul | blurb-header | 38 | 0.895 | 0.172 | 0.496 | 0.216 | +0.026 [+0.000, +0.079] | +0.0607 [-0.0175, +0.1022] | +0.0218 [-0.0242, +0.0868] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | letters | 2208 | 0.915 | 0.032 | 0.214 | 0.130 | baseline | baseline | baseline |
| 2 | blurb-header | 2208 | 0.916 | 0.017 | 0.208 | 0.127 | +0.001 [-0.005, +0.007] | -0.0156 [-0.0201, -0.0008] | -0.0063 [-0.0108, -0.0014] |
| 3-5 | letters | 808 | 0.777 | 0.022 | 0.583 | 0.311 | baseline | baseline | baseline |
| 3-5 | blurb-header | 808 | 0.781 | 0.028 | 0.581 | 0.308 | +0.004 [-0.007, +0.016] | +0.0069 [-0.0187, +0.0273] | -0.0015 [-0.0136, +0.0126] |
| 6-26 | letters | 505 | 0.303 | 0.275 | 2.732 | 0.959 | baseline | baseline | baseline |
| 6-26 | blurb-header | 505 | 0.313 | 0.261 | 2.655 | 0.942 | +0.010 [-0.004, +0.024] | -0.0139 [-0.0304, +0.0007] | -0.0765 [-0.1078, -0.0433] |
| 27+ | letters | 207 | 0.556 | 0.088 | 2.000 | 0.553 | baseline | baseline | baseline |
| 27+ | blurb-header | 207 | 0.575 | 0.093 | 1.905 | 0.544 | +0.019 [+0.005, +0.039] | +0.0043 [-0.0364, +0.0422] | -0.0948 [-0.1465, -0.0486] |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | blurb-header |
|---|---|---|---|
| overall | all | 0.098 | 0.094 |
| type | choice | 0.098 | 0.094 |
| options | 2 | 0.033 | 0.033 |
| options | 3-5 | 0.134 | 0.119 |
| options | 6-26 | 0.232 | 0.232 |
| options | 27+ | 0.319 | 0.304 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 664 1506 |
| letters | 2 | gold | 613 1557 |
| letters | 3-5 | chosen | 256 213 207 129 3 |
| letters | 3-5 | gold | 240 230 199 137 2 |
| letters | 6-26 | chosen | 61 70 49 48 32 40 52 46 40 37 24 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| letters | 27+ | chosen | 4 5 4 2 3 7 9 2 3 3 7 3 3 6 3 2 3 3 2 1 2 1 1 2 3 2 2 |
| letters | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |
| blurb-header | 2 | chosen | 650 1520 |
| blurb-header | 2 | gold | 613 1557 |
| blurb-header | 3-5 | chosen | 255 217 209 123 4 |
| blurb-header | 3-5 | gold | 240 230 199 137 2 |
| blurb-header | 6-26 | chosen | 64 70 51 47 36 41 49 40 40 37 24 1 2 0 0 1 1 1 0 0 0 0 0 0 0 0 |
| blurb-header | 6-26 | gold | 132 58 44 44 28 45 35 39 38 30 7 0 0 0 0 0 0 2 0 0 1 0 1 1 0 0 |
| blurb-header | 27+ | chosen | 6 5 4 2 3 8 8 2 3 3 5 2 3 5 3 3 2 2 2 1 3 2 1 1 3 2 3 |
| blurb-header | 27+ | gold | 4 4 2 2 2 2 3 0 1 3 2 3 3 2 4 3 1 1 3 2 2 0 3 1 3 3 4 |

