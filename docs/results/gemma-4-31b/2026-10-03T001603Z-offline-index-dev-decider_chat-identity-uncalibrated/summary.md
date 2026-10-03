# gemma-4-31b offline: index-dev

## Provenance

- timestamp: 2026-10-03T001603Z
- repo commit: ae318d3
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- split: index-dev
- collected: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.749

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.749 | 0.241 | 3.486 | 0.488 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.748 | 0.242 | 3.494 | 0.490 |
| noul | 143 | 0.846 | 0.158 | 2.648 | 0.310 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.749 | 0.241 | 3.486 | 0.488 |

Noul: 143 rows, said yes 69, gold yes 57, false no 5, false yes 17

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.871 | 0.126 | 1.905 | 0.252 |
| index/ANLI | 171 | 0.737 | 0.261 | 3.295 | 0.521 |
| index/API-Bank | 27 | 0.889 | 0.111 | 1.897 | 0.222 |
| index/ARC-Challenge | 62 | 1.000 | 0.000 | 0.000 | 0.000 |
| index/ARC-Easy | 126 | 0.984 | 0.016 | 0.173 | 0.031 |
| index/Amazon ESCI | 266 | 0.620 | 0.371 | 5.963 | 0.748 |
| index/BANKING77 | 164 | 0.744 | 0.248 | 4.404 | 0.494 |
| index/BBH fixed-option tasks | 293 | 0.737 | 0.247 | 2.852 | 0.507 |
| index/BFCL | 258 | 1.000 | 0.000 | 0.000 | 0.000 |
| index/BPoMP | 258 | 0.884 | 0.120 | 1.543 | 0.234 |
| index/BRIGHT | 20 | 0.600 | 0.400 | 7.296 | 0.800 |
| index/CLINC150+OOS | 293 | 0.891 | 0.111 | 1.741 | 0.219 |
| index/CLadder | 266 | 0.729 | 0.271 | 3.275 | 0.534 |
| index/CRUXEval | 30 | 0.700 | 0.290 | 2.989 | 0.580 |
| index/ChessBench | 266 | 0.203 | 0.736 | 9.485 | 1.504 |
| index/ContractNLI | 102 | 0.725 | 0.274 | 3.771 | 0.546 |
| index/FinEntity | 111 | 0.901 | 0.092 | 0.973 | 0.187 |
| index/ForecastBench | 539 | 0.751 | 0.235 | 2.966 | 0.473 |
| index/GPQA Diamond | 11 | 0.455 | 0.514 | 3.747 | 1.024 |
| index/GSM8K | 142 | 0.873 | 0.098 | 0.672 | 0.220 |
| index/HLE | 27 | 0.148 | 0.772 | 9.503 | 1.615 |
| index/Habermas Machine | 90 | 0.389 | 0.599 | 7.154 | 1.194 |
| index/HellaSwag | 534 | 0.918 | 0.079 | 0.718 | 0.160 |
| index/HoVer claim verification | 213 | 0.798 | 0.203 | 3.282 | 0.404 |
| index/Home appliance simulator | 90 | 0.967 | 0.036 | 0.320 | 0.068 |
| index/Humicroedit | 140 | 0.621 | 0.375 | 4.854 | 0.741 |
| index/MMLU | 747 | 0.851 | 0.145 | 1.525 | 0.290 |
| index/MMLU-Pro | 641 | 0.672 | 0.295 | 3.144 | 0.609 |
| index/MuSR | 40 | 0.600 | 0.392 | 4.905 | 0.766 |
| index/NLI4CT | 293 | 0.829 | 0.170 | 2.422 | 0.336 |
| index/New Yorker caption matching | 28 | 0.857 | 0.140 | 1.398 | 0.280 |
| index/POP909-CL | 106 | 0.340 | 0.468 | 6.479 | 1.081 |
| index/PhishNChips phishing decisions | 106 | 0.877 | 0.118 | 1.395 | 0.232 |
| index/RAGTruth response-level hallucination | 143 | 0.846 | 0.158 | 2.648 | 0.310 |
| index/RouterBench | 1062 | 0.157 | 0.824 | 14.200 | 1.656 |
| index/SATA-Bench | 823 | 0.844 | 0.153 | 1.950 | 0.305 |
| index/SGD/SGD-X | 133 | 0.075 | 0.920 | 13.637 | 1.836 |
| index/SimpleBench | 1 | 1.000 | 0.000 | 0.000 | 0.000 |
| index/ToolRet | 46 | 0.913 | 0.087 | 1.455 | 0.174 |
| index/VAST | 160 | 0.681 | 0.317 | 4.777 | 0.631 |
| index/When2Call MCQ | 195 | 0.810 | 0.178 | 2.427 | 0.362 |
| index/WinoGrande | 68 | 0.882 | 0.117 | 1.726 | 0.235 |
| index/cfcolor | 266 | 0.620 | 0.381 | 5.124 | 0.754 |
| index/iSarcasmEval | 620 | 0.697 | 0.302 | 3.854 | 0.600 |
