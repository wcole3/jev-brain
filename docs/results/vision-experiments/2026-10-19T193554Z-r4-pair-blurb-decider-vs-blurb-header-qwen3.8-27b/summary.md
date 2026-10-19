# qwen3.8-27b R4 pair screen: blurb-decider vs blurb-header, image dev

## Provenance

- timestamp: 2026-10-19T193554Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- title: R4 pair screen
- set: blurb-decider
- control: blurb-header
- collect blurb-header calib-600: .cache/collect/qwen3.8-27b/calib-600-blurb-header.jsonl.gz
- collect blurb-header index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-blurb-header.jsonl.gz
- collect blurb-decider calib-600: .cache/collect/qwen3.8-27b/calib-600-blurb-decider.jsonl.gz
- collect blurb-decider index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-blurb-decider.jsonl.gz
- collect blurb-header image dev: .cache/vision-collect/qwen3.8-27b/r4-blurb-header/dev.jsonl.gz
- collect blurb-decider image dev: .cache/vision-collect/qwen3.8-27b/r4-blurb-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered

Reports only; the owner picks.

## T (choice, from each arm's text calib-600 fit)

- blurb-header: 1.567
- blurb-decider: 1.546

## all (1462 rows)

vision_compare: `2026-10-19T193619Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| blurb-header | 73.66 | baseline | 0.772 | 0.0631 |  | 0.6059 |  |  |
| blurb-decider | 72.96 | -0.70 [-2.58, +1.17] | 0.767 | 0.0893 | +0.0262 | 0.6333 | +0.0275 | 0.9248 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | blurb-header | blurb-decider |
|---|---|---|---|
| overall | all | 0.172 | 0.174 |
| type | choice | 0.172 | 0.174 |
| options | 2 | 0.076 | 0.078 |
| options | 3-5 | 0.119 | 0.139 |
| options | 6-26 | 0.506 | 0.464 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| blurb-header | 2 | chosen | 247 292 |
| blurb-header | 2 | gold | 247 292 |
| blurb-header | 3-5 | chosen | 191 144 186 139 2 |
| blurb-header | 3-5 | gold | 187 155 175 143 2 |
| blurb-header | 6-26 | chosen | 65 46 50 29 19 13 13 6 6 14 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| blurb-header | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| blurb-decider | 2 | chosen | 257 282 |
| blurb-decider | 2 | gold | 247 292 |
| blurb-decider | 3-5 | chosen | 185 146 187 142 2 |
| blurb-decider | 3-5 | gold | 187 155 175 143 2 |
| blurb-decider | 6-26 | chosen | 70 40 53 31 19 16 12 6 5 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| blurb-decider | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

