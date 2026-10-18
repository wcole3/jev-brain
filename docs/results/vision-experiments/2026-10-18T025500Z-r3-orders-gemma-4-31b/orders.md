# gemma-4-31b R3 option-order policies: image dev

## Provenance

- timestamp: 2026-10-18T025500Z
- commit: 995c64d
- profile: gemma-4-31b
- collects: ['/home/welb/devspace/jev-brain/.cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz']
- text fit: /home/welb/devspace/jev-brain/docs/results/archive/2026-10-18T021201Z-r3-orders-text-gemma-4-31b/summary.json
- arms dir: .cache/vision-orders/gemma-4-31b/baseline
- gate T (choice): 4.262737987560785

## Notes

- Each arm uses its text fit on text calib (choice T, or tn-prob's α + β ln n); gates read the identity read at the shipped choice T.
- A half policy without a text fit of its own uses the reversed policy's (ruling R3).
- Orders: half = cyclic:2's second order; aleria adds cyclic:4's other shifts; shifts are round(i·n/k) (R6).
- xfit arms: 2-fold group cross-fit on image dev (vision_offline.fold), a reference only; a fold under 30 questions keeps the text fit.

## Arms (1462 rows, Δ vs identity)

Index, CIs, ECE and NLL come from vision_compare (summary.md beside this file): paired bootstrap over image groups. Extra suffix tokens: the suffixes of every read after the first. Reports; the owner picks.

| arm | mean reads | share paying | extra suffix tokens | mean input tokens | index | Δ index [95% CI] | ECE | NLL | fit (choice) |
|---|---|---|---|---|---|---|---|---|---|
| identity | 1.000 | 0.000 | 0.0 | 719 | 77.06 | baseline | 0.0808 | 0.6072 | T 4.263 |
| always reversed/mean-prob | 2.000 | 1.000 | 96.8 | 816 | 76.79 | -0.27 [-1.51, +0.96] | 0.0648 | 0.6051 | T 4.090 |
| always reversed/mean-logprob | 2.000 | 1.000 | 96.8 | 816 | 76.79 | -0.27 [-1.55, +0.96] | 0.0619 | 0.6005 | T 4.198 |
| always reversed/tn-prob | 2.000 | 1.000 | 96.8 | 816 | 76.67 | -0.39 [-1.62, +0.79] | 0.0443 | 0.5736 | α 7.100, β -0.855 |
| top_p 0.5 reversed/mean-prob | 1.066 | 0.066 | 10.3 | 730 | 76.99 | -0.07 [-0.58, +0.41] | 0.0813 | 0.6051 | T 4.266 |
| top_p 0.5 reversed/mean-logprob | 1.066 | 0.066 | 10.3 | 730 | 77.01 | -0.05 [-0.55, +0.42] | 0.0772 | 0.6034 | T 4.281 |
| top_p 0.5 reversed/tn-prob | 1.066 | 0.066 | 10.3 | 730 | 76.99 | -0.07 [-0.57, +0.41] | 0.0420 | 0.5703 | α 7.338, β -0.872 |
| top_p 0.6 reversed/mean-prob | 1.114 | 0.114 | 17.7 | 737 | 77.13 | +0.07 [-0.68, +0.82] | 0.0750 | 0.6031 | T 4.262 |
| top_p 0.6 reversed/mean-logprob | 1.114 | 0.114 | 17.7 | 737 | 77.25 | +0.18 [-0.56, +0.94] | 0.0741 | 0.6007 | T 4.273 |
| top_p 0.6 reversed/tn-prob | 1.114 | 0.114 | 17.7 | 737 | 77.13 | +0.07 [-0.67, +0.83] | 0.0442 | 0.5692 | α 7.331, β -0.872 |
| top_p 0.7 reversed/mean-prob | 1.161 | 0.161 | 25.7 | 745 | 77.01 | -0.05 [-0.95, +0.85] | 0.0736 | 0.6050 | T 4.250 |
| top_p 0.7 reversed/mean-logprob | 1.161 | 0.161 | 25.7 | 745 | 77.01 | -0.05 [-0.94, +0.85] | 0.0731 | 0.6016 | T 4.272 |
| top_p 0.7 reversed/tn-prob | 1.161 | 0.161 | 25.7 | 745 | 76.89 | -0.17 [-1.05, +0.69] | 0.0447 | 0.5714 | α 7.365, β -0.888 |
| top_p 0.8 reversed/mean-prob | 1.222 | 0.222 | 35.7 | 755 | 76.65 | -0.41 [-1.49, +0.67] | 0.0731 | 0.6081 | T 4.210 |
| top_p 0.8 reversed/mean-logprob | 1.222 | 0.222 | 35.7 | 755 | 76.75 | -0.31 [-1.40, +0.80] | 0.0710 | 0.6021 | T 4.237 |
| top_p 0.8 reversed/tn-prob | 1.222 | 0.222 | 35.7 | 755 | 76.53 | -0.53 [-1.59, +0.52] | 0.0466 | 0.5733 | α 7.376, β -0.906 |
| top_p 0.9 reversed/mean-prob | 1.305 | 0.305 | 44.8 | 764 | 76.91 | -0.15 [-1.35, +1.05] | 0.0671 | 0.6088 | T 4.154 |
| top_p 0.9 reversed/mean-logprob | 1.305 | 0.305 | 44.8 | 764 | 76.91 | -0.15 [-1.39, +1.08] | 0.0652 | 0.6024 | T 4.236 |
| top_p 0.9 reversed/tn-prob | 1.305 | 0.305 | 44.8 | 764 | 76.78 | -0.28 [-1.47, +0.91] | 0.0479 | 0.5739 | α 7.312, β -0.902 |
| min_n 3 reversed/mean-prob | 1.631 | 0.631 | 77.5 | 797 | 77.09 | +0.03 [-0.93, +0.99] | 0.0704 | 0.6144 | T 4.092 |
| min_n 3 reversed/mean-logprob | 1.631 | 0.631 | 77.5 | 797 | 77.09 | +0.03 [-0.96, +1.00] | 0.0646 | 0.6051 | T 4.199 |
| min_n 3 reversed/tn-prob | 1.631 | 0.631 | 77.5 | 797 | 76.96 | -0.10 [-1.03, +0.82] | 0.0489 | 0.5766 | α 7.107, β -0.857 |
| min_n 4 reversed/mean-prob | 1.560 | 0.560 | 72.8 | 792 | 76.84 | -0.22 [-1.04, +0.61] | 0.0706 | 0.6161 | T 4.092 |
| min_n 4 reversed/mean-logprob | 1.560 | 0.560 | 72.8 | 792 | 76.84 | -0.22 [-1.09, +0.64] | 0.0642 | 0.6071 | T 4.192 |
| min_n 4 reversed/tn-prob | 1.560 | 0.560 | 72.8 | 792 | 76.72 | -0.34 [-1.15, +0.44] | 0.0512 | 0.5773 | α 7.105, β -0.856 |
| min_n 5 reversed/mean-prob | 1.185 | 0.185 | 35.3 | 755 | 77.08 | +0.02 [-0.34, +0.38] | 0.0730 | 0.6142 | T 4.090 |
| min_n 5 reversed/mean-logprob | 1.185 | 0.185 | 35.3 | 755 | 77.30 | +0.24 [-0.12, +0.61] | 0.0666 | 0.6022 | T 4.191 |
| min_n 5 reversed/tn-prob | 1.185 | 0.185 | 35.3 | 755 | 77.08 | +0.02 [-0.34, +0.38] | 0.0488 | 0.5731 | α 7.101, β -0.855 |
| min_n 6 reversed/mean-prob | 1.179 | 0.179 | 34.9 | 754 | 77.08 | +0.02 [-0.34, +0.38] | 0.0718 | 0.6127 | T 4.116 |
| min_n 6 reversed/mean-logprob | 1.179 | 0.179 | 34.9 | 754 | 77.30 | +0.24 [-0.12, +0.61] | 0.0674 | 0.6012 | T 4.218 |
| min_n 6 reversed/tn-prob | 1.179 | 0.179 | 34.9 | 754 | 77.08 | +0.02 [-0.34, +0.38] | 0.0506 | 0.5730 | α 7.197, β -0.878 |
| min_n 8 reversed/mean-prob | 1.077 | 0.077 | 7.9 | 727 | 77.17 | +0.11 [-0.02, +0.24] | 0.0812 | 0.6138 | T 4.126 |
| min_n 8 reversed/mean-logprob | 1.077 | 0.077 | 7.9 | 727 | 77.17 | +0.11 [+0.00, +0.24] | 0.0787 | 0.6084 | T 4.226 |
| min_n 8 reversed/tn-prob | 1.077 | 0.077 | 7.9 | 727 | 77.17 | +0.11 [-0.02, +0.24] | 0.0496 | 0.5709 | α 7.232, β -0.886 |
| xfit always reversed/mean-prob | 2.000 | 1.000 | 96.8 | 816 | 76.67 | -0.39 [-1.62, +0.79] | 0.0411 | 0.5773 | fold 0: T 5.401; fold 1: T 5.792 |
| xfit always reversed/mean-logprob | 2.000 | 1.000 | 96.8 | 816 | 76.79 | -0.27 [-1.55, +0.96] | 0.0336 | 0.5754 | fold 0: T 5.458; fold 1: T 5.793 |
| xfit always reversed/tn-prob | 2.000 | 1.000 | 96.8 | 816 | 76.67 | -0.39 [-1.62, +0.79] | 0.0401 | 0.5733 | fold 0: α 6.862, β -1.030; fold 1: α 7.258, β -1.060 |

## Skipped

- cyclic:2/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- cyclic:2/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- cyclic:2/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- cyclic:3/mean-prob: needs perms no planned collect holds (full_blink:val_Counting_105: missing perm [1, 2, 3, 0])
- cyclic:3/mean-logprob: needs perms no planned collect holds (full_blink:val_Counting_105: missing perm [1, 2, 3, 0])
- cyclic:3/tn-prob: needs perms no planned collect holds (full_blink:val_Counting_105: missing perm [1, 2, 3, 0])
- cyclic:4/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [1, 2, 3, 0])
- cyclic:4/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [1, 2, 3, 0])
- cyclic:4/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [1, 2, 3, 0])
- aleria half/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- aleria half/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- aleria half/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- always half/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- always half/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- always half/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- top_p 0.5 half/mean-prob: needs cyclic:4 collect (full_charxiv:38: missing perm [2, 3, 0, 1])
- top_p 0.5 half/mean-logprob: needs cyclic:4 collect (full_charxiv:38: missing perm [2, 3, 0, 1])
- top_p 0.5 half/tn-prob: needs cyclic:4 collect (full_charxiv:38: missing perm [2, 3, 0, 1])
- top_p 0.6 half/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_91: missing perm [2, 3, 0, 1])
- top_p 0.6 half/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_91: missing perm [2, 3, 0, 1])
- top_p 0.6 half/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_91: missing perm [2, 3, 0, 1])
- top_p 0.7 half/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_91: missing perm [2, 3, 0, 1])
- top_p 0.7 half/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_91: missing perm [2, 3, 0, 1])
- top_p 0.7 half/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_91: missing perm [2, 3, 0, 1])
- top_p 0.8 half/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_19: missing perm [2, 3, 0, 1])
- top_p 0.8 half/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_19: missing perm [2, 3, 0, 1])
- top_p 0.8 half/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_19: missing perm [2, 3, 0, 1])
- top_p 0.9 half/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_19: missing perm [2, 3, 0, 1])
- top_p 0.9 half/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_19: missing perm [2, 3, 0, 1])
- top_p 0.9 half/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_19: missing perm [2, 3, 0, 1])
- min_n 3 half/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- min_n 3 half/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- min_n 3 half/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- min_n 4 half/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- min_n 4 half/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- min_n 4 half/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- min_n 5 half/mean-prob: needs cyclic:4 collect (full_cvbench:1006: missing perm [3, 4, 5, 0, 1, 2])
- min_n 5 half/mean-logprob: needs cyclic:4 collect (full_cvbench:1006: missing perm [3, 4, 5, 0, 1, 2])
- min_n 5 half/tn-prob: needs cyclic:4 collect (full_cvbench:1006: missing perm [3, 4, 5, 0, 1, 2])
- min_n 6 half/mean-prob: needs cyclic:4 collect (full_cvbench:1006: missing perm [3, 4, 5, 0, 1, 2])
- min_n 6 half/mean-logprob: needs cyclic:4 collect (full_cvbench:1006: missing perm [3, 4, 5, 0, 1, 2])
- min_n 6 half/tn-prob: needs cyclic:4 collect (full_cvbench:1006: missing perm [3, 4, 5, 0, 1, 2])
- min_n 8 half/mean-prob: needs cyclic:4 collect (full_mmmu_pro_vision:test_Accounting_170: missing perm [4, 5, 6, 7, 8, 0, 1, 2, 3])
- min_n 8 half/mean-logprob: needs cyclic:4 collect (full_mmmu_pro_vision:test_Accounting_170: missing perm [4, 5, 6, 7, 8, 0, 1, 2, 3])
- min_n 8 half/tn-prob: needs cyclic:4 collect (full_mmmu_pro_vision:test_Accounting_170: missing perm [4, 5, 6, 7, 8, 0, 1, 2, 3])
- xfit always half/mean-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- xfit always half/mean-logprob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
- xfit always half/tn-prob: needs cyclic:4 collect (full_blink:val_Counting_105: missing perm [2, 3, 0, 1])
