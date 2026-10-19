# qwen3.8-27b R4 pair screen: blurb-header vs letters, image dev

## Provenance

- timestamp: 2026-10-19T185753Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- title: R4 pair screen
- set: blurb-header
- control: letters
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib-600-letters.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-letters.jsonl.gz
- collect blurb-header calib-600: .cache/collect/qwen3.8-27b/calib-600-blurb-header.jsonl.gz
- collect blurb-header index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-blurb-header.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/labels-letters/dev.jsonl.gz
- collect blurb-header image dev: .cache/vision-collect/qwen3.8-27b/r4-blurb-header/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered

Reports only; the owner picks.

## T (choice, from each arm's text calib-600 fit)

- letters: 1.492
- blurb-header: 1.567

## all (1462 rows)

vision_compare: `2026-10-19T185820Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.49 | baseline | 0.770 | 0.0399 |  | 0.5999 |  |  |
| blurb-header | 73.66 | +0.17 [-1.53, +1.89] | 0.772 | 0.0631 | +0.0232 | 0.6059 | +0.0059 | 0.9357 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | blurb-header |
|---|---|---|---|
| overall | all | 0.204 | 0.172 |
| type | choice | 0.204 | 0.172 |
| options | 2 | 0.102 | 0.076 |
| options | 3-5 | 0.171 | 0.119 |
| options | 6-26 | 0.498 | 0.506 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 227 312 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 139 198 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 42 38 28 19 15 13 5 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| blurb-header | 2 | chosen | 247 292 |
| blurb-header | 2 | gold | 247 292 |
| blurb-header | 3-5 | chosen | 191 144 186 139 2 |
| blurb-header | 3-5 | gold | 187 155 175 143 2 |
| blurb-header | 6-26 | chosen | 65 46 50 29 19 13 13 6 6 14 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| blurb-header | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

