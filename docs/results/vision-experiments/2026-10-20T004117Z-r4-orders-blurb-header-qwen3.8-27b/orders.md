# qwen3.8-27b R3 option-order policies: image dev

## Provenance

- timestamp: 2026-10-20T004117Z
- commit: 438d4b5-dirty
- profile: qwen3.8-27b
- collects: ['/home/welb/devspace/jev-brain/.cache/vision-collect/qwen3.8-27b/r4-blurb-header/dev.jsonl.gz', '/home/welb/devspace/jev-brain/.cache/vision-collect/qwen3.8-27b/r4-blurb-header-cyclic4/dev.jsonl.gz']
- text fit: /home/welb/devspace/jev-brain/docs/results/archive/2026-10-20T002658Z-r4-orders-text-blurb-header-2k-qwen3.8-27b/summary.json
- arms dir: .cache/r4/arms/orders-blurb-header-qwen3.8-27b
- gate T (choice): 1.566456602123322

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
| identity | 1.000 | 0.000 | 0.0 | 1138 | 73.66 | baseline | 0.0631 | 0.6058 | T 1.566 |
| always reversed/mean-prob | 2.000 | 1.000 | 93.8 | 1232 | 74.11 | +0.46 [-1.26, +2.17] | 0.0810 | 0.6141 | T 1.506 |
| always reversed/mean-logprob | 2.000 | 1.000 | 93.8 | 1232 | 74.20 | +0.55 [-1.15, +2.23] | 0.0881 | 0.6151 | T 1.595 |
| always reversed/tn-prob | 2.000 | 1.000 | 93.8 | 1232 | 74.11 | +0.46 [-1.26, +2.17] | 0.0919 | 0.6228 | α 1.648, β -0.042 |
| cyclic:2/mean-prob | 2.000 | 1.000 | 93.8 | 1232 | 74.49 | +0.84 [-0.86, +2.58] | 0.0868 | 0.6091 | T 1.494 |
| cyclic:2/mean-logprob | 2.000 | 1.000 | 93.8 | 1232 | 74.58 | +0.92 [-0.79, +2.65] | 0.0943 | 0.6139 | T 1.613 |
| cyclic:2/tn-prob | 2.000 | 1.000 | 93.8 | 1232 | 74.45 | +0.79 [-0.92, +2.54] | 0.0959 | 0.6173 | α 1.625, β -0.039 |
| cyclic:4/mean-prob | 3.191 | 1.000 | 239.7 | 1378 | 74.77 | +1.11 [-0.66, +2.89] | 0.0947 | 0.6177 | T 1.463 |
| cyclic:4/mean-logprob | 3.191 | 1.000 | 239.7 | 1378 | 74.74 | +1.09 [-0.66, +2.82] | 0.1036 | 0.6222 | T 1.614 |
| cyclic:4/tn-prob | 3.191 | 1.000 | 239.7 | 1378 | 74.77 | +1.11 [-0.66, +2.89] | 0.1080 | 0.6279 | α 1.621, β -0.046 |
| top_p 0.5 reversed/mean-prob | 1.211 | 0.211 | 35.7 | 1174 | 73.16 | -0.49 [-1.62, +0.59] | 0.0631 | 0.6116 | T 1.563 |
| top_p 0.5 reversed/mean-logprob | 1.211 | 0.211 | 35.7 | 1174 | 73.38 | -0.28 [-1.43, +0.85] | 0.0655 | 0.6095 | T 1.566 |
| top_p 0.5 reversed/tn-prob | 1.211 | 0.211 | 35.7 | 1174 | 73.21 | -0.45 [-1.57, +0.63] | 0.0821 | 0.6233 | α 1.795, β -0.069 |
| top_p 0.6 reversed/mean-prob | 1.316 | 0.316 | 44.3 | 1182 | 73.85 | +0.19 [-1.50, +1.87] | 0.0671 | 0.6128 | T 1.559 |
| top_p 0.6 reversed/mean-logprob | 1.316 | 0.316 | 44.3 | 1182 | 73.94 | +0.28 [-1.40, +1.95] | 0.0692 | 0.6101 | T 1.566 |
| top_p 0.6 reversed/tn-prob | 1.316 | 0.316 | 44.3 | 1182 | 73.85 | +0.19 [-1.50, +1.87] | 0.0843 | 0.6228 | α 1.759, β -0.059 |
| top_p 0.7 reversed/mean-prob | 1.406 | 0.406 | 52.7 | 1191 | 74.11 | +0.46 [-1.26, +2.17] | 0.0743 | 0.6118 | T 1.564 |
| top_p 0.7 reversed/mean-logprob | 1.406 | 0.406 | 52.7 | 1191 | 74.20 | +0.55 [-1.15, +2.23] | 0.0750 | 0.6087 | T 1.574 |
| top_p 0.7 reversed/tn-prob | 1.406 | 0.406 | 52.7 | 1191 | 74.09 | +0.44 [-1.28, +2.14] | 0.0881 | 0.6210 | α 1.742, β -0.053 |
| top_p 0.8 reversed/mean-prob | 1.505 | 0.505 | 61.3 | 1199 | 74.11 | +0.46 [-1.26, +2.17] | 0.0772 | 0.6150 | T 1.564 |
| top_p 0.8 reversed/mean-logprob | 1.505 | 0.505 | 61.3 | 1199 | 74.20 | +0.55 [-1.15, +2.23] | 0.0780 | 0.6115 | T 1.584 |
| top_p 0.8 reversed/tn-prob | 1.505 | 0.505 | 61.3 | 1199 | 74.09 | +0.44 [-1.28, +2.14] | 0.0901 | 0.6239 | α 1.736, β -0.051 |
| top_p 0.9 reversed/mean-prob | 1.686 | 0.686 | 74.8 | 1213 | 74.11 | +0.46 [-1.26, +2.17] | 0.0816 | 0.6190 | T 1.565 |
| top_p 0.9 reversed/mean-logprob | 1.686 | 0.686 | 74.8 | 1213 | 74.20 | +0.55 [-1.15, +2.23] | 0.0824 | 0.6147 | T 1.593 |
| top_p 0.9 reversed/tn-prob | 1.686 | 0.686 | 74.8 | 1213 | 74.09 | +0.44 [-1.28, +2.14] | 0.0950 | 0.6282 | α 1.739, β -0.051 |
| min_n 3 reversed/mean-prob | 1.631 | 0.631 | 75.2 | 1213 | 73.67 | +0.01 [-1.29, +1.29] | 0.0713 | 0.6181 | T 1.506 |
| min_n 3 reversed/mean-logprob | 1.631 | 0.631 | 75.2 | 1213 | 73.76 | +0.10 [-1.20, +1.39] | 0.0813 | 0.6174 | T 1.596 |
| min_n 3 reversed/tn-prob | 1.631 | 0.631 | 75.2 | 1213 | 73.67 | +0.01 [-1.29, +1.29] | 0.0865 | 0.6255 | α 1.650, β -0.042 |
| min_n 4 reversed/mean-prob | 1.560 | 0.560 | 70.7 | 1209 | 74.03 | +0.38 [-0.85, +1.60] | 0.0728 | 0.6166 | T 1.508 |
| min_n 4 reversed/mean-logprob | 1.560 | 0.560 | 70.7 | 1209 | 74.13 | +0.47 [-0.78, +1.70] | 0.0827 | 0.6163 | T 1.597 |
| min_n 4 reversed/tn-prob | 1.560 | 0.560 | 70.7 | 1209 | 74.03 | +0.38 [-0.85, +1.60] | 0.0881 | 0.6244 | α 1.659, β -0.044 |
| min_n 5 reversed/mean-prob | 1.185 | 0.185 | 34.7 | 1173 | 73.77 | +0.11 [-0.36, +0.56] | 0.0688 | 0.6086 | T 1.508 |
| min_n 5 reversed/mean-logprob | 1.185 | 0.185 | 34.7 | 1173 | 73.98 | +0.32 [-0.19, +0.86] | 0.0759 | 0.6135 | T 1.597 |
| min_n 5 reversed/tn-prob | 1.185 | 0.185 | 34.7 | 1173 | 73.77 | +0.11 [-0.36, +0.56] | 0.0742 | 0.6158 | α 1.661, β -0.045 |
| min_n 6 reversed/mean-prob | 1.179 | 0.179 | 34.3 | 1172 | 73.77 | +0.11 [-0.36, +0.56] | 0.0688 | 0.6086 | T 1.508 |
| min_n 6 reversed/mean-logprob | 1.179 | 0.179 | 34.3 | 1172 | 73.98 | +0.32 [-0.19, +0.86] | 0.0759 | 0.6136 | T 1.598 |
| min_n 6 reversed/tn-prob | 1.179 | 0.179 | 34.3 | 1172 | 73.77 | +0.11 [-0.36, +0.56] | 0.0736 | 0.6158 | α 1.661, β -0.045 |
| min_n 8 reversed/mean-prob | 1.077 | 0.077 | 7.0 | 1145 | 73.72 | +0.07 [-0.06, +0.20] | 0.0671 | 0.6058 | T 1.508 |
| min_n 8 reversed/mean-logprob | 1.077 | 0.077 | 7.0 | 1145 | 73.72 | +0.07 [-0.07, +0.20] | 0.0686 | 0.6121 | T 1.597 |
| min_n 8 reversed/tn-prob | 1.077 | 0.077 | 7.0 | 1145 | 73.72 | +0.07 [-0.06, +0.20] | 0.0719 | 0.6127 | α 1.660, β -0.045 |
| aleria half/mean-prob | 2.304 | 1.000 | 145.2 | 1283 | 75.13 | +1.48 [-0.26, +3.20] | 0.0917 | 0.6096 | T 1.489 |
| aleria half/mean-logprob | 2.304 | 1.000 | 145.2 | 1283 | 75.13 | +1.48 [-0.23, +3.17] | 0.1012 | 0.6154 | T 1.618 |
| aleria half/tn-prob | 2.304 | 1.000 | 145.2 | 1283 | 75.13 | +1.48 [-0.26, +3.20] | 0.1027 | 0.6183 | α 1.627, β -0.041 |
| always half/mean-prob | 2.000 | 1.000 | 93.8 | 1232 | 74.49 | +0.84 [-0.86, +2.58] | 0.0888 | 0.6103 | T 1.506 (from always reversed/mean-prob) |
| always half/mean-logprob | 2.000 | 1.000 | 93.8 | 1232 | 74.58 | +0.92 [-0.79, +2.65] | 0.0925 | 0.6120 | T 1.595 (from always reversed/mean-logprob) |
| always half/tn-prob | 2.000 | 1.000 | 93.8 | 1232 | 74.45 | +0.79 [-0.92, +2.54] | 0.0982 | 0.6193 | α 1.648, β -0.042 (from always reversed/tn-prob) |
| top_p 0.5 half/mean-prob | 1.211 | 0.211 | 35.7 | 1174 | 73.79 | +0.13 [-0.95, +1.22] | 0.0699 | 0.6071 | T 1.563 (from top_p 0.5 reversed/mean-prob) |
| top_p 0.5 half/mean-logprob | 1.211 | 0.211 | 35.7 | 1174 | 73.96 | +0.30 [-0.78, +1.38] | 0.0707 | 0.6053 | T 1.566 (from top_p 0.5 reversed/mean-logprob) |
| top_p 0.5 half/tn-prob | 1.211 | 0.211 | 35.7 | 1174 | 73.79 | +0.13 [-0.95, +1.22] | 0.0883 | 0.6190 | α 1.795, β -0.069 (from top_p 0.5 reversed/tn-prob) |
| top_p 0.6 half/mean-prob | 1.316 | 0.316 | 44.3 | 1182 | 74.32 | +0.67 [-0.99, +2.35] | 0.0738 | 0.6080 | T 1.559 (from top_p 0.6 reversed/mean-prob) |
| top_p 0.6 half/mean-logprob | 1.316 | 0.316 | 44.3 | 1182 | 74.45 | +0.80 [-0.88, +2.47] | 0.0746 | 0.6054 | T 1.566 (from top_p 0.6 reversed/mean-logprob) |
| top_p 0.6 half/tn-prob | 1.316 | 0.316 | 44.3 | 1182 | 74.32 | +0.67 [-0.99, +2.35] | 0.0908 | 0.6183 | α 1.759, β -0.059 (from top_p 0.6 reversed/tn-prob) |
| top_p 0.7 half/mean-prob | 1.406 | 0.406 | 52.7 | 1191 | 74.55 | +0.89 [-0.80, +2.61] | 0.0803 | 0.6081 | T 1.564 (from top_p 0.7 reversed/mean-prob) |
| top_p 0.7 half/mean-logprob | 1.406 | 0.406 | 52.7 | 1191 | 74.68 | +1.02 [-0.68, +2.73] | 0.0796 | 0.6050 | T 1.574 (from top_p 0.7 reversed/mean-logprob) |
| top_p 0.7 half/tn-prob | 1.406 | 0.406 | 52.7 | 1191 | 74.55 | +0.89 [-0.80, +2.61] | 0.0946 | 0.6174 | α 1.742, β -0.053 (from top_p 0.7 reversed/tn-prob) |
| top_p 0.8 half/mean-prob | 1.505 | 0.505 | 61.3 | 1199 | 74.55 | +0.89 [-0.80, +2.61] | 0.0833 | 0.6121 | T 1.564 (from top_p 0.8 reversed/mean-prob) |
| top_p 0.8 half/mean-logprob | 1.505 | 0.505 | 61.3 | 1199 | 74.68 | +1.02 [-0.68, +2.73] | 0.0826 | 0.6085 | T 1.584 (from top_p 0.8 reversed/mean-logprob) |
| top_p 0.8 half/tn-prob | 1.505 | 0.505 | 61.3 | 1199 | 74.55 | +0.89 [-0.80, +2.61] | 0.0967 | 0.6211 | α 1.736, β -0.051 (from top_p 0.8 reversed/tn-prob) |
| top_p 0.9 half/mean-prob | 1.686 | 0.686 | 74.8 | 1213 | 74.45 | +0.79 [-0.92, +2.54] | 0.0880 | 0.6152 | T 1.565 (from top_p 0.9 reversed/mean-prob) |
| top_p 0.9 half/mean-logprob | 1.686 | 0.686 | 74.8 | 1213 | 74.58 | +0.92 [-0.79, +2.65] | 0.0866 | 0.6114 | T 1.593 (from top_p 0.9 reversed/mean-logprob) |
| top_p 0.9 half/tn-prob | 1.686 | 0.686 | 74.8 | 1213 | 74.45 | +0.79 [-0.92, +2.54] | 0.1015 | 0.6246 | α 1.739, β -0.051 (from top_p 0.9 reversed/tn-prob) |
| min_n 3 half/mean-prob | 1.631 | 0.631 | 75.2 | 1213 | 74.04 | +0.39 [-0.91, +1.69] | 0.0791 | 0.6143 | T 1.506 (from min_n 3 reversed/mean-prob) |
| min_n 3 half/mean-logprob | 1.631 | 0.631 | 75.2 | 1213 | 74.13 | +0.47 [-0.83, +1.75] | 0.0856 | 0.6143 | T 1.596 (from min_n 3 reversed/mean-logprob) |
| min_n 3 half/tn-prob | 1.631 | 0.631 | 75.2 | 1213 | 74.00 | +0.34 [-0.96, +1.64] | 0.0928 | 0.6220 | α 1.650, β -0.042 (from min_n 3 reversed/tn-prob) |
| min_n 4 half/mean-prob | 1.560 | 0.560 | 70.7 | 1209 | 74.17 | +0.51 [-0.70, +1.74] | 0.0795 | 0.6127 | T 1.508 (from min_n 4 reversed/mean-prob) |
| min_n 4 half/mean-logprob | 1.560 | 0.560 | 70.7 | 1209 | 74.25 | +0.59 [-0.61, +1.81] | 0.0858 | 0.6132 | T 1.597 (from min_n 4 reversed/mean-logprob) |
| min_n 4 half/tn-prob | 1.560 | 0.560 | 70.7 | 1209 | 74.12 | +0.47 [-0.75, +1.70] | 0.0932 | 0.6208 | α 1.659, β -0.044 (from min_n 4 reversed/tn-prob) |
| min_n 5 half/mean-prob | 1.185 | 0.185 | 34.7 | 1173 | 74.05 | +0.39 [-0.09, +0.90] | 0.0731 | 0.6032 | T 1.508 (from min_n 5 reversed/mean-prob) |
| min_n 5 half/mean-logprob | 1.185 | 0.185 | 34.7 | 1173 | 73.92 | +0.26 [-0.23, +0.77] | 0.0747 | 0.6085 | T 1.597 (from min_n 5 reversed/mean-logprob) |
| min_n 5 half/tn-prob | 1.185 | 0.185 | 34.7 | 1173 | 74.01 | +0.35 [-0.14, +0.85] | 0.0787 | 0.6106 | α 1.661, β -0.045 (from min_n 5 reversed/tn-prob) |
| min_n 6 half/mean-prob | 1.179 | 0.179 | 34.3 | 1172 | 74.05 | +0.39 [-0.09, +0.90] | 0.0727 | 0.6031 | T 1.508 (from min_n 6 reversed/mean-prob) |
| min_n 6 half/mean-logprob | 1.179 | 0.179 | 34.3 | 1172 | 73.92 | +0.26 [-0.23, +0.77] | 0.0746 | 0.6085 | T 1.598 (from min_n 6 reversed/mean-logprob) |
| min_n 6 half/tn-prob | 1.179 | 0.179 | 34.3 | 1172 | 74.01 | +0.35 [-0.14, +0.85] | 0.0784 | 0.6105 | α 1.661, β -0.045 (from min_n 6 reversed/tn-prob) |
| min_n 8 half/mean-prob | 1.077 | 0.077 | 7.0 | 1145 | 73.66 | +0.00 [-0.11, +0.11] | 0.0664 | 0.6022 | T 1.508 (from min_n 8 reversed/mean-prob) |
| min_n 8 half/mean-logprob | 1.077 | 0.077 | 7.0 | 1145 | 73.66 | +0.00 [-0.11, +0.11] | 0.0702 | 0.6081 | T 1.597 (from min_n 8 reversed/mean-logprob) |
| min_n 8 half/tn-prob | 1.077 | 0.077 | 7.0 | 1145 | 73.66 | +0.00 [-0.11, +0.11] | 0.0713 | 0.6093 | α 1.660, β -0.045 (from min_n 8 reversed/tn-prob) |
| xfit always reversed/mean-prob | 2.000 | 1.000 | 93.8 | 1232 | 73.89 | +0.23 [-1.46, +1.91] | 0.0340 | 0.5859 | fold 0: T 1.014; fold 1: T 1.041 |
| xfit always reversed/mean-logprob | 2.000 | 1.000 | 93.8 | 1232 | 74.20 | +0.55 [-1.15, +2.23] | 0.0326 | 0.5810 | fold 0: T 1.040; fold 1: T 1.085 |
| xfit always reversed/tn-prob | 2.000 | 1.000 | 93.8 | 1232 | 73.89 | +0.23 [-1.46, +1.91] | 0.0302 | 0.5848 | fold 0: α 0.851, β +0.117; fold 1: α 0.874, β +0.120 |
| xfit always half/mean-prob | 2.000 | 1.000 | 93.8 | 1232 | 74.44 | +0.79 [-0.89, +2.50] | 0.0363 | 0.5786 | fold 0: T 1.007; fold 1: T 0.991 |
| xfit always half/mean-logprob | 2.000 | 1.000 | 93.8 | 1232 | 74.58 | +0.92 [-0.79, +2.65] | 0.0458 | 0.5750 | fold 0: T 1.043; fold 1: T 1.042 |
| xfit always half/tn-prob | 2.000 | 1.000 | 93.8 | 1232 | 74.46 | +0.81 [-0.86, +2.53] | 0.0340 | 0.5786 | fold 0: α 0.861, β +0.104; fold 1: α 0.961, β +0.022 |

## Skipped

- cyclic:3/mean-prob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
- cyclic:3/mean-logprob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
- cyclic:3/tn-prob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
