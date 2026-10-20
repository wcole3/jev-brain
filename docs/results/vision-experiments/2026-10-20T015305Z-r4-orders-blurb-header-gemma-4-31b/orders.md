# gemma-4-31b R3 option-order policies: image dev

## Provenance

- timestamp: 2026-10-20T015305Z
- commit: 438d4b5-dirty
- profile: gemma-4-31b
- collects: ['/home/welb/devspace/jev-brain/.cache/vision-collect/gemma-4-31b/r4-blurb-header/dev.jsonl.gz', '/home/welb/devspace/jev-brain/.cache/vision-collect/gemma-4-31b/r4-blurb-header-cyclic4/dev.jsonl.gz']
- text fit: /home/welb/devspace/jev-brain/docs/results/archive/2026-10-20T014817Z-r4-orders-text-blurb-header-2k-gemma-4-31b/summary.json
- arms dir: .cache/r4/arms/orders-blurb-header-gemma-4-31b
- gate T (choice): 3.9127002036540444

## Notes

- Each arm uses its text fit on text calib (choice T, or tn-prob's α + β ln n); gates read the identity read at the shipped choice T.
- A half policy without a text fit of its own uses the reversed policy's (ruling R3).
- Orders: half = cyclic:2's second order; aleria adds cyclic:4's other shifts; shifts are round(i·n/k) (R6).
- xfit arms: 2-fold group cross-fit on image dev (vision_offline.fold), a reference only; a fold under 30 questions keeps the text fit.

## Arms (1462 rows, Δ vs identity)

Index, CIs, ECE and NLL come from vision_compare (summary.md beside this file): paired bootstrap over image groups. Extra suffix tokens: the suffixes of every read after the first. Reports; the owner picks.

| arm | mean reads | share paying | extra suffix tokens | mean input tokens | index | Δ index [95% CI] | ECE | NLL | fit (choice) |
|---|---|---|---|---|---|---|---|---|---|
| identity | 1.000 | 0.000 | 0.0 | 740 | 78.25 | baseline | 0.0814 | 0.6065 | T 3.913 |
| always reversed/mean-prob | 2.000 | 1.000 | 96.8 | 837 | 77.44 | -0.81 [-2.09, +0.38] | 0.0645 | 0.6064 | T 3.773 |
| always reversed/mean-logprob | 2.000 | 1.000 | 96.8 | 837 | 77.50 | -0.75 [-2.06, +0.47] | 0.0701 | 0.6034 | T 3.920 |
| always reversed/tn-prob | 2.000 | 1.000 | 96.8 | 837 | 77.40 | -0.86 [-2.14, +0.34] | 0.0343 | 0.5636 | α 5.951, β -0.601 |
| cyclic:2/mean-prob | 2.000 | 1.000 | 96.8 | 837 | 77.11 | -1.15 [-2.46, +0.11] | 0.0756 | 0.6058 | T 3.728 |
| cyclic:2/mean-logprob | 2.000 | 1.000 | 96.8 | 837 | 77.39 | -0.87 [-2.18, +0.42] | 0.0756 | 0.6012 | T 3.888 |
| cyclic:2/tn-prob | 2.000 | 1.000 | 96.8 | 837 | 77.13 | -1.13 [-2.43, +0.13] | 0.0357 | 0.5617 | α 5.709, β -0.550 |
| cyclic:4/mean-prob | 3.191 | 1.000 | 247.1 | 987 | 77.71 | -0.55 [-1.87, +0.71] | 0.0684 | 0.6142 | T 3.617 |
| cyclic:4/mean-logprob | 3.191 | 1.000 | 247.1 | 987 | 77.82 | -0.43 [-1.75, +0.84] | 0.0694 | 0.6041 | T 3.886 |
| cyclic:4/tn-prob | 3.191 | 1.000 | 247.1 | 987 | 77.71 | -0.55 [-1.87, +0.71] | 0.0406 | 0.5666 | α 5.624, β -0.558 |
| top_p 0.5 reversed/mean-prob | 1.062 | 0.062 | 9.6 | 750 | 78.59 | +0.34 [-0.20, +0.90] | 0.0751 | 0.6038 | T 3.924 |
| top_p 0.5 reversed/mean-logprob | 1.062 | 0.062 | 9.6 | 750 | 78.61 | +0.36 [-0.18, +0.92] | 0.0776 | 0.6032 | T 3.934 |
| top_p 0.5 reversed/tn-prob | 1.062 | 0.062 | 9.6 | 750 | 78.59 | +0.34 [-0.20, +0.90] | 0.0365 | 0.5582 | α 6.360, β -0.680 |
| top_p 0.6 reversed/mean-prob | 1.103 | 0.103 | 15.6 | 756 | 78.30 | +0.05 [-0.87, +0.94] | 0.0749 | 0.6024 | T 3.928 |
| top_p 0.6 reversed/mean-logprob | 1.103 | 0.103 | 15.6 | 756 | 78.33 | +0.07 [-0.86, +0.96] | 0.0783 | 0.6012 | T 3.932 |
| top_p 0.6 reversed/tn-prob | 1.103 | 0.103 | 15.6 | 756 | 78.30 | +0.05 [-0.87, +0.94] | 0.0340 | 0.5574 | α 6.379, β -0.685 |
| top_p 0.7 reversed/mean-prob | 1.154 | 0.154 | 24.1 | 764 | 78.12 | -0.13 [-1.24, +0.94] | 0.0741 | 0.6066 | T 3.904 |
| top_p 0.7 reversed/mean-logprob | 1.154 | 0.154 | 24.1 | 764 | 78.28 | +0.03 [-1.09, +1.11] | 0.0801 | 0.6060 | T 3.921 |
| top_p 0.7 reversed/tn-prob | 1.154 | 0.154 | 24.1 | 764 | 78.12 | -0.13 [-1.24, +0.94] | 0.0374 | 0.5605 | α 6.338, β -0.681 |
| top_p 0.8 reversed/mean-prob | 1.218 | 0.218 | 33.4 | 774 | 77.85 | -0.40 [-1.57, +0.72] | 0.0681 | 0.6050 | T 3.909 |
| top_p 0.8 reversed/mean-logprob | 1.218 | 0.218 | 33.4 | 774 | 77.91 | -0.34 [-1.55, +0.81] | 0.0721 | 0.6037 | T 3.931 |
| top_p 0.8 reversed/tn-prob | 1.218 | 0.218 | 33.4 | 774 | 77.81 | -0.45 [-1.62, +0.68] | 0.0344 | 0.5608 | α 6.350, β -0.686 |
| top_p 0.9 reversed/mean-prob | 1.287 | 0.287 | 42.5 | 783 | 77.56 | -0.69 [-1.95, +0.48] | 0.0666 | 0.6088 | T 3.843 |
| top_p 0.9 reversed/mean-logprob | 1.287 | 0.287 | 42.5 | 783 | 77.62 | -0.64 [-1.93, +0.58] | 0.0721 | 0.6058 | T 3.915 |
| top_p 0.9 reversed/tn-prob | 1.287 | 0.287 | 42.5 | 783 | 77.51 | -0.74 [-2.01, +0.43] | 0.0347 | 0.5631 | α 6.144, β -0.641 |
| min_n 3 reversed/mean-prob | 1.631 | 0.631 | 77.5 | 818 | 78.42 | +0.17 [-0.68, +1.01] | 0.0663 | 0.6130 | T 3.774 |
| min_n 3 reversed/mean-logprob | 1.631 | 0.631 | 77.5 | 818 | 78.48 | +0.23 [-0.66, +1.11] | 0.0689 | 0.6027 | T 3.920 |
| min_n 3 reversed/tn-prob | 1.631 | 0.631 | 77.5 | 818 | 78.38 | +0.13 [-0.74, +0.97] | 0.0358 | 0.5653 | α 5.956, β -0.603 |
| min_n 4 reversed/mean-prob | 1.560 | 0.560 | 72.8 | 813 | 78.30 | +0.05 [-0.79, +0.84] | 0.0684 | 0.6137 | T 3.773 |
| min_n 4 reversed/mean-logprob | 1.560 | 0.560 | 72.8 | 813 | 78.36 | +0.11 [-0.75, +0.94] | 0.0697 | 0.6035 | T 3.919 |
| min_n 4 reversed/tn-prob | 1.560 | 0.560 | 72.8 | 813 | 78.26 | +0.00 [-0.84, +0.80] | 0.0367 | 0.5658 | α 5.959, β -0.603 |
| min_n 5 reversed/mean-prob | 1.185 | 0.185 | 35.3 | 776 | 78.80 | +0.55 [+0.08, +1.04] | 0.0722 | 0.6092 | T 3.774 |
| min_n 5 reversed/mean-logprob | 1.185 | 0.185 | 35.3 | 776 | 78.98 | +0.73 [+0.24, +1.26] | 0.0706 | 0.5960 | T 3.919 |
| min_n 5 reversed/tn-prob | 1.185 | 0.185 | 35.3 | 776 | 78.75 | +0.50 [+0.03, +1.02] | 0.0446 | 0.5607 | α 5.963, β -0.604 |
| min_n 6 reversed/mean-prob | 1.179 | 0.179 | 34.9 | 775 | 78.68 | +0.42 [+0.02, +0.85] | 0.0708 | 0.6074 | T 3.795 |
| min_n 6 reversed/mean-logprob | 1.179 | 0.179 | 34.9 | 775 | 78.86 | +0.60 [+0.17, +1.05] | 0.0683 | 0.5951 | T 3.930 |
| min_n 6 reversed/tn-prob | 1.179 | 0.179 | 34.9 | 775 | 78.63 | +0.38 [-0.03, +0.81] | 0.0438 | 0.5597 | α 6.043, β -0.623 |
| min_n 8 reversed/mean-prob | 1.077 | 0.077 | 7.9 | 748 | 78.41 | +0.15 [+0.00, +0.32] | 0.0804 | 0.6099 | T 3.820 |
| min_n 8 reversed/mean-logprob | 1.077 | 0.077 | 7.9 | 748 | 78.41 | +0.15 [+0.00, +0.32] | 0.0819 | 0.6033 | T 3.945 |
| min_n 8 reversed/tn-prob | 1.077 | 0.077 | 7.9 | 748 | 78.41 | +0.15 [+0.00, +0.32] | 0.0380 | 0.5590 | α 6.142, β -0.645 |
| aleria half/mean-prob | 2.192 | 1.000 | 135.1 | 875 | 77.80 | -0.45 [-1.75, +0.78] | 0.0738 | 0.6054 | T 3.715 |
| aleria half/mean-logprob | 2.192 | 1.000 | 135.1 | 875 | 77.92 | -0.34 [-1.65, +0.91] | 0.0740 | 0.6018 | T 3.890 |
| aleria half/tn-prob | 2.192 | 1.000 | 135.1 | 875 | 77.80 | -0.45 [-1.75, +0.78] | 0.0338 | 0.5610 | α 5.725, β -0.558 |
| always half/mean-prob | 2.000 | 1.000 | 96.8 | 837 | 77.11 | -1.15 [-2.46, +0.11] | 0.0741 | 0.6031 | T 3.773 (from always reversed/mean-prob) |
| always half/mean-logprob | 2.000 | 1.000 | 96.8 | 837 | 77.39 | -0.87 [-2.18, +0.42] | 0.0740 | 0.5994 | T 3.920 (from always reversed/mean-logprob) |
| always half/tn-prob | 2.000 | 1.000 | 96.8 | 837 | 77.13 | -1.13 [-2.43, +0.13] | 0.0303 | 0.5598 | α 5.951, β -0.601 (from always reversed/tn-prob) |
| top_p 0.5 half/mean-prob | 1.062 | 0.062 | 9.6 | 750 | 78.20 | -0.05 [-0.52, +0.40] | 0.0806 | 0.6047 | T 3.924 (from top_p 0.5 reversed/mean-prob) |
| top_p 0.5 half/mean-logprob | 1.062 | 0.062 | 9.6 | 750 | 78.27 | +0.02 [-0.46, +0.47] | 0.0810 | 0.6045 | T 3.934 (from top_p 0.5 reversed/mean-logprob) |
| top_p 0.5 half/tn-prob | 1.062 | 0.062 | 9.6 | 750 | 78.23 | -0.03 [-0.49, +0.41] | 0.0383 | 0.5586 | α 6.360, β -0.680 (from top_p 0.5 reversed/tn-prob) |
| top_p 0.6 half/mean-prob | 1.103 | 0.103 | 15.6 | 756 | 77.85 | -0.40 [-1.29, +0.43] | 0.0808 | 0.6046 | T 3.928 (from top_p 0.6 reversed/mean-prob) |
| top_p 0.6 half/mean-logprob | 1.103 | 0.103 | 15.6 | 756 | 78.02 | -0.23 [-1.15, +0.64] | 0.0819 | 0.6036 | T 3.932 (from top_p 0.6 reversed/mean-logprob) |
| top_p 0.6 half/tn-prob | 1.103 | 0.103 | 15.6 | 756 | 77.87 | -0.38 [-1.27, +0.45] | 0.0367 | 0.5588 | α 6.379, β -0.685 (from top_p 0.6 reversed/tn-prob) |
| top_p 0.7 half/mean-prob | 1.154 | 0.154 | 24.1 | 764 | 77.55 | -0.71 [-1.85, +0.41] | 0.0806 | 0.6085 | T 3.904 (from top_p 0.7 reversed/mean-prob) |
| top_p 0.7 half/mean-logprob | 1.154 | 0.154 | 24.1 | 764 | 77.78 | -0.47 [-1.64, +0.69] | 0.0797 | 0.6071 | T 3.921 (from top_p 0.7 reversed/mean-logprob) |
| top_p 0.7 half/tn-prob | 1.154 | 0.154 | 24.1 | 764 | 77.57 | -0.69 [-1.82, +0.43] | 0.0373 | 0.5615 | α 6.338, β -0.681 (from top_p 0.7 reversed/tn-prob) |
| top_p 0.8 half/mean-prob | 1.218 | 0.218 | 33.4 | 774 | 77.42 | -0.83 [-2.08, +0.36] | 0.0755 | 0.6044 | T 3.909 (from top_p 0.8 reversed/mean-prob) |
| top_p 0.8 half/mean-logprob | 1.218 | 0.218 | 33.4 | 774 | 77.70 | -0.55 [-1.81, +0.68] | 0.0755 | 0.6022 | T 3.931 (from top_p 0.8 reversed/mean-logprob) |
| top_p 0.8 half/tn-prob | 1.218 | 0.218 | 33.4 | 774 | 77.44 | -0.81 [-2.05, +0.38] | 0.0334 | 0.5597 | α 6.350, β -0.686 (from top_p 0.8 reversed/tn-prob) |
| top_p 0.9 half/mean-prob | 1.287 | 0.287 | 42.5 | 783 | 77.22 | -1.03 [-2.31, +0.20] | 0.0755 | 0.6054 | T 3.843 (from top_p 0.9 reversed/mean-prob) |
| top_p 0.9 half/mean-logprob | 1.287 | 0.287 | 42.5 | 783 | 77.50 | -0.75 [-2.06, +0.52] | 0.0758 | 0.6019 | T 3.915 (from top_p 0.9 reversed/mean-logprob) |
| top_p 0.9 half/tn-prob | 1.287 | 0.287 | 42.5 | 783 | 77.24 | -1.01 [-2.29, +0.22] | 0.0312 | 0.5595 | α 6.144, β -0.641 (from top_p 0.9 reversed/tn-prob) |
| min_n 3 half/mean-prob | 1.631 | 0.631 | 77.5 | 818 | 78.09 | -0.17 [-1.07, +0.74] | 0.0723 | 0.6096 | T 3.774 (from min_n 3 reversed/mean-prob) |
| min_n 3 half/mean-logprob | 1.631 | 0.631 | 77.5 | 818 | 78.37 | +0.12 [-0.83, +1.06] | 0.0699 | 0.5987 | T 3.920 (from min_n 3 reversed/mean-logprob) |
| min_n 3 half/tn-prob | 1.631 | 0.631 | 77.5 | 818 | 78.11 | -0.14 [-1.05, +0.76] | 0.0276 | 0.5615 | α 5.956, β -0.603 (from min_n 3 reversed/tn-prob) |
| min_n 4 half/mean-prob | 1.560 | 0.560 | 72.8 | 813 | 78.09 | -0.17 [-0.91, +0.57] | 0.0740 | 0.6107 | T 3.773 (from min_n 4 reversed/mean-prob) |
| min_n 4 half/mean-logprob | 1.560 | 0.560 | 72.8 | 813 | 78.37 | +0.12 [-0.67, +0.92] | 0.0700 | 0.5999 | T 3.919 (from min_n 4 reversed/mean-logprob) |
| min_n 4 half/tn-prob | 1.560 | 0.560 | 72.8 | 813 | 78.11 | -0.14 [-0.89, +0.59] | 0.0306 | 0.5621 | α 5.959, β -0.603 (from min_n 4 reversed/tn-prob) |
| min_n 5 half/mean-prob | 1.185 | 0.185 | 35.3 | 776 | 78.43 | +0.18 [-0.18, +0.54] | 0.0728 | 0.6063 | T 3.774 (from min_n 5 reversed/mean-prob) |
| min_n 5 half/mean-logprob | 1.185 | 0.185 | 35.3 | 776 | 78.59 | +0.34 [-0.07, +0.75] | 0.0685 | 0.5927 | T 3.919 (from min_n 5 reversed/mean-logprob) |
| min_n 5 half/tn-prob | 1.185 | 0.185 | 35.3 | 776 | 78.43 | +0.18 [-0.18, +0.54] | 0.0337 | 0.5574 | α 5.963, β -0.604 (from min_n 5 reversed/tn-prob) |
| min_n 6 half/mean-prob | 1.179 | 0.179 | 34.9 | 775 | 78.43 | +0.18 [-0.18, +0.54] | 0.0733 | 0.6051 | T 3.795 (from min_n 6 reversed/mean-prob) |
| min_n 6 half/mean-logprob | 1.179 | 0.179 | 34.9 | 775 | 78.59 | +0.34 [-0.07, +0.75] | 0.0683 | 0.5926 | T 3.930 (from min_n 6 reversed/mean-logprob) |
| min_n 6 half/tn-prob | 1.179 | 0.179 | 34.9 | 775 | 78.43 | +0.18 [-0.18, +0.54] | 0.0303 | 0.5568 | α 6.043, β -0.623 (from min_n 6 reversed/tn-prob) |
| min_n 8 half/mean-prob | 1.077 | 0.077 | 7.9 | 748 | 78.30 | +0.04 [-0.09, +0.18] | 0.0826 | 0.6074 | T 3.820 (from min_n 8 reversed/mean-prob) |
| min_n 8 half/mean-logprob | 1.077 | 0.077 | 7.9 | 748 | 78.30 | +0.04 [-0.11, +0.20] | 0.0801 | 0.6000 | T 3.945 (from min_n 8 reversed/mean-logprob) |
| min_n 8 half/tn-prob | 1.077 | 0.077 | 7.9 | 748 | 78.30 | +0.04 [-0.09, +0.18] | 0.0380 | 0.5572 | α 6.142, β -0.645 (from min_n 8 reversed/tn-prob) |
| xfit always reversed/mean-prob | 2.000 | 1.000 | 96.8 | 837 | 77.40 | -0.86 [-2.14, +0.34] | 0.0300 | 0.5661 | fold 0: T 5.328; fold 1: T 5.693 |
| xfit always reversed/mean-logprob | 2.000 | 1.000 | 96.8 | 837 | 77.50 | -0.75 [-2.06, +0.47] | 0.0322 | 0.5659 | fold 0: T 5.435; fold 1: T 5.741 |
| xfit always reversed/tn-prob | 2.000 | 1.000 | 96.8 | 837 | 77.40 | -0.86 [-2.14, +0.34] | 0.0232 | 0.5623 | fold 0: α 6.720, β -0.974; fold 1: α 7.147, β -1.046 |
| xfit always half/mean-prob | 2.000 | 1.000 | 96.8 | 837 | 77.17 | -1.08 [-2.38, +0.18] | 0.0260 | 0.5616 | fold 0: T 5.409; fold 1: T 5.607 |
| xfit always half/mean-logprob | 2.000 | 1.000 | 96.8 | 837 | 77.39 | -0.87 [-2.18, +0.42] | 0.0257 | 0.5607 | fold 0: T 5.541; fold 1: T 5.637 |
| xfit always half/tn-prob | 2.000 | 1.000 | 96.8 | 837 | 77.13 | -1.13 [-2.43, +0.13] | 0.0277 | 0.5580 | fold 0: α 6.685, β -0.892; fold 1: α 7.307, β -1.220 |

## Skipped

- cyclic:3/mean-prob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
- cyclic:3/mean-logprob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
- cyclic:3/tn-prob: needs perms no planned collect holds (full_cvbench:1050: missing perm [3, 4, 0, 1, 2])
