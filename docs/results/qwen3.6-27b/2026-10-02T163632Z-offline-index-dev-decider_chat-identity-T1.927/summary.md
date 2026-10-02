# qwen3.6-27b offline: index-dev

## Provenance

- timestamp: 2026-10-02T163632Z
- repo commit: e93c263
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: index-dev
- collected: .cache/collect/qwen3.6-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.927, 'score': 1.927, 'noul': 1.927}, 'b': 0.0, 'source': 'override T=1.927', 'orders': None}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.761

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.761 | 0.025 | 0.710 | 0.320 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.760 | 0.027 | 0.712 | 0.320 |
| noul | 143 | 0.846 | 0.112 | 0.470 | 0.276 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.761 | 0.025 | 0.710 | 0.320 |

Noul: 143 rows, said yes 71, gold yes 57, false no 4, false yes 18

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.935 | 0.039 | 0.160 | 0.087 |
| index/ANLI | 171 | 0.760 | 0.061 | 0.630 | 0.358 |
| index/API-Bank | 27 | 0.852 | 0.159 | 0.928 | 0.256 |
| index/ARC-Challenge | 62 | 0.968 | 0.076 | 0.145 | 0.060 |
| index/ARC-Easy | 126 | 0.968 | 0.060 | 0.083 | 0.027 |
| index/Amazon ESCI | 266 | 0.609 | 0.140 | 0.913 | 0.515 |
| index/BANKING77 | 164 | 0.695 | 0.136 | 1.475 | 0.439 |
| index/BBH fixed-option tasks | 293 | 0.734 | 0.094 | 0.677 | 0.351 |
| index/BFCL | 258 | 0.996 | 0.041 | 0.045 | 0.012 |
| index/BPoMP | 258 | 0.868 | 0.170 | 0.387 | 0.227 |
| index/BRIGHT | 20 | 0.650 | 0.287 | 0.795 | 0.498 |
| index/CLINC150+OOS | 293 | 0.860 | 0.229 | 0.814 | 0.273 |
| index/CLadder | 266 | 0.692 | 0.076 | 0.567 | 0.385 |
| index/CRUXEval | 30 | 0.567 | 0.293 | 0.862 | 0.489 |
| index/ChessBench | 266 | 0.150 | 0.149 | 3.365 | 0.953 |
| index/ContractNLI | 102 | 0.775 | 0.157 | 0.638 | 0.346 |
| index/FinEntity | 111 | 0.856 | 0.047 | 0.439 | 0.234 |
| index/ForecastBench | 539 | 0.711 | 0.086 | 0.557 | 0.375 |
| index/GPQA Diamond | 11 | 0.364 | 0.361 | 1.006 | 0.561 |
| index/GSM8K | 142 | 0.641 | 0.175 | 1.067 | 0.510 |
| index/HLE | 27 | 0.222 | 0.302 | 1.905 | 0.914 |
| index/Habermas Machine | 90 | 0.344 | 0.250 | 1.404 | 0.772 |
| index/HellaSwag | 534 | 0.953 | 0.107 | 0.215 | 0.083 |
| index/HoVer claim verification | 213 | 0.690 | 0.139 | 0.618 | 0.423 |
| index/Home appliance simulator | 90 | 0.944 | 0.085 | 0.234 | 0.095 |
| index/Humicroedit | 140 | 0.571 | 0.170 | 0.749 | 0.531 |
| index/MMLU | 747 | 0.851 | 0.069 | 0.439 | 0.219 |
| index/MMLU-Pro | 641 | 0.637 | 0.086 | 1.145 | 0.493 |
| index/MuSR | 40 | 0.500 | 0.217 | 0.908 | 0.562 |
| index/NLI4CT | 293 | 0.843 | 0.062 | 0.415 | 0.257 |
| index/New Yorker caption matching | 28 | 0.750 | 0.287 | 0.699 | 0.348 |
| index/POP909-CL | 106 | 0.198 | 0.103 | 4.295 | 0.947 |
| index/PhishNChips phishing decisions | 106 | 0.736 | 0.121 | 0.538 | 0.361 |
| index/RAGTruth response-level hallucination | 143 | 0.846 | 0.112 | 0.470 | 0.276 |
| index/RouterBench | 1062 | 0.148 | 0.362 | 3.033 | 1.114 |
| index/SATA-Bench | 823 | 0.866 | 0.035 | 0.312 | 0.190 |
| index/SGD/SGD-X | 133 | 0.165 | 0.427 | 1.370 | 0.889 |
| index/SimpleBench | 1 | 0.000 | 0.584 | 2.095 | 1.140 |
| index/ToolRet | 46 | 0.891 | 0.105 | 0.200 | 0.135 |
| index/VAST | 160 | 0.594 | 0.148 | 1.003 | 0.574 |
| index/When2Call MCQ | 195 | 0.815 | 0.091 | 0.545 | 0.285 |
| index/WinoGrande | 68 | 0.897 | 0.166 | 0.352 | 0.200 |
| index/cfcolor | 266 | 0.609 | 0.047 | 0.667 | 0.472 |
| index/iSarcasmEval | 620 | 0.776 | 0.049 | 0.507 | 0.333 |
