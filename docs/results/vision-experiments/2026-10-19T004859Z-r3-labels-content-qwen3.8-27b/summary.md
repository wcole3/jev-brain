# qwen3.8-27b R3 label screen: content vs letters, image dev

## Provenance

- timestamp: 2026-10-19T004859Z
- repo commit: 76fcba1-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: content
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-content calib-600: .cache/collect/qwen3.8-27b/calib-600-content.jsonl.gz
- collect labels-content index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-content.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-content image dev: .cache/vision-collect/qwen3.8-27b/labels-content/dev.jsonl.gz
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
- labels-content: 1.352

## all (1462 rows)

vision_compare: `2026-10-19T004934Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.31 | baseline | 0.769 | 0.0376 |  | 0.6008 |  |  |
| labels-content | 72.63 | -0.68 [-2.51, +1.15] | 0.767 | 0.0256 | -0.0120 | 0.6262 | +0.0254 | 0.8906 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-content |
|---|---|---|---|
| overall | all | 0.202 | 0.159 |
| type | choice | 0.202 | 0.159 |
| options | 2 | 0.106 | 0.078 |
| options | 3-5 | 0.162 | 0.134 |
| options | 6-26 | 0.506 | 0.387 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 226 313 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 141 196 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 41 38 29 19 15 12 6 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 2 | chosen | 214 325 |
| labels-content | 2 | gold | 247 292 |
| labels-content | 3-5 | chosen | 170 155 197 138 2 |
| labels-content | 3-5 | gold | 187 155 175 143 2 |
| labels-content | 6-26 | chosen | 24 35 66 54 19 27 13 6 5 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |


## pure (1462 rows)

vision_compare: `2026-10-19T004938Z-compare-pure/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.31 | baseline | 0.769 | 0.0376 |  | 0.6008 |  |  |
| labels-content | 72.63 | -0.68 [-2.51, +1.15] | 0.767 | 0.0256 | -0.0120 | 0.6262 | +0.0254 | 0.8906 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-content |
|---|---|---|---|
| overall | all | 0.202 | 0.159 |
| type | choice | 0.202 | 0.159 |
| options | 2 | 0.106 | 0.078 |
| options | 3-5 | 0.162 | 0.134 |
| options | 6-26 | 0.506 | 0.387 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 226 313 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 141 196 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 41 38 29 19 15 12 6 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 2 | chosen | 214 325 |
| labels-content | 2 | gold | 247 292 |
| labels-content | 3-5 | chosen | 170 155 197 138 2 |
| labels-content | 3-5 | gold | 187 155 175 143 2 |
| labels-content | 6-26 | chosen | 24 35 66 54 19 27 13 6 5 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-content | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

