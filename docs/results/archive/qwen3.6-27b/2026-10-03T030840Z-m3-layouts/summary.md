# qwen3.6-27b M3 layouts

## Provenance

- timestamp: 2026-10-03T030840Z
- repo commit: 8076f88
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- defaults: PROMPT_LAYOUT decider_chat, OPTION_ORDERS identity (profiles/qwen3.6-27b.env)
- orders: identity
- collect calib: .cache/collect/qwen3.6-27b/calib.jsonl.gz
- collect index-dev: .cache/collect/qwen3.6-27b/index-dev.jsonl.gz
- collect eval: .cache/collect/qwen3.6-27b/eval.jsonl.gz
- temperatures: each arm's T is an ungated fit on the calib split (b = 0), not the shipped calibration.json
- shipped calibration (reference): qwen3.6-27b/decider_chat/calibration.json: T choice 1.648, score 1.927, noul 1.386, b 0.000
- T decider_chat: choice 1.648, score 6.323, noul 1.386
- T header: choice 1.627, score 7.195, noul 1.284
- T question_first: choice 1.484, score 8.055, noul 1.207

## Recommendation

Default: decider_chat, each arm at its own calib-fitted T (b = 0).

- index-dev qualifies: header (Δ accuracy +0.020)
- eval qualifies: header (Δ accuracy +0.017)
- **verdict: header**
- read cost: the same reads per question for each layout (identity); latency measured live on the latency sample (latency.py)
- shipped calibration (reference): index-dev Δ accuracy +0.000 [+0.000, +0.000], Δ ECE +0.0000 [+0.0000, +0.0000]; eval Δ accuracy +0.000 [+0.000, +0.000], Δ ECE -0.0445 [-0.0567, -0.0296]

An arm qualifies on a split on an accuracy CI low > 0 or an ECE CI high < 0 over the default, without the other metric getting worse beyond its CI. The verdict is an arm that qualifies on both index-dev and eval: the cheapest by mean reads per question, then the larger mean Δ accuracy. Each arm is tested at 95%, so one of several can clear by chance; needing both splits guards against that. pride and the shipped-calibration row are never candidates. The owner makes the final call.

Auto-switch on both splits: none.

## index-dev

Every layout reads with identity, on the questions all of them answered. Δ is layout − decider_chat with a 95% paired-bootstrap CI. State length is the rendered state in the profile's tokens.

Questions answered: decider_chat 14684, header 14684, question_first 14684, of 14684 answered by any; compared on 14684.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | decider_chat | 14684 | 0.761 | 0.040 | 0.723 | 0.322 | baseline | baseline | baseline |
| all | header | 14684 | 0.780 | 0.045 | 0.672 | 0.299 | +0.020 [+0.015, +0.024] | +0.0049 [-0.0001, +0.0095] | -0.0508 [-0.0565, -0.0454] |
| all | question_first | 14684 | 0.751 | 0.046 | 0.751 | 0.340 | -0.010 [-0.014, -0.005] | +0.0056 [+0.0001, +0.0112] | +0.0287 [+0.0212, +0.0356] |
| all | shipped calibration (reference) | 14684 | 0.761 | 0.040 | 0.723 | 0.322 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | decider_chat | 14541 | 0.760 | 0.041 | 0.725 | 0.323 | baseline | baseline | baseline |
| choice | header | 14541 | 0.780 | 0.046 | 0.674 | 0.300 | +0.020 [+0.016, +0.024] | +0.0046 [-0.0002, +0.0092] | -0.0505 [-0.0560, -0.0450] |
| choice | question_first | 14541 | 0.750 | 0.046 | 0.755 | 0.341 | -0.010 [-0.015, -0.005] | +0.0052 [-0.0003, +0.0110] | +0.0305 [+0.0231, +0.0376] |
| choice | shipped calibration (reference) | 14541 | 0.760 | 0.041 | 0.725 | 0.323 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| noul | decider_chat | 143 | 0.846 | 0.097 | 0.506 | 0.270 | baseline | baseline | baseline |
| noul | header | 143 | 0.832 | 0.110 | 0.423 | 0.230 | -0.014 [-0.049, +0.014] | +0.0125 [-0.0400, +0.0547] | -0.0835 [-0.1306, -0.0416] |
| noul | question_first | 143 | 0.874 | 0.052 | 0.357 | 0.201 | +0.028 [-0.014, +0.077] | -0.0450 [-0.0886, +0.0072] | -0.1497 [-0.2290, -0.0795] |
| noul | shipped calibration (reference) | 143 | 0.846 | 0.097 | 0.506 | 0.270 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| state length | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| <512 | decider_chat | 11642 | 0.819 | 0.019 | 0.491 | 0.242 | baseline | baseline | baseline |
| <512 | header | 11642 | 0.842 | 0.015 | 0.445 | 0.213 | +0.024 [+0.019, +0.028] | -0.0042 [-0.0085, +0.0020] | -0.0454 [-0.0508, -0.0403] |
| <512 | question_first | 11642 | 0.811 | 0.019 | 0.522 | 0.253 | -0.008 [-0.013, -0.003] | -0.0003 [-0.0065, +0.0062] | +0.0314 [+0.0246, +0.0385] |
| <512 | shipped calibration (reference) | 11642 | 0.819 | 0.019 | 0.491 | 0.242 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| 512-2k | decider_chat | 2345 | 0.617 | 0.112 | 1.237 | 0.526 | baseline | baseline | baseline |
| 512-2k | header | 2345 | 0.616 | 0.125 | 1.199 | 0.532 | -0.002 [-0.013, +0.010] | +0.0125 [+0.0020, +0.0264] | -0.0384 [-0.0557, -0.0220] |
| 512-2k | question_first | 2345 | 0.601 | 0.144 | 1.271 | 0.565 | -0.016 [-0.029, -0.004] | +0.0322 [+0.0202, +0.0458] | +0.0335 [+0.0102, +0.0551] |
| 512-2k | shipped calibration (reference) | 2345 | 0.617 | 0.112 | 1.237 | 0.526 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| 2k-8k | decider_chat | 697 | 0.268 | 0.317 | 2.870 | 0.972 | baseline | baseline | baseline |
| 2k-8k | header | 697 | 0.296 | 0.335 | 2.688 | 0.956 | +0.027 [+0.010, +0.046] | +0.0187 [-0.0034, +0.0412] | -0.1826 [-0.2312, -0.1342] |
| 2k-8k | question_first | 697 | 0.255 | 0.362 | 2.837 | 1.029 | -0.013 [-0.033, +0.007] | +0.0451 [+0.0245, +0.0652] | -0.0331 [-0.1001, +0.0353] |
| 2k-8k | shipped calibration (reference) | 697 | 0.268 | 0.317 | 2.870 | 0.972 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| slice | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| long | decider_chat | 415 | 0.817 | 0.054 | 0.483 | 0.286 | baseline | baseline | baseline |
| long | header | 415 | 0.829 | 0.050 | 0.457 | 0.273 | +0.012 [-0.014, +0.039] | -0.0042 [-0.0427, +0.0332] | -0.0257 [-0.0538, +0.0046] |
| long | question_first | 415 | 0.766 | 0.030 | 0.522 | 0.325 | -0.051 [-0.084, -0.019] | -0.0239 [-0.0491, +0.0256] | +0.0392 [+0.0024, +0.0734] |
| long | shipped calibration (reference) | 415 | 0.817 | 0.054 | 0.483 | 0.286 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| rest | decider_chat | 14269 | 0.759 | 0.042 | 0.730 | 0.323 | baseline | baseline | baseline |
| rest | header | 14269 | 0.779 | 0.047 | 0.678 | 0.300 | +0.020 [+0.016, +0.024] | +0.0043 [-0.0004, +0.0088] | -0.0516 [-0.0572, -0.0462] |
| rest | question_first | 14269 | 0.751 | 0.047 | 0.758 | 0.340 | -0.008 [-0.013, -0.004] | +0.0048 [-0.0006, +0.0105] | +0.0284 [+0.0208, +0.0361] |
| rest | shipped calibration (reference) | 14269 | 0.759 | 0.042 | 0.730 | 0.323 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

### Bucket winners (auto-switch needs a different winner with an accuracy CI clear of zero)

Baseline: header (the verdict's layout, or the default when it stays), on both splits.

| grouping | bucket | winner | accuracy | Δ accuracy vs header | auto-switch |
|---|---|---|---|---|---|
| length | <512 | header | 0.842 | same layout | no |
| length | 512-2k | decider_chat | 0.617 | +0.002 [-0.010, +0.013] | no |
| length | 2k-8k | header | 0.296 | same layout | no |
| slice | long | header | 0.829 | same layout | no |
| slice | rest | header | 0.779 | same layout | no |

## eval

Every layout reads with identity, on the questions all of them answered. Δ is layout − decider_chat with a 95% paired-bootstrap CI. State length is the rendered state in the profile's tokens.

Questions answered: decider_chat 2827, header 2827, question_first 2827, of 2827 answered by any; compared on 2827.

| overall | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| all | decider_chat | 2827 | 0.789 | 0.067 | 0.583 | 0.310 | baseline | baseline | baseline |
| all | header | 2827 | 0.805 | 0.075 | 0.576 | 0.304 | +0.017 [+0.008, +0.025] | +0.0083 [-0.0060, +0.0186] | -0.0075 [-0.0156, +0.0004] |
| all | question_first | 2827 | 0.752 | 0.040 | 0.626 | 0.332 | -0.037 [-0.051, -0.023] | -0.0270 [-0.0404, -0.0082] | +0.0425 [+0.0257, +0.0586] |
| all | shipped calibration (reference) | 2827 | 0.789 | 0.022 | 0.580 | 0.299 | +0.000 [+0.000, +0.000] | -0.0445 [-0.0567, -0.0296] | -0.0033 [-0.0165, +0.0109] |

| type | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| choice | decider_chat | 1607 | 0.811 | 0.041 | 0.501 | 0.255 | baseline | baseline | baseline |
| choice | header | 1607 | 0.817 | 0.029 | 0.496 | 0.251 | +0.006 [-0.005, +0.018] | -0.0117 [-0.0278, +0.0040] | -0.0048 [-0.0148, +0.0052] |
| choice | question_first | 1607 | 0.811 | 0.025 | 0.529 | 0.265 | +0.001 [-0.015, +0.016] | -0.0153 [-0.0323, +0.0056] | +0.0284 [+0.0029, +0.0529] |
| choice | shipped calibration (reference) | 1607 | 0.811 | 0.041 | 0.501 | 0.255 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| noul | decider_chat | 666 | 0.880 | 0.038 | 0.286 | 0.173 | baseline | baseline | baseline |
| noul | header | 666 | 0.895 | 0.023 | 0.266 | 0.155 | +0.015 [-0.002, +0.032] | -0.0150 [-0.0378, +0.0108] | -0.0205 [-0.0428, +0.0017] |
| noul | question_first | 666 | 0.860 | 0.043 | 0.283 | 0.173 | -0.020 [-0.039, +0.000] | +0.0054 [-0.0214, +0.0328] | -0.0037 [-0.0288, +0.0209] |
| noul | shipped calibration (reference) | 666 | 0.880 | 0.038 | 0.286 | 0.173 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| score | decider_chat | 554 | 0.616 | 0.236 | 1.179 | 0.636 | baseline | baseline | baseline |
| score | header | 554 | 0.664 | 0.304 | 1.179 | 0.637 | +0.049 [+0.027, +0.072] | +0.0677 [+0.0355, +0.0976] | +0.0005 [-0.0059, +0.0066] |
| score | question_first | 554 | 0.448 | 0.167 | 1.318 | 0.716 | -0.168 [-0.211, -0.126] | -0.0692 [-0.1170, -0.0199] | +0.1387 [+0.1218, +0.1554] |
| score | shipped calibration (reference) | 554 | 0.616 | 0.122 | 1.162 | 0.581 | +0.000 [+0.000, +0.000] | -0.1147 [-0.1502, -0.0555] | -0.0169 [-0.0869, +0.0552] |

| state length | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| <512 | decider_chat | 2271 | 0.799 | 0.068 | 0.584 | 0.300 | baseline | baseline | baseline |
| <512 | header | 2271 | 0.820 | 0.076 | 0.575 | 0.291 | +0.021 [+0.012, +0.030] | +0.0076 [-0.0048, +0.0210] | -0.0094 [-0.0184, -0.0001] |
| <512 | question_first | 2271 | 0.761 | 0.050 | 0.614 | 0.311 | -0.038 [-0.052, -0.023] | -0.0180 [-0.0340, -0.0003] | +0.0294 [+0.0126, +0.0454] |
| <512 | shipped calibration (reference) | 2271 | 0.799 | 0.022 | 0.588 | 0.291 | +0.000 [+0.000, +0.000] | -0.0455 [-0.0578, -0.0250] | +0.0035 [-0.0140, +0.0214] |
| 512-2k | decider_chat | 83 | 0.783 | 0.279 | 0.811 | 0.446 | baseline | baseline | baseline |
| 512-2k | header | 83 | 0.819 | 0.314 | 0.802 | 0.441 | +0.036 [-0.024, +0.096] | +0.0351 [-0.0230, +0.1080] | -0.0084 [-0.0354, +0.0174] |
| 512-2k | question_first | 83 | 0.723 | 0.266 | 0.981 | 0.537 | -0.060 [-0.157, +0.036] | -0.0128 [-0.0934, +0.0978] | +0.1699 [+0.0920, +0.2639] |
| 512-2k | shipped calibration (reference) | 83 | 0.783 | 0.126 | 0.601 | 0.327 | +0.000 [+0.000, +0.000] | -0.1529 [-0.2104, -0.0561] | -0.2094 [-0.2751, -0.1468] |
| 2k-8k | decider_chat | 473 | 0.740 | 0.069 | 0.538 | 0.334 | baseline | baseline | baseline |
| 2k-8k | header | 473 | 0.734 | 0.058 | 0.540 | 0.344 | -0.006 [-0.034, +0.023] | -0.0118 [-0.0439, +0.0227] | +0.0022 [-0.0160, +0.0199] |
| 2k-8k | question_first | 473 | 0.710 | 0.077 | 0.621 | 0.395 | -0.030 [-0.066, +0.008] | +0.0077 [-0.0374, +0.0461] | +0.0828 [+0.0309, +0.1335] |
| 2k-8k | shipped calibration (reference) | 473 | 0.740 | 0.069 | 0.538 | 0.334 | +0.000 [+0.000, +0.000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |

| slice | arm | n | accuracy | ECE | NLL | Brier | Δ accuracy | Δ ECE | Δ NLL |
|---|---|---|---|---|---|---|---|---|---|
| long | decider_chat | 680 | 0.760 | 0.066 | 0.546 | 0.333 | baseline | baseline | baseline |
| long | header | 680 | 0.772 | 0.095 | 0.518 | 0.318 | +0.012 [-0.009, +0.032] | +0.0295 [-0.0073, +0.0516] | -0.0282 [-0.0456, -0.0122] |
| long | question_first | 680 | 0.751 | 0.063 | 0.573 | 0.354 | -0.009 [-0.038, +0.019] | -0.0020 [-0.0302, +0.0327] | +0.0274 [-0.0136, +0.0662] |
| long | shipped calibration (reference) | 680 | 0.760 | 0.051 | 0.514 | 0.316 | +0.000 [+0.000, +0.000] | -0.0142 [-0.0271, +0.0033] | -0.0312 [-0.0425, -0.0208] |
| rest | decider_chat | 2147 | 0.798 | 0.075 | 0.595 | 0.303 | baseline | baseline | baseline |
| rest | header | 2147 | 0.816 | 0.087 | 0.594 | 0.300 | +0.018 [+0.008, +0.028] | +0.0114 [-0.0019, +0.0241] | -0.0009 [-0.0103, +0.0086] |
| rest | question_first | 2147 | 0.752 | 0.050 | 0.642 | 0.325 | -0.046 [-0.062, -0.031] | -0.0248 [-0.0407, -0.0065] | +0.0472 [+0.0304, +0.0635] |
| rest | shipped calibration (reference) | 2147 | 0.798 | 0.024 | 0.600 | 0.294 | +0.000 [+0.000, +0.000] | -0.0517 [-0.0635, -0.0325] | +0.0055 [-0.0129, +0.0232] |

### Bucket winners (auto-switch needs a different winner with an accuracy CI clear of zero)

Baseline: header (the verdict's layout, or the default when it stays), on both splits.

| grouping | bucket | winner | accuracy | Δ accuracy vs header | auto-switch |
|---|---|---|---|---|---|
| length | <512 | header | 0.820 | same layout | no |
| length | 512-2k | header | 0.819 | same layout | no |
| length | 2k-8k | decider_chat | 0.740 | +0.006 [-0.023, +0.034] | no |
| slice | long | header | 0.772 | same layout | no |
| slice | rest | header | 0.816 | same layout | no |
