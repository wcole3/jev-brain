# qwen3.8-27b R3 label screen: lower vs letters, image dev

## Provenance

- timestamp: 2026-10-18T220610Z
- repo commit: e4d2608-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: lower
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-lower calib-600: .cache/collect/qwen3.8-27b/calib-600-lower.jsonl.gz
- collect labels-lower index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-lower.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-lower image dev: .cache/vision-collect/qwen3.8-27b/labels-lower/dev.jsonl.gz
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
- labels-lower: 1.490

## all (1462 rows)

vision_compare: `2026-10-18T220656Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.31 | baseline | 0.769 | 0.0376 |  | 0.6008 |  |  |
| labels-lower | 73.16 | -0.15 [-1.52, +1.20] | 0.765 | 0.0402 | +0.0026 | 0.6105 | +0.0096 | 0.9460 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-lower |
|---|---|---|---|
| overall | all | 0.202 | 0.178 |
| type | choice | 0.202 | 0.178 |
| options | 2 | 0.106 | 0.091 |
| options | 3-5 | 0.162 | 0.133 |
| options | 6-26 | 0.506 | 0.471 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 226 313 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 141 196 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 41 38 29 19 15 12 6 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-lower | 2 | chosen | 235 304 |
| labels-lower | 2 | gold | 247 292 |
| labels-lower | 3-5 | chosen | 187 150 188 135 2 |
| labels-lower | 3-5 | gold | 187 155 175 143 2 |
| labels-lower | 6-26 | chosen | 73 43 32 34 20 19 14 8 7 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-lower | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |


## pure (1462 rows)

vision_compare: `2026-10-18T220700Z-compare-pure/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.31 | baseline | 0.769 | 0.0376 |  | 0.6008 |  |  |
| labels-lower | 73.16 | -0.15 [-1.52, +1.20] | 0.765 | 0.0402 | +0.0026 | 0.6105 | +0.0096 | 0.9460 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-lower |
|---|---|---|---|
| overall | all | 0.202 | 0.178 |
| type | choice | 0.202 | 0.178 |
| options | 2 | 0.106 | 0.091 |
| options | 3-5 | 0.162 | 0.133 |
| options | 6-26 | 0.506 | 0.471 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 226 313 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 141 196 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 41 38 29 19 15 12 6 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-lower | 2 | chosen | 235 304 |
| labels-lower | 2 | gold | 247 292 |
| labels-lower | 3-5 | chosen | 187 150 188 135 2 |
| labels-lower | 3-5 | gold | 187 155 175 143 2 |
| labels-lower | 6-26 | chosen | 73 43 32 34 20 19 14 8 7 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-lower | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

