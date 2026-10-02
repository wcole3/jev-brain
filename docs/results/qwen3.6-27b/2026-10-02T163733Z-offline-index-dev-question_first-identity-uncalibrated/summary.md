# qwen3.6-27b offline: index-dev

## Provenance

- timestamp: 2026-10-02T163733Z
- repo commit: e93c263
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: index-dev
- collected: .cache/collect/qwen3.6-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'question_first', 'orders': 'identity', 'calibration': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.751

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.751 | 0.103 | 0.881 | 0.362 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.750 | 0.103 | 0.886 | 0.364 |
| noul | 143 | 0.874 | 0.058 | 0.382 | 0.203 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.751 | 0.103 | 0.881 | 0.362 |

Noul: 143 rows, said yes 61, gold yes 57, false no 7, false yes 11

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.937 | 0.018 | 0.147 | 0.090 |
| index/ANLI | 171 | 0.760 | 0.168 | 0.778 | 0.395 |
| index/API-Bank | 27 | 0.815 | 0.245 | 1.764 | 0.403 |
| index/ARC-Challenge | 62 | 0.968 | 0.035 | 0.114 | 0.061 |
| index/ARC-Easy | 126 | 0.976 | 0.022 | 0.036 | 0.024 |
| index/Amazon ESCI | 266 | 0.639 | 0.189 | 1.116 | 0.543 |
| index/BANKING77 | 164 | 0.695 | 0.195 | 1.903 | 0.470 |
| index/BBH fixed-option tasks | 293 | 0.734 | 0.046 | 0.677 | 0.365 |
| index/BFCL | 258 | 0.996 | 0.006 | 0.013 | 0.007 |
| index/BPoMP | 258 | 0.922 | 0.073 | 0.213 | 0.123 |
| index/BRIGHT | 20 | 0.550 | 0.334 | 0.989 | 0.581 |
| index/CLINC150+OOS | 293 | 0.836 | 0.093 | 0.786 | 0.244 |
| index/CLadder | 266 | 0.688 | 0.076 | 0.566 | 0.389 |
| index/CRUXEval | 30 | 0.367 | 0.331 | 1.175 | 0.709 |
| index/ChessBench | 266 | 0.132 | 0.402 | 4.715 | 1.165 |
| index/ContractNLI | 102 | 0.775 | 0.049 | 0.588 | 0.318 |
| index/FinEntity | 111 | 0.883 | 0.064 | 0.323 | 0.180 |
| index/ForecastBench | 539 | 0.712 | 0.087 | 0.527 | 0.349 |
| index/GPQA Diamond | 11 | 0.455 | 0.397 | 1.013 | 0.616 |
| index/GSM8K | 142 | 0.401 | 0.085 | 1.442 | 0.695 |
| index/HLE | 27 | 0.185 | 0.476 | 2.476 | 1.083 |
| index/Habermas Machine | 90 | 0.389 | 0.319 | 1.537 | 0.773 |
| index/HellaSwag | 534 | 0.951 | 0.022 | 0.133 | 0.067 |
| index/HoVer claim verification | 213 | 0.695 | 0.247 | 1.036 | 0.527 |
| index/Home appliance simulator | 90 | 0.933 | 0.054 | 0.252 | 0.099 |
| index/Humicroedit | 140 | 0.607 | 0.256 | 1.023 | 0.606 |
| index/MMLU | 747 | 0.858 | 0.053 | 0.425 | 0.214 |
| index/MMLU-Pro | 641 | 0.505 | 0.094 | 1.552 | 0.631 |
| index/MuSR | 40 | 0.525 | 0.334 | 1.152 | 0.667 |
| index/NLI4CT | 293 | 0.778 | 0.081 | 0.508 | 0.321 |
| index/New Yorker caption matching | 28 | 0.571 | 0.185 | 1.093 | 0.526 |
| index/POP909-CL | 106 | 0.226 | 0.090 | 3.772 | 0.892 |
| index/PhishNChips phishing decisions | 106 | 0.792 | 0.112 | 0.484 | 0.319 |
| index/RAGTruth response-level hallucination | 143 | 0.874 | 0.058 | 0.382 | 0.203 |
| index/RouterBench | 1062 | 0.137 | 0.611 | 4.375 | 1.387 |
| index/SATA-Bench | 823 | 0.827 | 0.030 | 0.390 | 0.249 |
| index/SGD/SGD-X | 133 | 0.150 | 0.761 | 2.647 | 1.442 |
| index/SimpleBench | 1 | 0.000 | 0.831 | 2.935 | 1.595 |
| index/ToolRet | 46 | 0.891 | 0.074 | 0.260 | 0.157 |
| index/VAST | 160 | 0.569 | 0.272 | 1.522 | 0.687 |
| index/When2Call MCQ | 195 | 0.738 | 0.115 | 0.747 | 0.384 |
| index/WinoGrande | 68 | 0.912 | 0.076 | 0.270 | 0.163 |
| index/cfcolor | 266 | 0.647 | 0.132 | 0.709 | 0.485 |
| index/iSarcasmEval | 620 | 0.797 | 0.062 | 0.428 | 0.287 |
