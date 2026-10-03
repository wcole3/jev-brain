# qwen3.6-27b offline: index-dev

## Provenance

- timestamp: 2026-10-02T163641Z
- repo commit: e93c263
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: index-dev
- collected: .cache/collect/qwen3.6-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.943, 'score': 1.943, 'noul': 1.943}, 'b': 0.0, 'source': 'override T=1.943', 'orders': None}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.761

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.761 | 0.025 | 0.710 | 0.320 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.760 | 0.026 | 0.712 | 0.320 |
| noul | 143 | 0.846 | 0.123 | 0.470 | 0.276 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.761 | 0.025 | 0.710 | 0.320 |

Noul: 143 rows, said yes 71, gold yes 57, false no 4, false yes 18

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.935 | 0.040 | 0.161 | 0.087 |
| index/ANLI | 171 | 0.760 | 0.061 | 0.631 | 0.358 |
| index/API-Bank | 27 | 0.852 | 0.154 | 0.929 | 0.257 |
| index/ARC-Challenge | 62 | 0.968 | 0.086 | 0.146 | 0.060 |
| index/ARC-Easy | 126 | 0.968 | 0.061 | 0.084 | 0.028 |
| index/Amazon ESCI | 266 | 0.609 | 0.135 | 0.912 | 0.514 |
| index/BANKING77 | 164 | 0.695 | 0.145 | 1.480 | 0.441 |
| index/BBH fixed-option tasks | 293 | 0.734 | 0.095 | 0.679 | 0.351 |
| index/BFCL | 258 | 0.996 | 0.042 | 0.046 | 0.012 |
| index/BPoMP | 258 | 0.868 | 0.171 | 0.389 | 0.228 |
| index/BRIGHT | 20 | 0.650 | 0.287 | 0.791 | 0.497 |
| index/CLINC150+OOS | 293 | 0.860 | 0.237 | 0.824 | 0.277 |
| index/CLadder | 266 | 0.692 | 0.077 | 0.567 | 0.385 |
| index/CRUXEval | 30 | 0.567 | 0.293 | 0.862 | 0.489 |
| index/ChessBench | 266 | 0.150 | 0.146 | 3.357 | 0.952 |
| index/ContractNLI | 102 | 0.775 | 0.172 | 0.639 | 0.347 |
| index/FinEntity | 111 | 0.856 | 0.046 | 0.440 | 0.235 |
| index/ForecastBench | 539 | 0.711 | 0.087 | 0.558 | 0.375 |
| index/GPQA Diamond | 11 | 0.364 | 0.361 | 1.007 | 0.561 |
| index/GSM8K | 142 | 0.641 | 0.178 | 1.070 | 0.511 |
| index/HLE | 27 | 0.222 | 0.251 | 1.901 | 0.913 |
| index/Habermas Machine | 90 | 0.344 | 0.246 | 1.400 | 0.770 |
| index/HellaSwag | 534 | 0.953 | 0.109 | 0.217 | 0.084 |
| index/HoVer claim verification | 213 | 0.690 | 0.134 | 0.617 | 0.422 |
| index/Home appliance simulator | 90 | 0.944 | 0.087 | 0.235 | 0.096 |
| index/Humicroedit | 140 | 0.571 | 0.167 | 0.747 | 0.530 |
| index/MMLU | 747 | 0.851 | 0.070 | 0.441 | 0.219 |
| index/MMLU-Pro | 641 | 0.637 | 0.089 | 1.147 | 0.493 |
| index/MuSR | 40 | 0.500 | 0.217 | 0.906 | 0.561 |
| index/NLI4CT | 293 | 0.843 | 0.063 | 0.415 | 0.258 |
| index/New Yorker caption matching | 28 | 0.750 | 0.288 | 0.701 | 0.349 |
| index/POP909-CL | 106 | 0.198 | 0.111 | 4.293 | 0.948 |
| index/PhishNChips phishing decisions | 106 | 0.736 | 0.121 | 0.539 | 0.361 |
| index/RAGTruth response-level hallucination | 143 | 0.846 | 0.123 | 0.470 | 0.276 |
| index/RouterBench | 1062 | 0.148 | 0.359 | 3.021 | 1.111 |
| index/SATA-Bench | 823 | 0.866 | 0.036 | 0.313 | 0.190 |
| index/SGD/SGD-X | 133 | 0.165 | 0.425 | 1.366 | 0.887 |
| index/SimpleBench | 1 | 0.000 | 0.580 | 2.088 | 1.135 |
| index/ToolRet | 46 | 0.891 | 0.106 | 0.200 | 0.135 |
| index/VAST | 160 | 0.594 | 0.151 | 1.001 | 0.573 |
| index/When2Call MCQ | 195 | 0.815 | 0.093 | 0.546 | 0.285 |
| index/WinoGrande | 68 | 0.897 | 0.168 | 0.353 | 0.201 |
| index/cfcolor | 266 | 0.609 | 0.050 | 0.667 | 0.472 |
| index/iSarcasmEval | 620 | 0.776 | 0.048 | 0.507 | 0.333 |
