# DS-020: why qwen3.8 and gemma trail other readouts on the Decision Index

Data: our three full 0.2.1 runs (commit 7a5d9b6 boxes, 7a5d9b6/5eb50c9 local) against the board's
per-benchmark skill (`.firecrawl/infer/index-v0.2.1.json`), weighted exactly as the harness weights
the index. Readout details of the other entries come from their source (raw scrapes in
`.firecrawl/ds020/`, git-ignored).

## Short answer

- **Our harness is faithful.** qwen3.6 matches Decider chat · Qwen3.6 benchmark by benchmark
  (index +0.26; no benchmark off by more than 0.1 index points).
- **gemma's −1.0 is calibration, not accuracy.** Three benchmarks hold the whole gap; all three
  score probabilities rather than the top answer: ForecastBench (Brier, skill 0 vs 19),
  ToolRet and BRIGHT (nDCG rankings across separate requests). At T = 1 gemma's probabilities
  saturate to 0 or 1, and 4-decimal rounding turns many candidates into ties. Every other gemma
  benchmark is within a point of decider's.
- **qwen3.8's −4.3 against simple-jev is mostly a first-option bias.** qwen3.8 picks the
  first-listed option far more often than gold does, much more than qwen3.6 or gemma
  (table below). The loss sits on binary and 3-class benchmarks scored by macro-F1 (VAST,
  PhishNChips, CLadder, iSarcasm, ACOS, WinoGrande).
- **simple-jev's prompt is very different:** a system prompt with reasoning rules and seven
  worked examples, every question briefed before the state, the question repeated, JSON options,
  and a fake thinking prefill. reflex reads letters like we do but averages two option orders.

## Where the gaps sit

Index points lost (−) or gained per benchmark, ours minus theirs:

| Comparison | Index gap | Largest contributors |
|---|---|---|
| qwen3.6 vs Decider chat · Qwen3.6 | +0.26 | none above ±0.1 |
| gemma vs Decider chat · Gemma | −1.02 | ToolRet −0.43, ForecastBench −0.32, BRIGHT −0.27 |
| qwen3.8 vs simple-jev (same model) | −4.30 | VAST −0.82, PhishNChips −0.72, CLadder −0.54, iSarcasm −0.44, ACOS −0.31, WinoGrande −0.27, ESCI −0.23 |
| qwen3.8 vs reflex (same model, FP8) | −0.72 | VAST −0.41, CLadder −0.18, GPQA −0.18, RAGTruth −0.17 |

## First-option bias

Share of choice answers that are the first-listed option, against the gold share:

| Benchmark | Gold | qwen3.6 | qwen3.8 | gemma |
|---|---|---|---|---|
| CLadder | 49.9% | 49.7% (acc 66.5) | **73.8%** (acc 59.8) | 49.1% (acc 74.6) |
| VAST | 33.9% | 55.0% | **59.3%** | 42.3% |
| MMLU-Pro | 11.7% | 19.5% | **22.8%** | 11.6% |
| BBH | 30.4% | 34.8% | 39.2% | 32.1% |
| WinoGrande | 49.6% | 55.5% | 57.9% | 47.4% |

qwen3.8 loses 7 accuracy points on CLadder to this alone. Both Qwens lean to the first option on
VAST; gemma is close to unbiased everywhere.

## How the other readouts differ from ours

| | Ours (= decider chat) | reflex | simple-jev |
|---|---|---|---|
| System prompt | none | short role line | rules ("lack of mention is not falsity" …) + 7 worked examples |
| Questions | one per row, after the state | one per row | all questions briefed before the state; selected question repeated twice |
| Options | `(A) text` | `A. key: description` | JSON array with labels |
| Thinking | closed | closed | fake `[thinking]` prefill on choice rows |
| Read at | `Answer: (` | next token | after `{"answer": "` |
| Option orders | identity | identity + 1 random shuffle (`--permutations 2`) | identity |
| Calibration | fitted T (qwen3.6 only) | none shipped | none (ECE 0.113) |

simple-jev's prompts were selected on its own dev set ("quick477"), and its worked examples look
close to some benchmark item types (causal ladders, deadlines, code). Part of its lead may not
transfer to unseen tasks.

## What to test next (ranked by cost and expected gain)

1. **Option-order averaging and PriDe on qwen3.8 (M3, offline).** Directly targets the measured
   first-option bias. The collect files hold every order, so this needs no new GPU work once
   the qwen3.8 index-dev collect lands. reflex's own measurements: hard-tier accuracy 0.658 to
   0.685, pooled ECE 0.055 to 0.032. qwen3.8's bias is stronger than reflex's base, so the gain
   may be larger than reflex's +0.7.
2. **Fitted temperatures (M2) for gemma and qwen3.8.** Recovers ForecastBench, ToolRet and BRIGHT
   for gemma. Also check whether 4-decimal rounding of probabilities (`gateway/answers.py`) creates
   ranking ties that cost nDCG even after T is fitted.
3. **Prompt changes (a new layout, after M3).** Port pieces of simple-jev's prompt one at a time:
   the rules text, the question briefing and repeat, the JSON options. Each needs a new layout
   TOML, rebuilt label tables, a fresh collect and a refit. Judge them on our eval split and
   DecisionBench before the Index, so we don't tune to the Index.
4. **Yes/no lean.** Fold into 1 (swapping no/yes is one of the averaged orders) and 2 (the
   noul offset in M2).

## Caveats

- decider2 (the Gemma board run) and reflex's wide-choice overlay are not public.
- None of the three projects published ablations, so the size of each prompt part is unknown.
- reflex ran FP8, which moves about 1% of answers.
- Board numbers are a 2026-09-27 snapshot.
