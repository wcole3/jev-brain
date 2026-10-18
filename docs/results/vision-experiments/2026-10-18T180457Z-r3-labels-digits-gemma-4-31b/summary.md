# gemma-4-31b R3 label screen: digits vs letters, image dev

## Provenance

- timestamp: 2026-10-18T180457Z
- repo commit: 37a70a9
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: digits
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-digits calib-600: .cache/collect/gemma-4-31b/calib-600-digits.jsonl.gz
- collect labels-digits index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-digits.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-digits image dev: .cache/vision-collect/gemma-4-31b/labels-digits/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered; pure = those the set run tagged `set`

all = every question both arms answered; pure = the questions the set run showed with its own labels (fallback questions use today's letters).
Reports only; the owner picks.

### Fallback share (all questions, set run)

| grouping | bucket | share |
|---|---|---|
| overall | all | 0.065 |
| type | choice | 0.065 |
| options | 2 | 0.000 |
| options | 3-5 | 0.000 |
| options | 6-26 | 0.364 |

## T (choice, from each arm's text calib-600 fit)

- letters: 4.092
- labels-digits: 3.876

## all (1462 rows)

vision_compare: `2026-10-18T180529Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 77.06 | baseline | 0.800 | 0.0861 |  | 0.6166 |  |  |
| labels-digits | 75.26 | -1.80 [-3.16, -0.47] | 0.789 | 0.0882 | +0.0021 | 0.6246 | +0.0080 | 0.9562 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-digits |
|---|---|---|---|
| overall | all | 0.124 | 0.114 |
| type | choice | 0.124 | 0.114 |
| options | 2 | 0.043 | 0.032 |
| options | 3-5 | 0.062 | 0.053 |
| options | 6-26 | 0.448 | 0.437 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 227 312 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 186 157 169 147 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 50 37 29 36 31 33 15 12 9 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 2 | chosen | 240 299 |
| labels-digits | 2 | gold | 247 292 |
| labels-digits | 3-5 | chosen | 190 154 163 152 3 |
| labels-digits | 3-5 | gold | 187 155 175 143 2 |
| labels-digits | 6-26 | chosen | 55 39 27 34 33 30 14 11 9 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |


## pure (1367 rows)

vision_compare: `2026-10-18T180532Z-compare-pure/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 77.09 | baseline | 0.830 | 0.0793 |  | 0.5242 |  |  |
| labels-digits | 75.33 | -1.76 [-3.19, -0.40] | 0.816 | 0.0800 | +0.0007 | 0.5291 | +0.0049 | 0.9554 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-digits |
|---|---|---|---|
| overall | all | 0.110 | 0.100 |
| type | choice | 0.110 | 0.100 |
| options | 2 | 0.043 | 0.032 |
| options | 3-5 | 0.062 | 0.053 |
| options | 6-26 | 0.518 | 0.512 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 227 312 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 186 157 169 147 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 38 31 19 29 21 23 3 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 25 24 21 33 34 24 3 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 2 | chosen | 240 299 |
| labels-digits | 2 | gold | 247 292 |
| labels-digits | 3-5 | chosen | 190 154 163 152 3 |
| labels-digits | 3-5 | gold | 187 155 175 143 2 |
| labels-digits | 6-26 | chosen | 44 33 16 27 23 19 2 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 6-26 | gold | 25 24 21 33 34 24 3 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

