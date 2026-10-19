# qwen3.8-27b R3 label screen: shuffled-q vs letters, image dev

## Provenance

- timestamp: 2026-10-19T042017Z
- repo commit: 8d38bd7-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: shuffled-q
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-shuffled-q calib-600: .cache/collect/qwen3.8-27b/calib-600-shuffled-q.jsonl.gz
- collect labels-shuffled-q index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-shuffled-q.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-shuffled-q image dev: .cache/vision-collect/qwen3.8-27b/labels-shuffled-q/dev.jsonl.gz
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

- letters: 1.491
- labels-shuffled-q: 1.457

## all (1462 rows)

vision_compare: `2026-10-19T042053Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.31 | baseline | 0.769 | 0.0376 |  | 0.6008 |  |  |
| labels-shuffled-q | 71.62 | -1.69 [-3.82, +0.40] | 0.757 | 0.0388 | +0.0012 | 0.6479 | +0.0470 | 0.8659 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled-q |
|---|---|---|---|
| overall | all | 0.202 | 0.170 |
| type | choice | 0.202 | 0.170 |
| options | 2 | 0.106 | 0.076 |
| options | 3-5 | 0.162 | 0.113 |
| options | 6-26 | 0.506 | 0.506 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 226 313 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 141 196 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 41 38 29 19 15 12 6 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-shuffled-q | 2 | chosen | 247 292 |
| labels-shuffled-q | 2 | gold | 247 292 |
| labels-shuffled-q | 3-5 | chosen | 196 161 164 138 3 |
| labels-shuffled-q | 3-5 | gold | 187 155 175 143 2 |
| labels-shuffled-q | 6-26 | chosen | 86 29 20 26 43 17 10 16 4 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-shuffled-q | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |


## pure (1462 rows)

vision_compare: `2026-10-19T042056Z-compare-pure/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.31 | baseline | 0.769 | 0.0376 |  | 0.6008 |  |  |
| labels-shuffled-q | 71.62 | -1.69 [-3.82, +0.40] | 0.757 | 0.0388 | +0.0012 | 0.6479 | +0.0470 | 0.8659 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled-q |
|---|---|---|---|
| overall | all | 0.202 | 0.170 |
| type | choice | 0.202 | 0.170 |
| options | 2 | 0.106 | 0.076 |
| options | 3-5 | 0.162 | 0.113 |
| options | 6-26 | 0.506 | 0.506 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 226 313 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 141 196 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 41 38 29 19 15 12 6 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-shuffled-q | 2 | chosen | 247 292 |
| labels-shuffled-q | 2 | gold | 247 292 |
| labels-shuffled-q | 3-5 | chosen | 196 161 164 138 3 |
| labels-shuffled-q | 3-5 | gold | 187 155 175 143 2 |
| labels-shuffled-q | 6-26 | chosen | 86 29 20 26 43 17 10 16 4 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-shuffled-q | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

