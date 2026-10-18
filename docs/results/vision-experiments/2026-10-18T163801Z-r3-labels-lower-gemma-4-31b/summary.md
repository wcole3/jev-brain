# gemma-4-31b R3 label screen: lower vs letters, image dev

## Provenance

- timestamp: 2026-10-18T163801Z
- repo commit: b784d38
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: lower
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-lower calib-600: .cache/collect/gemma-4-31b/calib-600-lower.jsonl.gz
- collect labels-lower index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-lower.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-lower image dev: .cache/vision-collect/gemma-4-31b/labels-lower/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`

all = every question both arms answered; pure = the questions the set run showed with its own labels (fallback questions use today's letters).
Reports only; the owner picks.

### Fallback share (all questions, set run)

| grouping | bucket | share |
|---|---|---|
| overall | all | 0.000 |
| type | choice | 0.000 |
| options | 2 | 0.000 |
| options | 3-5 | 0.000 |
| options | 6-26 | 0.000 |

## T (choice, from each arm's text calib-600 fit)

- letters: 4.092
- labels-lower: 3.862

## all (1462 rows)

vision_compare: `2026-10-18T163832Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 77.06 | baseline | 0.800 | 0.0861 |  | 0.6166 |  |  |
| labels-lower | 76.47 | -0.59 [-1.44, +0.19] | 0.799 | 0.0858 | -0.0003 | 0.6120 | -0.0046 | 0.9767 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-lower |
|---|---|---|---|
| overall | all | 0.124 | 0.118 |
| type | choice | 0.124 | 0.118 |
| options | 2 | 0.043 | 0.050 |
| options | 3-5 | 0.062 | 0.062 |
| options | 6-26 | 0.448 | 0.402 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 227 312 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 186 157 169 147 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 50 37 29 36 31 33 15 12 9 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-lower | 2 | chosen | 232 307 |
| labels-lower | 2 | gold | 247 292 |
| labels-lower | 3-5 | chosen | 188 155 168 147 4 |
| labels-lower | 3-5 | gold | 187 155 175 143 2 |
| labels-lower | 6-26 | chosen | 50 33 27 33 37 38 14 11 7 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-lower | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |


## pure (1462 rows)

vision_compare: `2026-10-18T163836Z-compare-pure/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 77.06 | baseline | 0.800 | 0.0861 |  | 0.6166 |  |  |
| labels-lower | 76.47 | -0.59 [-1.44, +0.19] | 0.799 | 0.0858 | -0.0003 | 0.6120 | -0.0046 | 0.9767 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-lower |
|---|---|---|---|
| overall | all | 0.124 | 0.118 |
| type | choice | 0.124 | 0.118 |
| options | 2 | 0.043 | 0.050 |
| options | 3-5 | 0.062 | 0.062 |
| options | 6-26 | 0.448 | 0.402 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 227 312 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 186 157 169 147 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 50 37 29 36 31 33 15 12 9 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-lower | 2 | chosen | 232 307 |
| labels-lower | 2 | gold | 247 292 |
| labels-lower | 3-5 | chosen | 188 155 168 147 4 |
| labels-lower | 3-5 | gold | 187 155 175 143 2 |
| labels-lower | 6-26 | chosen | 50 33 27 33 37 38 14 11 7 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-lower | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

