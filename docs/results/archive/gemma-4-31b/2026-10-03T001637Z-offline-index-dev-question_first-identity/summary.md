# gemma-4-31b offline: index-dev

## Provenance

- timestamp: 2026-10-03T001637Z
- repo commit: ae318d3
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- split: index-dev
- collected: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'question_first', 'orders': 'identity', 'calibration': {'T': {'choice': 3.8391851723192945, 'score': 5.278388968615397, 'noul': 7.266257519634274}, 'b': -0.4595075807224698, 'source': 'gemma-4-31b/question_first/calibration.json', 'orders': 'identity'}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.749

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.749 | 0.163 | 0.982 | 0.407 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.748 | 0.164 | 0.988 | 0.408 |
| noul | 143 | 0.846 | 0.085 | 0.391 | 0.234 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.749 | 0.163 | 0.982 | 0.407 |

Noul: 143 rows, said yes 69, gold yes 57, false no 5, false yes 17

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.900 | 0.077 | 0.370 | 0.176 |
| index/ANLI | 171 | 0.754 | 0.181 | 0.890 | 0.412 |
| index/API-Bank | 27 | 0.889 | 0.146 | 0.693 | 0.188 |
| index/ARC-Challenge | 62 | 1.000 | 0.033 | 0.036 | 0.006 |
| index/ARC-Easy | 126 | 0.984 | 0.027 | 0.065 | 0.027 |
| index/Amazon ESCI | 266 | 0.650 | 0.273 | 1.455 | 0.607 |
| index/BANKING77 | 164 | 0.744 | 0.085 | 1.462 | 0.394 |
| index/BBH fixed-option tasks | 293 | 0.744 | 0.142 | 0.923 | 0.419 |
| index/BFCL | 258 | 0.992 | 0.009 | 0.014 | 0.008 |
| index/BPoMP | 258 | 0.872 | 0.103 | 0.447 | 0.214 |
| index/BRIGHT | 20 | 0.650 | 0.335 | 1.659 | 0.679 |
| index/CLINC150+OOS | 293 | 0.894 | 0.097 | 0.663 | 0.181 |
| index/CLadder | 266 | 0.733 | 0.210 | 0.902 | 0.465 |
| index/CRUXEval | 30 | 0.433 | 0.388 | 1.399 | 0.820 |
| index/ChessBench | 266 | 0.158 | 0.301 | 3.513 | 1.031 |
| index/ContractNLI | 102 | 0.804 | 0.163 | 0.735 | 0.355 |
| index/FinEntity | 111 | 0.928 | 0.049 | 0.192 | 0.109 |
| index/ForecastBench | 539 | 0.755 | 0.184 | 0.872 | 0.433 |
| index/GPQA Diamond | 11 | 0.455 | 0.293 | 1.304 | 0.715 |
| index/GSM8K | 142 | 0.577 | 0.117 | 1.234 | 0.605 |
| index/HLE | 27 | 0.185 | 0.569 | 2.943 | 1.261 |
| index/Habermas Machine | 90 | 0.400 | 0.405 | 1.565 | 0.812 |
| index/HellaSwag | 534 | 0.923 | 0.040 | 0.242 | 0.119 |
| index/HoVer claim verification | 213 | 0.765 | 0.217 | 1.097 | 0.448 |
| index/Home appliance simulator | 90 | 0.967 | 0.028 | 0.153 | 0.065 |
| index/Humicroedit | 140 | 0.636 | 0.331 | 1.415 | 0.661 |
| index/MMLU | 747 | 0.847 | 0.078 | 0.480 | 0.237 |
| index/MMLU-Pro | 641 | 0.535 | 0.166 | 1.467 | 0.622 |
| index/MuSR | 40 | 0.600 | 0.310 | 1.392 | 0.663 |
| index/NLI4CT | 293 | 0.826 | 0.150 | 0.693 | 0.314 |
| index/New Yorker caption matching | 28 | 0.679 | 0.174 | 0.915 | 0.463 |
| index/POP909-CL | 106 | 0.406 | 0.171 | 3.108 | 0.810 |
| index/PhishNChips phishing decisions | 106 | 0.896 | 0.102 | 0.413 | 0.199 |
| index/RAGTruth response-level hallucination | 143 | 0.846 | 0.085 | 0.391 | 0.234 |
| index/RouterBench | 1062 | 0.153 | 0.639 | 3.907 | 1.378 |
| index/SATA-Bench | 823 | 0.852 | 0.121 | 0.576 | 0.267 |
| index/SGD/SGD-X | 133 | 0.090 | 0.852 | 3.745 | 1.673 |
| index/SimpleBench | 1 | 1.000 | 0.058 | 0.059 | 0.004 |
| index/ToolRet | 46 | 0.978 | 0.025 | 0.110 | 0.045 |
| index/VAST | 160 | 0.637 | 0.297 | 1.420 | 0.632 |
| index/When2Call MCQ | 195 | 0.667 | 0.247 | 1.154 | 0.553 |
| index/WinoGrande | 68 | 0.882 | 0.096 | 0.417 | 0.204 |
| index/cfcolor | 266 | 0.624 | 0.314 | 1.347 | 0.652 |
| index/iSarcasmEval | 620 | 0.723 | 0.223 | 0.814 | 0.444 |
