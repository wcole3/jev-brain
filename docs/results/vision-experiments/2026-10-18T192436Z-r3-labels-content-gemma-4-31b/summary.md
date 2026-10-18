# gemma-4-31b R3 label screen: content vs letters, image dev

## Provenance

- timestamp: 2026-10-18T192436Z
- repo commit: 1c9af21-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- set: content
- collect letters calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- collect labels-content calib-600: .cache/collect/gemma-4-31b/calib-600-content.jsonl.gz
- collect labels-content index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-content.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz
- collect labels-content image dev: .cache/vision-collect/gemma-4-31b/labels-content/dev.jsonl.gz
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
- labels-content: 3.971

## all (1462 rows)

vision_compare: `2026-10-18T192512Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 77.06 | baseline | 0.800 | 0.0861 |  | 0.6166 |  |  |
| labels-content | 76.54 | -0.52 [-1.72, +0.63] | 0.798 | 0.0723 | -0.0138 | 0.6287 | +0.0121 | 0.9514 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-content |
|---|---|---|---|
| overall | all | 0.124 | 0.104 |
| type | choice | 0.124 | 0.104 |
| options | 2 | 0.043 | 0.045 |
| options | 3-5 | 0.062 | 0.053 |
| options | 6-26 | 0.448 | 0.356 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 227 312 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 186 157 169 147 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 50 37 29 36 31 33 15 12 9 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 2 | chosen | 226 313 |
| labels-content | 2 | gold | 247 292 |
| labels-content | 3-5 | chosen | 186 162 164 148 2 |
| labels-content | 3-5 | gold | 187 155 175 143 2 |
| labels-content | 6-26 | chosen | 47 46 25 33 37 24 15 9 14 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |


## pure (1462 rows)

vision_compare: `2026-10-18T192515Z-compare-pure/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 77.06 | baseline | 0.800 | 0.0861 |  | 0.6166 |  |  |
| labels-content | 76.54 | -0.52 [-1.72, +0.63] | 0.798 | 0.0723 | -0.0138 | 0.6287 | +0.0121 | 0.9514 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-content |
|---|---|---|---|
| overall | all | 0.124 | 0.104 |
| type | choice | 0.124 | 0.104 |
| options | 2 | 0.043 | 0.045 |
| options | 3-5 | 0.062 | 0.053 |
| options | 6-26 | 0.448 | 0.356 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 227 312 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 186 157 169 147 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 50 37 29 36 31 33 15 12 9 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 2 | chosen | 226 313 |
| labels-content | 2 | gold | 247 292 |
| labels-content | 3-5 | chosen | 186 162 164 148 2 |
| labels-content | 3-5 | gold | 187 155 175 143 2 |
| labels-content | 6-26 | chosen | 47 46 25 33 37 24 15 9 14 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

