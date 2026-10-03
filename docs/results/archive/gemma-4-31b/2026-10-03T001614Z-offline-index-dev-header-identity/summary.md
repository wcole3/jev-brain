# gemma-4-31b offline: index-dev

## Provenance

- timestamp: 2026-10-03T001614Z
- repo commit: ae318d3
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- split: index-dev
- collected: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'header', 'orders': 'identity', 'calibration': {'T': {'choice': 4.262737987560785, 'score': 5.603443226920255, 'noul': 7.608748625511332}, 'b': 0.0, 'source': 'gemma-4-31b/header/calibration.json', 'orders': 'identity'}}

Status: ok 7989, unsupported 1

All rows (refused questions count as wrong): n 14684, refused 4, accuracy 0.789

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14680 | 0.789 | 0.126 | 0.814 | 0.340 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14537 | 0.789 | 0.126 | 0.818 | 0.341 |
| noul | 143 | 0.832 | 0.090 | 0.430 | 0.253 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14680 | 0.789 | 0.126 | 0.814 | 0.340 |

Noul: 143 rows, said yes 71, gold yes 57, false no 5, false yes 19

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.969 | 0.021 | 0.109 | 0.054 |
| index/ANLI | 171 | 0.801 | 0.144 | 0.716 | 0.340 |
| index/API-Bank | 27 | 0.889 | 0.091 | 0.768 | 0.212 |
| index/ARC-Challenge | 62 | 0.984 | 0.042 | 0.058 | 0.021 |
| index/ARC-Easy | 126 | 0.984 | 0.034 | 0.058 | 0.023 |
| index/Amazon ESCI | 266 | 0.643 | 0.281 | 1.434 | 0.617 |
| index/BANKING77 | 164 | 0.768 | 0.115 | 1.347 | 0.366 |
| index/BBH fixed-option tasks | 293 | 0.724 | 0.164 | 0.906 | 0.432 |
| index/BFCL | 258 | 0.992 | 0.004 | 0.025 | 0.012 |
| index/BPoMP | 258 | 0.880 | 0.093 | 0.400 | 0.205 |
| index/BRIGHT | 16 | 0.625 | 0.313 | 1.270 | 0.644 |
| index/CLINC150+OOS | 293 | 0.891 | 0.173 | 0.743 | 0.203 |
| index/CLadder | 266 | 0.797 | 0.166 | 0.718 | 0.353 |
| index/CRUXEval | 30 | 0.700 | 0.177 | 0.874 | 0.483 |
| index/ChessBench | 266 | 0.222 | 0.216 | 3.177 | 0.957 |
| index/ContractNLI | 102 | 0.824 | 0.125 | 0.608 | 0.298 |
| index/FinEntity | 111 | 0.937 | 0.046 | 0.190 | 0.105 |
| index/ForecastBench | 539 | 0.711 | 0.187 | 0.824 | 0.466 |
| index/GPQA Diamond | 11 | 0.455 | 0.418 | 1.350 | 0.712 |
| index/GSM8K | 142 | 0.845 | 0.121 | 0.484 | 0.218 |
| index/HLE | 27 | 0.185 | 0.557 | 2.800 | 1.212 |
| index/Habermas Machine | 90 | 0.411 | 0.438 | 1.919 | 0.921 |
| index/HellaSwag | 534 | 0.918 | 0.029 | 0.243 | 0.119 |
| index/HoVer claim verification | 213 | 0.775 | 0.207 | 0.938 | 0.418 |
| index/Home appliance simulator | 90 | 0.956 | 0.030 | 0.159 | 0.076 |
| index/Humicroedit | 140 | 0.636 | 0.314 | 1.291 | 0.642 |
| index/MMLU | 747 | 0.862 | 0.055 | 0.436 | 0.214 |
| index/MMLU-Pro | 641 | 0.686 | 0.076 | 1.081 | 0.448 |
| index/MuSR | 40 | 0.650 | 0.287 | 1.130 | 0.568 |
| index/NLI4CT | 293 | 0.799 | 0.172 | 0.786 | 0.354 |
| index/New Yorker caption matching | 28 | 0.857 | 0.084 | 0.479 | 0.220 |
| index/POP909-CL | 106 | 0.443 | 0.175 | 2.848 | 0.763 |
| index/PhishNChips phishing decisions | 106 | 0.981 | 0.020 | 0.050 | 0.030 |
| index/RAGTruth response-level hallucination | 143 | 0.832 | 0.090 | 0.430 | 0.253 |
| index/RouterBench | 1062 | 0.162 | 0.644 | 3.766 | 1.376 |
| index/SATA-Bench | 823 | 0.869 | 0.102 | 0.461 | 0.227 |
| index/SGD/SGD-X | 133 | 0.105 | 0.778 | 2.912 | 1.519 |
| index/SimpleBench | 1 | 1.000 | 0.067 | 0.069 | 0.006 |
| index/ToolRet | 46 | 0.935 | 0.064 | 0.299 | 0.128 |
| index/VAST | 160 | 0.688 | 0.266 | 1.267 | 0.560 |
| index/When2Call MCQ | 195 | 0.831 | 0.094 | 0.598 | 0.281 |
| index/WinoGrande | 68 | 0.926 | 0.082 | 0.257 | 0.145 |
| index/cfcolor | 266 | 0.639 | 0.321 | 1.407 | 0.643 |
| index/iSarcasmEval | 620 | 0.760 | 0.200 | 0.737 | 0.399 |
