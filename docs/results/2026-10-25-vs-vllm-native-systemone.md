# jev-brain vs vLLM's native `/v1/systemone` (qwen3.8-27b, 2026-10-25)

Same weights (`Qwen/Qwen3.8-27B`, bf16), same vLLM 0.32.0 process and GPU (one RTX PRO 6000), same requests.
jev-brain serves `blurb_header_reread` (read-twice, option orders `min_n:4+reversed`, per-type T fitted on
JevBench calib); vLLM's endpoint reads each question once at T = 1 and takes at most 26 options. vLLM 0.32 does not
serve the endpoint for Gemma 4 (HTTP 501), so this comparison is Qwen only.

## Accuracy: index-dev-2k (1,994 Decision Index public requests, 3,728 gold questions)

Top answer against gold; a refused request counts as wrong. "Index est." is the board's scorer on the index-dev-2k
cut of the suite (the 2026-10-20 full run scores 62.53 on this cut vs 62.98 on the full suite).

| metric | qwen38-ours | qwen38-native |
|---|---|---|
| rows answered | 1994/1994 (split 1994) | 1787/1994 (split 1994) |
| status | {'ok': 1994} | {'ok': 1787, 'error': 207} |
| acc, all gold q | 79.72% (2972/3728) | 71.81% (2677/3728) |
| acc, choice | 79.67% (2940/3690) | 71.65% (2644/3690) |
| acc, noul | 84.21% (32/38) | 86.84% (33/38) |
| acc, score | n/a | n/a |
| acc, rows all runs answered | 80.94% (2850/3521) | 76.03% (2677/3521) |
| Index est. (subset) | 60.56 | 38.11 |
| median ms (concurrent) | 1946 | 526 |

The "median ms" row is wall time per request with 8 concurrent clients, not the board's latency.

Per benchmark:

| family | qwen38-ours | qwen38-native |
|---|---|---|
| ACOS | 98.54% (1150/1167) | 96.92% (1131/1167) |
| ANLI | 69.57% (32/46) | 56.52% (26/46) |
| API-Bank | 100.00% (7/7) | 0.00% (0/7) |
| ARC-Challenge | 100.00% (17/17) | 100.00% (17/17) |
| ARC-Easy | 100.00% (33/33) | 100.00% (33/33) |
| Amazon ESCI | 68.06% (49/72) | 63.89% (46/72) |
| BANKING77 | 77.27% (34/44) | 0.00% (0/44) |
| BBH fixed-option tasks | 75.95% (60/79) | 68.35% (54/79) |
| BFCL | 100.00% (65/65) | 100.00% (65/65) |
| BPoMP | 98.51% (66/67) | 94.03% (63/67) |
| BRIGHT | 50.00% (2/4) | 50.00% (2/4) |
| CLINC150+OOS | 79.75% (63/79) | 0.00% (0/79) |
| CLadder | 70.83% (51/72) | 44.44% (32/72) |
| CRUXEval | 75.00% (6/8) | 25.00% (2/8) |
| ChessBench | 20.83% (15/72) | 5.56% (4/72) |
| ContractNLI | 82.35% (28/34) | 85.29% (29/34) |
| FinEntity | 89.66% (26/29) | 82.76% (24/29) |
| GPQA Diamond | 0.00% (0/3) | 0.00% (0/3) |
| GSM8K | 50.00% (18/36) | 33.33% (12/36) |
| HLE | 28.57% (2/7) | 14.29% (1/7) |
| Habermas Machine | 33.33% (8/24) | 37.50% (9/24) |
| HellaSwag | 93.75% (135/144) | 95.14% (137/144) |
| HoVer claim verification | 84.21% (48/57) | 78.95% (45/57) |
| Home appliance simulator | 97.30% (36/37) | 94.59% (35/37) |
| Humicroedit | 71.05% (27/38) | 68.42% (26/38) |
| MMLU | 90.00% (180/200) | 81.00% (162/200) |
| MMLU-Pro | 73.84% (127/172) | 65.12% (112/172) |
| MuSR | 70.00% (7/10) | 40.00% (4/10) |
| NLI4CT | 87.18% (68/78) | 83.33% (65/78) |
| New Yorker caption matching | 87.50% (7/8) | 62.50% (5/8) |
| POP909-CL | 35.71% (10/28) | 0.00% (0/28) |
| PhishNChips phishing decisions | 82.14% (23/28) | 57.14% (16/28) |
| RAGTruth response-level hallucination | 84.21% (32/38) | 86.84% (33/38) |
| RouterBench | 11.97% (34/284) | 9.51% (27/284) |
| SATA-Bench | 85.06% (205/241) | 85.89% (207/241) |
| SGD/SGD-X | 31.43% (11/35) | 34.29% (12/35) |
| ToolRet | 100.00% (14/14) | 92.86% (13/14) |
| VAST | 65.12% (28/43) | 37.21% (16/43) |
| When2Call MCQ | 80.77% (42/52) | 75.00% (39/52) |
| WinoGrande | 100.00% (18/18) | 77.78% (14/18) |
| cfcolor | 61.11% (44/72) | 59.72% (43/72) |
| iSarcasmEval | 86.75% (144/166) | 69.88% (116/166) |

## Latency: latency-v1 (board design: one sequential client, 750 timed requests), 600 W

| | median | mean | p80 | p95 |
|---|---|---|---|---|
| jev-brain, all 750 requests | 287.5 | 622.0 | 822.3 | 1,272.3 |
| vLLM native, the 672 it answers | 137.9 | 272.4 | 276.0 | 971.7 |
| jev-brain, the same 672 requests | 263.4 | 540.1 | 597.5 | 1,190.5 |

Both pass the board's gate (median, mean and p80 each ≤ 1,000 ms). vLLM refuses 78 of the 750 (over 26 options).

## Reading it

- jev-brain is more accurate: +7.9 points on all questions, +4.9 on the questions both endpoints answer, and it
  answers the 207 requests vLLM refuses. Its biggest leads come from reading several option orders and the
  read-twice layout (iSarcasmEval, VAST, CLadder, PhishNChips, WinoGrande, MMLU/MMLU-Pro); vLLM is ahead by 1-4
  questions on noul, HellaSwag, RAGTruth, ContractNLI, Habermas and SGD.
- vLLM's endpoint is about 2x faster on the requests it answers: one read per question, no second order, no
  re-read.
- index-dev-2k is suite data and our layout choices were screened on it; treat the accuracy gap as indicative, not as
  a held-out result.

## Sources

- Bench script and raw answers: `.firecrawl/native-systemone/` (`bench.py`, `runs/qwen38-ours`, `runs/qwen38-native`,
  git-ignored).
- Latency: `docs/results/archive/qwen3.8-27b/2026-10-25T124823Z-latency/` (jev-brain),
  `.firecrawl/native-systemone/runs/2026-10-25T125140Z-latency-native/` (vLLM), subset by
  `.firecrawl/native-systemone/subset_latency.py`.
- Our fit: `docs/results/archive/qwen3.8-27b/2026-10-25T111642Z-calibrate/`.
