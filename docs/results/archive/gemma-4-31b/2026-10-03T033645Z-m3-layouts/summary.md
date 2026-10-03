# gemma-4-31b M3 layouts

## Provenance

- timestamp: 2026-10-03T033645Z
- repo commit: 8076f88
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- defaults: PROMPT_LAYOUT decider_chat, OPTION_ORDERS identity (profiles/gemma-4-31b.env)
- orders: identity
- collect calib: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect index-dev: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect eval: .cache/collect/gemma-4-31b/eval.jsonl.gz
- temperatures: each arm's T is an ungated fit on the calib split (b = 0), not the shipped calibration.json
- shipped calibration (reference): gemma-4-31b/decider_chat/calibration.json: T choice 4.123, score 5.378, noul 7.528, b -0.636
- T decider_chat: choice 4.123, score 18.187, noul 7.620
- T header: choice 4.263, score 19.999, noul 7.609
- T question_first: choice 3.839, score 19.999, noul 7.292

## Recommendation

Default: decider_chat, each arm at its own calib-fitted T (b = 0).

- index-dev qualifies: header (Δ accuracy +0.041)
- eval qualifies: none
- **verdict: keep the default**
- read cost: the same reads per question for each layout (identity); latency measured live on the latency sample (latency.py)
- shipped calibration (reference): index-dev Δ accuracy +0.000 [+0.000, +0.000], Δ ECE -0.0000 [-0.0003, +0.0001]; eval Δ accuracy +0.002 [-0.001, +0.004], Δ ECE -0.0240 [-0.0370, -0.0057]

An arm qualifies on a split on an accuracy CI low > 0 or an ECE CI high < 0 over the default, without the other metric getting worse beyond its CI. The verdict is an arm that qualifies on both index-dev and eval: the cheapest by mean reads per question, then the larger mean Δ accuracy. Each arm is tested at 95%, so one of several can clear by chance; needing both splits guards against that. pride and the shipped-calibration row are never candidates. The owner makes the final call.

Auto-switch on both splits: none.

## index-dev

Every layout reads with identity, on the questions all of them answered. Δ is layout − decider_chat with a 95% paired-bootstrap CI. State length is the rendered state in the profile's tokens.

Questions answered: decider_chat 14684, header 14680, question_first 14684, of 14684 answered by any; compared on 14680.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | decider_chat | 14680 | 0.749 | 0.156 | 0.971 | 0.409 | baseline | baseline | baseline |
| all | header | 14680 | 0.789 | 0.126 | 0.814 | 0.340 | +0.041 [+0.036, +0.045] | -0.0295 [-0.0343, -0.0252] | -0.1567 [-0.1719, -0.1431] |
| all | question_first | 14680 | 0.748 | 0.163 | 0.982 | 0.407 | -0.000 [-0.005, +0.004] | +0.0078 [+0.0030, +0.0124] | +0.0116 [-0.0018, +0.0245] |
| all | shipped calibration (reference) | 14680 | 0.749 | 0.155 | 0.970 | 0.409 | +0.000 [+0.000, +0.000] | -0.0000 [-0.0003, +0.0001] | -0.0005 [-0.0008, -0.0001] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | decider_chat | 14537 | 0.748 | 0.156 | 0.976 | 0.411 | baseline | baseline | baseline |
| choice | header | 14537 | 0.789 | 0.126 | 0.818 | 0.341 | +0.041 [+0.037, +0.046] | -0.0300 [-0.0348, -0.0255] | -0.1581 [-0.1733, -0.1447] |
| choice | question_first | 14537 | 0.747 | 0.164 | 0.988 | 0.408 | -0.000 [-0.005, +0.004] | +0.0077 [+0.0029, +0.0122] | +0.0119 [-0.0018, +0.0247] |
| choice | shipped calibration (reference) | 14537 | 0.748 | 0.156 | 0.976 | 0.411 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| noul | decider_chat | 143 | 0.846 | 0.085 | 0.444 | 0.258 | baseline | baseline | baseline |
| noul | header | 143 | 0.832 | 0.090 | 0.430 | 0.253 | -0.014 [-0.042, +0.014] | +0.0055 [-0.0266, +0.0306] | -0.0143 [-0.0446, +0.0188] |
| noul | question_first | 143 | 0.846 | 0.084 | 0.428 | 0.247 | +0.000 [-0.035, +0.035] | -0.0006 [-0.0360, +0.0304] | -0.0165 [-0.0637, +0.0283] |
| noul | shipped calibration (reference) | 143 | 0.853 | 0.081 | 0.394 | 0.236 | +0.007 [+0.000, +0.021] | -0.0033 [-0.0304, +0.0238] | -0.0501 [-0.0844, -0.0147] |

| state length | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| <512 | decider_chat | 11641 | 0.802 | 0.116 | 0.723 | 0.324 | baseline | baseline | baseline |
| <512 | header | 11641 | 0.853 | 0.075 | 0.539 | 0.235 | +0.051 [+0.045, +0.055] | -0.0407 [-0.0452, -0.0353] | -0.1840 [-0.1999, -0.1668] |
| <512 | question_first | 11641 | 0.801 | 0.120 | 0.714 | 0.316 | -0.001 [-0.006, +0.004] | +0.0039 [-0.0008, +0.0093] | -0.0086 [-0.0228, +0.0064] |
| <512 | shipped calibration (reference) | 11641 | 0.802 | 0.116 | 0.722 | 0.324 | +0.000 [+0.000, +0.000] | +0.0000 [-0.0000, +0.0001] | -0.0004 [-0.0006, -0.0002] |
| 512-2k | decider_chat | 2110 | 0.664 | 0.236 | 1.346 | 0.560 | baseline | baseline | baseline |
| 512-2k | header | 2110 | 0.658 | 0.253 | 1.311 | 0.567 | -0.007 [-0.019, +0.006] | +0.0169 [+0.0047, +0.0305] | -0.0349 [-0.0646, -0.0033] |
| 512-2k | question_first | 2110 | 0.666 | 0.258 | 1.427 | 0.575 | +0.001 [-0.010, +0.013] | +0.0222 [+0.0090, +0.0341] | +0.0815 [+0.0463, +0.1160] |
| 512-2k | shipped calibration (reference) | 2110 | 0.665 | 0.235 | 1.344 | 0.559 | +0.000 [+0.000, +0.001] | -0.0005 [-0.0018, +0.0004] | -0.0015 [-0.0035, +0.0005] |
| 2k-8k | decider_chat | 929 | 0.270 | 0.478 | 3.227 | 1.136 | baseline | baseline | baseline |
| 2k-8k | header | 929 | 0.295 | 0.490 | 3.136 | 1.134 | +0.025 [+0.009, +0.041] | +0.0120 [-0.0074, +0.0326] | -0.0906 [-0.1483, -0.0321] |
| 2k-8k | question_first | 929 | 0.276 | 0.503 | 3.333 | 1.164 | +0.005 [-0.011, +0.020] | +0.0257 [+0.0108, +0.0475] | +0.1063 [+0.0447, +0.1664] |
| 2k-8k | shipped calibration (reference) | 929 | 0.270 | 0.478 | 3.227 | 1.136 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| slice | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| long | decider_chat | 411 | 0.791 | 0.178 | 0.773 | 0.370 | baseline | baseline | baseline |
| long | header | 411 | 0.798 | 0.166 | 0.761 | 0.352 | +0.007 [-0.022, +0.034] | -0.0123 [-0.0392, +0.0140] | -0.0124 [-0.1013, +0.0815] |
| long | question_first | 411 | 0.810 | 0.164 | 0.757 | 0.345 | +0.019 [-0.012, +0.054] | -0.0146 [-0.0479, +0.0157] | -0.0161 [-0.1240, +0.0798] |
| long | shipped calibration (reference) | 411 | 0.791 | 0.178 | 0.773 | 0.370 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| rest | decider_chat | 14269 | 0.747 | 0.155 | 0.976 | 0.410 | baseline | baseline | baseline |
| rest | header | 14269 | 0.789 | 0.125 | 0.816 | 0.339 | +0.042 [+0.037, +0.046] | -0.0301 [-0.0348, -0.0255] | -0.1608 [-0.1747, -0.1466] |
| rest | question_first | 14269 | 0.747 | 0.163 | 0.989 | 0.409 | -0.001 [-0.005, +0.004] | +0.0083 [+0.0038, +0.0130] | +0.0124 [-0.0010, +0.0257] |
| rest | shipped calibration (reference) | 14269 | 0.748 | 0.155 | 0.976 | 0.410 | +0.000 [+0.000, +0.000] | -0.0001 [-0.0003, +0.0001] | -0.0005 [-0.0009, -0.0001] |

### Bucket winners (auto-switch needs a different winner with an accuracy CI clear of zero)

Baseline: decider_chat (the verdict's layout, or the default when it stays), on both splits.

| grouping | bucket | winner | accuracy | Δ accuracy vs decider_chat | auto-switch |
|---|---|---|---|---|---|
| length | <512 | header | 0.853 | +0.051 [+0.045, +0.055] | yes |
| length | 512-2k | question_first | 0.666 | +0.001 [-0.010, +0.013] | no |
| length | 2k-8k | header | 0.295 | +0.025 [+0.009, +0.041] | yes |
| slice | long | question_first | 0.810 | +0.019 [-0.012, +0.054] | no |
| slice | rest | header | 0.789 | +0.042 [+0.037, +0.046] | yes |

## eval

Every layout reads with identity, on the questions all of them answered. Δ is layout − decider_chat with a 95% paired-bootstrap CI. State length is the rendered state in the profile's tokens.

Questions answered: decider_chat 2827, header 2827, question_first 2827, of 2827 answered by any; compared on 2827.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | decider_chat | 2827 | 0.814 | 0.095 | 0.630 | 0.312 | baseline | baseline | baseline |
| all | header | 2827 | 0.811 | 0.097 | 0.660 | 0.321 | -0.004 [-0.012, +0.005] | +0.0020 [-0.0069, +0.0153] | +0.0295 [+0.0123, +0.0474] |
| all | question_first | 2827 | 0.794 | 0.112 | 0.682 | 0.339 | -0.020 [-0.032, -0.008] | +0.0172 [+0.0025, +0.0310] | +0.0520 [+0.0279, +0.0773] |
| all | shipped calibration (reference) | 2827 | 0.816 | 0.071 | 0.637 | 0.302 | +0.002 [-0.001, +0.004] | -0.0240 [-0.0370, -0.0057] | +0.0065 [-0.0107, +0.0247] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | decider_chat | 1607 | 0.837 | 0.073 | 0.608 | 0.273 | baseline | baseline | baseline |
| choice | header | 1607 | 0.830 | 0.079 | 0.650 | 0.285 | -0.007 [-0.017, +0.004] | +0.0063 [-0.0065, +0.0164] | +0.0421 [+0.0143, +0.0721] |
| choice | question_first | 1607 | 0.816 | 0.082 | 0.668 | 0.300 | -0.021 [-0.035, -0.007] | +0.0095 [-0.0069, +0.0206] | +0.0605 [+0.0215, +0.1027] |
| choice | shipped calibration (reference) | 1607 | 0.837 | 0.073 | 0.608 | 0.273 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| noul | decider_chat | 666 | 0.881 | 0.075 | 0.282 | 0.172 | baseline | baseline | baseline |
| noul | header | 666 | 0.884 | 0.051 | 0.291 | 0.173 | +0.003 [-0.014, +0.020] | -0.0243 [-0.0455, -0.0021] | +0.0081 [-0.0178, +0.0354] |
| noul | question_first | 666 | 0.880 | 0.072 | 0.291 | 0.178 | -0.002 [-0.021, +0.018] | -0.0033 [-0.0262, +0.0191] | +0.0083 [-0.0239, +0.0410] |
| noul | shipped calibration (reference) | 666 | 0.889 | 0.028 | 0.275 | 0.164 | +0.008 [-0.003, +0.018] | -0.0473 [-0.0600, -0.0191] | -0.0076 [-0.0215, +0.0060] |
| score | decider_chat | 554 | 0.668 | 0.248 | 1.114 | 0.595 | baseline | baseline | baseline |
| score | header | 554 | 0.666 | 0.240 | 1.132 | 0.606 | -0.002 [-0.025, +0.022] | -0.0078 [-0.0296, +0.0414] | +0.0184 [+0.0070, +0.0299] |
| score | question_first | 554 | 0.628 | 0.302 | 1.193 | 0.646 | -0.040 [-0.070, -0.009] | +0.0539 [+0.0055, +0.1009] | +0.0797 [+0.0639, +0.0961] |
| score | shipped calibration (reference) | 554 | 0.668 | 0.159 | 1.156 | 0.552 | +0.000 [+0.000, +0.000] | -0.0883 [-0.1413, -0.0093] | +0.0425 [-0.0451, +0.1327] |

| state length | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| <512 | decider_chat | 2272 | 0.818 | 0.076 | 0.602 | 0.296 | baseline | baseline | baseline |
| <512 | header | 2272 | 0.818 | 0.075 | 0.611 | 0.300 | -0.000 [-0.009, +0.008] | -0.0004 [-0.0123, +0.0142] | +0.0089 [-0.0065, +0.0236] |
| <512 | question_first | 2272 | 0.803 | 0.100 | 0.644 | 0.318 | -0.015 [-0.027, -0.004] | +0.0242 [+0.0063, +0.0377] | +0.0417 [+0.0174, +0.0653] |
| <512 | shipped calibration (reference) | 2272 | 0.820 | 0.060 | 0.620 | 0.289 | +0.002 [-0.001, +0.005] | -0.0157 [-0.0343, +0.0031] | +0.0180 [-0.0033, +0.0391] |
| 512-2k | decider_chat | 92 | 0.837 | 0.305 | 0.789 | 0.411 | baseline | baseline | baseline |
| 512-2k | header | 92 | 0.837 | 0.314 | 0.850 | 0.418 | +0.000 [-0.054, +0.054] | +0.0093 [-0.0394, +0.0560] | +0.0617 [-0.0234, +0.1645] |
| 512-2k | question_first | 92 | 0.761 | 0.235 | 0.840 | 0.444 | -0.076 [-0.163, +0.011] | -0.0695 [-0.1554, +0.0082] | +0.0515 [-0.0570, +0.1535] |
| 512-2k | shipped calibration (reference) | 92 | 0.837 | 0.113 | 0.545 | 0.265 | +0.000 [+0.000, +0.000] | -0.1919 [-0.2356, -0.1033] | -0.2440 [-0.3197, -0.1704] |
| 2k-8k | decider_chat | 463 | 0.790 | 0.152 | 0.738 | 0.369 | baseline | baseline | baseline |
| 2k-8k | header | 463 | 0.771 | 0.177 | 0.862 | 0.406 | -0.019 [-0.045, +0.006] | +0.0248 [-0.0028, +0.0471] | +0.1240 [+0.0489, +0.2033] |
| 2k-8k | question_first | 463 | 0.758 | 0.155 | 0.840 | 0.421 | -0.032 [-0.065, -0.002] | +0.0028 [-0.0228, +0.0394] | +0.1023 [+0.0186, +0.1910] |
| 2k-8k | shipped calibration (reference) | 463 | 0.790 | 0.152 | 0.738 | 0.369 | +0.000 [+0.000, +0.000] | +0.0001 [+0.0000, +0.0002] | -0.0001 [-0.0002, +0.0000] |

| slice | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| long | decider_chat | 674 | 0.804 | 0.146 | 0.665 | 0.345 | baseline | baseline | baseline |
| long | header | 674 | 0.791 | 0.161 | 0.751 | 0.369 | -0.013 [-0.036, +0.007] | +0.0145 [-0.0090, +0.0355] | +0.0861 [+0.0317, +0.1437] |
| long | question_first | 674 | 0.782 | 0.154 | 0.741 | 0.387 | -0.022 [-0.046, +0.001] | +0.0072 [-0.0155, +0.0356] | +0.0760 [+0.0142, +0.1375] |
| long | shipped calibration (reference) | 674 | 0.810 | 0.110 | 0.621 | 0.320 | +0.006 [-0.001, +0.015] | -0.0360 [-0.0552, -0.0174] | -0.0440 [-0.0577, -0.0314] |
| rest | decider_chat | 2153 | 0.817 | 0.079 | 0.619 | 0.302 | baseline | baseline | baseline |
| rest | header | 2153 | 0.817 | 0.083 | 0.631 | 0.307 | -0.000 [-0.010, +0.008] | +0.0040 [-0.0085, +0.0167] | +0.0117 [-0.0038, +0.0278] |
| rest | question_first | 2153 | 0.798 | 0.105 | 0.664 | 0.324 | -0.019 [-0.032, -0.006] | +0.0261 [+0.0075, +0.0390] | +0.0444 [+0.0196, +0.0703] |
| rest | shipped calibration (reference) | 2153 | 0.818 | 0.064 | 0.642 | 0.296 | +0.000 [-0.001, +0.003] | -0.0144 [-0.0311, +0.0032] | +0.0224 [-0.0009, +0.0448] |

### Bucket winners (auto-switch needs a different winner with an accuracy CI clear of zero)

Baseline: decider_chat (the verdict's layout, or the default when it stays), on both splits.

| grouping | bucket | winner | accuracy | Δ accuracy vs decider_chat | auto-switch |
|---|---|---|---|---|---|
| length | <512 | decider_chat | 0.818 | same layout | no |
| length | 512-2k | decider_chat | 0.837 | same layout | no |
| length | 2k-8k | decider_chat | 0.790 | same layout | no |
| slice | long | decider_chat | 0.804 | same layout | no |
| slice | rest | decider_chat | 0.817 | same layout | no |
