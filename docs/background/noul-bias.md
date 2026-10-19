# The noul yes/no lean

Why our models answer JevBench's yes/no (`noul`) questions with a lean to one side, where the
lean comes from, and what to test in phase 2 (DS-002). Numbers come from the three
2026-09-30 JevBench runs (625 gold noul rows each), the upstream rows' `domain` and
`stratum`, our code, and the papers under Sources. Jev appears only as aggregate counts.

## Short answer

- **The lean is real and model-specific.** Gold is 42.7% "yes". qwen3.6 says "yes" 35.2% of
  the time (75 false "no", 28 false "yes"), gemma 53.3% (6 false "no", 72 false "yes").
- **It is not a constant shift in log-odds.** 75–91% of each model's errors sit in three
  question families: summing invoice lines, one logic template and averaging numbers. On those the
  model barely separates yes from no, and a global offset can't create a signal that isn't
  there.
- **A global offset helps little (in-sample illustration, not a fit to adopt):** at best
  +0.3 points (qwen3.6), +0.4 (qwen3.8) and +1.6 (gemma), and each gain mostly trades one error
  kind for the other.
- **The main cause looks like difficulty, not wording or position:** when a model can't
  compute the answer in one forward pass, it falls back to a default answer, and that
  default is "no" for Qwen and "yes" for gemma on the same rows.
- **Phase 2 should test** a per-profile offset, `identity+reversed` for noul and contextual
  calibration, each on a held-out split. None of them is likely to fix the arithmetic rows.

## 1. The lean

How each model's noul answers split (625 rows, 267 gold "yes", 358 gold "no"):

| Model | Said yes | Gold yes | False "no" (of 267) | False "yes" (of 358) | Accuracy |
|---|---|---|---|---|---|
| Jev | 44.5% | 42.7% | 8 | 19 | 95.7% |
| qwen3.6-27b | **35.2%** | 42.7% | **75** | 28 | 83.5% |
| qwen3.8-27b | 39.2% | 42.7% | 54 | 32 | 86.2% |
| gemma-4-31b | **53.3%** | 42.7% | 6 | **72** | 87.5% |

(Earlier reports show 74 false "no" for qwen3.6; today's run has 75, one near-tie row.)

In the gateway a noul answer is `yes` when p(yes) ≥ 0.5 (`scripts/bench_data.py`). The prompt
is the same for every model (`prompts/decider_chat.toml`, `gateway/questions.py`):

```
Question: <the row's instructions>
Options:
(A) no
(B) yes
Answer: (
```

## 2. Distributions: shift or something else?

Histograms of p(yes), split by gold. Bins are 0.1 wide; a perfect model puts gold "yes" in
the right-most bin and gold "no" in the left-most.

| Model | Gold | 0– | .1– | .2– | .3– | .4– | .5– | .6– | .7– | .8– | .9–1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3.6 | yes | 0 | 10 | 36 | 22 | 7 | 7 | 7 | 16 | 26 | 136 |
| qwen3.6 | no | 75 | 118 | 106 | 25 | 6 | 5 | 2 | 1 | 20 | 0 |
| qwen3.8 | yes | 1 | 12 | 27 | 5 | 9 | 11 | 17 | 19 | 14 | 152 |
| qwen3.8 | no | 129 | 72 | 78 | 25 | 22 | 8 | 0 | 23 | 1 | 0 |
| gemma | yes | 5 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 260 |
| gemma | no | 282 | 2 | 2 | 0 | 0 | 0 | 0 | 2 | 2 | 68 |

qwen3.6 ran at T = 1.943, so its probabilities are flatter; the others ran at T = 1.0.

What a constant shift would look like: the two gold groups form two humps, with one hump
partly on the wrong side of 0.5, so sliding the 0.5 line fixes most errors. What we see
instead:

- **Qwen:** the false "no" rows form their own hump at 0.1–0.4, and the false "yes" rows
  sit at 0.7–0.9, a lump of 20 (§3 shows it is one logic template). Neither is a tail of
  the correct hump.
- **gemma:** saturated. 535 of 625 answers are exactly 0 or 1 after the gateway's
  4-decimal rounding (`gateway/answers.py`). 35 of its 72 false "yes" rows read p(yes) =
  1.0000, the same value as 222 of the gold-yes rows. No offset can split them.

**What an offset would do (in-sample illustration).** We added an offset b to logit(p) and
picked b two ways on all 625 rows: lowest error count, and lowest NLL (the loss Platt
scaling uses). These rows are also the test rows, so the gains are optimistic. **Do not
adopt these numbers;** phase 2 must fit on a held-out split.

| Model | Today: acc (FN/FP) | Error-minimising b | acc (FN/FP) | NLL-minimising b | acc (FN/FP) |
|---|---|---|---|---|---|
| qwen3.6 | 83.5% (75/28) | +0.78 (+0.78 to +0.83) | 83.8% (50/51) | −0.08 | 83.4% (78/26) |
| qwen3.8 | 86.2% (54/32) | −0.13 (−0.37 to −0.13) | 86.6% (56/28) | −0.21 | 86.6% (56/28) |
| gemma | 87.5% (6/72) | −5.5 (−5.74 to −5.5) | 89.1% (9/59) | about −6 to −10 | 87–89% |

- **qwen3.6:** the offset that cuts errors trades 25 false "no" for 23 new false "yes".
  NLL wants almost no offset. On raw logprobs (before T) +0.78 is +1.52.
- **qwen3.8:** already close to balanced; a small negative offset removes 4 false "yes".
- **gemma:** the NLL optimum depends on where we clip the rounded 0 and 1 values (−7.7 at
  a 5e-5 clip, −9.6 at 1e-6), so it isn't a real number. Even the best offset leaves 59
  false "yes".
- **A scale as well (full Platt):** the NLL fit gives a = 1.2, b = 0.0 for qwen3.6 and
  a = 1.05, b = −0.2 for qwen3.8: a temperature change, which never flips an answer
  ([calibration.md §3](calibration.md)).

So for all three models the lean is **not** mainly a constant log-odds shift. It is a
few question families where the model's score carries little information.

## 3. Where it happens

By upstream domain (`.cache/jev-bench-upstream/data/<domain>/noul.jsonl`). Cells are false
"no" / false "yes".

| Source | Domain (stratum) | Rows | Gold yes | Jev | qwen3.6 | qwen3.8 | gemma |
|---|---|---|---|---|---|---|---|
| panoramic | invoices: "Does the stated total equal the sum of the line items?" (compositional) | 100 | 49 | 0 / 12 | **48 / 0** | **48 / 1** | 5 / **35** |
| panoramic | quant: "Is the average … greater than N?" (compositional) | 100 | 49 | 0 / 5 | 8 / 1 | 4 / 5 | 1 / **26** |
| panoramic | logic: "Does the conclusion logically follow?" (compositional) | 100 | 37 | 0 / 0 | 0 / **20** | 0 / **20** | 0 / 0 |
| panoramic | observability: "Does this log line indicate an error?" (atomic) | 100 | 42 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| typed_decisions | invoice_processing (compositional) | 200 | 71 | 6 / 0 | **17** / 4 | 0 / 3 | 0 / 6 |
| typed_decisions | security_incidents (decomposable) | 15 | 10 | 1 / 2 | 2 / 2 | 2 / 2 | 0 / 4 |
| typed_decisions | customer_service (decomposable) | 10 | 9 | 1 / 0 | 0 / 1 | 0 / 1 | 0 / 1 |

What the rows show:

- **invoices (sum the line items):** Qwen says "no" to 98–99 of 100. It misses 48 of the
  49 rows where the total is correct and gets all but at most one mismatch right, so it is always saying
  "no", not checking. Its p(yes) histograms for gold yes and gold no are almost the same
  (qwen3.6: mostly 0.1–0.4 for both). gemma does the opposite: 44 of 49 correct totals
  right, but 35 of 51 mismatches wrong, including all 6 where the gap is $1 or less.
- **quant (average vs a threshold):** Qwen's 9 errors cluster near the threshold (5 of 11
  rows within 2 of it, 1 of 79 rows 5 or more away). gemma's false "yes" rows spread
  further (15 of 79 rows 5 or more away).
- **logic:** only 5 distinct premises, each repeated 17–22 times. All 20 Qwen false "yes"
  are one template: *"If a number is even, it is divisible by 2. The number is not even.
  Conclusion: It is not divisible by 2."* The conclusion is true in arithmetic but does not
  follow from the premises (denying the antecedent). 20 rows, one mistake.
- **invoice_processing:** all 17 qwen3.6 false "no" come from *"This invoice appears to
  duplicate an invoice already submitted"*: it says "no" to all 100 of those rows. qwen3.8
  and gemma get all 100 right.
- **Atomic rows (observability) are perfect** for every model, so the lean isn't a blanket
  preference for one word.

Together, invoices, quant and logic hold 77 of qwen3.6's 103 errors, 78 of qwen3.8's 86
and 67 of gemma's 78.

## 4. Why: candidate causes and how to test each

| Cause | What the data says | How to test |
|---|---|---|
| **Option order.** `no` is always `(A)`, `yes` always `(B)` (`noul = ["no", "yes"]` in `prompts/decider_chat.toml`; `render_noul` in `gateway/questions.py`) | Can't explain opposite leans on the same prompt, or perfect atomic rows. It may still add a small push | Run with `yes` shown first (§5, experiment 2). The share of flipped answers measures the order effect |
| **Fixed question wording.** The frame "Question: … Options: (A) no (B) yes Answer: (" is fixed. Each JevBench row brings its own instructions, so the default `noul_question` is never used | Some instructions are statements, not questions ("This invoice appears to duplicate…"); qwen3.6 misses all 17 of those gold yes. But "The invoice reconciles with…" is also a statement and qwen3.6 gets 96/100 | Rephrase the frame (e.g. "Is the following true? …"), rebuild labels, rerun the affected domains |
| **Model priors.** Each model's default when unsure | Fits best: on the invoices rows Qwen defaults to "no", gemma to "yes". Papers find leans in both directions: a pull towards "no" across models and languages (Braun et al. 2025), and a lean towards the last-printed option plus the word "no" that varies by model (Huang 2026) | Contextual calibration (§5, experiment 3): score a content-free state and read the prior directly |
| **Computed questions are hard.** Sums, averages and formal logic with no reasoning step (`max_tokens=1`) | Fits best: invoices, quant and logic hold 75–91% of each model's errors; atomic rows are 100% for everyone. Errors cluster where the arithmetic is closest (quant margins, $1 invoice gaps) | Compare accuracy with a reasoning pass on the same rows (chat model, thinking on). If accuracy jumps, the gap is compute, not bias |

The two middle rows are linked: a model that can't compute an answer falls back to its
prior, so difficulty decides *where* it fails and the prior decides *which way*. This is why
the lean flips between Qwen and gemma on the same rows.

Background: position and letter bias in [option-ordering.md §2](option-ordering.md#2-position-and-letter-bias)
(Zheng et al. find it is mostly a prior over option letters, not position alone), and why
temperature can't move an answer across 0.5 in [calibration.md §3 and §6](calibration.md).

## 5. Fixes to test in phase 2 (DS-002)

All three rely only on JevBench gold labels or our own data, **never Jev outputs**. Split
the 625 noul rows once, by domain and label, into a fit half and a test half, and report
every result on the test half only. Keep a copy of today's run as the baseline.

**Experiment 1: per-profile noul offset (Platt-style).**

1. Done (2026-10-02): `calibration.json` v2 carries noul `b`, applied as σ(Δ/T + b);
   for qwen3.6 it ships only in `question_first` ([calibration.md §2](calibration.md)).
2. Fit b (and optionally a scale a) by NLL on the fit half, per profile + layout; log the
   unrounded letter logprobs, not the 4-decimal answers, so gemma's saturated rows stay
   distinguishable.
3. Report on the test half: accuracy, false "no" / false "yes", ECE, and accuracy per
   domain. Adopt only if accuracy rises and no domain drops by more than noise.
4. Expected (from §2, an estimate): under 1 point for Qwen, 1–2 for gemma.

**Experiment 2: `identity+reversed` for noul.** Moved, with M3's p(yes) under both orders:
[option-ordering.md §4](option-ordering.md#4-noul-order-and-the-yesno-lean).

**Experiment 3: contextual calibration (Zhao et al. 2021).**

1. For each noul question, also score a content-free state (e.g. `N/A`) with the same
   instructions; this costs one extra row.
2. Subtract that row's logit from the real one (per-option offset −log p_baseline).
3. A cheaper form is one baseline per profile, averaged over many content-free rows; the
   label-free relatives are domain-context calibration (random in-domain words) and batch
   calibration (the mean over a batch of real inputs).
4. Judge it on the test half as in experiment 1. It needs no labels to set, but still needs
   labelled rows to judge.

**Experiment 4 (diagnostic): a reasoning pass on the computed domains.** Not a fix for the
single-token readout, but it tells us how much of the gap any calibration could ever close.

## Caveats

- **Offsets in §2 are in-sample** on the same 625 rows they are scored on. They show the
  size of the effect, not a value to ship.
- **Duplicates inflate some counts:** logic has only 5 distinct premises, so "20 errors" is
  one mistake. observability has 6 distinct log lines.
- **Rounding:** answers carry 4 decimals, so logits beyond about ±9 can't be resolved. This
  mostly hides gemma's true margins.
- **Temperatures differ:** qwen3.6's probabilities are at T = 1.943, the others at 1.0. It
  doesn't change any answer, only the offsets' scale.
- **bf16 noise:** probabilities move ~0.03 under load, so near-tie rows can flip between
  runs (qwen3.6's false "no" went from 74 to 75).
- **Small cells:** security_incidents and customer_service have 15 and 10 gold noul rows.
- **One layout:** all runs use `decider_chat` with `option_orders = identity`.

## Sources

- Our runs: `docs/results/{qwen3.6-27b,qwen3.8-27b,gemma-4-31b}/2026-09-30T*/raw.jsonl`; Jev aggregates from `.cache/jev-results/2026-09-30T060719Z-jevbench/`; rows from `.cache/jev-bench-upstream/data/`.
- Zhao et al. (2021), *Calibrate Before Use* (contextual calibration): https://arxiv.org/abs/2102.09690
- Fei et al. (2023), *Mitigating Label Biases for In-context Learning* (domain-context calibration): https://arxiv.org/abs/2305.19148
- Zhou et al. (2024), *Batch Calibration* (ICLR 2024): https://arxiv.org/abs/2309.17249
- Zheng et al. (2024), *Large Language Models Are Not Robust Multiple Choice Selectors*: https://arxiv.org/abs/2309.03882
- Braun et al. (2025), *Acquiescence Bias in Large Language Models* (EMNLP 2025 Findings): https://arxiv.org/abs/2509.08480
- Huang (2026), *The yes-no bias of large language models reflects answer order and wording*: https://arxiv.org/abs/2607.05552
- Platt (1999), sigmoid calibration: https://home.cs.colorado.edu/~mozer/Teaching/syllabi/6622/papers/Platt1999.pdf
