# qwen3.6-27b offline: index-dev

## Provenance

- timestamp: 2026-10-02T163611Z
- repo commit: e93c263
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: index-dev
- collected: .cache/collect/qwen3.6-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.761

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.761 | 0.108 | 0.887 | 0.348 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.760 | 0.109 | 0.890 | 0.349 |
| noul | 143 | 0.846 | 0.088 | 0.590 | 0.270 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.761 | 0.108 | 0.887 | 0.348 |

Noul: 143 rows, said yes 71, gold yes 57, false no 4, false yes 18

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.935 | 0.028 | 0.149 | 0.091 |
| index/ANLI | 171 | 0.760 | 0.130 | 0.736 | 0.381 |
| index/API-Bank | 27 | 0.852 | 0.127 | 1.342 | 0.259 |
| index/ARC-Challenge | 62 | 0.968 | 0.033 | 0.134 | 0.062 |
| index/ARC-Easy | 126 | 0.968 | 0.023 | 0.038 | 0.027 |
| index/Amazon ESCI | 266 | 0.609 | 0.247 | 1.221 | 0.611 |
| index/BANKING77 | 164 | 0.695 | 0.184 | 1.770 | 0.460 |
| index/BBH fixed-option tasks | 293 | 0.734 | 0.082 | 0.670 | 0.356 |
| index/BFCL | 258 | 0.996 | 0.006 | 0.013 | 0.006 |
| index/BPoMP | 258 | 0.868 | 0.090 | 0.285 | 0.171 |
| index/BRIGHT | 20 | 0.650 | 0.268 | 1.302 | 0.558 |
| index/CLINC150+OOS | 293 | 0.860 | 0.088 | 0.671 | 0.230 |
| index/CLadder | 266 | 0.692 | 0.058 | 0.566 | 0.383 |
| index/CRUXEval | 30 | 0.567 | 0.251 | 0.955 | 0.522 |
| index/ChessBench | 266 | 0.150 | 0.368 | 4.655 | 1.107 |
| index/ContractNLI | 102 | 0.775 | 0.118 | 0.642 | 0.335 |
| index/FinEntity | 111 | 0.856 | 0.097 | 0.496 | 0.240 |
| index/ForecastBench | 539 | 0.711 | 0.048 | 0.517 | 0.351 |
| index/GPQA Diamond | 11 | 0.364 | 0.365 | 0.999 | 0.615 |
| index/GSM8K | 142 | 0.641 | 0.080 | 0.936 | 0.466 |
| index/HLE | 27 | 0.222 | 0.434 | 2.476 | 1.081 |
| index/Habermas Machine | 90 | 0.344 | 0.385 | 1.938 | 0.918 |
| index/HellaSwag | 534 | 0.953 | 0.013 | 0.132 | 0.067 |
| index/HoVer claim verification | 213 | 0.690 | 0.220 | 0.856 | 0.495 |
| index/Home appliance simulator | 90 | 0.944 | 0.033 | 0.223 | 0.094 |
| index/Humicroedit | 140 | 0.571 | 0.273 | 1.014 | 0.625 |
| index/MMLU | 747 | 0.851 | 0.066 | 0.440 | 0.224 |
| index/MMLU-Pro | 641 | 0.637 | 0.103 | 1.214 | 0.504 |
| index/MuSR | 40 | 0.500 | 0.316 | 1.198 | 0.675 |
| index/NLI4CT | 293 | 0.843 | 0.065 | 0.435 | 0.253 |
| index/New Yorker caption matching | 28 | 0.750 | 0.256 | 0.624 | 0.356 |
| index/POP909-CL | 106 | 0.198 | 0.149 | 4.939 | 0.960 |
| index/PhishNChips phishing decisions | 106 | 0.736 | 0.110 | 0.518 | 0.352 |
| index/RAGTruth response-level hallucination | 143 | 0.846 | 0.088 | 0.590 | 0.270 |
| index/RouterBench | 1062 | 0.148 | 0.575 | 4.720 | 1.346 |
| index/SATA-Bench | 823 | 0.866 | 0.059 | 0.331 | 0.198 |
| index/SGD/SGD-X | 133 | 0.165 | 0.586 | 1.907 | 1.170 |
| index/SimpleBench | 1 | 0.000 | 0.870 | 3.139 | 1.676 |
| index/ToolRet | 46 | 0.891 | 0.094 | 0.251 | 0.172 |
| index/VAST | 160 | 0.594 | 0.237 | 1.355 | 0.637 |
| index/When2Call MCQ | 195 | 0.815 | 0.107 | 0.605 | 0.290 |
| index/WinoGrande | 68 | 0.897 | 0.072 | 0.259 | 0.154 |
| index/cfcolor | 266 | 0.609 | 0.143 | 0.747 | 0.515 |
| index/iSarcasmEval | 620 | 0.776 | 0.106 | 0.572 | 0.351 |
