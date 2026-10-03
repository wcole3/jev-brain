# qwen3.8-27b offline: index-dev

## Provenance

- timestamp: 2026-10-03T004756Z
- repo commit: 49152c6
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- split: index-dev
- collected: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'question_first', 'orders': 'identity', 'calibration': {'T': {'choice': 1.3522738771932372, 'score': 6.26411640450269, 'noul': 0.8245982249217311}, 'b': 0.0, 'source': 'qwen3.8-27b/question_first/calibration.json', 'orders': 'identity'}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.755

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.755 | 0.038 | 0.784 | 0.340 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.754 | 0.038 | 0.787 | 0.341 |
| noul | 143 | 0.825 | 0.096 | 0.503 | 0.265 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.755 | 0.038 | 0.784 | 0.340 |

Noul: 143 rows, said yes 74, gold yes 57, false no 4, false yes 21

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.977 | 0.071 | 0.126 | 0.058 |
| index/ANLI | 171 | 0.737 | 0.074 | 0.661 | 0.382 |
| index/API-Bank | 27 | 0.852 | 0.130 | 0.913 | 0.250 |
| index/ARC-Challenge | 62 | 0.984 | 0.049 | 0.062 | 0.024 |
| index/ARC-Easy | 126 | 0.984 | 0.029 | 0.044 | 0.021 |
| index/Amazon ESCI | 266 | 0.579 | 0.130 | 0.994 | 0.531 |
| index/BANKING77 | 164 | 0.738 | 0.084 | 1.178 | 0.370 |
| index/BBH fixed-option tasks | 293 | 0.737 | 0.093 | 0.678 | 0.360 |
| index/BFCL | 258 | 0.996 | 0.026 | 0.035 | 0.012 |
| index/BPoMP | 258 | 0.926 | 0.085 | 0.224 | 0.123 |
| index/BRIGHT | 20 | 0.550 | 0.333 | 1.038 | 0.668 |
| index/CLINC150+OOS | 293 | 0.860 | 0.033 | 0.559 | 0.202 |
| index/CLadder | 266 | 0.586 | 0.129 | 0.608 | 0.427 |
| index/CRUXEval | 30 | 0.400 | 0.250 | 0.982 | 0.618 |
| index/ChessBench | 266 | 0.158 | 0.246 | 3.610 | 1.033 |
| index/ContractNLI | 102 | 0.843 | 0.171 | 0.576 | 0.300 |
| index/FinEntity | 111 | 0.892 | 0.121 | 0.376 | 0.189 |
| index/ForecastBench | 539 | 0.712 | 0.055 | 0.551 | 0.376 |
| index/GPQA Diamond | 11 | 0.455 | 0.218 | 0.934 | 0.509 |
| index/GSM8K | 142 | 0.430 | 0.128 | 1.467 | 0.710 |
| index/HLE | 27 | 0.111 | 0.407 | 2.236 | 1.039 |
| index/Habermas Machine | 90 | 0.422 | 0.147 | 1.229 | 0.650 |
| index/HellaSwag | 534 | 0.949 | 0.053 | 0.176 | 0.082 |
| index/HoVer claim verification | 213 | 0.718 | 0.050 | 0.540 | 0.366 |
| index/Home appliance simulator | 90 | 0.944 | 0.089 | 0.263 | 0.110 |
| index/Humicroedit | 140 | 0.571 | 0.209 | 0.801 | 0.561 |
| index/MMLU | 747 | 0.829 | 0.033 | 0.483 | 0.256 |
| index/MMLU-Pro | 641 | 0.488 | 0.054 | 1.530 | 0.637 |
| index/MuSR | 40 | 0.500 | 0.271 | 1.181 | 0.692 |
| index/NLI4CT | 293 | 0.778 | 0.066 | 0.475 | 0.312 |
| index/New Yorker caption matching | 28 | 0.500 | 0.161 | 1.239 | 0.600 |
| index/POP909-CL | 106 | 0.226 | 0.114 | 3.585 | 0.897 |
| index/PhishNChips phishing decisions | 106 | 0.774 | 0.085 | 0.398 | 0.265 |
| index/RAGTruth response-level hallucination | 143 | 0.825 | 0.096 | 0.503 | 0.265 |
| index/RouterBench | 1062 | 0.129 | 0.522 | 3.861 | 1.286 |
| index/SATA-Bench | 823 | 0.815 | 0.114 | 0.445 | 0.280 |
| index/SGD/SGD-X | 133 | 0.353 | 0.261 | 1.233 | 0.753 |
| index/SimpleBench | 1 | 0.000 | 0.411 | 1.537 | 0.868 |
| index/ToolRet | 46 | 0.913 | 0.120 | 0.294 | 0.168 |
| index/VAST | 160 | 0.531 | 0.165 | 1.136 | 0.647 |
| index/When2Call MCQ | 195 | 0.631 | 0.097 | 0.807 | 0.443 |
| index/WinoGrande | 68 | 0.838 | 0.101 | 0.345 | 0.223 |
| index/cfcolor | 266 | 0.620 | 0.035 | 0.651 | 0.460 |
| index/iSarcasmEval | 620 | 0.721 | 0.036 | 0.562 | 0.381 |
