# gemma-4-31b offline: index-dev

## Provenance

- timestamp: 2026-10-03T001624Z
- repo commit: ae318d3
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- split: index-dev
- collected: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'header', 'orders': 'identity', 'calibration': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}

Status: ok 7989, unsupported 1

All rows (refused questions count as wrong): n 14684, refused 4, accuracy 0.789

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14680 | 0.789 | 0.204 | 3.013 | 0.411 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14537 | 0.789 | 0.204 | 3.017 | 0.412 |
| noul | 143 | 0.832 | 0.167 | 2.629 | 0.332 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14680 | 0.789 | 0.204 | 3.013 | 0.411 |

Noul: 143 rows, said yes 71, gold yes 57, false no 5, false yes 19

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.969 | 0.031 | 0.415 | 0.061 |
| index/ANLI | 171 | 0.801 | 0.197 | 2.767 | 0.389 |
| index/API-Bank | 27 | 0.889 | 0.111 | 2.347 | 0.222 |
| index/ARC-Challenge | 62 | 0.984 | 0.016 | 0.083 | 0.032 |
| index/ARC-Easy | 126 | 0.984 | 0.016 | 0.131 | 0.032 |
| index/Amazon ESCI | 266 | 0.643 | 0.354 | 5.708 | 0.712 |
| index/BANKING77 | 164 | 0.768 | 0.236 | 4.212 | 0.466 |
| index/BBH fixed-option tasks | 293 | 0.724 | 0.271 | 3.232 | 0.537 |
| index/BFCL | 258 | 0.992 | 0.008 | 0.079 | 0.015 |
| index/BPoMP | 258 | 0.880 | 0.120 | 1.563 | 0.238 |
| index/BRIGHT | 16 | 0.625 | 0.374 | 5.125 | 0.749 |
| index/CLINC150+OOS | 293 | 0.891 | 0.109 | 1.766 | 0.218 |
| index/CLadder | 266 | 0.797 | 0.198 | 2.875 | 0.396 |
| index/CRUXEval | 30 | 0.700 | 0.282 | 3.111 | 0.551 |
| index/ChessBench | 266 | 0.222 | 0.731 | 9.744 | 1.485 |
| index/ContractNLI | 102 | 0.824 | 0.176 | 2.354 | 0.352 |
| index/FinEntity | 111 | 0.937 | 0.065 | 0.665 | 0.127 |
| index/ForecastBench | 539 | 0.711 | 0.278 | 3.004 | 0.556 |
| index/GPQA Diamond | 11 | 0.455 | 0.490 | 4.114 | 1.014 |
| index/GSM8K | 142 | 0.845 | 0.120 | 0.759 | 0.251 |
| index/HLE | 27 | 0.185 | 0.789 | 10.217 | 1.556 |
| index/Habermas Machine | 90 | 0.411 | 0.577 | 7.306 | 1.145 |
| index/HellaSwag | 534 | 0.918 | 0.078 | 0.699 | 0.155 |
| index/HoVer claim verification | 213 | 0.775 | 0.226 | 3.878 | 0.449 |
| index/Home appliance simulator | 90 | 0.956 | 0.044 | 0.592 | 0.089 |
| index/Humicroedit | 140 | 0.636 | 0.363 | 5.234 | 0.722 |
| index/MMLU | 747 | 0.862 | 0.132 | 1.455 | 0.265 |
| index/MMLU-Pro | 641 | 0.686 | 0.288 | 3.245 | 0.587 |
| index/MuSR | 40 | 0.650 | 0.347 | 4.469 | 0.689 |
| index/NLI4CT | 293 | 0.799 | 0.196 | 3.197 | 0.390 |
| index/New Yorker caption matching | 28 | 0.857 | 0.147 | 1.445 | 0.282 |
| index/POP909-CL | 106 | 0.443 | 0.485 | 6.047 | 1.006 |
| index/PhishNChips phishing decisions | 106 | 0.981 | 0.019 | 0.153 | 0.038 |
| index/RAGTruth response-level hallucination | 143 | 0.832 | 0.167 | 2.629 | 0.332 |
| index/RouterBench | 1062 | 0.162 | 0.826 | 15.008 | 1.655 |
| index/SATA-Bench | 823 | 0.869 | 0.131 | 1.822 | 0.260 |
| index/SGD/SGD-X | 133 | 0.105 | 0.893 | 11.862 | 1.780 |
| index/SimpleBench | 1 | 1.000 | 0.000 | 0.000 | 0.000 |
| index/ToolRet | 46 | 0.935 | 0.065 | 1.238 | 0.130 |
| index/VAST | 160 | 0.688 | 0.318 | 5.098 | 0.628 |
| index/When2Call MCQ | 195 | 0.831 | 0.165 | 2.137 | 0.327 |
| index/WinoGrande | 68 | 0.926 | 0.081 | 0.923 | 0.153 |
| index/cfcolor | 266 | 0.639 | 0.357 | 5.776 | 0.708 |
| index/iSarcasmEval | 620 | 0.760 | 0.240 | 2.937 | 0.477 |
