# Calibration and confidence

What "calibrated" means, how the gateway calibrates today, how we measure it, what Jev's
`confidence` field really is, and why our biggest yes/no problem needs more than a
temperature. Numbers come from our code, [jevbench-vs-jev.md](../results/jevbench-vs-jev.md)
and the papers under Sources.

## Short answer

- **Calibrated** means: of all answers given at 80%, about 80% are right. It is a property
  of many answers together, not of one answer.
- **The gateway calibrates with a temperature T per question type:**
  `p = softmax(logprobs / T)`. Only `qwen3.6-27b` + `decider_chat` has one (T = 1.943 for
  all types, borrowed from decider). Everything else runs at T = 1.0, uncalibrated.
- **T never changes which answer wins,** so accuracy and the side of 0.5 a `noul` lands on
  are unchanged. T only changes how sure the answers sound.
- **We measure calibration with ECE (15 bins) and the Brier score.** JevBench summaries
  report both, plus a noul yes/no bias table (runs from 2026-09-30 on).
- **Jev's `confidence` is not a chance of being right.** It rescales the probabilities so
  that a uniform guess reads 0 and certainty reads 1.
- **Our biggest noul error is a lean, and T can't fix a lean.** qwen3.6 says "no" on 74 of
  267 gold-yes rows (Jev: 8); gemma says "yes" on 72 of 358 gold-no rows. A fix needs an
  offset term or option-order averaging, fitted in phase 2 (DS-002) on labelled data,
  never on Jev's outputs.

## 1. What calibration means

A model is calibrated when its stated probability matches how often it is right. You can
only check this over many answers: group them by stated probability ("bins"), then compare
each bin's average probability with its accuracy.

A **reliability diagram** draws that comparison: one bar per bin, bar height = accuracy.
A calibrated model's bars reach the diagonal (accuracy = confidence). Below, an
illustrative overconfident model (made-up numbers; the axis starts at 0.5):

```
accuracy
1.00 |                                ·· = perfect calibration (accuracy = confidence)
     |                          ··    ██ = measured accuracy of the bin
0.90 |
     |                    ··
0.80 |                          ██
     |              ··          ██    bars below the dots: overconfident
0.70 |                    ██    ██    ("says 95%, is right 81%")
     |        ··    ██    ██    ██
0.60 |              ██    ██    ██    bars above the dots would mean underconfident
     |  ··    ██    ██    ██    ██
0.50 |  ██    ██    ██    ██    ██
     +------------------------------
       0.5-  0.6-  0.7-  0.8-  0.9-   stated probability of the chosen answer (bin)
        0.6   0.7   0.8   0.9   1.0
```

Guo et al. (2017) found modern neural networks look like this: more accurate than older
ones, but overconfident. Letter-reading language models do too: a stock 7B was over 90%
confident on 13 of its 20 wrong answers ([4-inference-technique.md](../4-inference-technique.md)).

## 2. Temperature scaling, and how the gateway applies it

**Temperature scaling** (Guo et al. 2017) divides the scores by one number T before the
softmax. `T > 1` flattens the probabilities (fixes overconfidence); `T < 1` sharpens them.
T is fitted on held-out labelled data by minimising the negative log-likelihood (NLL, the
average −log p(correct answer)). The paper found this one number "surprisingly effective",
often beating methods with more parameters.

In the gateway (full flow in [decision-readout.md](decision-readout.md)):

```
vLLM letter logprobs  →  softmax(logprobs / T)  →  average over option orders  →  Jev answer
  readout.py             calibration.py            orders.py                       answers.py
```

- [`calibration.py`](../../gateway/calibration.py): `load_temperatures` reads `choice`,
  `score` and `noul` from `data/<profile>/<layout>/calibration.json`. A missing file or type
  means T = 1.0 plus a startup warning ([test](../../tests/unit/test_calibration.py)).
- vLLM returns logprobs over the whole vocabulary: `logprob = logit − log Z`. The
  `log Z / T` term is the same for every letter and cancels, so scaling logprobs equals
  scaling logits.

| Profile | `decider_chat` (default) | `header` | `question_first` |
|---|---|---|---|
| qwen3.6-27b | **T = 1.943** for all three types ([file](../../data/qwen3.6-27b/decider_chat/calibration.json)) | 1.0 | 1.0 |
| qwen3.8-27b | 1.0 | 1.0 | 1.0 |
| gemma-4-31b | 1.0 | 1.0 | 1.0 |

- **Where 1.943 comes from:** decider's fit for stock Qwen3.6-27B, bf16, chat layout, one
  temperature for every type (decider SERVING.md §8). Our `decider_chat` matches that
  prompt token for token ([`tests/parity`](../../tests/parity)).
- **How it did there:** ECE 0.021 on the Decision Index board
  ([3-leaderboard.md](../3-leaderboard.md)). We have not measured our own ECE yet.

Worked example, three options with letter logprobs −0.1, −2.5, −5.0:

| | p(A) | p(B) | p(C) | Winner | Jev `confidence` |
|---|---|---|---|---|---|
| T = 1.0 | 0.911 | 0.083 | 0.007 | A | 0.866 |
| T = 1.943 | 0.729 | 0.212 | 0.059 | A | 0.594 |

Same winner and same order of options; only the certainty changes.

## 3. Why temperature never changes the winner

Dividing every score by the same positive T keeps their order, and softmax preserves order.
So the top option stays on top and **accuracy does not depend on T** (Guo et al. say the
same). That is why the JevBench accuracy comparison is fair even though qwen3.6 ran at
T = 1.943 and the others at 1.0.

For `noul` the softmax has two options, `no` (shown as A) and `yes` (B). With
Δ = logprob(yes) − logprob(no):

```
p(yes) = e^(lp_yes/T) / (e^(lp_no/T) + e^(lp_yes/T)) = 1 / (1 + e^(−Δ/T)) = σ(Δ/T)
```

σ (the sigmoid) is above 0.5 exactly when its input is above 0. T > 0, so Δ/T has the sign
of Δ: **p(yes) ≥ 0.5 at any T exactly when it is at T = 1.**

| Δ (yes − no) | p(yes), T = 1 | p(yes), T = 1.943 | Answer |
|---|---|---|---|
| +3.0 | 0.953 | 0.824 | yes at both |
| +1.0 | 0.731 | 0.626 | yes at both |
| −0.4 | 0.401 | 0.449 | no at both |

T pulls p(yes) towards or away from 0.5; it never moves it across.

**Option-order averaging** ([`orders.py`](../../gateway/orders.py)) averages probabilities
*after* the softmax. For noul the rule still holds: two orders average above 0.5 exactly
when their two Δs sum above 0, whatever T is. With 3+ options it can break: a check on
random synthetic logprobs found cases where T changed the averaged winner. Today's default
is one order (`identity`), so current runs are unaffected.

## 4. Measuring calibration: ECE and Brier

The bench's calibration table ([`bench_report.py`](../../scripts/bench_report.py)) uses
JevBench's gold labels and these definitions:

- **Confidence** = the probability of the predicted answer (the largest probability). For
  noul that is max(p, 1 − p), since "yes" is predicted when `noul` ≥ 0.5
  ([`bench_data.py`](../../scripts/bench_data.py)). This is *not* Jev's `confidence` (§5).
- **ECE** (expected calibration error, as in Guo et al.): split confidence into 15
  equal-width bins (a confidence of 1.0 goes in the top bin), then take the row-weighted
  average of each bin's |accuracy − mean confidence|:

  ```
  ECE = Σ over bins  (rows in bin / all rows) × |accuracy(bin) − mean confidence(bin)|
  ```

- **Brier:** per row, Σ over options of (p_k − y_k)², with y_k = 1 for the gold option and
  0 otherwise; averaged over rows. A gold option missing from the answer counts as p = 0.

Worked ECE (illustrative, 1,000 answers in three occupied bins):

| Bin | Rows | Mean confidence | Accuracy | Gap | Weight × gap |
|---|---|---|---|---|---|
| 0.533–0.600 | 100 | 0.57 | 0.55 | 0.02 | 0.002 |
| 0.867–0.933 | 300 | 0.90 | 0.78 | 0.12 | 0.036 |
| 0.933–1.000 | 600 | 0.98 | 0.93 | 0.05 | 0.030 |
| | | | | **ECE** | **0.068** |

Worked Brier: probabilities (0.7, 0.2, 0.1) score 0.3² + 0.2² + 0.1² = **0.14** if option 1
is gold, and 0.7² + 0.8² + 0.1² = **1.14** if option 2 is. A noul at p(yes) = 0.9 scores
**0.02** if gold is yes, **1.62** if no.

| | Perfect | Uniform guess | Worst | Reference points |
|---|---|---|---|---|
| ECE | 0 | depends on accuracy | 1 | Decision Index: Jev 0.074, decider chat · Qwen3.6-27B 0.021, Jebadiah 27B 0.014, raw logits with no calibration 0.20–0.37 ([3-leaderboard.md](../3-leaderboard.md)). Guo et al.: uncalibrated networks typically 0.04–0.10 |
| Brier | 0 | (K − 1)/K: 0.5 noul, 0.667 for 3 options | 2 | Compare models on the same rows only |

ECE only asks whether probabilities are honest: always 60% sure and right 60% of the time
gives ECE 0. Brier also rewards being right. Report both.

The table also adds **noul bias** columns: % of noul rows answered "yes", % whose gold is
"yes", false "no" count (gold yes) and false "yes" count (gold no). §6 explains why.

## 5. Jev's `confidence` field

Jev returns `confidence` for `choice` and `score`, never for `noul`, computed from the
probabilities. Our [`answers.py`](../../gateway/answers.py) matches TypeSafe's adapter
(`_utils/confidence_metrics.py`, read for this doc) and
[6-answer-compatibility.md](../6-answer-compatibility.md):

- **choice:** `(p_max − 1/K) / (1 − 1/K)` for K options: uniform guess 0, certainty 1.
- **score:** `1 − (expected distance from the most likely level) / (the same for a uniform
  guess)`, clipped at 0. For n levels the uniform distance is the mean of |i − (n − 1)/2|.
- The adapter first renormalises the probabilities to sum to 1 (ours already do); both
  return 1.0 for a single option.

| Question | Probabilities | Working | `confidence` |
|---|---|---|---|
| choice, K = 3 | 0.88, 0.12, 0.00 | (0.88 − 0.333) / 0.667 | **0.82** (Jev showed 0.81, [doc 6](../6-answer-compatibility.md)) |
| choice, K = 2 | 0.60, 0.40 | (0.60 − 0.5) / 0.5 | **0.20** |
| choice, K = 6 | 0.60, 0.10, 0.10, 0.10, 0.05, 0.05 | (0.60 − 0.167) / 0.833 | **0.52** |
| score, 3 levels | 0.65, 0.30, 0.05 | mode 0; distance 0.40; uniform 0.667 | **0.40** |
| score, 3 levels | 0.10, 0.80, 0.10 | mode 1; distance 0.20 | **0.70** |
| score, 3 levels | 0.45, 0.10, 0.45 | mode 0; distance 1.00 > uniform | **0** (`score` = 1.0) |

**Why it is not the probability of being right:**

- **It can sit far below it.** A calibrated model at p = 0.60 on two options is right 60% of
  the time, yet `confidence` reads 0.20.
- **The same p_max reads differently with K:** 0.60 gives 0.20 with 2 options, 0.52 with 6.
- **Score confidence measures concentration, not correctness.** In the last row the model is
  split between levels 0 and 2; `confidence` is 0 and `score` 1.0 is a level it barely chose.
- **Measured on Jev:** its `confidence` field was worse calibrated than its top probability
  (ECE 0.035 / 0.078 / 0.18 on three sets), hence "Don't threshold on the confidence field"
  ([jev-notes.md §5](../appendix/jev-notes.md)).

For fixed K it rises with p_max, so it still ranks answers and can serve as a gate. Choose
any threshold on our own labelled data, not Jev's.

## 6. Why a yes/no lean can't be fixed by temperature

JevBench's 625 gold noul rows ([jevbench-vs-jev.md](../results/jevbench-vs-jev.md); the
"said yes" column is derived from its counts):

| Model | Gold yes, said no | Gold no, said yes | Said yes | Gold yes |
|---|---|---|---|---|
| Jev | 8 / 267 | 19 / 358 | 44.5% | 42.7% |
| qwen3.6-27b | **74 / 267** | 28 / 358 | 35.4% | 42.7% |
| qwen3.8-27b | 54 / 267 | 32 / 358 | 39.2% | 42.7% |
| gemma-4-31b | 6 / 267 | **72 / 358** | 53.3% | 42.7% |

qwen3.6 leans "no" and gemma leans "yes". Our reading (not yet measured): their Δ is shifted
by roughly a constant. T scales Δ but never flips its sign (§3), so every wrong row stays wrong.

A fix needs an **offset** that shifts Δ before the sigmoid. Illustration: a gold-yes row
with Δ = −0.4 gets p(yes) = 0.449 at T = 1.943, still "no". With an offset of +0.6,
σ(−0.4 + 0.6) = 0.550, "yes". The offset also flips gold-no rows with Δ between −0.6 and 0,
so it must be fitted on labelled data to balance the two.

| Fix | What it fits | Labels? | Changes answers? | Notes |
|---|---|---|---|---|
| Temperature (today) | σ(Δ/T) | yes | no | Over/underconfidence only |
| **Platt scaling** (Platt 1999) | σ(aΔ + b): scale + offset | yes | yes | Temperature is Platt with b = 0. For noul: one `b` per profile, layout, type |
| **Vector / matrix scaling** (Guo et al.) | softmax(w ⊙ z + b), or softmax(Wz + b) | yes | yes | Multi-option Platt; matrix has K² parameters and overfits with many options |
| **Contextual calibration** (Zhao et al. 2021) | Divide by the probabilities for a content-free input ("N/A") | **no**, one extra row | yes | = a per-option offset of −log p_baseline. Up to 30 points accuracy gained on GPT-3/GPT-2 |
| **Option-order averaging** ([`orders.py`](../../gateway/orders.py)) | Nothing: ask `no`-first and `yes`-first, average | no | yes | 2× rows. Cancels a lean to a position or letter, not to the word "no" |
| Noul wording ([`decider_chat.toml`](../../prompts/decider_chat.toml)) | New `noul_question` or labels | to evaluate | yes | Needs rebuilt labels and a refit T |

The noul layout always shows `no` first as `(A)`, so a lean to position A and a lean to the
word "no" are mixed together; the option-order experiment would separate them. An offset
can trade false "no" for false "yes", so judge it on held-out rows, never on its fit rows.

## 7. The phase-2 plan (DS-002)

DS-002 is still in triage (no spec yet). The ticket and the JevBench report propose:

1. **Labelled data only:** JevBench gold plus Decision Index, DecisionBench and
   typed-decisions, with a **calibration split** kept apart from the evaluation rows.
2. **Fit T per question type,** per profile and layout, by NLL (`calibrate.py`, not written
   yet). Per type because the direction differs: Jev was underconfident on noul (refit
   T = 0.66) but overconfident on choice and score (1.30, 1.92) ([jev-notes.md §5](../appendix/jev-notes.md)).
3. **Fit a noul offset per profile** (Platt-style) on the same split. The gateway has no
   offset term yet; [`calibration.py`](../../gateway/calibration.py) only knows T.
4. **Run the option-order experiment** (flip rate, accuracy, ECE) before changing the
   `identity` default.
5. **Stamp `calibration.json`** with tokenizer hash, layout hash and model revision, and
   refuse stale files as the gateway does for `labels.json`. Today a stale T loads silently.

**Never calibrate on Jev's outputs:** TypeSafe's terms forbid it
([1-what-is-jev.md](../1-what-is-jev.md)). Jev's per-row answers stay in `.cache/jev-results/`.

**Refit after any model, precision or layout change.** NVFP4 made reflex's calibration ~50%
worse ([5-combined-server.md](../5-combined-server.md)), so FP8/NVFP4 profiles (DS-005) or
DS-008's prompt padding would each need their own fit.

## Caveats

- **1.943 is decider's fit on decider's data, not ours.** Our own ECE is not measured yet;
  JevBench runs recorded before the new table have no probabilities to compute it from.
- **Pooled ECE:** the bench pools choice, score and noul, so opposite errors in one bin can
  partly cancel. A per-type split would show them.
- **ECE is not portable:** it depends on binning and sample size, so numbers from different
  benchmarks don't compare directly.
- **Noul Brier is doubled:** summing over both options gives twice the usual binary (p − y)².
- **bf16 noise:** probabilities can move ~0.03 under load; the live test allows 0.05
  ([`test_stability.py`](../../tests/live/test_stability.py)).
- **Averages, not guarantees:** good average calibration doesn't make each answer
  trustworthy, and a T may not transfer across datasets (Jev's refit T was 2.7 on unseen
  tickets, [3-leaderboard.md](../3-leaderboard.md)).

## Sources

- Guo et al. (2017), *On Calibration of Modern Neural Networks* (reliability diagrams, 15-bin ECE, temperature/vector/matrix scaling): https://arxiv.org/abs/1706.04599
- Platt (1999), *Probabilistic Outputs for Support Vector Machines…* (sigmoid fit 1/(1 + exp(Af + B))): https://home.cs.colorado.edu/~mozer/Teaching/syllabi/6622/papers/Platt1999.pdf
- Zhao et al. (2021), *Calibrate Before Use* (contextual calibration): https://arxiv.org/abs/2102.09690
- TypeSafe adapter, `confidence_metrics.py`: https://github.com/typesafe-ai/system-one-adapter-python/blob/main/src/system_one_adapter/_utils/confidence_metrics.py
- decider `docs/SERVING.md` §8 (Qwen3.6-27B bf16, chat layout, T 1.943): https://github.com/Mapika/decider/blob/main/docs/SERVING.md
- jev-ood-calibration (per-type refit T; ECE of the `confidence` field): https://github.com/scienthoon/jev-ood-calibration
