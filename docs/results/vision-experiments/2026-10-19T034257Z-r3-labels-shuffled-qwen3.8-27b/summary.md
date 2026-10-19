# qwen3.8-27b R3 label screen: shuffled vs letters, image dev

## Provenance

- timestamp: 2026-10-19T034257Z
- repo commit: 8d38bd7-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: shuffled
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-shuffled calib-600: .cache/collect/qwen3.8-27b/calib-600-shuffled.jsonl.gz
- collect labels-shuffled index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-shuffled.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-shuffled image dev: .cache/vision-collect/qwen3.8-27b/labels-shuffled/dev.jsonl.gz
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
- labels-shuffled: 1.440

## all (1462 rows)

vision_compare: `2026-10-19T034336Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.31 | baseline | 0.769 | 0.0376 |  | 0.6008 |  |  |
| labels-shuffled | 71.88 | -1.42 [-3.63, +0.71] | 0.754 | 0.0508 | +0.0132 | 0.6402 | +0.0394 | 0.8550 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled |
|---|---|---|---|
| overall | all | 0.202 | 0.170 |
| type | choice | 0.202 | 0.170 |
| options | 2 | 0.106 | 0.071 |
| options | 3-5 | 0.162 | 0.094 |
| options | 6-26 | 0.506 | 0.567 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 226 313 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 141 196 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 41 38 29 19 15 12 6 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-shuffled | 2 | chosen | 240 299 |
| labels-shuffled | 2 | gold | 247 292 |
| labels-shuffled | 3-5 | chosen | 202 165 153 139 3 |
| labels-shuffled | 3-5 | gold | 187 155 175 143 2 |
| labels-shuffled | 6-26 | chosen | 72 29 2 20 17 69 30 4 1 17 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-shuffled | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |


## pure (1462 rows)

vision_compare: `2026-10-19T034339Z-compare-pure/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.31 | baseline | 0.769 | 0.0376 |  | 0.6008 |  |  |
| labels-shuffled | 71.88 | -1.42 [-3.63, +0.71] | 0.754 | 0.0508 | +0.0132 | 0.6402 | +0.0394 | 0.8550 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-shuffled |
|---|---|---|---|
| overall | all | 0.202 | 0.170 |
| type | choice | 0.202 | 0.170 |
| options | 2 | 0.106 | 0.071 |
| options | 3-5 | 0.162 | 0.094 |
| options | 6-26 | 0.506 | 0.567 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 226 313 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 141 196 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 41 38 29 19 15 12 6 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-shuffled | 2 | chosen | 240 299 |
| labels-shuffled | 2 | gold | 247 292 |
| labels-shuffled | 3-5 | chosen | 202 165 153 139 3 |
| labels-shuffled | 3-5 | gold | 187 155 175 143 2 |
| labels-shuffled | 6-26 | chosen | 72 29 2 20 17 69 30 4 1 17 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-shuffled | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

