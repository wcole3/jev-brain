# gemma-4-31b M3 option orders: header

## Provenance

- timestamp: 2026-10-03T033153Z
- repo commit: 8076f88
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- defaults: PROMPT_LAYOUT decider_chat, OPTION_ORDERS identity (profiles/gemma-4-31b.env)
- layout: header
- collect calib: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect index-dev: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect eval: .cache/collect/gemma-4-31b/eval.jsonl.gz
- temperatures: each arm's T is an ungated fit on the calib split (b = 0), not the shipped calibration.json
- shipped calibration (reference): gemma-4-31b/header/calibration.json: T choice 4.263, score 5.603, noul 7.609, b 0.000
- T identity: choice 4.263, score 19.999, noul 7.609
- T identity+reversed: choice 4.090, score 19.999, noul 7.167
- T cyclic:2: choice 4.053, score 19.478, noul 7.167
- T cyclic:3: choice 3.989, score 19.585, noul 7.167
- T cyclic:4: choice 3.960, score 19.299, noul 7.167
- T pride: choice 4.263, score 19.999, noul 7.609

## Recommendation

Default: identity, each arm at its own calib-fitted T (b = 0).

- index-dev qualifies: cyclic:2 (Δ accuracy +0.003, 2.000 mean reads), cyclic:3 (Δ accuracy +0.004, 2.387 mean reads), cyclic:4 (Δ accuracy +0.005, 2.724 mean reads), identity+reversed (Δ accuracy +0.005, 2.000 mean reads)
- eval qualifies: cyclic:2 (Δ accuracy +0.013, 2.000 mean reads), cyclic:3 (Δ accuracy +0.009, 2.646 mean reads), cyclic:4 (Δ accuracy +0.011, 3.171 mean reads), identity+reversed (Δ accuracy +0.015, 2.000 mean reads)
- **verdict: identity+reversed**
- read cost: identity+reversed: at most 2 reads per question, 2.000 on average on index-dev; latency measured live on the latency sample (latency.py)
- pride (diagnostic, needs gateway support (no OPTION_ORDERS value)): index-dev Δ accuracy -0.000 [-0.001, -0.000], Δ ECE -0.0008 [-0.0014, +0.0002]; eval Δ accuracy -0.001 [-0.002, +0.001], Δ ECE +0.0223 [+0.0109, +0.0296]
- shipped calibration (reference): index-dev Δ accuracy +0.000 [+0.000, +0.000], Δ ECE +0.0000 [+0.0000, +0.0000]; eval Δ accuracy +0.000 [+0.000, +0.000], Δ ECE -0.0179 [-0.0309, -0.0050]

An arm qualifies on a split on an accuracy CI low > 0 or an ECE CI high < 0 over the default, without the other metric getting worse beyond its CI. The verdict is an arm that qualifies on both index-dev and eval: the cheapest by mean reads per question, then the larger mean Δ accuracy. Each arm is tested at 95%, so one of several can clear by chance; needing both splits guards against that. pride and the shipped-calibration row are never candidates. The owner makes the final call.

## index-dev

Δ is arm − identity on the same questions, with a 95% paired-bootstrap CI.

| arm | reads (max) | mean reads |
|---|---|---|
| identity | 1 | 1.000 |
| identity+reversed | 2 | 2.000 |
| cyclic:2 | 2 | 2.000 |
| cyclic:3 | 3 | 2.387 |
| cyclic:4 | 4 | 2.724 |
| pride | 1 | 1.000 |
| shipped calibration (reference) | 1 | 1.000 |

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | identity | 14680 | 0.789 | 0.126 | 0.814 | 0.340 | baseline | baseline | baseline |
| all | identity+reversed | 14680 | 0.795 | 0.114 | 0.794 | 0.331 | +0.005 [+0.003, +0.008] | -0.0119 [-0.0146, -0.0087] | -0.0200 [-0.0258, -0.0142] |
| all | cyclic:2 | 14680 | 0.793 | 0.118 | 0.797 | 0.333 | +0.003 [+0.001, +0.006] | -0.0085 [-0.0109, -0.0055] | -0.0174 [-0.0231, -0.0120] |
| all | cyclic:3 | 14680 | 0.794 | 0.117 | 0.793 | 0.333 | +0.004 [+0.002, +0.007] | -0.0085 [-0.0111, -0.0056] | -0.0209 [-0.0270, -0.0150] |
| all | cyclic:4 | 14680 | 0.794 | 0.117 | 0.796 | 0.333 | +0.005 [+0.002, +0.007] | -0.0088 [-0.0116, -0.0059] | -0.0183 [-0.0245, -0.0122] |
| all | pride | 14680 | 0.789 | 0.125 | 0.818 | 0.341 | -0.000 [-0.001, -0.000] | -0.0008 [-0.0014, +0.0002] | +0.0036 [+0.0022, +0.0050] |
| all | shipped calibration (reference) | 14680 | 0.789 | 0.126 | 0.814 | 0.340 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | identity | 14537 | 0.789 | 0.126 | 0.818 | 0.341 | baseline | baseline | baseline |
| choice | identity+reversed | 14537 | 0.794 | 0.114 | 0.798 | 0.332 | +0.005 [+0.003, +0.008] | -0.0120 [-0.0147, -0.0087] | -0.0203 [-0.0260, -0.0145] |
| choice | cyclic:2 | 14537 | 0.792 | 0.118 | 0.800 | 0.334 | +0.003 [+0.001, +0.006] | -0.0086 [-0.0111, -0.0056] | -0.0176 [-0.0235, -0.0120] |
| choice | cyclic:3 | 14537 | 0.793 | 0.118 | 0.797 | 0.334 | +0.005 [+0.002, +0.007] | -0.0086 [-0.0113, -0.0056] | -0.0211 [-0.0273, -0.0151] |
| choice | cyclic:4 | 14537 | 0.794 | 0.117 | 0.799 | 0.334 | +0.005 [+0.002, +0.007] | -0.0089 [-0.0118, -0.0060] | -0.0185 [-0.0248, -0.0123] |
| choice | pride | 14537 | 0.789 | 0.126 | 0.822 | 0.341 | -0.000 [-0.001, -0.000] | -0.0008 [-0.0015, +0.0002] | +0.0036 [+0.0023, +0.0050] |
| choice | shipped calibration (reference) | 14537 | 0.789 | 0.126 | 0.818 | 0.341 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| noul | identity | 143 | 0.832 | 0.090 | 0.430 | 0.253 | baseline | baseline | baseline |
| noul | identity+reversed | 143 | 0.832 | 0.094 | 0.436 | 0.257 | +0.000 [+0.000, +0.000] | +0.0041 [-0.0153, +0.0308] | +0.0055 [-0.0078, +0.0199] |
| noul | cyclic:2 | 143 | 0.832 | 0.094 | 0.436 | 0.257 | +0.000 [+0.000, +0.000] | +0.0041 [-0.0153, +0.0308] | +0.0055 [-0.0078, +0.0199] |
| noul | cyclic:3 | 143 | 0.832 | 0.094 | 0.436 | 0.257 | +0.000 [+0.000, +0.000] | +0.0041 [-0.0153, +0.0308] | +0.0055 [-0.0078, +0.0199] |
| noul | cyclic:4 | 143 | 0.832 | 0.094 | 0.436 | 0.257 | +0.000 [+0.000, +0.000] | +0.0041 [-0.0153, +0.0308] | +0.0055 [-0.0078, +0.0199] |
| noul | pride | 143 | 0.832 | 0.090 | 0.430 | 0.253 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| noul | shipped calibration (reference) | 143 | 0.832 | 0.090 | 0.430 | 0.253 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | identity | 8997 | 0.890 | 0.083 | 0.373 | 0.188 | baseline | baseline | baseline |
| 2 | identity+reversed | 8997 | 0.893 | 0.078 | 0.359 | 0.181 | +0.003 [+0.000, +0.006] | -0.0048 [-0.0073, -0.0024] | -0.0140 [-0.0197, -0.0078] |
| 2 | cyclic:2 | 8997 | 0.893 | 0.079 | 0.361 | 0.182 | +0.003 [+0.000, +0.006] | -0.0043 [-0.0068, -0.0020] | -0.0116 [-0.0174, -0.0054] |
| 2 | cyclic:3 | 8997 | 0.893 | 0.079 | 0.365 | 0.182 | +0.003 [+0.000, +0.006] | -0.0037 [-0.0062, -0.0014] | -0.0073 [-0.0132, -0.0010] |
| 2 | cyclic:4 | 8997 | 0.893 | 0.079 | 0.367 | 0.182 | +0.003 [+0.000, +0.006] | -0.0035 [-0.0060, -0.0012] | -0.0053 [-0.0113, +0.0010] |
| 2 | pride | 8997 | 0.890 | 0.083 | 0.373 | 0.188 | +0.000 [+0.000, +0.000] | -0.0000 [-0.0000, -0.0000] | +0.0000 [+0.0000, +0.0000] |
| 2 | shipped calibration (reference) | 8997 | 0.890 | 0.083 | 0.373 | 0.188 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| 3-5 | identity | 3015 | 0.787 | 0.129 | 0.724 | 0.346 | baseline | baseline | baseline |
| 3-5 | identity+reversed | 3015 | 0.795 | 0.111 | 0.698 | 0.332 | +0.009 [+0.002, +0.015] | -0.0173 [-0.0238, -0.0101] | -0.0264 [-0.0390, -0.0148] |
| 3-5 | cyclic:2 | 3015 | 0.790 | 0.119 | 0.719 | 0.340 | +0.004 [-0.002, +0.010] | -0.0096 [-0.0154, -0.0036] | -0.0052 [-0.0159, +0.0056] |
| 3-5 | cyclic:3 | 3015 | 0.794 | 0.115 | 0.710 | 0.335 | +0.007 [+0.002, +0.013] | -0.0132 [-0.0193, -0.0071] | -0.0141 [-0.0262, -0.0024] |
| 3-5 | cyclic:4 | 3015 | 0.793 | 0.117 | 0.709 | 0.336 | +0.006 [+0.000, +0.013] | -0.0120 [-0.0185, -0.0061] | -0.0149 [-0.0280, -0.0023] |
| 3-5 | pride | 3015 | 0.786 | 0.129 | 0.724 | 0.346 | -0.001 [-0.002, +0.000] | +0.0006 [-0.0018, +0.0013] | -0.0002 [-0.0009, +0.0004] |
| 3-5 | shipped calibration (reference) | 3015 | 0.787 | 0.129 | 0.724 | 0.346 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| 6-26 | identity | 1896 | 0.378 | 0.394 | 2.646 | 0.985 | baseline | baseline | baseline |
| 6-26 | identity+reversed | 1896 | 0.386 | 0.365 | 2.659 | 0.981 | +0.008 [-0.002, +0.018] | -0.0297 [-0.0386, -0.0187] | +0.0135 [-0.0097, +0.0356] |
| 6-26 | cyclic:2 | 1896 | 0.385 | 0.374 | 2.631 | 0.982 | +0.007 [-0.002, +0.015] | -0.0203 [-0.0281, -0.0104] | -0.0146 [-0.0356, +0.0055] |
| 6-26 | cyclic:3 | 1896 | 0.388 | 0.376 | 2.618 | 0.986 | +0.010 [+0.001, +0.019] | -0.0182 [-0.0258, -0.0067] | -0.0277 [-0.0533, -0.0019] |
| 6-26 | cyclic:4 | 1896 | 0.391 | 0.370 | 2.626 | 0.982 | +0.013 [+0.004, +0.021] | -0.0243 [-0.0322, -0.0138] | -0.0196 [-0.0453, +0.0047] |
| 6-26 | pride | 1896 | 0.378 | 0.395 | 2.646 | 0.985 | +0.000 [+0.000, +0.000] | +0.0002 [-0.0015, +0.0004] | +0.0008 [-0.0002, +0.0018] |
| 6-26 | shipped calibration (reference) | 1896 | 0.378 | 0.394 | 2.646 | 0.985 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| 27+ | identity | 772 | 0.637 | 0.096 | 1.810 | 0.497 | baseline | baseline | baseline |
| 27+ | identity+reversed | 772 | 0.649 | 0.096 | 1.663 | 0.478 | +0.012 [-0.004, +0.027] | +0.0003 [-0.0282, +0.0240] | -0.1475 [-0.1972, -0.1005] |
| 27+ | cyclic:2 | 772 | 0.633 | 0.090 | 1.671 | 0.484 | -0.004 [-0.022, +0.013] | -0.0056 [-0.0295, +0.0183] | -0.1387 [-0.1944, -0.0877] |
| 27+ | cyclic:3 | 772 | 0.633 | 0.090 | 1.622 | 0.482 | -0.004 [-0.022, +0.014] | -0.0061 [-0.0329, +0.0159] | -0.1884 [-0.2509, -0.1307] |
| 27+ | cyclic:4 | 772 | 0.633 | 0.085 | 1.631 | 0.485 | -0.004 [-0.022, +0.014] | -0.0113 [-0.0370, +0.0142] | -0.1791 [-0.2397, -0.1184] |
| 27+ | pride | 772 | 0.635 | 0.085 | 1.878 | 0.512 | -0.003 [-0.006, +0.000] | -0.0114 [-0.0348, +0.0118] | +0.0675 [+0.0417, +0.0947] |
| 27+ | shipped calibration (reference) | 772 | 0.637 | 0.096 | 1.810 | 0.497 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

### Order diagnostics

| grouping | bucket | flip rate | AUROC |
|---|---|---|---|
| overall | all | 0.073 | 0.813 |
| type | choice | 0.073 | 0.813 |
| type | noul | n/a | 0.640 |
| options | 2 | 0.031 | 0.774 |
| options | 3-5 | 0.078 | 0.756 |
| options | 6-26 | 0.175 | 0.535 |
| options | 27+ | 0.290 | 0.850 |

flip rate: identity vs reversed top answer (noul left out). AUROC: identity-vs-reversed TVD as a predictor of identity+reversed errors (0.5 = no signal).

Noul lean: n 143, p(yes) identity 0.502, reversed 0.510, gold yes 0.399. p(yes) that moves with the order is a lean to a position; p(yes) that stays put is a lean to the word.

PriDe prior from the calib split (deployable without extra reads): the arithmetic mean of cyclic:4 probabilities at identity's T (the paper averages log-probabilities), for option counts 2, 3, 4, 5, 6, 7, 8, 9, 16, 32, 64, 77, 128; other counts pass through unchanged.

### Position histograms: identity and the most accurate other arm (identity+reversed)

| arm | options | series | count by caller position |
|---|---|---|---|
| identity | 2 | chosen | 2443 6411 |
| identity | 2 | gold | 2277 6577 |
| identity | 3-5 | chosen | 784 804 874 542 11 |
| identity | 3-5 | gold | 818 872 776 535 14 |
| identity | 6-26 | chosen | 184 206 185 226 166 186 184 179 147 136 70 3 7 3 3 2 2 2 0 2 0 3 0 0 0 0 |
| identity | 6-26 | gold | 436 249 166 171 158 135 131 133 127 106 58 3 5 3 1 2 4 2 2 0 1 0 3 0 0 0 |
| identity | 27+ | chosen | 30 17 24 15 13 12 12 8 13 13 6 13 17 16 19 8 15 6 14 10 8 7 4 8 8 6 19 |
| identity | 27+ | gold | 13 12 11 12 7 10 12 9 8 10 8 9 11 15 17 5 13 9 14 10 9 6 2 7 15 11 20 |
| identity+reversed | 2 | chosen | 2439 6415 |
| identity+reversed | 2 | gold | 2277 6577 |
| identity+reversed | 3-5 | chosen | 772 789 878 565 11 |
| identity+reversed | 3-5 | gold | 818 872 776 535 14 |
| identity+reversed | 6-26 | chosen | 179 195 176 222 167 177 182 177 153 148 84 4 6 2 3 2 3 5 3 4 0 2 1 0 1 0 |
| identity+reversed | 6-26 | gold | 436 249 166 171 158 135 131 133 127 106 58 3 5 3 1 2 4 2 2 0 1 0 3 0 0 0 |
| identity+reversed | 27+ | chosen | 23 10 14 11 11 12 10 6 11 10 5 11 15 11 19 7 12 6 13 11 6 6 6 11 9 7 20 |
| identity+reversed | 27+ | gold | 13 12 11 12 7 10 12 9 8 10 8 9 11 15 17 5 13 9 14 10 9 6 2 7 15 11 20 |

## eval

Δ is arm − identity on the same questions, with a 95% paired-bootstrap CI.

| arm | reads (max) | mean reads |
|---|---|---|
| identity | 1 | 1.000 |
| identity+reversed | 2 | 2.000 |
| cyclic:2 | 2 | 2.000 |
| cyclic:3 | 3 | 2.646 |
| cyclic:4 | 4 | 3.171 |
| pride | 1 | 1.000 |
| shipped calibration (reference) | 1 | 1.000 |

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | identity | 2827 | 0.811 | 0.097 | 0.660 | 0.321 | baseline | baseline | baseline |
| all | identity+reversed | 2827 | 0.826 | 0.108 | 0.643 | 0.310 | +0.015 [+0.009, +0.022] | +0.0112 [-0.0001, +0.0197] | -0.0172 [-0.0251, -0.0093] |
| all | cyclic:2 | 2827 | 0.824 | 0.099 | 0.643 | 0.310 | +0.013 [+0.007, +0.019] | +0.0025 [-0.0059, +0.0096] | -0.0164 [-0.0248, -0.0081] |
| all | cyclic:3 | 2827 | 0.820 | 0.098 | 0.643 | 0.311 | +0.009 [+0.002, +0.016] | +0.0017 [-0.0079, +0.0094] | -0.0162 [-0.0261, -0.0063] |
| all | cyclic:4 | 2827 | 0.822 | 0.099 | 0.644 | 0.310 | +0.011 [+0.005, +0.018] | +0.0022 [-0.0062, +0.0107] | -0.0158 [-0.0258, -0.0057] |
| all | pride | 2827 | 0.810 | 0.119 | 0.705 | 0.336 | -0.001 [-0.002, +0.001] | +0.0223 [+0.0109, +0.0296] | +0.0458 [+0.0386, +0.0535] |
| all | shipped calibration (reference) | 2827 | 0.811 | 0.079 | 0.672 | 0.314 | +0.000 [+0.000, +0.000] | -0.0179 [-0.0309, -0.0050] | +0.0128 [-0.0049, +0.0317] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | identity | 1607 | 0.830 | 0.079 | 0.650 | 0.285 | baseline | baseline | baseline |
| choice | identity+reversed | 1607 | 0.839 | 0.078 | 0.630 | 0.273 | +0.009 [+0.002, +0.017] | -0.0008 [-0.0088, +0.0114] | -0.0194 [-0.0327, -0.0065] |
| choice | cyclic:2 | 1607 | 0.834 | 0.077 | 0.637 | 0.277 | +0.004 [-0.002, +0.011] | -0.0022 [-0.0078, +0.0078] | -0.0125 [-0.0257, +0.0002] |
| choice | cyclic:3 | 1607 | 0.832 | 0.082 | 0.632 | 0.275 | +0.002 [-0.006, +0.009] | +0.0033 [-0.0049, +0.0130] | -0.0177 [-0.0344, -0.0021] |
| choice | cyclic:4 | 1607 | 0.836 | 0.081 | 0.635 | 0.274 | +0.006 [-0.001, +0.014] | +0.0022 [-0.0060, +0.0116] | -0.0149 [-0.0314, +0.0013] |
| choice | pride | 1607 | 0.829 | 0.119 | 0.729 | 0.309 | -0.001 [-0.003, +0.001] | +0.0401 [+0.0261, +0.0531] | +0.0788 [+0.0653, +0.0920] |
| choice | shipped calibration (reference) | 1607 | 0.830 | 0.079 | 0.650 | 0.285 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| noul | identity | 666 | 0.884 | 0.051 | 0.291 | 0.173 | baseline | baseline | baseline |
| noul | identity+reversed | 666 | 0.916 | 0.030 | 0.254 | 0.146 | +0.032 [+0.018, +0.047] | -0.0202 [-0.0359, +0.0054] | -0.0364 [-0.0497, -0.0235] |
| noul | cyclic:2 | 666 | 0.916 | 0.030 | 0.254 | 0.146 | +0.032 [+0.018, +0.047] | -0.0202 [-0.0359, +0.0054] | -0.0364 [-0.0497, -0.0235] |
| noul | cyclic:3 | 666 | 0.916 | 0.030 | 0.254 | 0.146 | +0.032 [+0.018, +0.047] | -0.0202 [-0.0359, +0.0054] | -0.0364 [-0.0497, -0.0235] |
| noul | cyclic:4 | 666 | 0.916 | 0.030 | 0.254 | 0.146 | +0.032 [+0.018, +0.047] | -0.0202 [-0.0359, +0.0054] | -0.0364 [-0.0497, -0.0235] |
| noul | pride | 666 | 0.884 | 0.051 | 0.291 | 0.173 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| noul | shipped calibration (reference) | 666 | 0.884 | 0.051 | 0.291 | 0.173 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| score | identity | 554 | 0.666 | 0.240 | 1.132 | 0.606 | baseline | baseline | baseline |
| score | identity+reversed | 554 | 0.679 | 0.305 | 1.145 | 0.613 | +0.013 [-0.005, +0.032] | +0.0647 [+0.0181, +0.0874] | +0.0125 [+0.0067, +0.0183] |
| score | cyclic:2 | 554 | 0.682 | 0.273 | 1.128 | 0.604 | +0.016 [+0.000, +0.032] | +0.0332 [+0.0055, +0.0535] | -0.0040 [-0.0102, +0.0022] |
| score | cyclic:3 | 554 | 0.670 | 0.274 | 1.144 | 0.614 | +0.004 [-0.014, +0.022] | +0.0344 [+0.0053, +0.0588] | +0.0123 [+0.0048, +0.0202] |
| score | cyclic:4 | 554 | 0.668 | 0.287 | 1.138 | 0.610 | +0.002 [-0.018, +0.020] | +0.0470 [+0.0106, +0.0699] | +0.0063 [-0.0019, +0.0143] |
| score | pride | 554 | 0.664 | 0.248 | 1.137 | 0.609 | -0.002 [-0.009, +0.004] | +0.0077 [-0.0080, +0.0160] | +0.0049 [+0.0038, +0.0060] |
| score | shipped calibration (reference) | 554 | 0.666 | 0.170 | 1.197 | 0.567 | +0.000 [+0.000, +0.000] | -0.0695 [-0.1176, -0.0151] | +0.0653 [-0.0320, +0.1622] |

| options | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| 2 | identity | 1000 | 0.829 | 0.106 | 0.564 | 0.289 | baseline | baseline | baseline |
| 2 | identity+reversed | 1000 | 0.850 | 0.104 | 0.545 | 0.272 | +0.021 [+0.011, +0.032] | -0.0015 [-0.0099, +0.0100] | -0.0186 [-0.0305, -0.0074] |
| 2 | cyclic:2 | 1000 | 0.850 | 0.104 | 0.548 | 0.272 | +0.021 [+0.011, +0.032] | -0.0013 [-0.0097, +0.0102] | -0.0156 [-0.0276, -0.0042] |
| 2 | cyclic:3 | 1000 | 0.850 | 0.105 | 0.554 | 0.272 | +0.021 [+0.011, +0.032] | -0.0010 [-0.0096, +0.0101] | -0.0102 [-0.0224, +0.0014] |
| 2 | cyclic:4 | 1000 | 0.850 | 0.105 | 0.556 | 0.273 | +0.021 [+0.011, +0.032] | -0.0009 [-0.0094, +0.0103] | -0.0076 [-0.0200, +0.0042] |
| 2 | pride | 1000 | 0.829 | 0.106 | 0.564 | 0.289 | +0.000 [+0.000, +0.000] | -0.0000 [-0.0000, +0.0000] | +0.0000 [-0.0000, +0.0000] |
| 2 | shipped calibration (reference) | 1000 | 0.829 | 0.106 | 0.564 | 0.289 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| 3-5 | identity | 1210 | 0.783 | 0.145 | 0.736 | 0.383 | baseline | baseline | baseline |
| 3-5 | identity+reversed | 1210 | 0.788 | 0.170 | 0.733 | 0.383 | +0.006 [-0.003, +0.016] | +0.0258 [+0.0052, +0.0377] | -0.0025 [-0.0122, +0.0069] |
| 3-5 | cyclic:2 | 1210 | 0.790 | 0.159 | 0.729 | 0.380 | +0.007 [-0.001, +0.016] | +0.0145 [+0.0008, +0.0255] | -0.0067 [-0.0165, +0.0034] |
| 3-5 | cyclic:3 | 1210 | 0.783 | 0.158 | 0.729 | 0.382 | +0.000 [-0.011, +0.011] | +0.0136 [-0.0027, +0.0262] | -0.0071 [-0.0206, +0.0055] |
| 3-5 | cyclic:4 | 1210 | 0.783 | 0.163 | 0.728 | 0.381 | +0.000 [-0.011, +0.010] | +0.0185 [+0.0007, +0.0321] | -0.0080 [-0.0208, +0.0046] |
| 3-5 | pride | 1210 | 0.782 | 0.150 | 0.738 | 0.384 | -0.001 [-0.004, +0.002] | +0.0056 [-0.0030, +0.0092] | +0.0025 [+0.0018, +0.0033] |
| 3-5 | shipped calibration (reference) | 1210 | 0.783 | 0.103 | 0.766 | 0.365 | +0.000 [+0.000, +0.000] | -0.0417 [-0.0685, -0.0142] | +0.0299 [-0.0137, +0.0730] |
| 6-26 | identity | 314 | 0.777 | 0.116 | 0.810 | 0.331 | baseline | baseline | baseline |
| 6-26 | identity+reversed | 314 | 0.806 | 0.085 | 0.759 | 0.303 | +0.029 [+0.003, +0.054] | -0.0313 [-0.0502, -0.0038] | -0.0514 [-0.0925, -0.0131] |
| 6-26 | cyclic:2 | 314 | 0.796 | 0.103 | 0.766 | 0.308 | +0.019 [-0.003, +0.045] | -0.0136 [-0.0317, +0.0113] | -0.0443 [-0.0897, -0.0051] |
| 6-26 | cyclic:3 | 314 | 0.809 | 0.090 | 0.731 | 0.295 | +0.032 [+0.006, +0.057] | -0.0267 [-0.0499, +0.0028] | -0.0791 [-0.1335, -0.0291] |
| 6-26 | cyclic:4 | 314 | 0.815 | 0.081 | 0.737 | 0.291 | +0.038 [+0.013, +0.067] | -0.0355 [-0.0564, -0.0018] | -0.0734 [-0.1303, -0.0233] |
| 6-26 | pride | 314 | 0.780 | 0.113 | 0.805 | 0.330 | +0.003 [+0.000, +0.010] | -0.0036 [-0.0102, +0.0027] | -0.0052 [-0.0108, +0.0004] |
| 6-26 | shipped calibration (reference) | 314 | 0.777 | 0.116 | 0.810 | 0.331 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| 27+ | identity | 303 | 0.898 | 0.119 | 0.516 | 0.175 | baseline | baseline | baseline |
| 27+ | identity+reversed | 303 | 0.917 | 0.128 | 0.481 | 0.151 | +0.020 [+0.003, +0.040] | +0.0090 [-0.0141, +0.0292] | -0.0351 [-0.0661, -0.0072] |
| 27+ | cyclic:2 | 303 | 0.901 | 0.118 | 0.487 | 0.157 | +0.003 [-0.013, +0.020] | -0.0012 [-0.0269, +0.0203] | -0.0293 [-0.0588, -0.0018] |
| 27+ | cyclic:3 | 303 | 0.881 | 0.102 | 0.509 | 0.169 | -0.017 [-0.033, +0.000] | -0.0164 [-0.0402, +0.0135] | -0.0074 [-0.0410, +0.0256] |
| 27+ | cyclic:4 | 303 | 0.894 | 0.098 | 0.502 | 0.164 | -0.003 [-0.023, +0.017] | -0.0206 [-0.0440, +0.0066] | -0.0146 [-0.0487, +0.0189] |
| 27+ | pride | 303 | 0.891 | 0.300 | 0.938 | 0.304 | -0.007 [-0.017, +0.000] | +0.1816 [+0.1461, +0.2052] | +0.4222 [+0.3689, +0.4791] |
| 27+ | shipped calibration (reference) | 303 | 0.898 | 0.119 | 0.516 | 0.175 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

### Order diagnostics

| grouping | bucket | flip rate | AUROC |
|---|---|---|---|
| overall | all | 0.071 | 0.646 |
| type | choice | 0.053 | 0.642 |
| type | noul | n/a | 0.618 |
| type | score | 0.125 | 0.458 |
| options | 2 | 0.009 | 0.522 |
| options | 3-5 | 0.076 | 0.716 |
| options | 6-26 | 0.118 | 0.832 |
| options | 27+ | 0.073 | 0.780 |

flip rate: identity vs reversed top answer (noul left out). AUROC: identity-vs-reversed TVD as a predictor of identity+reversed errors (0.5 = no signal).

Noul lean: n 666, p(yes) identity 0.367, reversed 0.346, gold yes 0.359. p(yes) that moves with the order is a lean to a position; p(yes) that stays put is a lean to the word.

PriDe prior from the calib split (deployable without extra reads): the arithmetic mean of cyclic:4 probabilities at identity's T (the paper averages log-probabilities), for option counts 2, 3, 4, 5, 6, 7, 8, 9, 16, 32, 64, 77, 128; other counts pass through unchanged.

### Position histograms: identity and the most accurate other arm (identity+reversed)

| arm | options | series | count by caller position |
|---|---|---|---|
| identity | 2 | chosen | 173 161 |
| identity | 2 | gold | 161 173 |
| identity | 3-5 | chosen | 358 499 230 112 11 |
| identity | 3-5 | gold | 231 552 264 154 9 |
| identity | 6-26 | chosen | 35 47 41 29 41 30 26 22 20 5 8 0 4 1 2 3 0 0 0 0 0 0 0 0 0 0 |
| identity | 6-26 | gold | 42 36 36 33 41 30 23 33 17 5 8 0 4 1 2 3 0 0 0 0 0 0 0 0 0 0 |
| identity | 27+ | chosen | 2 5 2 2 6 1 4 3 2 2 3 3 21 16 20 3 1 4 25 1 1 4 1 3 3 3 2 |
| identity | 27+ | gold | 2 3 2 2 7 1 4 2 2 2 3 3 21 17 21 3 1 3 28 1 1 3 2 3 3 3 2 |
| identity+reversed | 2 | chosen | 173 161 |
| identity+reversed | 2 | gold | 161 173 |
| identity+reversed | 3-5 | chosen | 340 501 244 114 11 |
| identity+reversed | 3-5 | gold | 231 552 264 154 9 |
| identity+reversed | 6-26 | chosen | 35 41 40 28 44 34 23 27 19 5 8 0 4 1 2 3 0 0 0 0 0 0 0 0 0 0 |
| identity+reversed | 6-26 | gold | 42 36 36 33 41 30 23 33 17 5 8 0 4 1 2 3 0 0 0 0 0 0 0 0 0 0 |
| identity+reversed | 27+ | chosen | 2 5 2 2 6 1 4 3 2 2 3 3 22 15 20 3 1 3 25 1 1 4 1 3 3 3 2 |
| identity+reversed | 27+ | gold | 2 3 2 2 7 1 4 2 2 2 3 3 21 17 21 3 1 3 28 1 1 3 2 3 3 3 2 |
