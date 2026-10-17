# R2 CPU R1: temperature per option count (vision dev, both models)

Created 2026-10-17T013235Z, commit a306b77 (clean tree). Reports; the owner picks. Index is unchanged by any T (agreement 1.0000 with the text arm on every arm, both models: confirmed).

## Method

- Text fits use `calibrate.questions_by_type` on the text calib collect (header layout, ok records, identity order, choice questions only: 898 per model); refitting one T there reproduces the shipped choice T exactly.
- Buckets of option count n with >= 100 calib questions each: 2-3, 4-5, 6-8, 9-10, 11-64, >64; `fit_temperature` per bucket. T(n) = alpha + beta ln n (floored at 0.05) minimises calib NLL by nested golden search over T(2), T(16).
- Aleria T(n) = max(0.05, 6.9 - 0.7 ln n) as a fixed arm. Dev references (never candidates): `vision_offline.py --arm fit-T` and an alpha + beta ln n fit, both 2-fold cross-fitted by the shipped `fold()`.
- Image dev identity reads scored with `gateway.decide.blend`; index, ECE, NLL from `vision_compare.py`; ΔECE/ΔNLL CIs use the compare's own group-bootstrap draws (10,000, seed 0) re-implemented in `calstats.py`.

## Data

- `.cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz` (sha256 `a4b9fcaf89675bd5…`)
- `.cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz` (sha256 `86af73abf00b2369…`)
- `.cache/collect/gemma-4-31b/calib.jsonl.gz` (sha256 `77ca1e9af90a7698…`)
- `.cache/collect/qwen3.8-27b/calib.jsonl.gz` (sha256 `2faeb8feb6ada00f…`)
- `.cache/collect/gemma-4-31b/eval.jsonl.gz` (sha256 `976424e941b013f7…`)
- `.cache/collect/qwen3.8-27b/eval.jsonl.gz` (sha256 `6e09b7b3a7456ed7…`)
- `data/gemma-4-31b/header/calibration.json` (sha256 `907179a67fdea7df…`)
- `data/qwen3.8-27b/header/calibration.json` (sha256 `58c75d522e2385bb…`)
- `data/splits/calib.json` (sha256 `c8c8dba6f809a0e3…`)
- `data/splits/eval.json` (sha256 `91e41b1fd18bf857…`)
- `data/splits/vision-dev.json` (sha256 `ec05c385e0c0eca7…`)
- Text eval collect is used only to judge the text fits (held out), as `calibrate.py` does. No holdout rows, no Jev outputs.

## Text fits

### gemma-4-31b (text choice T 4.263)

| bucket | calib questions | T |
|---|---|---|
| 2-3 | 172 | 4.669 |
| 4-5 | 121 | 4.804 |
| 6-8 | 106 | 3.532 |
| 9-10 | 167 | 7.743 |
| 11-64 | 120 | 2.957 |
| >64 | 212 | 3.546 |

alpha + beta ln n on calib: alpha 7.350, beta -0.876. Aleria: alpha 6.9, beta -0.7. Dev cross-fit (reference): fold 0 alpha 7.444 beta -1.211, fold 1 alpha 7.226 beta -0.897.

T applied per image option count:

| arm | n=2 | n=3 | n=4 | n=6 | n=10 |
|---|---|---|---|---|---|
| text | 4.263 | 4.263 | 4.263 | 4.263 | 4.263 |
| Tn_bucket | 4.669 | 4.669 | 4.804 | 3.532 | 7.743 |
| Tn_log | 6.743 | 6.387 | 6.135 | 5.780 | 5.333 |
| Tn_aleria | 6.415 | 6.131 | 5.930 | 5.646 | 5.288 |
| ref_dev_fitT (folds) | 5.736 / 5.985 (all n) | | | | |

Per-n T on calib (n with >= 30 questions; noisy, see notes) vs Aleria:

| n | 2 | 3 | 4 | 5 | 6 | 8 | 9 | 16 | 32 | 64 | 77 | 128 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ours | 7.05 | 4.11 | 0.10 | 6.03 | 0.46 | 3.22 | 7.90 | 0.44 | 0.26 | 3.07 | 3.87 | 0.21 |
| Aleria | 6.41 | 6.13 | 5.93 | 5.77 | 5.65 | 5.44 | 5.36 | 4.96 | 4.47 | 3.99 | 3.86 | 3.50 |

Text-side check (calib in-sample, eval held out):

| formula | calib NLL | calib ECE | eval NLL | eval ECE |
|---|---|---|---|---|
| text | 0.6044 | 0.0412 | 0.6498 | 0.0790 |
| Tn_bucket | 0.5160 | 0.0225 | 0.5955 | 0.0733 |
| Tn_log | 0.5552 | 0.0391 | 0.5434 | 0.0443 |
| Tn_aleria | 0.5587 | 0.0351 | 0.5525 | 0.0497 |

### qwen3.8-27b (text choice T 1.536)

| bucket | calib questions | T |
|---|---|---|
| 2-3 | 172 | 0.144 |
| 4-5 | 121 | 0.969 |
| 6-8 | 106 | 1.029 |
| 9-10 | 167 | 2.236 |
| 11-64 | 120 | 1.351 |
| >64 | 212 | 1.385 |

alpha + beta ln n on calib: alpha 1.786, beta -0.079. Aleria: alpha 6.9, beta -0.7. Dev cross-fit (reference): fold 0 alpha 1.196 beta +0.045, fold 1 alpha 1.340 beta -0.016.

T applied per image option count:

| arm | n=2 | n=3 | n=4 | n=6 | n=10 |
|---|---|---|---|---|---|
| text | 1.536 | 1.536 | 1.536 | 1.536 | 1.536 |
| Tn_bucket | 0.144 | 0.144 | 0.969 | 1.029 | 2.236 |
| Tn_log | 1.731 | 1.699 | 1.677 | 1.645 | 1.605 |
| Tn_aleria | 6.415 | 6.131 | 5.930 | 5.646 | 5.288 |
| ref_dev_fitT (folds) | 1.260 / 1.317 (all n) | | | | |

Per-n T on calib (n with >= 30 questions; noisy, see notes) vs Aleria:

| n | 2 | 3 | 4 | 5 | 6 | 8 | 9 | 16 | 32 | 64 | 77 | 128 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ours | 0.09 | 0.14 | 0.58 | 1.23 | 0.05 | 1.23 | 2.26 | 0.15 | 0.05 | 1.37 | 1.44 | 0.05 |
| Aleria | 6.41 | 6.13 | 5.93 | 5.77 | 5.65 | 5.44 | 5.36 | 4.96 | 4.47 | 3.99 | 3.86 | 3.50 |

Text-side check (calib in-sample, eval held out):

| formula | calib NLL | calib ECE | eval NLL | eval ECE |
|---|---|---|---|---|
| text | 0.4904 | 0.0268 | 0.4754 | 0.0449 |
| Tn_bucket | 0.4565 | 0.0350 | 1.0231 | 0.0947 |
| Tn_log | 0.4887 | 0.0268 | 0.4784 | 0.0498 |
| Tn_aleria | 1.1280 | 0.4783 | 0.9653 | 0.3890 |

## Image dev (1,462 rows, identity order)

### gemma-4-31b

| arm | index | agreement vs text | ECE | ΔECE [95% CI] | NLL | ΔNLL [95% CI] | ECE n=2 | n=3 | n=4-5 | n=6-8 | n=9-10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| text | 77.06 | 1.0000 | 0.0808 | baseline | 0.6072 | baseline | 0.102 | 0.076 | 0.049 | 0.148 | 0.261 |
| Tn_bucket | 77.06 | 1.0000 | 0.0670 | -0.0138 [-0.0231, -0.0024] | 0.5973 | -0.0100 [-0.0202, -0.0000] | 0.102 | 0.066 | 0.048 | 0.211 | 0.131 |
| Tn_log | 77.06 | 1.0000 | 0.0420 | -0.0388 [-0.0483, -0.0183] | 0.5712 | -0.0361 [-0.0531, -0.0196] | 0.069 | 0.088 | 0.076 | 0.087 | 0.172 |
| Tn_aleria | 77.06 | 1.0000 | 0.0478 | -0.0330 [-0.0428, -0.0169] | 0.5708 | -0.0364 [-0.0520, -0.0213] | 0.071 | 0.074 | 0.075 | 0.106 | 0.161 |
| ref_dev_fitT | 77.06 | 1.0000 | 0.0426 | -0.0382 [-0.0467, -0.0196] | 0.5746 | -0.0326 [-0.0470, -0.0188] | 0.076 | 0.084 | 0.071 | 0.072 | 0.141 |
| ref_dev_Tn_log | 77.06 | 1.0000 | 0.0512 | -0.0296 [-0.0395, -0.0134] | 0.5710 | -0.0362 [-0.0521, -0.0212] | 0.071 | 0.084 | 0.072 | 0.123 | 0.181 |

Rows per n bucket: {'n=2': 539, 'n=3': 105, 'n=4-5': 557, 'n=6-8': 150, 'n=9-10': 111}.

Per-benchmark ECE:

| benchmark | text | Tn_bucket | Tn_log | Tn_aleria | ref_dev_fitT | ref_dev_Tn_log |
|---|---|---|---|---|---|---|
| BLINK | 0.151 | 0.132 | 0.102 | 0.114 | 0.117 | 0.100 |
| CV-Bench | 0.080 | 0.072 | 0.063 | 0.074 | 0.055 | 0.075 |
| CharXiv | 0.090 | 0.092 | 0.144 | 0.132 | 0.135 | 0.135 |
| InfographicVQA | 0.052 | 0.058 | 0.109 | 0.100 | 0.096 | 0.097 |
| KIE (CORD+FUNSD) | 0.026 | 0.019 | 0.045 | 0.036 | 0.035 | 0.031 |
| MMMU-Pro vision | 0.223 | 0.100 | 0.152 | 0.142 | 0.130 | 0.155 |
| Mind2Web | 0.050 | 0.060 | 0.108 | 0.104 | 0.106 | 0.107 |
| Moderation (Hateful Memes) | 0.198 | 0.200 | 0.159 | 0.165 | 0.174 | 0.161 |
| R-Bench-M | 0.142 | 0.205 | 0.078 | 0.097 | 0.071 | 0.130 |
| RealWorldQA | 0.123 | 0.088 | 0.090 | 0.089 | 0.098 | 0.088 |
| Winoground | 0.079 | 0.075 | 0.049 | 0.053 | 0.061 | 0.050 |

### qwen3.8-27b

| arm | index | agreement vs text | ECE | ΔECE [95% CI] | NLL | ΔNLL [95% CI] | ECE n=2 | n=3 | n=4-5 | n=6-8 | n=9-10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| text | 73.31 | 1.0000 | 0.0424 | baseline | 0.6029 | baseline | 0.038 | 0.159 | 0.091 | 0.036 | 0.134 |
| Tn_bucket | 73.31 | 1.0000 | 0.0627 | +0.0203 [-0.0033, +0.0415] | 1.0545 | +0.4517 [+0.3172, +0.5952] | 0.129 | 0.093 | 0.019 | 0.082 | 0.095 |
| Tn_log | 73.31 | 1.0000 | 0.0598 | +0.0174 [+0.0049, +0.0225] | 0.6112 | +0.0084 [+0.0054, +0.0112] | 0.053 | 0.159 | 0.112 | 0.066 | 0.121 |
| Tn_aleria | 73.31 | 1.0000 | 0.3030 | +0.2606 [+0.2326, +0.2665] | 0.9064 | +0.3035 [+0.2784, +0.3277] | 0.210 | 0.405 | 0.439 | 0.167 | 0.155 |
| ref_dev_fitT | 73.31 | 1.0000 | 0.0255 | -0.0169 [-0.0279, -0.0015] | 0.5965 | -0.0064 [-0.0123, -0.0005] | 0.045 | 0.107 | 0.067 | 0.067 | 0.162 |
| ref_dev_Tn_log | 73.31 | 1.0000 | 0.0256 | -0.0168 [-0.0288, -0.0026] | 0.5966 | -0.0062 [-0.0122, -0.0002] | 0.054 | 0.106 | 0.066 | 0.067 | 0.159 |

Rows per n bucket: {'n=2': 539, 'n=3': 105, 'n=4-5': 557, 'n=6-8': 150, 'n=9-10': 111}.

Per-benchmark ECE:

| benchmark | text | Tn_bucket | Tn_log | Tn_aleria | ref_dev_fitT | ref_dev_Tn_log |
|---|---|---|---|---|---|---|
| BLINK | 0.113 | 0.097 | 0.138 | 0.364 | 0.084 | 0.087 |
| CV-Bench | 0.102 | 0.068 | 0.100 | 0.309 | 0.068 | 0.067 |
| CharXiv | 0.103 | 0.075 | 0.106 | 0.390 | 0.069 | 0.069 |
| InfographicVQA | 0.101 | 0.046 | 0.086 | 0.436 | 0.064 | 0.064 |
| KIE (CORD+FUNSD) | 0.030 | 0.041 | 0.043 | 0.338 | 0.020 | 0.020 |
| MMMU-Pro vision | 0.088 | 0.081 | 0.102 | 0.181 | 0.139 | 0.127 |
| Mind2Web | 0.148 | 0.061 | 0.172 | 0.500 | 0.109 | 0.109 |
| Moderation (Hateful Memes) | 0.125 | 0.229 | 0.114 | 0.125 | 0.130 | 0.131 |
| R-Bench-M | 0.052 | 0.076 | 0.066 | 0.167 | 0.080 | 0.079 |
| RealWorldQA | 0.136 | 0.125 | 0.141 | 0.355 | 0.103 | 0.114 |
| Winoground | 0.068 | 0.113 | 0.065 | 0.256 | 0.054 | 0.052 |

## Notes

- **Aleria scale.** For gemma, Aleria's formula sits close to our own text fit (alpha 6.9 vs 7.35, beta -0.7 vs -0.88; T(2) 6.41 vs 6.74, T(10) 5.29 vs 5.33), so the letter logprob scale matches (same base model). For qwen it does not: our qwen T is 1.3-1.5 and Aleria's ~6 flattens qwen's probabilities (image ECE 0.30). Read the Aleria arm as a gemma-only reference.
- **n is confounded with task family.** On text, n = 9 is mostly patent_section (150 of 162), n = 77 is jevbench banking (150/150), n = 3 is mostly jevbench commerce/org; per-n fits swing from 0.05 to 7.9. On image, n = 2 is Hateful Memes, Winoground and parts of BLINK/CV-Bench/KIE; n = 6 is R-Bench-M; n = 9-10 is MMMU-Pro. A T(n) partly acts as a T per benchmark.
- **Text calib has 32 questions with n = 2** (image dev: 539). Bucket 2-3 is mostly n = 3. The bucket arm overfits for qwen (bucket 2-3 T 0.14; text eval NLL 0.48 -> 1.02, image NLL 0.60 -> 1.05). The two-parameter form is stable on text eval for both models.
- **qwen**: the shipped text T already gives image ECE 0.042; every text-fitted T(n) is worse on image. Only the dev cross-fits (references) reach 0.026.
- `data/splits/calib.json` was recut (0583abf) after the shipped fit, so its sha256 differs from the one in the calibration files (`a4e492db…`); the header choice questions are the same (898, refit T equal to 15 digits).
- `compare-<profile>/` holds the shipped `vision_compare.py` output (index CIs are all [0, 0]); `provenance/` holds each arm's `arm.json`; `summary.json` has every fit and statistic.
