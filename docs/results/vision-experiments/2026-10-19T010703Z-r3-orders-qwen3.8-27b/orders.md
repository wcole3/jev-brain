# qwen3.8-27b R3 option-order policies: image dev

## Provenance

- timestamp: 2026-10-19T010703Z
- commit: 07cdb4a-dirty
- profile: qwen3.8-27b
- collects: ['/home/welb/devspace/jev-brain/.cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz', '/home/welb/devspace/jev-brain/.cache/vision-collect/qwen3.8-27b/r3-cyclic4/dev.jsonl.gz']
- text fit: /home/welb/devspace/jev-brain/docs/results/archive/2026-10-18T023336Z-r3-orders-text-qwen3.8-27b/summary.json
- arms dir: .cache/vision-orders/qwen3.8-27b/cyclic4
- gate T (choice): 1.535520473719803

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
| identity | 1.000 | 0.000 | 0.0 | 1117 | 73.31 | baseline | 0.0424 | 0.6029 | T 1.536 |
| always reversed/mean-prob | 2.000 | 1.000 | 93.8 | 1211 | 74.07 | +0.76 [-1.11, +2.60] | 0.0702 | 0.6157 | T 1.457 |
| always reversed/mean-logprob | 2.000 | 1.000 | 93.8 | 1211 | 74.56 | +1.26 [-0.65, +3.14] | 0.0723 | 0.6100 | T 1.553 |
| always reversed/tn-prob | 2.000 | 1.000 | 93.8 | 1211 | 74.07 | +0.76 [-1.11, +2.60] | 0.0798 | 0.6215 | α 1.589, β -0.041 |
| cyclic:2/mean-prob | 2.000 | 1.000 | 93.8 | 1211 | 73.69 | +0.38 [-1.59, +2.39] | 0.0671 | 0.6098 | T 1.462 |
| cyclic:2/mean-logprob | 2.000 | 1.000 | 93.8 | 1211 | 73.48 | +0.18 [-1.83, +2.18] | 0.0634 | 0.6065 | T 1.550 |
| cyclic:2/tn-prob | 2.000 | 1.000 | 93.8 | 1211 | 73.69 | +0.38 [-1.59, +2.39] | 0.0776 | 0.6162 | α 1.599, β -0.043 |
| cyclic:4/mean-prob | 3.191 | 1.000 | 239.7 | 1357 | 73.99 | +0.68 [-1.34, +2.73] | 0.0807 | 0.6202 | T 1.423 |
| cyclic:4/mean-logprob | 3.191 | 1.000 | 239.7 | 1357 | 73.88 | +0.57 [-1.45, +2.62] | 0.0732 | 0.6140 | T 1.543 |
| cyclic:4/tn-prob | 3.191 | 1.000 | 239.7 | 1357 | 73.99 | +0.68 [-1.34, +2.73] | 0.0901 | 0.6269 | α 1.561, β -0.043 |
| top_p 0.5 reversed/mean-prob | 1.202 | 0.202 | 34.6 | 1152 | 73.98 | +0.68 [-0.57, +1.93] | 0.0493 | 0.6090 | T 1.525 |
| top_p 0.5 reversed/mean-logprob | 1.202 | 0.202 | 34.6 | 1152 | 74.26 | +0.95 [-0.26, +2.20] | 0.0506 | 0.6066 | T 1.535 |
| top_p 0.5 reversed/tn-prob | 1.202 | 0.202 | 34.6 | 1152 | 74.03 | +0.72 [-0.52, +1.98] | 0.0672 | 0.6163 | α 1.744, β -0.069 |
| top_p 0.6 reversed/mean-prob | 1.298 | 0.298 | 43.5 | 1160 | 74.16 | +0.85 [-0.90, +2.55] | 0.0505 | 0.6102 | T 1.508 |
| top_p 0.6 reversed/mean-logprob | 1.298 | 0.298 | 43.5 | 1160 | 74.55 | +1.25 [-0.52, +3.00] | 0.0528 | 0.6067 | T 1.527 |
| top_p 0.6 reversed/tn-prob | 1.298 | 0.298 | 43.5 | 1160 | 74.20 | +0.90 [-0.86, +2.61] | 0.0650 | 0.6158 | α 1.685, β -0.055 |
| top_p 0.7 reversed/mean-prob | 1.374 | 0.374 | 49.7 | 1167 | 73.97 | +0.66 [-1.20, +2.48] | 0.0530 | 0.6085 | T 1.509 |
| top_p 0.7 reversed/mean-logprob | 1.374 | 0.374 | 49.7 | 1167 | 74.36 | +1.05 [-0.84, +2.94] | 0.0550 | 0.6053 | T 1.534 |
| top_p 0.7 reversed/tn-prob | 1.374 | 0.374 | 49.7 | 1167 | 74.01 | +0.70 [-1.15, +2.53] | 0.0671 | 0.6142 | α 1.682, β -0.054 |
| top_p 0.8 reversed/mean-prob | 1.479 | 0.479 | 58.0 | 1175 | 74.07 | +0.76 [-1.11, +2.60] | 0.0572 | 0.6092 | T 1.499 |
| top_p 0.8 reversed/mean-logprob | 1.479 | 0.479 | 58.0 | 1175 | 74.56 | +1.26 [-0.65, +3.14] | 0.0592 | 0.6049 | T 1.533 |
| top_p 0.8 reversed/tn-prob | 1.479 | 0.479 | 58.0 | 1175 | 74.11 | +0.80 [-1.06, +2.65] | 0.0705 | 0.6150 | α 1.674, β -0.055 |
| top_p 0.9 reversed/mean-prob | 1.611 | 0.611 | 69.2 | 1186 | 74.07 | +0.76 [-1.11, +2.60] | 0.0618 | 0.6146 | T 1.490 |
| top_p 0.9 reversed/mean-logprob | 1.611 | 0.611 | 69.2 | 1186 | 74.56 | +1.26 [-0.65, +3.14] | 0.0630 | 0.6086 | T 1.540 |
| top_p 0.9 reversed/tn-prob | 1.611 | 0.611 | 69.2 | 1186 | 74.11 | +0.80 [-1.06, +2.65] | 0.0749 | 0.6205 | α 1.669, β -0.056 |
| min_n 3 reversed/mean-prob | 1.631 | 0.631 | 75.2 | 1192 | 74.60 | +1.30 [-0.25, +2.80] | 0.0681 | 0.6206 | T 1.457 |
| min_n 3 reversed/mean-logprob | 1.631 | 0.631 | 75.2 | 1192 | 75.10 | +1.79 [+0.21, +3.37] | 0.0706 | 0.6138 | T 1.553 |
| min_n 3 reversed/tn-prob | 1.631 | 0.631 | 75.2 | 1192 | 74.60 | +1.30 [-0.25, +2.80] | 0.0766 | 0.6250 | α 1.589, β -0.042 |
| min_n 4 reversed/mean-prob | 1.560 | 0.560 | 70.7 | 1188 | 74.73 | +1.42 [+0.08, +2.74] | 0.0662 | 0.6185 | T 1.459 |
| min_n 4 reversed/mean-logprob | 1.560 | 0.560 | 70.7 | 1188 | 75.35 | +2.04 [+0.67, +3.42] | 0.0700 | 0.6125 | T 1.552 |
| min_n 4 reversed/tn-prob | 1.560 | 0.560 | 70.7 | 1188 | 74.73 | +1.42 [+0.08, +2.74] | 0.0760 | 0.6231 | α 1.600, β -0.044 |
| min_n 5 reversed/mean-prob | 1.185 | 0.185 | 34.7 | 1152 | 73.47 | +0.16 [-0.37, +0.69] | 0.0433 | 0.6072 | T 1.460 |
| min_n 5 reversed/mean-logprob | 1.185 | 0.185 | 34.7 | 1152 | 73.65 | +0.34 [-0.21, +0.90] | 0.0533 | 0.6089 | T 1.553 |
| min_n 5 reversed/tn-prob | 1.185 | 0.185 | 34.7 | 1152 | 73.47 | +0.16 [-0.37, +0.69] | 0.0529 | 0.6111 | α 1.604, β -0.045 |
| min_n 6 reversed/mean-prob | 1.179 | 0.179 | 34.3 | 1151 | 73.59 | +0.28 [-0.18, +0.77] | 0.0440 | 0.6068 | T 1.464 |
| min_n 6 reversed/mean-logprob | 1.179 | 0.179 | 34.3 | 1151 | 73.77 | +0.46 [-0.03, +0.97] | 0.0540 | 0.6088 | T 1.556 |
| min_n 6 reversed/tn-prob | 1.179 | 0.179 | 34.3 | 1151 | 73.64 | +0.33 [-0.14, +0.82] | 0.0556 | 0.6113 | α 1.623, β -0.050 |
| min_n 8 reversed/mean-prob | 1.077 | 0.077 | 7.0 | 1124 | 73.29 | -0.02 [-0.15, +0.11] | 0.0398 | 0.6040 | T 1.462 |
| min_n 8 reversed/mean-logprob | 1.077 | 0.077 | 7.0 | 1124 | 73.29 | -0.02 [-0.15, +0.11] | 0.0498 | 0.6078 | T 1.554 |
| min_n 8 reversed/tn-prob | 1.077 | 0.077 | 7.0 | 1124 | 73.29 | -0.02 [-0.15, +0.11] | 0.0493 | 0.6081 | α 1.616, β -0.048 |
| aleria half/mean-prob | 2.331 | 1.000 | 145.3 | 1262 | 74.09 | +0.78 [-1.23, +2.81] | 0.0727 | 0.6105 | T 1.453 |
| aleria half/mean-logprob | 2.331 | 1.000 | 145.3 | 1262 | 74.00 | +0.69 [-1.32, +2.71] | 0.0709 | 0.6072 | T 1.548 |
| aleria half/tn-prob | 2.331 | 1.000 | 145.3 | 1262 | 74.09 | +0.78 [-1.23, +2.81] | 0.0851 | 0.6183 | α 1.616, β -0.051 |
| always half/mean-prob | 2.000 | 1.000 | 93.8 | 1211 | 73.69 | +0.38 [-1.59, +2.39] | 0.0664 | 0.6095 | T 1.457 (from always reversed/mean-prob) |
| always half/mean-logprob | 2.000 | 1.000 | 93.8 | 1211 | 73.48 | +0.18 [-1.83, +2.18] | 0.0643 | 0.6067 | T 1.553 (from always reversed/mean-logprob) |
| always half/tn-prob | 2.000 | 1.000 | 93.8 | 1211 | 73.69 | +0.38 [-1.59, +2.39] | 0.0765 | 0.6156 | α 1.589, β -0.041 (from always reversed/tn-prob) |
| top_p 0.5 half/mean-prob | 1.202 | 0.202 | 34.6 | 1152 | 73.43 | +0.12 [-1.21, +1.44] | 0.0454 | 0.6040 | T 1.525 (from top_p 0.5 reversed/mean-prob) |
| top_p 0.5 half/mean-logprob | 1.202 | 0.202 | 34.6 | 1152 | 73.39 | +0.08 [-1.27, +1.38] | 0.0449 | 0.6019 | T 1.535 (from top_p 0.5 reversed/mean-logprob) |
| top_p 0.5 half/tn-prob | 1.202 | 0.202 | 34.6 | 1152 | 73.43 | +0.12 [-1.21, +1.44] | 0.0612 | 0.6114 | α 1.744, β -0.069 (from top_p 0.5 reversed/tn-prob) |
| top_p 0.6 half/mean-prob | 1.298 | 0.298 | 43.5 | 1160 | 73.76 | +0.45 [-1.39, +2.28] | 0.0470 | 0.6047 | T 1.508 (from top_p 0.6 reversed/mean-prob) |
| top_p 0.6 half/mean-logprob | 1.298 | 0.298 | 43.5 | 1160 | 73.55 | +0.24 [-1.61, +2.09] | 0.0459 | 0.6023 | T 1.527 (from top_p 0.6 reversed/mean-logprob) |
| top_p 0.6 half/tn-prob | 1.298 | 0.298 | 43.5 | 1160 | 73.76 | +0.45 [-1.39, +2.28] | 0.0607 | 0.6105 | α 1.685, β -0.055 (from top_p 0.6 reversed/tn-prob) |
| top_p 0.7 half/mean-prob | 1.374 | 0.374 | 49.7 | 1167 | 73.69 | +0.38 [-1.59, +2.37] | 0.0505 | 0.6041 | T 1.509 (from top_p 0.7 reversed/mean-prob) |
| top_p 0.7 half/mean-logprob | 1.374 | 0.374 | 49.7 | 1167 | 73.48 | +0.18 [-1.82, +2.17] | 0.0494 | 0.6014 | T 1.534 (from top_p 0.7 reversed/mean-logprob) |
| top_p 0.7 half/tn-prob | 1.374 | 0.374 | 49.7 | 1167 | 73.69 | +0.38 [-1.59, +2.37] | 0.0630 | 0.6100 | α 1.682, β -0.054 (from top_p 0.7 reversed/tn-prob) |
| top_p 0.8 half/mean-prob | 1.479 | 0.479 | 58.0 | 1175 | 73.69 | +0.38 [-1.59, +2.39] | 0.0529 | 0.6047 | T 1.499 (from top_p 0.8 reversed/mean-prob) |
| top_p 0.8 half/mean-logprob | 1.479 | 0.479 | 58.0 | 1175 | 73.48 | +0.18 [-1.83, +2.18] | 0.0506 | 0.6016 | T 1.533 (from top_p 0.8 reversed/mean-logprob) |
| top_p 0.8 half/tn-prob | 1.479 | 0.479 | 58.0 | 1175 | 73.69 | +0.38 [-1.59, +2.39] | 0.0655 | 0.6106 | α 1.674, β -0.055 (from top_p 0.8 reversed/tn-prob) |
| top_p 0.9 half/mean-prob | 1.611 | 0.611 | 69.2 | 1186 | 73.69 | +0.38 [-1.59, +2.39] | 0.0576 | 0.6079 | T 1.490 (from top_p 0.9 reversed/mean-prob) |
| top_p 0.9 half/mean-logprob | 1.611 | 0.611 | 69.2 | 1186 | 73.48 | +0.18 [-1.83, +2.18] | 0.0544 | 0.6046 | T 1.540 (from top_p 0.9 reversed/mean-logprob) |
| top_p 0.9 half/tn-prob | 1.611 | 0.611 | 69.2 | 1186 | 73.69 | +0.38 [-1.59, +2.39] | 0.0697 | 0.6140 | α 1.669, β -0.056 (from top_p 0.9 reversed/tn-prob) |
| min_n 3 half/mean-prob | 1.631 | 0.631 | 75.2 | 1192 | 74.23 | +0.92 [-0.75, +2.64] | 0.0642 | 0.6144 | T 1.457 (from min_n 3 reversed/mean-prob) |
| min_n 3 half/mean-logprob | 1.631 | 0.631 | 75.2 | 1192 | 74.02 | +0.71 [-0.98, +2.47] | 0.0630 | 0.6104 | T 1.553 (from min_n 3 reversed/mean-logprob) |
| min_n 3 half/tn-prob | 1.631 | 0.631 | 75.2 | 1192 | 74.23 | +0.92 [-0.75, +2.64] | 0.0733 | 0.6190 | α 1.589, β -0.042 (from min_n 3 reversed/tn-prob) |
| min_n 4 half/mean-prob | 1.560 | 0.560 | 70.7 | 1188 | 74.35 | +1.04 [-0.45, +2.60] | 0.0621 | 0.6120 | T 1.459 (from min_n 4 reversed/mean-prob) |
| min_n 4 half/mean-logprob | 1.560 | 0.560 | 70.7 | 1188 | 74.14 | +0.84 [-0.69, +2.40] | 0.0618 | 0.6089 | T 1.552 (from min_n 4 reversed/mean-logprob) |
| min_n 4 half/tn-prob | 1.560 | 0.560 | 70.7 | 1188 | 74.35 | +1.04 [-0.45, +2.60] | 0.0725 | 0.6169 | α 1.600, β -0.044 (from min_n 4 reversed/tn-prob) |
| min_n 5 half/mean-prob | 1.185 | 0.185 | 34.7 | 1152 | 73.44 | +0.14 [-0.42, +0.68] | 0.0418 | 0.6008 | T 1.460 (from min_n 5 reversed/mean-prob) |
| min_n 5 half/mean-logprob | 1.185 | 0.185 | 34.7 | 1152 | 73.35 | +0.05 [-0.53, +0.60] | 0.0500 | 0.6045 | T 1.553 (from min_n 5 reversed/mean-logprob) |
| min_n 5 half/tn-prob | 1.185 | 0.185 | 34.7 | 1152 | 73.44 | +0.14 [-0.42, +0.68] | 0.0518 | 0.6050 | α 1.604, β -0.045 (from min_n 5 reversed/tn-prob) |
| min_n 6 half/mean-prob | 1.179 | 0.179 | 34.3 | 1151 | 73.57 | +0.26 [-0.22, +0.76] | 0.0428 | 0.6008 | T 1.464 (from min_n 6 reversed/mean-prob) |
| min_n 6 half/mean-logprob | 1.179 | 0.179 | 34.3 | 1151 | 73.48 | +0.17 [-0.34, +0.68] | 0.0507 | 0.6045 | T 1.556 (from min_n 6 reversed/mean-logprob) |
| min_n 6 half/tn-prob | 1.179 | 0.179 | 34.3 | 1151 | 73.57 | +0.26 [-0.22, +0.76] | 0.0544 | 0.6055 | α 1.623, β -0.050 (from min_n 6 reversed/tn-prob) |
| min_n 8 half/mean-prob | 1.077 | 0.077 | 7.0 | 1124 | 73.33 | +0.02 [-0.09, +0.13] | 0.0394 | 0.5989 | T 1.462 (from min_n 8 reversed/mean-prob) |
| min_n 8 half/mean-logprob | 1.077 | 0.077 | 7.0 | 1124 | 73.33 | +0.02 [-0.11, +0.15] | 0.0474 | 0.6033 | T 1.554 (from min_n 8 reversed/mean-logprob) |
| min_n 8 half/tn-prob | 1.077 | 0.077 | 7.0 | 1124 | 73.33 | +0.02 [-0.09, +0.13] | 0.0475 | 0.6032 | α 1.616, β -0.048 (from min_n 8 reversed/tn-prob) |
| xfit always reversed/mean-prob | 2.000 | 1.000 | 93.8 | 1211 | 74.07 | +0.76 [-1.11, +2.60] | 0.0442 | 0.6014 | fold 0: T 1.089; fold 1: T 1.122 |
| xfit always reversed/mean-logprob | 2.000 | 1.000 | 93.8 | 1211 | 74.56 | +1.26 [-0.65, +3.14] | 0.0351 | 0.5902 | fold 0: T 1.128; fold 1: T 1.152 |
| xfit always reversed/tn-prob | 2.000 | 1.000 | 93.8 | 1211 | 74.07 | +0.76 [-1.11, +2.60] | 0.0420 | 0.6008 | fold 0: α 0.964, β +0.088; fold 1: α 0.976, β +0.104 |
| xfit always half/mean-prob | 2.000 | 1.000 | 93.8 | 1211 | 73.69 | +0.38 [-1.59, +2.39] | 0.0303 | 0.5920 | fold 0: T 1.071; fold 1: T 1.065 |
| xfit always half/mean-logprob | 2.000 | 1.000 | 93.8 | 1211 | 73.48 | +0.18 [-1.83, +2.18] | 0.0262 | 0.5857 | fold 0: T 1.134; fold 1: T 1.124 |
| xfit always half/tn-prob | 2.000 | 1.000 | 93.8 | 1211 | 73.69 | +0.38 [-1.59, +2.39] | 0.0279 | 0.5921 | fold 0: α 0.988, β +0.060; fold 1: α 1.069, β -0.003 |

## Skipped

- cyclic:3/mean-prob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
- cyclic:3/mean-logprob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
- cyclic:3/tn-prob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
