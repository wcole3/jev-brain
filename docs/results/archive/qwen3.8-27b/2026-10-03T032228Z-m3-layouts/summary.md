# qwen3.8-27b M3 layouts

## Provenance

- timestamp: 2026-10-03T032228Z
- repo commit: 8076f88
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- defaults: PROMPT_LAYOUT decider_chat, OPTION_ORDERS identity (profiles/qwen3.8-27b.env)
- orders: identity
- collect calib: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect index-dev: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect eval: .cache/collect/qwen3.8-27b/eval.jsonl.gz
- temperatures: each arm's T is an ungated fit on the calib split (b = 0), not the shipped calibration.json
- shipped calibration (reference): qwen3.8-27b/decider_chat/calibration.json: T choice 1.496, score 1.664, noul 0.970, b 0.000
- T decider_chat: choice 1.496, score 4.420, noul 0.970
- T header: choice 1.536, score 5.308, noul 0.963
- T question_first: choice 1.352, score 6.264, noul 0.825

## Recommendation

Default: decider_chat, each arm at its own calib-fitted T (b = 0).

- index-dev qualifies: header (Δ accuracy +0.010)
- eval qualifies: none
- **verdict: keep the default**
- read cost: the same reads per question for each layout (identity); latency measured live on the latency sample (latency.py)
- shipped calibration (reference): index-dev Δ accuracy +0.000 [+0.000, +0.000], Δ ECE +0.0000 [+0.0000, +0.0000]; eval Δ accuracy +0.000 [+0.000, +0.000], Δ ECE -0.0401 [-0.0517, -0.0247]

An arm qualifies on a split on an accuracy CI low > 0 or an ECE CI high < 0 over the default, without the other metric getting worse beyond its CI. The verdict is an arm that qualifies on both index-dev and eval: the cheapest by mean reads per question, then the larger mean Δ accuracy. Each arm is tested at 95%, so one of several can clear by chance; needing both splits guards against that. pride and the shipped-calibration row are never candidates. The owner makes the final call.

Auto-switch on both splits: length <512: header, slice rest: header.

## index-dev

Every layout reads with identity, on the questions all of them answered. Δ is layout − decider_chat with a 95% paired-bootstrap CI. State length is the rendered state in the profile's tokens.

Questions answered: decider_chat 14684, header 14684, question_first 14684, of 14684 answered by any; compared on 14684.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | decider_chat | 14684 | 0.769 | 0.021 | 0.734 | 0.320 | baseline | baseline | baseline |
| all | header | 14684 | 0.779 | 0.021 | 0.694 | 0.302 | +0.010 [+0.006, +0.013] | +0.0002 [-0.0060, +0.0063] | -0.0403 [-0.0444, -0.0363] |
| all | question_first | 14684 | 0.755 | 0.038 | 0.784 | 0.340 | -0.014 [-0.018, -0.010] | +0.0171 [+0.0106, +0.0234] | +0.0504 [+0.0435, +0.0571] |
| all | shipped calibration (reference) | 14684 | 0.769 | 0.021 | 0.734 | 0.320 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | decider_chat | 14541 | 0.769 | 0.021 | 0.735 | 0.320 | baseline | baseline | baseline |
| choice | header | 14541 | 0.778 | 0.022 | 0.695 | 0.302 | +0.009 [+0.005, +0.013] | +0.0003 [-0.0061, +0.0065] | -0.0394 [-0.0435, -0.0352] |
| choice | question_first | 14541 | 0.754 | 0.038 | 0.787 | 0.341 | -0.015 [-0.019, -0.010] | +0.0167 [+0.0101, +0.0230] | +0.0525 [+0.0455, +0.0592] |
| choice | shipped calibration (reference) | 14541 | 0.769 | 0.021 | 0.735 | 0.320 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| noul | decider_chat | 143 | 0.776 | 0.145 | 0.669 | 0.347 | baseline | baseline | baseline |
| noul | header | 143 | 0.818 | 0.079 | 0.534 | 0.281 | +0.042 [+0.000, +0.091] | -0.0659 [-0.1053, -0.0094] | -0.1356 [-0.1846, -0.0918] |
| noul | question_first | 143 | 0.825 | 0.096 | 0.503 | 0.265 | +0.049 [+0.000, +0.105] | -0.0494 [-0.1102, +0.0009] | -0.1664 [-0.2333, -0.1038] |
| noul | shipped calibration (reference) | 143 | 0.776 | 0.145 | 0.669 | 0.347 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| state length | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| <512 | decider_chat | 11642 | 0.828 | 0.043 | 0.487 | 0.237 | baseline | baseline | baseline |
| <512 | header | 11642 | 0.841 | 0.025 | 0.447 | 0.215 | +0.012 [+0.008, +0.017] | -0.0186 [-0.0227, -0.0136] | -0.0393 [-0.0432, -0.0350] |
| <512 | question_first | 11642 | 0.818 | 0.032 | 0.517 | 0.251 | -0.011 [-0.016, -0.006] | -0.0114 [-0.0158, -0.0060] | +0.0303 [+0.0250, +0.0362] |
| <512 | shipped calibration (reference) | 11642 | 0.828 | 0.043 | 0.487 | 0.237 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| 512-2k | decider_chat | 2345 | 0.618 | 0.094 | 1.263 | 0.534 | baseline | baseline | baseline |
| 512-2k | header | 2345 | 0.615 | 0.098 | 1.247 | 0.531 | -0.003 [-0.014, +0.008] | +0.0045 [-0.0107, +0.0163] | -0.0160 [-0.0291, -0.0026] |
| 512-2k | question_first | 2345 | 0.591 | 0.114 | 1.349 | 0.566 | -0.027 [-0.040, -0.013] | +0.0203 [+0.0076, +0.0399] | +0.0857 [+0.0616, +0.1091] |
| 512-2k | shipped calibration (reference) | 2345 | 0.618 | 0.094 | 1.263 | 0.534 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| 2k-8k | decider_chat | 697 | 0.284 | 0.318 | 3.086 | 0.992 | baseline | baseline | baseline |
| 2k-8k | header | 697 | 0.293 | 0.341 | 2.946 | 0.987 | +0.009 [-0.004, +0.022] | +0.0232 [+0.0056, +0.0391] | -0.1401 [-0.1749, -0.1044] |
| 2k-8k | question_first | 697 | 0.260 | 0.378 | 3.353 | 1.072 | -0.024 [-0.044, -0.006] | +0.0598 [+0.0392, +0.0813] | +0.2667 [+0.1940, +0.3352] |
| 2k-8k | shipped calibration (reference) | 697 | 0.284 | 0.318 | 3.086 | 0.992 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| slice | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| long | decider_chat | 415 | 0.798 | 0.081 | 0.481 | 0.293 | baseline | baseline | baseline |
| long | header | 415 | 0.819 | 0.089 | 0.463 | 0.280 | +0.022 [-0.002, +0.046] | +0.0085 [-0.0313, +0.0383] | -0.0185 [-0.0386, +0.0010] |
| long | question_first | 415 | 0.783 | 0.076 | 0.527 | 0.326 | -0.014 [-0.048, +0.019] | -0.0046 [-0.0452, +0.0329] | +0.0458 [+0.0188, +0.0732] |
| long | shipped calibration (reference) | 415 | 0.798 | 0.081 | 0.481 | 0.293 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| rest | decider_chat | 14269 | 0.768 | 0.021 | 0.741 | 0.321 | baseline | baseline | baseline |
| rest | header | 14269 | 0.777 | 0.022 | 0.700 | 0.303 | +0.009 [+0.005, +0.013] | +0.0012 [-0.0055, +0.0082] | -0.0410 [-0.0452, -0.0366] |
| rest | question_first | 14269 | 0.754 | 0.038 | 0.792 | 0.340 | -0.014 [-0.018, -0.009] | +0.0172 [+0.0106, +0.0246] | +0.0505 [+0.0432, +0.0573] |
| rest | shipped calibration (reference) | 14269 | 0.768 | 0.021 | 0.741 | 0.321 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

### Bucket winners (auto-switch needs a different winner with an accuracy CI clear of zero)

Baseline: decider_chat (the verdict's layout, or the default when it stays), on both splits.

| grouping | bucket | winner | accuracy | Δ accuracy vs decider_chat | auto-switch |
|---|---|---|---|---|---|
| length | <512 | header | 0.841 | +0.012 [+0.008, +0.017] | yes |
| length | 512-2k | decider_chat | 0.618 | same layout | no |
| length | 2k-8k | header | 0.293 | +0.009 [-0.004, +0.022] | no |
| slice | long | header | 0.819 | +0.022 [-0.002, +0.046] | no |
| slice | rest | header | 0.777 | +0.009 [+0.005, +0.013] | yes |

## eval

Every layout reads with identity, on the questions all of them answered. Δ is layout − decider_chat with a 95% paired-bootstrap CI. State length is the rendered state in the profile's tokens.

Questions answered: decider_chat 2827, header 2827, question_first 2827, of 2827 answered by any; compared on 2827.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | decider_chat | 2827 | 0.794 | 0.071 | 0.568 | 0.306 | baseline | baseline | baseline |
| all | header | 2827 | 0.810 | 0.088 | 0.558 | 0.299 | +0.015 [+0.007, +0.023] | +0.0170 [+0.0045, +0.0290] | -0.0106 [-0.0171, -0.0042] |
| all | question_first | 2827 | 0.760 | 0.050 | 0.610 | 0.327 | -0.035 [-0.047, -0.022] | -0.0219 [-0.0358, -0.0059] | +0.0413 [+0.0293, +0.0534] |
| all | shipped calibration (reference) | 2827 | 0.794 | 0.031 | 0.563 | 0.294 | +0.000 [+0.000, +0.000] | -0.0401 [-0.0517, -0.0247] | -0.0049 [-0.0162, +0.0074] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | decider_chat | 1607 | 0.807 | 0.027 | 0.490 | 0.255 | baseline | baseline | baseline |
| choice | header | 1607 | 0.823 | 0.040 | 0.475 | 0.245 | +0.016 [+0.005, +0.026] | +0.0127 [-0.0065, +0.0232] | -0.0147 [-0.0237, -0.0058] |
| choice | question_first | 1607 | 0.809 | 0.042 | 0.510 | 0.262 | +0.002 [-0.012, +0.016] | +0.0145 [-0.0055, +0.0271] | +0.0197 [+0.0032, +0.0370] |
| choice | shipped calibration (reference) | 1607 | 0.807 | 0.027 | 0.490 | 0.255 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| noul | decider_chat | 666 | 0.892 | 0.027 | 0.269 | 0.164 | baseline | baseline | baseline |
| noul | header | 666 | 0.890 | 0.028 | 0.254 | 0.154 | -0.002 [-0.017, +0.015] | +0.0016 [-0.0228, +0.0232] | -0.0151 [-0.0308, +0.0010] |
| noul | question_first | 666 | 0.878 | 0.020 | 0.278 | 0.171 | -0.014 [-0.033, +0.005] | -0.0069 [-0.0250, +0.0173] | +0.0086 [-0.0156, +0.0347] |
| noul | shipped calibration (reference) | 666 | 0.892 | 0.027 | 0.269 | 0.164 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| score | decider_chat | 554 | 0.641 | 0.270 | 1.156 | 0.623 | baseline | baseline | baseline |
| score | header | 554 | 0.675 | 0.331 | 1.162 | 0.626 | +0.034 [+0.013, +0.058] | +0.0604 [+0.0319, +0.0885] | +0.0067 [-0.0012, +0.0147] |
| score | question_first | 554 | 0.475 | 0.156 | 1.299 | 0.704 | -0.166 [-0.208, -0.123] | -0.1142 [-0.1582, -0.0656] | +0.1432 [+0.1235, +0.1626] |
| score | shipped calibration (reference) | 554 | 0.641 | 0.147 | 1.130 | 0.562 | +0.000 [+0.000, +0.000] | -0.1231 [-0.1428, -0.0794] | -0.0252 [-0.0840, +0.0366] |

| state length | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| <512 | decider_chat | 2271 | 0.816 | 0.074 | 0.562 | 0.290 | baseline | baseline | baseline |
| <512 | header | 2271 | 0.834 | 0.094 | 0.551 | 0.283 | +0.018 [+0.008, +0.027] | +0.0195 [+0.0062, +0.0327] | -0.0101 [-0.0189, -0.0024] |
| <512 | question_first | 2271 | 0.773 | 0.047 | 0.603 | 0.311 | -0.043 [-0.058, -0.029] | -0.0270 [-0.0424, -0.0108] | +0.0415 [+0.0273, +0.0549] |
| <512 | shipped calibration (reference) | 2271 | 0.816 | 0.042 | 0.561 | 0.278 | +0.000 [+0.000, +0.000] | -0.0327 [-0.0443, -0.0186] | -0.0003 [-0.0148, +0.0149] |
| 512-2k | decider_chat | 83 | 0.747 | 0.253 | 0.801 | 0.442 | baseline | baseline | baseline |
| 512-2k | header | 83 | 0.735 | 0.228 | 0.815 | 0.449 | -0.012 [-0.060, +0.024] | -0.0247 [-0.0807, +0.0385] | +0.0146 [-0.0036, +0.0324] |
| 512-2k | question_first | 83 | 0.723 | 0.253 | 0.917 | 0.500 | -0.024 [-0.133, +0.072] | +0.0001 [-0.1067, +0.0873] | +0.1161 [+0.0582, +0.1703] |
| 512-2k | shipped calibration (reference) | 83 | 0.747 | 0.161 | 0.640 | 0.351 | +0.000 [+0.000, +0.000] | -0.0924 [-0.1574, -0.0316] | -0.1603 [-0.2092, -0.1102] |
| 2k-8k | decider_chat | 473 | 0.698 | 0.062 | 0.561 | 0.359 | baseline | baseline | baseline |
| 2k-8k | header | 473 | 0.706 | 0.065 | 0.543 | 0.349 | +0.008 [-0.008, +0.023] | +0.0031 [-0.0253, +0.0285] | -0.0173 [-0.0277, -0.0073] |
| 2k-8k | question_first | 473 | 0.702 | 0.054 | 0.588 | 0.375 | +0.004 [-0.021, +0.032] | -0.0075 [-0.0415, +0.0367] | +0.0270 [+0.0013, +0.0509] |
| 2k-8k | shipped calibration (reference) | 473 | 0.698 | 0.062 | 0.561 | 0.359 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| slice | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| long | decider_chat | 680 | 0.740 | 0.062 | 0.551 | 0.344 | baseline | baseline | baseline |
| long | header | 680 | 0.753 | 0.073 | 0.515 | 0.320 | +0.013 [+0.001, +0.026] | +0.0110 [-0.0161, +0.0380] | -0.0362 [-0.0482, -0.0254] |
| long | question_first | 680 | 0.754 | 0.085 | 0.536 | 0.332 | +0.015 [-0.010, +0.038] | +0.0238 [-0.0081, +0.0550] | -0.0153 [-0.0371, +0.0061] |
| long | shipped calibration (reference) | 680 | 0.740 | 0.054 | 0.526 | 0.330 | +0.000 [+0.000, +0.000] | -0.0074 [-0.0249, +0.0120] | -0.0251 [-0.0344, -0.0162] |
| rest | decider_chat | 2147 | 0.812 | 0.076 | 0.574 | 0.294 | baseline | baseline | baseline |
| rest | header | 2147 | 0.828 | 0.093 | 0.571 | 0.292 | +0.016 [+0.006, +0.026] | +0.0177 [+0.0036, +0.0312] | -0.0025 [-0.0102, +0.0054] |
| rest | question_first | 2147 | 0.762 | 0.047 | 0.633 | 0.325 | -0.050 [-0.066, -0.036] | -0.0282 [-0.0417, -0.0083] | +0.0592 [+0.0450, +0.0732] |
| rest | shipped calibration (reference) | 2147 | 0.812 | 0.045 | 0.575 | 0.283 | +0.000 [+0.000, +0.000] | -0.0304 [-0.0435, -0.0141] | +0.0015 [-0.0142, +0.0160] |

### Bucket winners (auto-switch needs a different winner with an accuracy CI clear of zero)

Baseline: decider_chat (the verdict's layout, or the default when it stays), on both splits.

| grouping | bucket | winner | accuracy | Δ accuracy vs decider_chat | auto-switch |
|---|---|---|---|---|---|
| length | <512 | header | 0.834 | +0.018 [+0.008, +0.027] | yes |
| length | 512-2k | decider_chat | 0.747 | same layout | no |
| length | 2k-8k | header | 0.706 | +0.008 [-0.008, +0.023] | no |
| slice | long | question_first | 0.754 | +0.015 [-0.010, +0.038] | no |
| slice | rest | header | 0.828 | +0.016 [+0.006, +0.026] | yes |
