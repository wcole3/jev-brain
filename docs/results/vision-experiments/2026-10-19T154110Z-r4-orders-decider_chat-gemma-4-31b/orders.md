# gemma-4-31b R3 option-order policies: image dev

## Provenance

- timestamp: 2026-10-19T154110Z
- commit: b953b23-dirty
- profile: gemma-4-31b
- collects: ['/home/welb/devspace/jev-brain/.cache/vision-collect/gemma-4-31b/r4-decider/dev.jsonl.gz', '/home/welb/devspace/jev-brain/.cache/vision-collect/gemma-4-31b/r4-decider-cyclic4/dev.jsonl.gz']
- text fit: /home/welb/devspace/jev-brain/docs/results/archive/2026-10-19T141129Z-r4-orders-text-decider_chat-gemma-4-31b/summary.json
- arms dir: .cache/r4/arms/orders-decider_chat-gemma-4-31b
- gate T (choice): 4.122840843073183

## Notes

- Each arm uses its text fit on text calib (choice T, or tn-prob's α + β ln n); gates read the identity read at the shipped choice T.
- A half policy without a text fit of its own uses the reversed policy's (ruling R3).
- Orders: half = cyclic:2's second order; aleria adds cyclic:4's other shifts; shifts are round(i·n/k) (R6).
- xfit arms: 2-fold group cross-fit on image dev (vision_offline.fold), a reference only; a fold under 30 questions keeps the text fit.

## Arms (1462 rows, Δ vs identity)

Index, CIs, ECE and NLL come from vision_compare (summary.md beside this file): paired bootstrap over image groups. Extra suffix tokens: the suffixes of every read after the first. Reports; the owner picks.

| arm | mean reads | share paying | extra suffix tokens | mean input tokens | index | Δ index [95% CI] | ECE | NLL | fit (choice) |
|---|---|---|---|---|---|---|---|---|---|
| identity | 1.000 | 0.000 | 0.0 | 672 | 77.96 | baseline | 0.0654 | 0.6009 | T 4.123 |
| always reversed/mean-prob | 2.000 | 1.000 | 96.8 | 769 | 77.67 | -0.29 [-1.58, +0.95] | 0.0510 | 0.5920 | T 3.951 |
| always reversed/mean-logprob | 2.000 | 1.000 | 96.8 | 769 | 77.79 | -0.18 [-1.46, +1.08] | 0.0497 | 0.5892 | T 4.060 |
| always reversed/tn-prob | 2.000 | 1.000 | 96.8 | 769 | 77.63 | -0.33 [-1.63, +0.91] | 0.0362 | 0.5716 | α 6.460, β -0.709 |
| cyclic:2/mean-prob | 2.000 | 1.000 | 96.8 | 769 | 77.36 | -0.60 [-1.76, +0.54] | 0.0518 | 0.5892 | T 3.952 |
| cyclic:2/mean-logprob | 2.000 | 1.000 | 96.8 | 769 | 77.25 | -0.71 [-1.88, +0.46] | 0.0532 | 0.5858 | T 4.056 |
| cyclic:2/tn-prob | 2.000 | 1.000 | 96.8 | 769 | 77.31 | -0.65 [-1.82, +0.50] | 0.0330 | 0.5676 | α 6.373, β -0.684 |
| cyclic:4/mean-prob | 3.191 | 1.000 | 247.1 | 919 | 77.75 | -0.21 [-1.47, +1.00] | 0.0523 | 0.5923 | T 3.857 |
| cyclic:4/mean-logprob | 3.191 | 1.000 | 247.1 | 919 | 77.96 | +0.00 [-1.25, +1.22] | 0.0529 | 0.5850 | T 4.065 |
| cyclic:4/tn-prob | 3.191 | 1.000 | 247.1 | 919 | 77.85 | -0.11 [-1.35, +1.09] | 0.0372 | 0.5696 | α 6.187, β -0.656 |
| top_p 0.5 reversed/mean-prob | 1.079 | 0.079 | 12.6 | 685 | 78.01 | +0.05 [-0.52, +0.62] | 0.0674 | 0.5986 | T 4.118 |
| top_p 0.5 reversed/mean-logprob | 1.079 | 0.079 | 12.6 | 685 | 78.10 | +0.14 [-0.44, +0.73] | 0.0637 | 0.5975 | T 4.120 |
| top_p 0.5 reversed/tn-prob | 1.079 | 0.079 | 12.6 | 685 | 78.01 | +0.05 [-0.52, +0.62] | 0.0511 | 0.5732 | α 6.697, β -0.730 |
| top_p 0.6 reversed/mean-prob | 1.116 | 0.116 | 18.5 | 691 | 77.86 | -0.10 [-0.82, +0.63] | 0.0652 | 0.5985 | T 4.113 |
| top_p 0.6 reversed/mean-logprob | 1.116 | 0.116 | 18.5 | 691 | 77.86 | -0.10 [-0.84, +0.65] | 0.0620 | 0.5972 | T 4.113 |
| top_p 0.6 reversed/tn-prob | 1.116 | 0.116 | 18.5 | 691 | 77.82 | -0.14 [-0.88, +0.59] | 0.0467 | 0.5733 | α 6.680, β -0.727 |
| top_p 0.7 reversed/mean-prob | 1.185 | 0.185 | 30.7 | 703 | 77.95 | -0.01 [-1.04, +0.99] | 0.0593 | 0.5994 | T 4.090 |
| top_p 0.7 reversed/mean-logprob | 1.185 | 0.185 | 30.7 | 703 | 78.06 | +0.10 [-0.92, +1.11] | 0.0622 | 0.5979 | T 4.089 |
| top_p 0.7 reversed/tn-prob | 1.185 | 0.185 | 30.7 | 703 | 77.86 | -0.10 [-1.13, +0.90] | 0.0468 | 0.5745 | α 6.662, β -0.730 |
| top_p 0.8 reversed/mean-prob | 1.247 | 0.247 | 38.1 | 710 | 77.96 | -0.00 [-1.16, +1.13] | 0.0591 | 0.5975 | T 4.048 |
| top_p 0.8 reversed/mean-logprob | 1.247 | 0.247 | 38.1 | 710 | 78.07 | +0.11 [-1.06, +1.27] | 0.0585 | 0.5957 | T 4.062 |
| top_p 0.8 reversed/tn-prob | 1.247 | 0.247 | 38.1 | 710 | 77.87 | -0.09 [-1.26, +1.05] | 0.0462 | 0.5728 | α 6.624, β -0.732 |
| top_p 0.9 reversed/mean-prob | 1.332 | 0.332 | 48.6 | 721 | 77.82 | -0.14 [-1.38, +1.07] | 0.0527 | 0.5987 | T 4.015 |
| top_p 0.9 reversed/mean-logprob | 1.332 | 0.332 | 48.6 | 721 | 77.94 | -0.02 [-1.29, +1.20] | 0.0527 | 0.5932 | T 4.085 |
| top_p 0.9 reversed/tn-prob | 1.332 | 0.332 | 48.6 | 721 | 77.73 | -0.23 [-1.47, +1.00] | 0.0378 | 0.5741 | α 6.657, β -0.751 |
| min_n 3 reversed/mean-prob | 1.631 | 0.631 | 77.5 | 750 | 78.07 | +0.11 [-0.96, +1.14] | 0.0582 | 0.6039 | T 3.951 |
| min_n 3 reversed/mean-logprob | 1.631 | 0.631 | 77.5 | 750 | 78.18 | +0.22 [-0.84, +1.26] | 0.0573 | 0.5955 | T 4.060 |
| min_n 3 reversed/tn-prob | 1.631 | 0.631 | 77.5 | 750 | 78.03 | +0.06 [-1.01, +1.11] | 0.0445 | 0.5766 | α 6.459, β -0.708 |
| min_n 4 reversed/mean-prob | 1.560 | 0.560 | 72.8 | 745 | 78.19 | +0.23 [-0.65, +1.12] | 0.0609 | 0.6045 | T 3.950 |
| min_n 4 reversed/mean-logprob | 1.560 | 0.560 | 72.8 | 745 | 78.31 | +0.34 [-0.55, +1.22] | 0.0609 | 0.5963 | T 4.055 |
| min_n 4 reversed/tn-prob | 1.560 | 0.560 | 72.8 | 745 | 78.15 | +0.19 [-0.70, +1.07] | 0.0460 | 0.5765 | α 6.451, β -0.706 |
| min_n 5 reversed/mean-prob | 1.185 | 0.185 | 35.3 | 708 | 78.07 | +0.11 [-0.28, +0.50] | 0.0624 | 0.6071 | T 3.949 |
| min_n 5 reversed/mean-logprob | 1.185 | 0.185 | 35.3 | 708 | 78.18 | +0.22 [-0.18, +0.63] | 0.0591 | 0.5982 | T 4.054 |
| min_n 5 reversed/tn-prob | 1.185 | 0.185 | 35.3 | 708 | 78.03 | +0.07 [-0.34, +0.47] | 0.0448 | 0.5761 | α 6.446, β -0.705 |
| min_n 6 reversed/mean-prob | 1.179 | 0.179 | 34.9 | 707 | 78.07 | +0.11 [-0.28, +0.50] | 0.0636 | 0.6061 | T 3.964 |
| min_n 6 reversed/mean-logprob | 1.179 | 0.179 | 34.9 | 707 | 78.18 | +0.22 [-0.18, +0.63] | 0.0610 | 0.5977 | T 4.066 |
| min_n 6 reversed/tn-prob | 1.179 | 0.179 | 34.9 | 707 | 78.03 | +0.07 [-0.34, +0.47] | 0.0450 | 0.5758 | α 6.499, β -0.718 |
| min_n 8 reversed/mean-prob | 1.077 | 0.077 | 7.9 | 680 | 78.05 | +0.09 [-0.04, +0.22] | 0.0668 | 0.6067 | T 3.973 |
| min_n 8 reversed/mean-logprob | 1.077 | 0.077 | 7.9 | 680 | 78.07 | +0.11 [-0.02, +0.26] | 0.0639 | 0.6027 | T 4.072 |
| min_n 8 reversed/tn-prob | 1.077 | 0.077 | 7.9 | 680 | 78.05 | +0.09 [-0.04, +0.22] | 0.0428 | 0.5736 | α 6.531, β -0.725 |
| aleria half/mean-prob | 2.202 | 1.000 | 136.0 | 808 | 77.67 | -0.29 [-1.51, +0.90] | 0.0507 | 0.5882 | T 3.930 |
| aleria half/mean-logprob | 2.202 | 1.000 | 136.0 | 808 | 77.89 | -0.07 [-1.29, +1.11] | 0.0504 | 0.5844 | T 4.073 |
| aleria half/tn-prob | 2.202 | 1.000 | 136.0 | 808 | 77.77 | -0.19 [-1.40, +0.99] | 0.0313 | 0.5665 | α 6.331, β -0.678 |
| always half/mean-prob | 2.000 | 1.000 | 96.8 | 769 | 77.36 | -0.60 [-1.76, +0.54] | 0.0513 | 0.5893 | T 3.951 (from always reversed/mean-prob) |
| always half/mean-logprob | 2.000 | 1.000 | 96.8 | 769 | 77.25 | -0.71 [-1.88, +0.46] | 0.0531 | 0.5857 | T 4.060 (from always reversed/mean-logprob) |
| always half/tn-prob | 2.000 | 1.000 | 96.8 | 769 | 77.31 | -0.65 [-1.82, +0.50] | 0.0316 | 0.5679 | α 6.460, β -0.709 (from always reversed/tn-prob) |
| top_p 0.5 half/mean-prob | 1.079 | 0.079 | 12.6 | 685 | 77.95 | -0.01 [-0.49, +0.47] | 0.0655 | 0.5982 | T 4.118 (from top_p 0.5 reversed/mean-prob) |
| top_p 0.5 half/mean-logprob | 1.079 | 0.079 | 12.6 | 685 | 77.93 | -0.04 [-0.52, +0.45] | 0.0655 | 0.5971 | T 4.120 (from top_p 0.5 reversed/mean-logprob) |
| top_p 0.5 half/tn-prob | 1.079 | 0.079 | 12.6 | 685 | 77.93 | -0.04 [-0.52, +0.45] | 0.0461 | 0.5726 | α 6.697, β -0.730 (from top_p 0.5 reversed/tn-prob) |
| top_p 0.6 half/mean-prob | 1.116 | 0.116 | 18.5 | 691 | 77.43 | -0.53 [-1.29, +0.19] | 0.0631 | 0.5976 | T 4.113 (from top_p 0.6 reversed/mean-prob) |
| top_p 0.6 half/mean-logprob | 1.116 | 0.116 | 18.5 | 691 | 77.41 | -0.55 [-1.31, +0.17] | 0.0643 | 0.5961 | T 4.113 (from top_p 0.6 reversed/mean-logprob) |
| top_p 0.6 half/tn-prob | 1.116 | 0.116 | 18.5 | 691 | 77.41 | -0.55 [-1.31, +0.17] | 0.0393 | 0.5722 | α 6.680, β -0.727 (from top_p 0.6 reversed/tn-prob) |
| top_p 0.7 half/mean-prob | 1.185 | 0.185 | 30.7 | 703 | 77.64 | -0.32 [-1.22, +0.58] | 0.0578 | 0.5970 | T 4.090 (from top_p 0.7 reversed/mean-prob) |
| top_p 0.7 half/mean-logprob | 1.185 | 0.185 | 30.7 | 703 | 77.55 | -0.41 [-1.33, +0.51] | 0.0624 | 0.5952 | T 4.089 (from top_p 0.7 reversed/mean-logprob) |
| top_p 0.7 half/tn-prob | 1.185 | 0.185 | 30.7 | 703 | 77.60 | -0.36 [-1.27, +0.54] | 0.0365 | 0.5721 | α 6.662, β -0.730 (from top_p 0.7 reversed/tn-prob) |
| top_p 0.8 half/mean-prob | 1.247 | 0.247 | 38.1 | 710 | 77.51 | -0.45 [-1.57, +0.65] | 0.0541 | 0.5934 | T 4.048 (from top_p 0.8 reversed/mean-prob) |
| top_p 0.8 half/mean-logprob | 1.247 | 0.247 | 38.1 | 710 | 77.42 | -0.54 [-1.68, +0.57] | 0.0582 | 0.5907 | T 4.062 (from top_p 0.8 reversed/mean-logprob) |
| top_p 0.8 half/tn-prob | 1.247 | 0.247 | 38.1 | 710 | 77.46 | -0.50 [-1.62, +0.61] | 0.0325 | 0.5687 | α 6.624, β -0.732 (from top_p 0.8 reversed/tn-prob) |
| top_p 0.9 half/mean-prob | 1.332 | 0.332 | 48.6 | 721 | 77.51 | -0.45 [-1.57, +0.65] | 0.0505 | 0.5967 | T 4.015 (from top_p 0.9 reversed/mean-prob) |
| top_p 0.9 half/mean-logprob | 1.332 | 0.332 | 48.6 | 721 | 77.40 | -0.56 [-1.70, +0.56] | 0.0535 | 0.5906 | T 4.085 (from top_p 0.9 reversed/mean-logprob) |
| top_p 0.9 half/tn-prob | 1.332 | 0.332 | 48.6 | 721 | 77.46 | -0.50 [-1.62, +0.61] | 0.0303 | 0.5712 | α 6.657, β -0.751 (from top_p 0.9 reversed/tn-prob) |
| min_n 3 half/mean-prob | 1.631 | 0.631 | 77.5 | 750 | 77.76 | -0.21 [-1.10, +0.69] | 0.0573 | 0.6012 | T 3.951 (from min_n 3 reversed/mean-prob) |
| min_n 3 half/mean-logprob | 1.631 | 0.631 | 77.5 | 750 | 77.64 | -0.32 [-1.23, +0.60] | 0.0573 | 0.5920 | T 4.060 (from min_n 3 reversed/mean-logprob) |
| min_n 3 half/tn-prob | 1.631 | 0.631 | 77.5 | 750 | 77.71 | -0.25 [-1.15, +0.65] | 0.0414 | 0.5730 | α 6.459, β -0.708 (from min_n 3 reversed/tn-prob) |
| min_n 4 half/mean-prob | 1.560 | 0.560 | 72.8 | 745 | 77.88 | -0.08 [-0.88, +0.70] | 0.0566 | 0.6015 | T 3.950 (from min_n 4 reversed/mean-prob) |
| min_n 4 half/mean-logprob | 1.560 | 0.560 | 72.8 | 745 | 77.77 | -0.19 [-1.01, +0.61] | 0.0574 | 0.5923 | T 4.055 (from min_n 4 reversed/mean-logprob) |
| min_n 4 half/tn-prob | 1.560 | 0.560 | 72.8 | 745 | 77.83 | -0.13 [-0.93, +0.66] | 0.0403 | 0.5726 | α 6.451, β -0.706 (from min_n 4 reversed/tn-prob) |
| min_n 5 half/mean-prob | 1.185 | 0.185 | 35.3 | 708 | 78.10 | +0.14 [-0.25, +0.52] | 0.0586 | 0.6019 | T 3.949 (from min_n 5 reversed/mean-prob) |
| min_n 5 half/mean-logprob | 1.185 | 0.185 | 35.3 | 708 | 77.98 | +0.02 [-0.40, +0.45] | 0.0599 | 0.5928 | T 4.054 (from min_n 5 reversed/mean-logprob) |
| min_n 5 half/tn-prob | 1.185 | 0.185 | 35.3 | 708 | 78.05 | +0.09 [-0.31, +0.49] | 0.0393 | 0.5715 | α 6.446, β -0.705 (from min_n 5 reversed/tn-prob) |
| min_n 6 half/mean-prob | 1.179 | 0.179 | 34.9 | 707 | 78.10 | +0.14 [-0.25, +0.52] | 0.0611 | 0.6013 | T 3.964 (from min_n 6 reversed/mean-prob) |
| min_n 6 half/mean-logprob | 1.179 | 0.179 | 34.9 | 707 | 77.98 | +0.02 [-0.40, +0.45] | 0.0599 | 0.5928 | T 4.066 (from min_n 6 reversed/mean-logprob) |
| min_n 6 half/tn-prob | 1.179 | 0.179 | 34.9 | 707 | 78.05 | +0.09 [-0.31, +0.49] | 0.0404 | 0.5715 | α 6.499, β -0.718 (from min_n 6 reversed/tn-prob) |
| min_n 8 half/mean-prob | 1.077 | 0.077 | 7.9 | 680 | 77.98 | +0.02 [-0.09, +0.13] | 0.0654 | 0.6024 | T 3.973 (from min_n 8 reversed/mean-prob) |
| min_n 8 half/mean-logprob | 1.077 | 0.077 | 7.9 | 680 | 77.96 | +0.00 [-0.13, +0.13] | 0.0626 | 0.5987 | T 4.072 (from min_n 8 reversed/mean-logprob) |
| min_n 8 half/tn-prob | 1.077 | 0.077 | 7.9 | 680 | 77.98 | +0.02 [-0.09, +0.13] | 0.0413 | 0.5702 | α 6.531, β -0.725 (from min_n 8 reversed/tn-prob) |
| xfit always reversed/mean-prob | 2.000 | 1.000 | 96.8 | 769 | 77.63 | -0.33 [-1.63, +0.91] | 0.0399 | 0.5751 | fold 0: T 4.867; fold 1: T 5.351 |
| xfit always reversed/mean-logprob | 2.000 | 1.000 | 96.8 | 769 | 77.79 | -0.18 [-1.46, +1.08] | 0.0420 | 0.5738 | fold 0: T 4.959; fold 1: T 5.345 |
| xfit always reversed/tn-prob | 2.000 | 1.000 | 96.8 | 769 | 77.67 | -0.29 [-1.58, +0.95] | 0.0302 | 0.5716 | fold 0: α 5.978, β -0.775; fold 1: α 6.705, β -0.975 |
| xfit always half/mean-prob | 2.000 | 1.000 | 96.8 | 769 | 77.33 | -0.63 [-1.79, +0.53] | 0.0216 | 0.5718 | fold 0: T 4.892; fold 1: T 5.350 |
| xfit always half/mean-logprob | 2.000 | 1.000 | 96.8 | 769 | 77.25 | -0.71 [-1.88, +0.46] | 0.0267 | 0.5696 | fold 0: T 4.984; fold 1: T 5.351 |
| xfit always half/tn-prob | 2.000 | 1.000 | 96.8 | 769 | 77.31 | -0.65 [-1.82, +0.50] | 0.0259 | 0.5676 | fold 0: α 6.087, β -0.834; fold 1: α 6.893, β -1.113 |

## Skipped

- cyclic:3/mean-prob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
- cyclic:3/mean-logprob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
- cyclic:3/tn-prob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
