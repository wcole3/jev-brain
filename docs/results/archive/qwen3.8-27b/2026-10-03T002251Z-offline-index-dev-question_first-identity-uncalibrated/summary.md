# qwen3.8-27b offline: index-dev

## Provenance

- timestamp: 2026-10-03T002251Z
- repo commit: a4ad243
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- split: index-dev
- collected: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'question_first', 'orders': 'identity', 'calibration': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.755

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.755 | 0.058 | 0.872 | 0.347 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.754 | 0.059 | 0.875 | 0.348 |
| noul | 143 | 0.825 | 0.080 | 0.473 | 0.265 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.755 | 0.058 | 0.872 | 0.347 |

Noul: 143 rows, said yes 74, gold yes 57, false no 4, false yes 21

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.977 | 0.040 | 0.098 | 0.047 |
| index/ANLI | 171 | 0.737 | 0.095 | 0.673 | 0.383 |
| index/API-Bank | 27 | 0.852 | 0.154 | 1.073 | 0.243 |
| index/ARC-Challenge | 62 | 0.984 | 0.030 | 0.040 | 0.019 |
| index/ARC-Easy | 126 | 0.984 | 0.018 | 0.036 | 0.022 |
| index/Amazon ESCI | 266 | 0.579 | 0.193 | 1.103 | 0.565 |
| index/BANKING77 | 164 | 0.738 | 0.144 | 1.404 | 0.400 |
| index/BBH fixed-option tasks | 293 | 0.737 | 0.057 | 0.659 | 0.355 |
| index/BFCL | 258 | 0.996 | 0.011 | 0.021 | 0.010 |
| index/BPoMP | 258 | 0.926 | 0.051 | 0.189 | 0.110 |
| index/BRIGHT | 20 | 0.550 | 0.374 | 1.264 | 0.718 |
| index/CLINC150+OOS | 293 | 0.860 | 0.074 | 0.620 | 0.214 |
| index/CLadder | 266 | 0.586 | 0.124 | 0.619 | 0.436 |
| index/CRUXEval | 30 | 0.400 | 0.279 | 1.021 | 0.651 |
| index/ChessBench | 266 | 0.158 | 0.359 | 4.248 | 1.133 |
| index/ContractNLI | 102 | 0.843 | 0.113 | 0.525 | 0.270 |
| index/FinEntity | 111 | 0.892 | 0.073 | 0.329 | 0.177 |
| index/ForecastBench | 539 | 0.712 | 0.031 | 0.540 | 0.370 |
| index/GPQA Diamond | 11 | 0.455 | 0.297 | 0.930 | 0.513 |
| index/GSM8K | 142 | 0.430 | 0.135 | 1.420 | 0.695 |
| index/HLE | 27 | 0.111 | 0.508 | 2.580 | 1.139 |
| index/Habermas Machine | 90 | 0.422 | 0.203 | 1.312 | 0.674 |
| index/HellaSwag | 534 | 0.949 | 0.023 | 0.152 | 0.076 |
| index/HoVer claim verification | 213 | 0.718 | 0.092 | 0.554 | 0.374 |
| index/Home appliance simulator | 90 | 0.944 | 0.041 | 0.241 | 0.101 |
| index/Humicroedit | 140 | 0.571 | 0.240 | 0.910 | 0.602 |
| index/MMLU | 747 | 0.829 | 0.051 | 0.506 | 0.259 |
| index/MMLU-Pro | 641 | 0.488 | 0.069 | 1.571 | 0.641 |
| index/MuSR | 40 | 0.500 | 0.288 | 1.405 | 0.745 |
| index/NLI4CT | 293 | 0.778 | 0.038 | 0.463 | 0.305 |
| index/New Yorker caption matching | 28 | 0.500 | 0.188 | 1.284 | 0.611 |
| index/POP909-CL | 106 | 0.226 | 0.079 | 3.536 | 0.871 |
| index/PhishNChips phishing decisions | 106 | 0.774 | 0.107 | 0.410 | 0.278 |
| index/RAGTruth response-level hallucination | 143 | 0.825 | 0.080 | 0.473 | 0.265 |
| index/RouterBench | 1062 | 0.129 | 0.601 | 4.892 | 1.377 |
| index/SATA-Bench | 823 | 0.815 | 0.066 | 0.415 | 0.263 |
| index/SGD/SGD-X | 133 | 0.353 | 0.351 | 1.390 | 0.818 |
| index/SimpleBench | 1 | 0.000 | 0.474 | 1.622 | 0.952 |
| index/ToolRet | 46 | 0.913 | 0.095 | 0.276 | 0.159 |
| index/VAST | 160 | 0.531 | 0.251 | 1.287 | 0.684 |
| index/When2Call MCQ | 195 | 0.631 | 0.106 | 0.832 | 0.457 |
| index/WinoGrande | 68 | 0.838 | 0.079 | 0.327 | 0.217 |
| index/cfcolor | 266 | 0.620 | 0.069 | 0.661 | 0.468 |
| index/iSarcasmEval | 620 | 0.721 | 0.060 | 0.571 | 0.385 |
