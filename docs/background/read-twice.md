# Read-twice (block stacking)

Based on DS-045 (2026-10-22/23): a review of the Decision Index board, four prompt arms collected on gemma-4-31b,
calibration fits on all four bf16 models, and one latency A/B. The analysis scripts are kept in
`.firecrawl/background/read-twice/` (git-ignored); the collect files are in `.cache/collect/<profile>/` under the
labels listed in [Runs](#runs).

## Short answer

- **Read-twice writes the shared block of the prompt a second time** (blurb, question list, state), behind one
  joiner line, before the per-question part. A causal model reading the second copy can attend to the whole first
  copy, so early state tokens get to "see" the end of the state.
- **The idea comes from the board.** FlexDM (stock Gemma-4-31B, our PR #193 layout, Full 67.56 vs our 64.61) and
  KnowLine both read short requests twice (the RE2 method). We tested where the second copy goes: stacked in the
  shared, cached prefix (arm B) or per row after the options (arm D).
- **Stacking the block (B) is the only arm that helped.** On gemma-4-31b, index-dev-2k: +0.5 points over 3,726
  questions, CI [−0.1, +1.0]; +1.9 points averaged per benchmark. Re-reading the options (D) did nothing.
- **It helps only requests with one question:** +1.2 points on those, +0.06 on requests with two or more. The
  shipped layout gates on that.
- **Dropping letter option names** ("(A) A: text" → "(A) text") changed nothing measurable, and ships anyway.
- **`blurb_header_reread` is the default on all 9 profiles** (B, one-question gate, letter names dropped). On the
  off-suite eval split, choice accuracy rises on all four bf16 models (+0.8 to +2.1 points); score and noul are mixed.
- **Aleria's other rendering cleanups ship too** (§8): a name equal to its description shown once, "(A)" names
  dropped, no `_index` on long state arrays. Accuracy-neutral on gemma-4-31b; the `_index` drop saves 2.7% of
  tokens. Shipping them made the §6 fits stale: **the default runs at T = 1 until the refit.**
- **Cost:** +22% median and mean latency on gemma-4-31b (151.5 → 185.5 ms median), all three board-gate figures
  still under 1,000 ms.

## 1. What it is

`blurb_header` builds one row per (question, option order). Every row of a request starts with the same shared
prefix (chat head, blurb, question list, state), which vLLM computes once and reuses from its prefix cache
([prompt-layouts.md §1](prompt-layouts.md#1-the-three-layouts),
[prompt-sharing.md](prompt-sharing.md)). `blurb_header_reread` adds one rule: when a request has exactly one
question, the shared parts are written a second time behind a joiner.

A one-question request as gemma-4-31b sees it (`‖` marks the end of the shared prefix):

```
<bos><|turn>user
You will be asked questions about the following context. Answer each with the letter of the best option.

Questions that will be asked about the context:
- When did it ship?

Context:
Order 17: 3 widgets shipped on Monday.

Hmm, I should read that again before answer

You will be asked questions about the following context. Answer each with the letter of the best option.

Questions that will be asked about the context:
- When did it ship?

Context:
Order 17: 3 widgets shipped on Monday.‖

Question: When did it ship?
Options:
(A) Monday
(B) Friday<turn|>
<|turn>model
<|channel>thought
<channel|>Answer: (
```

- **Shared prefix:** 121 tokens instead of 57; the row after it is unchanged. With two questions in the request, the
  block appears once and the row is `blurb_header`'s minus the letter names (96 tokens instead of 100).
- **The joiner** is the owner's wording, kept verbatim. It is a layout field (`again`), so it sits in
  [`prompts/blurb_header_reread.toml`](../../prompts/blurb_header_reread.toml) with the rest of the wording.
- **The gate** is `read_twice = "one-question"` in the same file. `"always"` and `"off"` also exist. A request with
  images never reads twice, because an image is shown once.

### Why it can help a causal model

In a causal decoder each token attends only to tokens before it, so the start of the state is encoded without
knowing how the state ends or which question follows. The question list placed before the state (the `header`
layouts) fixes the second part; read-twice addresses the first. Every token of the second copy can attend to the
whole first copy, which approximates bidirectional reading. Most top fine-tuned Qwen entries on the board instead
lift the causal mask on full-attention layers (Baseten measured 44.8 causal vs 48.6 bidirectional, same data).

Limits on Gemma 4: 50 of its 60 layers use a 1,024-token sliding window. Once the block is longer than about 1,000
tokens, the second copy reaches the first only through the 10 global layers. The data did not show a length effect
(§4), but only 90 single-question index-dev-2k questions had a shared prefix over 1,024 tokens. Qwen's Gated
DeltaNet layers carry state over the whole sequence and have no window
([model-architectures.md](model-architectures.md)).

### Where the code is

- [`gateway/layouts.py`](../../gateway/layouts.py): the `again`, `read_twice` and `drop_letter_names` keys, checked
  at load.
- [`gateway/prompts.py`](../../gateway/prompts.py): `reads_twice` decides per request and `as_read` rewrites the
  order (shared parts, `again`, then the full order) before `build_rows` encodes anything. The gate counts every
  question in the request, so a request's second readout pass (gated orders) keeps the first pass's prefix.
- [`gateway/questions.py`](../../gateway/questions.py): `drops_names` for the letter-name rule.
- Experiment layouts can also repeat parts directly in `order` (`blurb-header-again-{b,d,bd}.toml`). A joiner
  followed by a part that opens with a blank line drops its own trailing blank line, so the prompt never shows four
  newlines.

## 2. The arms

Four arms against the `blurb_header` control, all on gemma-4-31b:

| Arm | Layout file | What is read twice |
|---|---|---|
| nolettername | `blurb-header-nolettername.toml` | nothing; option names A, B, C… in order are not shown |
| B | `blurb-header-again-b.toml` | the shared block, stacked in the cached prefix |
| D | `blurb-header-again-d.toml` | the question and options, per row, after the first copy |
| BD | `blurb-header-again-bd.toml` | both |

- **Cost model.** B's second copy is computed once per request and shared by every row and option order. D's is
  paid by every row. FlexDM's variant (second copy of question list + state + question + options per row, gated at
  3,000 tokens) was not run: on HLE, D covers the same content.
- **What each arm re-reads.** B re-reads the state but never the options; D re-reads the options, with each option
  able to attend to all the others. The two arms separate "re-read the context" from "re-read the choices".

### Test beds

- **hle-focus** ([`data/splits/hle-focus.json`](../../data/splits/hle-focus.json),
  [`scripts/hle_focus.py`](../../scripts/hle_focus.py)): all 501 HLE rows plus whole index-dev groups of the other 36
  index benchmarks, 5–6 rows each; HLE is 73%. Quick to run (684 rows).
- **index-dev-2k**: 1,994 requests across all index benchmarks, with real states; the existing all-orders collect
  is the control.
- **calib-600 and eval** (JevBench, outside the suite): the off-suite checks and the calibration fits.

### HLE is a hard place to measure

- **Every HLE row has an empty state**; the content is the question and 5–26 options. The header layouts already
  write the question text twice (question list, then the row), so B only adds a third copy.
- **HLE kept only questions frontier LLMs got wrong** ("questions are rejected if LLMs can answer them correctly",
  arXiv 2501.14249). All nine of our profiles score below chance (0.108–0.138 vs 0.165), as do 207 of 228 board
  entries. On gemma-4-31b the gold answer is the model's second pick more often than its first (110 vs 69).
  A gain toward chance may mean less pull toward the trap answer, not better reasoning.
- **HLE does not count toward the Full score** on board v0.4: it has no private same-skill set.
- **Label noise:** FutureHouse found 29 ± 3.7% of HLE's text chemistry and biology answers contradicted by the
  literature.

## 3. Results

Paired accuracy against `blurb_header` on the same questions, identity + reversed reads averaged (T-free top
answers). Brackets are 95% bootstrap intervals; they resample questions, not requests, so they run narrow where a
request holds many questions.

### hle-focus

| Arm | HLE (501) | non-HLE (786) | All (1,287) |
|---|---|---|---|
| `blurb_header` | 0.140 | 0.906 | 0.608 |
| nolettername | 0.144 (+0.004) | 0.905 (−0.001) | 0.608 (+0.001) |
| B | 0.152 (+0.012) | 0.915 (+0.009) | 0.618 (+0.010) [+0.002, +0.019] |
| D | 0.144 (+0.004) | 0.908 (+0.003) | 0.611 (+0.003) |
| BD | 0.154 (+0.014) | 0.913 (+0.008) | 0.618 (+0.010) [−0.001, +0.022] |

- On identity reads alone BD is largest (+0.018 [+0.005, +0.030]); on reversed reads every arm moves +0.004 or
  less. The re-read helps the first-order reading, not the reversed one.
- Adding D to B gains nothing on the averaged reads.

### index-dev-2k

| Arm | All (3,726) | Letter-named options (890) | Other options (2,831) |
|---|---|---|---|
| `blurb_header` | 0.811 | 0.838 | 0.803 |
| nolettername | 0.810 (−0.000) | 0.839 (+0.001) | 0.803 (−0.001) |
| B | 0.815 (+0.005) [−0.001, +0.010], 65 fixes / 47 breaks | 0.846 (+0.008) | 0.807 (+0.004) |

D and BD were not collected on index-dev-2k (owner's scope cut, to save GPU time).

## 4. The gate: who gains

Per-benchmark change for B on index-dev-2k (identity + reversed, accuracy points):

| Gains | Δ | Losses | Δ |
|---|---|---|---|
| GSM8K | +13.9 (6/1) | Habermas | −12.5 (1/4) |
| HoVer | +10.5 (6/0) | Amazon ESCI | −2.8 (2/4) |
| RAGTruth | +7.9 (3/0) | iSarcasmEval | −1.8 (3/6) |
| CLadder | +4.2 (4/1) | SATA-Bench | −1.2 (0/3) |
| NLI4CT, Home appliances, ContractNLI | +2 to +3 | PhishNChips, BFCL | −1.5 to −3.6 |

Averaged per benchmark over the 24 index benchmarks with at least 30 questions: +1.9 points. The gains sit on
largely the same benchmarks where FlexDM gained over us (CRUXEval, HoVer, When2Call, Home appliances, BBH).

No single feature splits winners from losers cleanly: state length, shared-prefix length and option count show no
monotone pattern. The question count does:

| Requests | Questions | Benchmarks up / down | Δ accuracy | fixes / breaks |
|---|---|---|---|---|
| 1 question, state ≥ 64 tokens | 644 | 7 / 4 | +0.0155 | 26 / 16 |
| 1 question, state < 64 tokens | 791 | 7 / 3 | +0.0088 | 21 / 14 |
| ≥ 2 questions | 1,722 | 4 / 4 | +0.0006 | 12 / 11 |

- **The rule needs no tuned number**, and it also skips the long question lists that make B expensive on
  multi-question requests.
- **Off-suite check.** calib-600 holds only single-question requests, so it confirms no harm there but cannot test
  the exclusion: identity 0.829 → 0.829, identity + reversed 0.837 → 0.844, `min_n:4+reversed` 0.829 → 0.832 (all
  CIs include 0). The exclusion rests on index-dev-2k alone, which is suite data.

## 5. Letter names

Fifteen benchmarks (HLE, MMLU-Pro, HellaSwag, GPQA, CLadder, ANLI, VAST, WinoGrande, MuSR and others) key their
options A, B, C…, so `described` rendered `(A) A: text`, and a reversed order `(A) E: text`: two letters that
disagree. Aleria Judge drops such names; its PR credits that and two other rendering cleanups with +0.37 together.

- **Before the fix**, on gemma's index-dev-2k collect, letter-named options lost 1.8 points from identity to
  reversed reads (0.827 → 0.809) where other options held (0.797 → 0.795).
- **With the fix** the drop stays (2.0 → 1.8 points), and accuracy does not move on either split. The drop is
  position bias (options such as "None of the above"), not the clashing letters.
- **It ships in `blurb_header_reread`** as `drop_letter_names = true`, by owner decision. `Rendered.names` is unchanged,
  so answers still report the caller's keys.

## 6. The shipped layout

### Option-order settings

The layout against `blurb_header` on hle-focus, each side gated at its own identity T fitted on calib-600:

| Order setting | Profiles | All (1,287) | HLE (501) | non-HLE (786) | reads per question |
|---|---|---|---|---|---|
| `identity` | gemma-4-12b, qwen3.6 | +0.008 [−0.002, +0.019] | +0.012 | +0.005 | 1.00 |
| `top_p:0.9+reversed` | gemma-4-31b | +0.009 [−0.002, +0.019] | +0.024 [+0.000, +0.048] | −0.001 | 1.38 → 1.37 |
| `min_n:4+reversed` | qwen3.8 | +0.009 [−0.002, +0.020] | +0.024 [+0.000, +0.048] | +0.000 | 1.45 |

The gain does not depend on the order setting, and the gated settings read the reversed order about as often.
non-HLE ≈ 0 because most of its questions come from multi-question requests, where the gate is off.

### Calibration

These fits predate §8 and were removed when the cleanups shipped; the numbers stand as the read-twice
result. Fits from fresh `calib` + `eval` collects (identity + reversed reads, label `reread`), per bf16 profile at its
served order setting. eval is JevBench, outside the suite; every eval request has one question, so read-twice is on
for all of it. Columns: eval accuracy and ECE after T, original `blurb_header` → `blurb_header_reread`.

| Profile | Choice acc (1,619) | Score acc (554) | Noul acc (666) | Choice ECE | Noul ECE | T choice / score / noul |
|---|---|---|---|---|---|---|
| gemma-4-31b | 0.842 → 0.850 | 0.690 → 0.679 | 0.922 → 0.917 | 0.080 → 0.076 | 0.029 → 0.021 | 3.98/5.21/6.74 → 3.99/5.31/7.12 |
| gemma-4-12b | 0.804 → 0.815 | 0.560 → 0.605 | 0.862 → 0.878 | 0.073 → 0.078 | 0.046 → 0.029 | 4.04 pooled → 4.05/4.05/3.74 |
| qwen3.6-27b | 0.820 → 0.837 | 0.673 → 0.668 | 0.898 → 0.890 | 0.022 → 0.027 | 0.030 → 0.038 | 1.63/2.06/1.27 → 1.59/2.03/1.42 |
| qwen3.8-27b | 0.819 → 0.840 | 0.666 → 0.682 | 0.881 → 0.881 | 0.022 → 0.025 | 0.032 → 0.036 | 1.64/1.00/1.21 → 1.68/1.00/1.32 |

- **Choice gains on all four models**, +0.8 to +2.1 points. This is the strongest evidence, being off-suite.
- **Score and noul are mixed**: the 12B gains on all three types; gemma-4-31b and qwen3.6 lose up to 1.1 points.
- **No noul offset b ships** on any profile; none earned its place on eval.
- **T barely moves** (largest: gemma-4-31b noul 6.74 → 7.12).
- **The five quantized profiles borrow their bf16 base's fit**, restamped for the quant's tokenizer and revision
  ([`scripts/borrow_calibration.py`](../../scripts/borrow_calibration.py)), so they have no fit or score of their own.

## 7. Cost

Latency, gemma-4-31b, latency-v1 (the board's design: one sequential client, 750 timed rows), both layouts with
fixed `identity+reversed` orders, 510 W:

| Layout | median | mean | p80 | p95 |
|---|---|---|---|---|
| `blurb_header` | 151.5 ms | 416.6 ms | 537.5 ms | 1,136.8 ms |
| `blurb_header_reread` | 185.5 ms (+22%) | 506.5 ms (+22%) | 675.9 ms (+26%) | 1,363.8 ms |

- **The board gate holds:** median, mean and p80 each stay under 1,000 ms. The served `top_p` setting reads fewer
  reversed rows, so served times are lower than this table.
- **The cost lands on single-question requests with long states**, which now prefill their state twice: catalog 22
  went 3.2 → 4.2 s and catalog 10 0.47 → 1.20 s (median).
- **Input tokens** (collect records, shared prefix counted once): the median one-question JevBench request gains 165
  (calib) and 212 (eval) tokens on gemma, 187 and 240 on qwen3.8.
- **Collect throughput** roughly halves for B-heavy splits (hle-focus: 504 s → 992 s at concurrency 8).

## 8. Aleria's rendering cleanups

Aleria Judge (Full 66.67, stock Gemma-4-31B) renders options and states with four rules taken from Decider's
renderer and changed (`aleria_judge/vendor/systemone.py`); its PR credits them, with the letter-name drop, with
+0.37 together. Three apply to us; JSON indentation was not tested (+21% tokens on JSON states).

| Rule | Layout key | Where it fires on the suite |
|---|---|---|
| A name equal to its description is shown once ("Neutral", not "Neutral: Neutral") | `same_name_once` | 6,078 choice questions: SGD 2,500, FinEntity 2,129, BBH 1,437 |
| Names "(A)", "(B)", … in order drop like "A", "B", … | `drop_label_names` | BBH, 1,000 questions (`(A) (A): circle` before) |
| Options that come out alike are shown in full | (with either key) | 1 question |
| No Decider `_index` on arrays of 8 or more items | `index_arrays = false` | 16,866 states in 9 benchmarks |

gemma-4-31b, identity + reversed reads, against `blurb_header_reread` as it was:

| Arm | hle-focus (1,287) | index-dev-2k (3,728) | fixes / breaks (index-dev-2k) |
|---|---|---|---|
| clean (first three rules) | +0.001 | +0.000 [−0.001, +0.002] | 3 / 2 |
| no `_index` | −0.001 | +0.001 [−0.001, +0.003] | 10 / 7 |

- **The clean arm touches few questions and moves none of them much:** BBH +1.3 (2/1), SGD −2.9 (0/1), FinEntity 0.
- **No `_index`, on its 9 benchmarks:** POP909 +10.7 (4/1), SGD +2.9, Home appliances +2.7, cfcolor −1.4 (1/2),
  SATA-Bench −1.7 (0/4), the rest 0; 7 fixes and 7 breaks in all. Tokens per request fall 22.0% on NLI4CT, 20.7% on
  SGD, 8.8% on cfcolor, 2.7% over all of index-dev-2k. SATA-Bench's 0/4 is worth watching: its questions may point at
  list items by position, which is what `_index` was for.
- **Noise reference:** HLE states are empty, so no HLE prompt changes in the `_index` arm, yet HLE showed 0 fixes and
  2 breaks.
- **Both ship in `blurb_header_reread`** (owner decision, 2026-10-23). The served layout's hash changed, so its label
  tables were rebuilt and its calibration files removed; the bf16 calib/eval refit and the quant borrows are pending.

## Caveats

- **gemma-4-31b only for the arms, the gate and latency.** The other three bf16 models have eval fits only.
- **No full Index run** under the new default, and no private-set number: the board's Full score is 60% private
  same-skill and 40% private new-domain tests, and none of the numbers above measure those.
- **The gate was read off suite rows** (index-dev-2k, 36 benchmarks with 2–240 questions each). The board reads
  selection on public rows sceptically; the off-suite data has no multi-question requests to confirm it.
- **Single runs.** One collect and one latency run per arm; bf16 noise is about 0.25% of questions (5 fixes and
  2 breaks on questions the letter-name fix could not touch).
- **T-free comparisons.** §3 and §4 compare top answers of averaged reads, which T does not change; §6 refits T.
- **Joiner wording.** One wording, chosen by the owner; no wording screen was run.
- **Images.** Read-twice skips image requests, but `drop_letter_names` applies to them too (every image dev
  question is keyed A, B, …). Its effect on images has not been measured.

## Runs

- Collect labels, gemma-4-31b: hle-focus `blurb-all` (control), `{nolettername,again-b,again-d,again-bd}-idrev`,
  `reread-all`; index-dev-2k `len32768-blurb-header-all` (control), `len32768-{nolettername,again-b}-idrev`;
  calib-600 `len32768-blurb-header-all` (control), `reread-all`.
- Calibration collects, all four bf16 profiles: `{calib,eval}-reread` (new) and `{calib,eval}-blurb` (original).
- Calibration summaries: `docs/results/archive/<profile>/2026-10-23T*-calibrate/summary.md` (new) against the
  2026-10-20/21 `-calibrate` runs with collect label `blurb`.
- Latency: [blurb_header](../results/archive/gemma-4-31b/2026-10-23T051704Z-latency-blurb_header-identity+reversed/summary.md),
  [blurb_header_reread](../results/archive/gemma-4-31b/2026-10-23T052356Z-latency-blurb_header_reread-identity+reversed/summary.md).
- Ticket: DS-045. Follow-up idea (model thinking in the cached prefix): DS-046.

## Sources

- Our code: [`layouts.py`](../../gateway/layouts.py), [`prompts.py`](../../gateway/prompts.py),
  [`questions.py`](../../gateway/questions.py), [`hle_focus.py`](../../scripts/hle_focus.py),
  [`borrow_calibration.py`](../../scripts/borrow_calibration.py).
- Board entries: FlexDM v1.0 (https://github.com/1000luca/FlexDM, `jevlab/reader.py`), KnowLine
  (apolinario/decision-index PRs #268, #271, #272), Aleria Judge 1.1.1 (https://github.com/ALERIA-ML/aleria-judge).
- Xu et al., Re-Reading Improves Reasoning in Large Language Models (RE2): https://arxiv.org/abs/2309.06275
- Phan et al., Humanity's Last Exam: https://arxiv.org/abs/2501.14249
- FutureHouse, About 30% of HLE chemistry/biology answers are likely wrong: https://www.futurehouse.org/research/hle-exam
- Baseten, mammoth-1 and elephant-1: https://labs.baseten.co/articles/mammoth-1-and-elephant-1-frontier-decision-models
