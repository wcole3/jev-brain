# qwen3.8-27b R3 label screen: digits vs letters, image dev

## Provenance

- timestamp: 2026-10-18T232927Z
- repo commit: 2e72beb-dirty
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- set: digits
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- collect labels-digits calib-600: .cache/collect/qwen3.8-27b/calib-600-digits.jsonl.gz
- collect labels-digits index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-digits.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz
- collect labels-digits image dev: .cache/vision-collect/qwen3.8-27b/labels-digits/dev.jsonl.gz
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

- letters: 1.491
- labels-digits: 1.531

## all (1462 rows)

vision_compare: `2026-10-18T233019Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.31 | baseline | 0.769 | 0.0376 |  | 0.6008 |  |  |
| labels-digits | 73.16 | -0.15 [-1.79, +1.50] | 0.765 | 0.0546 | +0.0170 | 0.6314 | +0.0306 | 0.9261 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-digits |
|---|---|---|---|
| overall | all | 0.202 | 0.185 |
| type | choice | 0.202 | 0.185 |
| options | 2 | 0.106 | 0.113 |
| options | 3-5 | 0.162 | 0.133 |
| options | 6-26 | 0.506 | 0.467 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 226 313 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 141 196 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 41 38 29 19 15 12 6 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 2 | chosen | 221 318 |
| labels-digits | 2 | gold | 247 292 |
| labels-digits | 3-5 | chosen | 199 141 168 148 6 |
| labels-digits | 3-5 | gold | 187 155 175 143 2 |
| labels-digits | 6-26 | chosen | 110 30 32 21 21 12 13 5 5 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |


## pure (1367 rows)

vision_compare: `2026-10-18T233022Z-compare-pure/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.29 | baseline | 0.799 | 0.0408 |  | 0.5153 |  |  |
| labels-digits | 72.91 | -0.38 [-2.02, +1.32] | 0.794 | 0.0572 | +0.0164 | 0.5484 | +0.0331 | 0.9217 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | labels-digits |
|---|---|---|---|
| overall | all | 0.186 | 0.168 |
| type | choice | 0.186 | 0.168 |
| options | 2 | 0.106 | 0.113 |
| options | 3-5 | 0.162 | 0.133 |
| options | 6-26 | 0.542 | 0.482 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 226 313 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 141 196 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 58 38 20 23 12 10 2 1 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 25 24 21 33 34 24 3 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 2 | chosen | 221 318 |
| labels-digits | 2 | gold | 247 292 |
| labels-digits | 3-5 | chosen | 199 141 168 148 6 |
| labels-digits | 3-5 | gold | 187 155 175 143 2 |
| labels-digits | 6-26 | chosen | 86 27 13 15 14 7 3 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| labels-digits | 6-26 | gold | 25 24 21 33 34 24 3 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

