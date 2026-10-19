# qwen3.8-27b R3 option-order policies: image dev

## Provenance

- timestamp: 2026-10-19T182347Z
- commit: b953b23-dirty
- profile: qwen3.8-27b
- collects: ['/home/welb/devspace/jev-brain/.cache/vision-collect/qwen3.8-27b/r4-decider/dev.jsonl.gz', '/home/welb/devspace/jev-brain/.cache/vision-collect/qwen3.8-27b/r4-decider-cyclic4/dev.jsonl.gz']
- text fit: /home/welb/devspace/jev-brain/docs/results/archive/2026-10-19T144419Z-r4-orders-text-decider_chat-qwen3.8-27b/summary.json
- arms dir: .cache/r4/arms/orders-decider_chat-qwen3.8-27b
- gate T (choice): 1.4961189013294809

## Notes

- Each arm uses its text fit on text calib (choice T, or tn-prob's α + β ln n); gates read the identity read at the shipped choice T.
- A half policy without a text fit of its own uses the reversed policy's (ruling R3).
- Orders: half = cyclic:2's second order; aleria adds cyclic:4's other shifts; shifts are round(i·n/k) (R6).
- xfit arms: 2-fold group cross-fit on image dev (vision_offline.fold), a reference only; a fold under 30 questions keeps the text fit.
- qwen3.8-27b pads its prefix (prefix_pad front): reads were padded for one order, so two-order arms are not exactly live-equivalent (docs/background/vision-experiments.md §3).

## Arms (1462 rows, Δ vs identity)

Index, CIs, ECE and NLL come from vision_compare (summary.md beside this file): paired bootstrap over image groups. Extra suffix tokens: the suffixes of every read after the first. Reports; the owner picks.

| arm | mean reads | share paying | extra suffix tokens | mean input tokens | index | Δ index [95% CI] | ECE | NLL | fit (choice) |
|---|---|---|---|---|---|---|---|---|---|
| identity | 1.000 | 0.000 | 0.0 | 1070 | 72.45 | baseline | 0.1060 | 0.6604 | T 1.496 |
| always reversed/mean-prob | 2.000 | 1.000 | 93.8 | 1163 | 73.07 | +0.63 [-1.33, +2.61] | 0.1312 | 0.6800 | T 1.421 |
| always reversed/mean-logprob | 2.000 | 1.000 | 93.8 | 1163 | 73.02 | +0.57 [-1.41, +2.56] | 0.1324 | 0.6786 | T 1.514 |
| always reversed/tn-prob | 2.000 | 1.000 | 93.8 | 1163 | 73.12 | +0.67 [-1.31, +2.65] | 0.1497 | 0.6965 | α 1.634, β -0.068 |
| cyclic:2/mean-prob | 2.000 | 1.000 | 93.8 | 1163 | 73.07 | +0.63 [-1.54, +2.73] | 0.1300 | 0.6745 | T 1.428 |
| cyclic:2/mean-logprob | 2.000 | 1.000 | 93.8 | 1163 | 72.94 | +0.49 [-1.62, +2.54] | 0.1323 | 0.6760 | T 1.526 |
| cyclic:2/tn-prob | 2.000 | 1.000 | 93.8 | 1163 | 73.13 | +0.68 [-1.46, +2.76] | 0.1479 | 0.6917 | α 1.647, β -0.069 |
| cyclic:4/mean-prob | 3.191 | 1.000 | 239.7 | 1309 | 73.55 | +1.10 [-1.06, +3.31] | 0.1387 | 0.6817 | T 1.385 |
| cyclic:4/mean-logprob | 3.191 | 1.000 | 239.7 | 1309 | 73.41 | +0.97 [-1.24, +3.19] | 0.1390 | 0.6824 | T 1.512 |
| cyclic:4/tn-prob | 3.191 | 1.000 | 239.7 | 1309 | 73.55 | +1.10 [-1.06, +3.31] | 0.1561 | 0.6985 | α 1.591, β -0.065 |
| top_p 0.5 reversed/mean-prob | 1.243 | 0.243 | 37.9 | 1108 | 73.56 | +1.11 [-0.16, +2.40] | 0.1122 | 0.6647 | T 1.477 |
| top_p 0.5 reversed/mean-logprob | 1.243 | 0.243 | 37.9 | 1108 | 73.53 | +1.09 [-0.22, +2.38] | 0.1102 | 0.6616 | T 1.486 |
| top_p 0.5 reversed/tn-prob | 1.243 | 0.243 | 37.9 | 1108 | 73.56 | +1.11 [-0.16, +2.40] | 0.1318 | 0.6825 | α 1.730, β -0.080 |
| top_p 0.6 reversed/mean-prob | 1.387 | 0.387 | 51.5 | 1121 | 73.29 | +0.84 [-1.08, +2.77] | 0.1116 | 0.6641 | T 1.463 |
| top_p 0.6 reversed/mean-logprob | 1.387 | 0.387 | 51.5 | 1121 | 73.19 | +0.74 [-1.21, +2.68] | 0.1092 | 0.6611 | T 1.484 |
| top_p 0.6 reversed/tn-prob | 1.387 | 0.387 | 51.5 | 1121 | 73.29 | +0.84 [-1.08, +2.77] | 0.1286 | 0.6798 | α 1.684, β -0.070 |
| top_p 0.7 reversed/mean-prob | 1.498 | 0.498 | 59.4 | 1129 | 73.12 | +0.67 [-1.31, +2.65] | 0.1138 | 0.6656 | T 1.462 |
| top_p 0.7 reversed/mean-logprob | 1.498 | 0.498 | 59.4 | 1129 | 73.02 | +0.57 [-1.41, +2.56] | 0.1113 | 0.6624 | T 1.489 |
| top_p 0.7 reversed/tn-prob | 1.498 | 0.498 | 59.4 | 1129 | 73.12 | +0.67 [-1.31, +2.65] | 0.1304 | 0.6812 | α 1.682, β -0.069 |
| top_p 0.8 reversed/mean-prob | 1.626 | 0.626 | 69.7 | 1139 | 73.12 | +0.67 [-1.31, +2.65] | 0.1184 | 0.6686 | T 1.460 |
| top_p 0.8 reversed/mean-logprob | 1.626 | 0.626 | 69.7 | 1139 | 73.02 | +0.57 [-1.41, +2.56] | 0.1152 | 0.6647 | T 1.491 |
| top_p 0.8 reversed/tn-prob | 1.626 | 0.626 | 69.7 | 1139 | 73.12 | +0.67 [-1.31, +2.65] | 0.1365 | 0.6860 | α 1.704, β -0.078 |
| top_p 0.9 reversed/mean-prob | 1.825 | 0.825 | 82.8 | 1152 | 73.12 | +0.67 [-1.31, +2.65] | 0.1287 | 0.6790 | T 1.459 |
| top_p 0.9 reversed/mean-logprob | 1.825 | 0.825 | 82.8 | 1152 | 73.02 | +0.57 [-1.41, +2.56] | 0.1252 | 0.6742 | T 1.505 |
| top_p 0.9 reversed/tn-prob | 1.825 | 0.825 | 82.8 | 1152 | 73.12 | +0.67 [-1.31, +2.65] | 0.1457 | 0.6959 | α 1.693, β -0.074 |
| min_n 3 reversed/mean-prob | 1.631 | 0.631 | 75.2 | 1145 | 73.56 | +1.11 [-0.36, +2.57] | 0.1231 | 0.6727 | T 1.421 |
| min_n 3 reversed/mean-logprob | 1.631 | 0.631 | 75.2 | 1145 | 73.50 | +1.06 [-0.42, +2.54] | 0.1254 | 0.6729 | T 1.514 |
| min_n 3 reversed/tn-prob | 1.631 | 0.631 | 75.2 | 1145 | 73.60 | +1.16 [-0.32, +2.61] | 0.1403 | 0.6883 | α 1.634, β -0.068 |
| min_n 4 reversed/mean-prob | 1.560 | 0.560 | 70.7 | 1140 | 73.80 | +1.36 [+0.01, +2.70] | 0.1221 | 0.6698 | T 1.423 |
| min_n 4 reversed/mean-logprob | 1.560 | 0.560 | 70.7 | 1140 | 73.75 | +1.30 [-0.07, +2.68] | 0.1255 | 0.6708 | T 1.515 |
| min_n 4 reversed/tn-prob | 1.560 | 0.560 | 70.7 | 1140 | 73.85 | +1.40 [+0.04, +2.75] | 0.1407 | 0.6863 | α 1.647, β -0.071 |
| min_n 5 reversed/mean-prob | 1.185 | 0.185 | 34.7 | 1104 | 72.76 | +0.31 [-0.10, +0.70] | 0.1039 | 0.6584 | T 1.423 |
| min_n 5 reversed/mean-logprob | 1.185 | 0.185 | 34.7 | 1104 | 72.82 | +0.38 [-0.11, +0.83] | 0.1153 | 0.6658 | T 1.515 |
| min_n 5 reversed/tn-prob | 1.185 | 0.185 | 34.7 | 1104 | 72.80 | +0.35 [-0.06, +0.75] | 0.1238 | 0.6741 | α 1.647, β -0.071 |
| min_n 6 reversed/mean-prob | 1.179 | 0.179 | 34.3 | 1104 | 72.88 | +0.43 [+0.12, +0.77] | 0.1050 | 0.6584 | T 1.426 |
| min_n 6 reversed/mean-logprob | 1.179 | 0.179 | 34.3 | 1104 | 72.95 | +0.50 [+0.10, +0.90] | 0.1161 | 0.6661 | T 1.518 |
| min_n 6 reversed/tn-prob | 1.179 | 0.179 | 34.3 | 1104 | 72.92 | +0.48 [+0.16, +0.82] | 0.1254 | 0.6749 | α 1.661, β -0.075 |
| min_n 8 reversed/mean-prob | 1.077 | 0.077 | 7.0 | 1077 | 72.38 | -0.07 [-0.18, +0.04] | 0.0964 | 0.6559 | T 1.425 |
| min_n 8 reversed/mean-logprob | 1.077 | 0.077 | 7.0 | 1077 | 72.40 | -0.04 [-0.17, +0.07] | 0.1095 | 0.6658 | T 1.516 |
| min_n 8 reversed/tn-prob | 1.077 | 0.077 | 7.0 | 1077 | 72.38 | -0.07 [-0.18, +0.04] | 0.1173 | 0.6718 | α 1.656, β -0.073 |
| aleria half/mean-prob | 2.330 | 1.000 | 148.5 | 1218 | 73.43 | +0.98 [-1.04, +3.04] | 0.1343 | 0.6767 | T 1.422 |
| aleria half/mean-logprob | 2.330 | 1.000 | 148.5 | 1218 | 73.36 | +0.91 [-1.15, +2.99] | 0.1358 | 0.6773 | T 1.520 |
| aleria half/tn-prob | 2.330 | 1.000 | 148.5 | 1218 | 73.43 | +0.98 [-1.04, +3.04] | 0.1541 | 0.6948 | α 1.651, β -0.073 |
| always half/mean-prob | 2.000 | 1.000 | 93.8 | 1163 | 73.07 | +0.63 [-1.54, +2.73] | 0.1286 | 0.6735 | T 1.421 (from always reversed/mean-prob) |
| always half/mean-logprob | 2.000 | 1.000 | 93.8 | 1163 | 72.94 | +0.49 [-1.62, +2.54] | 0.1303 | 0.6743 | T 1.514 (from always reversed/mean-logprob) |
| always half/tn-prob | 2.000 | 1.000 | 93.8 | 1163 | 73.13 | +0.68 [-1.46, +2.76] | 0.1461 | 0.6902 | α 1.634, β -0.068 (from always reversed/tn-prob) |
| top_p 0.5 half/mean-prob | 1.243 | 0.243 | 37.9 | 1108 | 72.90 | +0.46 [-0.90, +1.80] | 0.1051 | 0.6615 | T 1.477 (from top_p 0.5 reversed/mean-prob) |
| top_p 0.5 half/mean-logprob | 1.243 | 0.243 | 37.9 | 1108 | 73.05 | +0.60 [-0.73, +1.93] | 0.1051 | 0.6591 | T 1.486 (from top_p 0.5 reversed/mean-logprob) |
| top_p 0.5 half/tn-prob | 1.243 | 0.243 | 37.9 | 1108 | 72.90 | +0.46 [-0.90, +1.80] | 0.1262 | 0.6794 | α 1.730, β -0.080 (from top_p 0.5 reversed/tn-prob) |
| top_p 0.6 half/mean-prob | 1.387 | 0.387 | 51.5 | 1121 | 73.10 | +0.65 [-1.44, +2.69] | 0.1071 | 0.6604 | T 1.463 (from top_p 0.6 reversed/mean-prob) |
| top_p 0.6 half/mean-logprob | 1.387 | 0.387 | 51.5 | 1121 | 73.01 | +0.56 [-1.50, +2.58] | 0.1061 | 0.6584 | T 1.484 (from top_p 0.6 reversed/mean-logprob) |
| top_p 0.6 half/tn-prob | 1.387 | 0.387 | 51.5 | 1121 | 73.20 | +0.75 [-1.32, +2.78] | 0.1264 | 0.6763 | α 1.684, β -0.070 (from top_p 0.6 reversed/tn-prob) |
| top_p 0.7 half/mean-prob | 1.498 | 0.498 | 59.4 | 1129 | 73.03 | +0.58 [-1.58, +2.67] | 0.1102 | 0.6628 | T 1.462 (from top_p 0.7 reversed/mean-prob) |
| top_p 0.7 half/mean-logprob | 1.498 | 0.498 | 59.4 | 1129 | 72.94 | +0.49 [-1.62, +2.54] | 0.1093 | 0.6606 | T 1.489 (from top_p 0.7 reversed/mean-logprob) |
| top_p 0.7 half/tn-prob | 1.498 | 0.498 | 59.4 | 1129 | 73.13 | +0.68 [-1.46, +2.76] | 0.1291 | 0.6786 | α 1.682, β -0.069 (from top_p 0.7 reversed/tn-prob) |
| top_p 0.8 half/mean-prob | 1.626 | 0.626 | 69.7 | 1139 | 73.03 | +0.58 [-1.58, +2.67] | 0.1148 | 0.6643 | T 1.460 (from top_p 0.8 reversed/mean-prob) |
| top_p 0.8 half/mean-logprob | 1.626 | 0.626 | 69.7 | 1139 | 72.94 | +0.49 [-1.62, +2.54] | 0.1129 | 0.6616 | T 1.491 (from top_p 0.8 reversed/mean-logprob) |
| top_p 0.8 half/tn-prob | 1.626 | 0.626 | 69.7 | 1139 | 73.13 | +0.68 [-1.46, +2.76] | 0.1352 | 0.6820 | α 1.704, β -0.078 (from top_p 0.8 reversed/tn-prob) |
| top_p 0.9 half/mean-prob | 1.825 | 0.825 | 82.8 | 1152 | 73.03 | +0.58 [-1.58, +2.67] | 0.1247 | 0.6729 | T 1.459 (from top_p 0.9 reversed/mean-prob) |
| top_p 0.9 half/mean-logprob | 1.825 | 0.825 | 82.8 | 1152 | 72.94 | +0.49 [-1.62, +2.54] | 0.1228 | 0.6700 | T 1.505 (from top_p 0.9 reversed/mean-logprob) |
| top_p 0.9 half/tn-prob | 1.825 | 0.825 | 82.8 | 1152 | 73.13 | +0.68 [-1.46, +2.76] | 0.1440 | 0.6900 | α 1.693, β -0.074 (from top_p 0.9 reversed/tn-prob) |
| min_n 3 half/mean-prob | 1.631 | 0.631 | 75.2 | 1145 | 73.56 | +1.11 [-0.53, +2.76] | 0.1203 | 0.6662 | T 1.421 (from min_n 3 reversed/mean-prob) |
| min_n 3 half/mean-logprob | 1.631 | 0.631 | 75.2 | 1145 | 73.43 | +0.98 [-0.64, +2.58] | 0.1233 | 0.6686 | T 1.514 (from min_n 3 reversed/mean-logprob) |
| min_n 3 half/tn-prob | 1.631 | 0.631 | 75.2 | 1145 | 73.62 | +1.17 [-0.47, +2.77] | 0.1367 | 0.6821 | α 1.634, β -0.068 (from min_n 3 reversed/tn-prob) |
| min_n 4 half/mean-prob | 1.560 | 0.560 | 70.7 | 1140 | 73.81 | +1.36 [-0.17, +2.87] | 0.1198 | 0.6633 | T 1.423 (from min_n 4 reversed/mean-prob) |
| min_n 4 half/mean-logprob | 1.560 | 0.560 | 70.7 | 1140 | 73.67 | +1.23 [-0.26, +2.70] | 0.1235 | 0.6667 | T 1.515 (from min_n 4 reversed/mean-logprob) |
| min_n 4 half/tn-prob | 1.560 | 0.560 | 70.7 | 1140 | 73.86 | +1.42 [-0.10, +2.91] | 0.1371 | 0.6800 | α 1.647, β -0.071 (from min_n 4 reversed/tn-prob) |
| min_n 5 half/mean-prob | 1.185 | 0.185 | 34.7 | 1104 | 72.86 | +0.42 [-0.04, +0.90] | 0.1020 | 0.6536 | T 1.423 (from min_n 5 reversed/mean-prob) |
| min_n 5 half/mean-logprob | 1.185 | 0.185 | 34.7 | 1104 | 72.89 | +0.44 [-0.02, +0.92] | 0.1135 | 0.6630 | T 1.515 (from min_n 5 reversed/mean-logprob) |
| min_n 5 half/tn-prob | 1.185 | 0.185 | 34.7 | 1104 | 72.82 | +0.37 [-0.08, +0.85] | 0.1199 | 0.6696 | α 1.647, β -0.071 (from min_n 5 reversed/tn-prob) |
| min_n 6 half/mean-prob | 1.179 | 0.179 | 34.3 | 1104 | 72.86 | +0.42 [-0.04, +0.90] | 0.1020 | 0.6537 | T 1.426 (from min_n 6 reversed/mean-prob) |
| min_n 6 half/mean-logprob | 1.179 | 0.179 | 34.3 | 1104 | 72.89 | +0.44 [-0.02, +0.92] | 0.1134 | 0.6632 | T 1.518 (from min_n 6 reversed/mean-logprob) |
| min_n 6 half/tn-prob | 1.179 | 0.179 | 34.3 | 1104 | 72.82 | +0.37 [-0.08, +0.85] | 0.1210 | 0.6705 | α 1.661, β -0.075 (from min_n 6 reversed/tn-prob) |
| min_n 8 half/mean-prob | 1.077 | 0.077 | 7.0 | 1077 | 72.45 | +0.00 [-0.11, +0.11] | 0.0968 | 0.6513 | T 1.425 (from min_n 8 reversed/mean-prob) |
| min_n 8 half/mean-logprob | 1.077 | 0.077 | 7.0 | 1077 | 72.47 | +0.02 [-0.09, +0.13] | 0.1110 | 0.6614 | T 1.516 (from min_n 8 reversed/mean-logprob) |
| min_n 8 half/tn-prob | 1.077 | 0.077 | 7.0 | 1077 | 72.45 | +0.00 [-0.11, +0.11] | 0.1184 | 0.6675 | α 1.656, β -0.073 (from min_n 8 reversed/tn-prob) |
| xfit always reversed/mean-prob | 2.000 | 1.000 | 93.8 | 1163 | 73.15 | +0.70 [-1.24, +2.68] | 0.0451 | 0.6294 | fold 0: T 0.820; fold 1: T 0.851 |
| xfit always reversed/mean-logprob | 2.000 | 1.000 | 93.8 | 1163 | 73.02 | +0.57 [-1.41, +2.56] | 0.0317 | 0.6142 | fold 0: T 0.841; fold 1: T 0.872 |
| xfit always reversed/tn-prob | 2.000 | 1.000 | 93.8 | 1163 | 73.20 | +0.75 [-1.20, +2.72] | 0.0437 | 0.6224 | fold 0: α 0.506, β +0.221; fold 1: α 0.466, β +0.274 |
| xfit always half/mean-prob | 2.000 | 1.000 | 93.8 | 1163 | 72.90 | +0.46 [-1.68, +2.54] | 0.0449 | 0.6175 | fold 0: T 0.816; fold 1: T 0.792 |
| xfit always half/mean-logprob | 2.000 | 1.000 | 93.8 | 1163 | 72.94 | +0.49 [-1.62, +2.54] | 0.0359 | 0.6082 | fold 0: T 0.849; fold 1: T 0.849 |
| xfit always half/tn-prob | 2.000 | 1.000 | 93.8 | 1163 | 72.90 | +0.46 [-1.68, +2.54] | 0.0378 | 0.6129 | fold 0: α 0.510, β +0.217; fold 1: α 0.548, β +0.175 |

## Skipped

- cyclic:3/mean-prob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
- cyclic:3/mean-logprob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
- cyclic:3/tn-prob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
