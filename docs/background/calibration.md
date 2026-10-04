# Calibration and confidence

What "calibrated" means, how the gateway calibrates today, how we measure it, what Jev's
`confidence` field really is, and why our biggest yes/no problem needs more than a
temperature. Numbers come from our code, [jevbench-vs-jev.md](../results/archive/jevbench-vs-jev.md)
and the papers under Sources.

## Short answer

- **Calibrated** means: of all answers given at 80%, about 80% are right. It is a property
  of many answers together, not of one answer.
- **The gateway calibrates with a temperature T per question type:**
  `p = softmax(logprobs / T)`, plus a yes-offset `b` for noul: `p(yes) = σ(Δ/T + b)`.
  All three profiles have our own fit for all three layouts (2026-10-02, §2).
- **T never changes which answer wins,** so accuracy and the side of 0.5 a `noul` lands on
  are unchanged. T only changes how sure the answers sound. `b` can flip a noul answer, so
  it ships only when it helps on held-out rows.
- **We measure calibration with ECE (15 bins) and the Brier score.** JevBench summaries
  report both, plus a noul yes/no bias table (runs from 2026-09-30 on).
- **Jev's `confidence` is not a chance of being right.** It rescales the probabilities so
  that a uniform guess reads 0 and certainty reads 1.
- **Our biggest noul error is a lean, and T can't fix a lean.** qwen3.6 says "no" on 74 of
  267 gold-yes rows (Jev: 8); gemma says "yes" on 72 of 358 gold-no rows. A fix needs an
  offset term or option-order averaging, fitted on labelled data, never on Jev's outputs.
  The offset exists now; for qwen3.6 it only earned its place in `question_first`.

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

- [`calibration.py`](../../gateway/calibration.py): `load_calibration` reads
  `data/<profile>/<layout>/calibration.json` (format 2): T for `choice`, `score` and `noul`,
  and the noul offset `b`, added per option order before averaging. A missing file means
  T = 1, b = 0 plus a startup warning ([test](../../tests/unit/test_calibration.py)).
- **Files are stamped.** Each records the tokenizer hash, layout hash, model revision and
  prefix padding it was fitted under. Startup refuses a stale, v1, unstamped or malformed
  file and names the field, as it does for `labels.json`. To refit, move the stale file
  aside, recollect calib and eval (`collect.py` ignores calibration files), then rerun
  `calibrate.py`.
- **A fit holds for one option-order setting** (`fit.orders`, `identity` today). Startup
  and `evaluate.py offline` warn when another setting uses it.
- vLLM returns logprobs over the whole vocabulary: `logprob = logit − log Z`. The
  `log Z / T` term is the same for every letter and cancels, so scaling logprobs equals
  scaling logits.

`header` ships for all three profiles (qwen3.6 since 2026-10-03, qwen3.8 and gemma since 2026-10-04; see
[m3-recommendations.md](../results/archive/m3-recommendations.md)).

Refit 2026-10-03 (T = 1 only when every candidate fails) by [`scripts/calibrate.py`](../../scripts/calibrate.py)
([report](../results/archive/qwen3.6-27b/2026-10-03T003833Z-calibrate/summary.md); file version 6 for qwen3.6, 3 for gemma and qwen3.8):

| Profile | Layout | T choice | T score | T noul | noul b |
|---|---|---|---|---|---|
| qwen3.6-27b | `decider_chat` | 1.648 | 1.927 (pooled; fitted 6.323) | 1.386 | 0 |
| qwen3.6-27b | `header` (shipped) | 1.627 | 1.958 (pooled; fitted 7.195) | 1.284 | 0 |
| qwen3.6-27b | `question_first` | 1.484 | 8.055 | 1.145 | +0.253 |
| gemma-4-31b ([report](../results/archive/gemma-4-31b/2026-10-03T004123Z-calibrate/summary.md)) | `decider_chat` | 4.123 | 5.378 (pooled; fitted 18.187) | 7.528 | −0.636 |
| | `header` (shipped) | 4.263 | 5.603 (pooled; fitted 19.999, edge) | 7.609 | 0 |
| | `question_first` | 3.839 | 5.278 (pooled; fitted 19.999, edge) | 7.266 | −0.460 |
| qwen3.8-27b ([report](../results/archive/qwen3.8-27b/2026-10-03T004419Z-calibrate/summary.md)) | `decider_chat` | 1.496 | 1.664 (pooled; fitted 4.420) | 0.970 | 0 |
| | `header` (shipped) | 1.536 | 1.775 (pooled; fitted 5.308) | 0.963 | 0 |
| | `question_first` | 1.352 | 6.264 | 0.825 | 0 |

Eval split, before (T = 1, b = 0) → after, from the report (each file's `fit.eval`):

| Layout | Type | n | NLL | ECE | Accuracy |
|---|---|---|---|---|---|
| `decider_chat` | choice | 1607 | 0.545 → 0.501 | 0.067 → 0.041 | 0.811, same |
| | score | 554 | 1.602 → 1.162 | 0.197 → 0.122 | 0.616, same |
| | noul | 666 | 0.296 → 0.286 | 0.045 → 0.038 | 0.880, same |
| `header` | choice | 1607 | 0.553 → 0.496 | 0.079 → 0.029 | 0.817, same |
| | score | 554 | 1.703 → 1.180 | 0.178 → 0.208 | 0.664, same |
| | noul | 666 | 0.278 → 0.266 | 0.040 → 0.023 | 0.895, same |
| `question_first` | choice | 1607 | 0.576 → 0.529 | 0.068 → 0.025 | 0.811, same |
| | score | 554 | 2.181 → 1.318 | 0.253 → 0.167 | 0.448, same |
| | noul | 666 | 0.287 → 0.277 | 0.037 → 0.026 | 0.860 → 0.877 |

- **How it is fitted:** minimise NLL on the calib split (JevBench gold + filtered
  DecisionBench), `identity` order. The eval split judges; Index rows are never used.
  Calib metrics sit in each file's `fit.calib`, eval metrics in `fit.eval`.
- **Per-type ECE gate:** the candidates are the fitted T, the pooled T (one T fitted on all
  types together) and, for noul with b shipping, the noul T refit at b = 0. One passes when
  eval ECE is no worse than at T = 1 beyond its bootstrap CI (CI low of the ECE change ≤ 0).
  The passing candidate with the lowest eval ECE change ships, ties to the earlier. T = 1
  ships only when every candidate fails, i.e. is significantly worse than T = 1: noise-level
  eval differences don't override the calib fit. A noul b that passes with its fitted T ships
  as is. Each file's `fit.t_decision` records, per type, the fitted, pooled and (when tried)
  b = 0 T with their ECE changes and the outcome. Pooled T: 1.927 `decider_chat`, 1.958
  `header`, 1.903 `question_first`.
- **NLL falls for every type and layout.** Accuracy is unchanged except `question_first`
  noul, where b ships (+1.65 points, 95% CI +0.30 to +3.00).
- **b ships only by the eval bootstrap rule.** `decider_chat` (+0.17) and `header` (+0.30)
  fitted a b that showed no gain on eval, so they run with b = 0.
- **Score is the weak spot.** Its fitted T is large (6–8). Calib's score rows are far more
  overconfident than eval's (NLL 2.7 vs 1.6 at T = 1), so one T can't suit both.
  - `header`: fitted 7.195 raised eval ECE by +0.127 (CI +0.050 to +0.178) and the pooled
    1.958 by +0.031 (CI −0.023 to +0.059). Fitted fails (CI low > 0); pooled passes, so it
    ships even though its point ECE is worse (eval ECE 0.178 → 0.208, NLL 1.703 → 1.180).
  - `decider_chat`: fitted 6.323 passes (+0.039, CI −0.036 to +0.104) but the pooled 1.927
    has the lower eval ECE change (−0.075, CI −0.114 to −0.019), so it ships.
  - `question_first`: fitted 8.055 passes (−0.086) and beats pooled (−0.050), so it ships.
- **One T for every type vs ours, `decider_chat`.** The pooled T (1.927) is close to
  decider's borrowed 1.943. Our per-type file (now with the pooled T for score) has the
  lowest eval ECE and NLL (offline runs, all 2,827 eval questions):

  | Calibration | ECE | NLL | Run |
  |---|---|---|---|
  | T = 1 | 0.085 | 0.694 | [eval](../results/archive/qwen3.6-27b/2026-10-02T163545Z-offline-eval-decider_chat-identity-uncalibrated/summary.md) |
  | ours (1.648 / 1.927 / 1.386) | 0.022 | 0.580 | [eval](../results/archive/qwen3.6-27b/2026-10-02T174816Z-offline-eval-decider_chat-identity/summary.md) |
  | pooled 1.927, every type | 0.038 | 0.597 | [eval](../results/archive/qwen3.6-27b/2026-10-02T163557Z-offline-eval-decider_chat-identity-T1.927/summary.md) |
  | decider's 1.943, every type | 0.041 | 0.598 | [eval](../results/archive/qwen3.6-27b/2026-10-02T163601Z-offline-eval-decider_chat-identity-T1.943/summary.md) |

- **Transfer check (index-dev, never fitted or chosen on).** 7,990 rows, 14,684 gold
  questions, 99% choice. Accuracy is unchanged by T; `question_first`'s b moves noul
  accuracy from 0.874 to 0.860 (143 questions).

  | Layout | Calibration | ECE | NLL | Accuracy | Run |
  |---|---|---|---|---|---|
  | `decider_chat` | T = 1 | 0.108 | 0.887 | 0.761 | [index-dev](../results/archive/qwen3.6-27b/2026-10-02T163611Z-offline-index-dev-decider_chat-identity-uncalibrated/summary.md) |
  | | ours | 0.040 | 0.723 | 0.761 | [index-dev](../results/archive/qwen3.6-27b/2026-10-02T174829Z-offline-index-dev-decider_chat-identity/summary.md) |
  | | pooled 1.927 | 0.025 | 0.710 | 0.761 | [index-dev](../results/archive/qwen3.6-27b/2026-10-02T163632Z-offline-index-dev-decider_chat-identity-T1.927/summary.md) |
  | | decider's 1.943 | 0.025 | 0.710 | 0.761 | [index-dev](../results/archive/qwen3.6-27b/2026-10-02T163641Z-offline-index-dev-decider_chat-identity-T1.943/summary.md) |
  | `header` | T = 1 | 0.105 | 0.829 | 0.780 | [index-dev](../results/archive/qwen3.6-27b/2026-10-02T163722Z-offline-index-dev-header-identity-uncalibrated/summary.md) |
  | | ours | 0.045 | 0.672 | 0.780 | [index-dev](../results/archive/qwen3.6-27b/2026-10-03T004723Z-offline-index-dev-header-identity/summary.md) |
  | `question_first` | T = 1 | 0.103 | 0.881 | 0.751 | [index-dev](../results/archive/qwen3.6-27b/2026-10-02T163733Z-offline-index-dev-question_first-identity-uncalibrated/summary.md) |
  | | ours | 0.046 | 0.752 | 0.751 | [index-dev](../results/archive/qwen3.6-27b/2026-10-02T174851Z-offline-index-dev-question_first-identity/summary.md) |

- **Transfer check, gemma and qwen3.8 (index-dev, same 14,684 questions).** Choice, score
  and noul pooled, `identity` order. Accuracy is unchanged by T except where noted.
  Gemma's shipped file is unchanged by the T = 1 rule; qwen3.8's T = 1 types now ship their
  fitted or pooled T.

  | Profile | Layout | ECE | NLL | Accuracy | Runs |
  |---|---|---|---|---|---|
  | gemma-4-31b | `decider_chat` | 0.241 → 0.155 | 3.486 → 0.970 | 0.749 | [T = 1](../results/archive/gemma-4-31b/2026-10-03T001603Z-offline-index-dev-decider_chat-identity-uncalibrated/summary.md), [shipped](../results/archive/gemma-4-31b/2026-10-03T001550Z-offline-index-dev-decider_chat-identity/summary.md) |
  | | `header` | 0.204 → 0.126 | 3.013 → 0.814 | 0.789 | [T = 1](../results/archive/gemma-4-31b/2026-10-03T001624Z-offline-index-dev-header-identity-uncalibrated/summary.md), [shipped](../results/archive/gemma-4-31b/2026-10-03T001614Z-offline-index-dev-header-identity/summary.md) |
  | | `question_first` | 0.241 → 0.163 | 3.340 → 0.982 | 0.749 | [T = 1](../results/archive/gemma-4-31b/2026-10-03T001647Z-offline-index-dev-question_first-identity-uncalibrated/summary.md), [shipped](../results/archive/gemma-4-31b/2026-10-03T001637Z-offline-index-dev-question_first-identity/summary.md) |
  | qwen3.8-27b | `decider_chat` | 0.060 → 0.021 | 0.837 → 0.734 | 0.769 | [T = 1](../results/archive/qwen3.8-27b/2026-10-03T002206Z-offline-index-dev-decider_chat-identity-uncalibrated/summary.md), [shipped](../results/archive/qwen3.8-27b/2026-10-03T004736Z-offline-index-dev-decider_chat-identity/summary.md) |
  | | `header` | 0.074 → 0.021 | 0.812 → 0.694 | 0.779 | [T = 1](../results/archive/qwen3.8-27b/2026-10-03T002229Z-offline-index-dev-header-identity-uncalibrated/summary.md), [shipped](../results/archive/qwen3.8-27b/2026-10-03T004746Z-offline-index-dev-header-identity/summary.md) |
  | | `question_first` | 0.058 → 0.038 | 0.872 → 0.784 | 0.755 | [T = 1](../results/archive/qwen3.8-27b/2026-10-03T002251Z-offline-index-dev-question_first-identity-uncalibrated/summary.md), [shipped](../results/archive/qwen3.8-27b/2026-10-03T004756Z-offline-index-dev-question_first-identity/summary.md) |

  Gemma stays far from calibrated on index-dev (ECE 0.13 to 0.16) although its eval ECE
  falls to 0.03 to 0.08, so its fitted Ts do not fully transfer. qwen3.8's `header` choice
  was the rule's motivating case (eval ECE change +0.002, CI −0.022 to +0.022, T = 1 under
  the old rule): with its fitted T the layout's index-dev ECE is 0.021, against 0.074 at T = 1.

- **Replaces decider's 1.943**, one T for every type (decider SERVING.md §8); the old value
  sits in the file's first comment.

Worked example, three options with letter logprobs −0.1, −2.5, −5.0:

| | p(A) | p(B) | p(C) | Winner | Jev `confidence` |
|---|---|---|---|---|---|
| T = 1.0 | 0.911 | 0.083 | 0.007 | A | 0.866 |
| T = 1.648 (qwen3.6 choice) | 0.779 | 0.182 | 0.040 | A | 0.668 |

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

JevBench's 625 gold noul rows ([jevbench-vs-jev.md](../results/archive/jevbench-vs-jev.md); the
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
| Temperature (all types) | σ(Δ/T) | yes | no | Over/underconfidence only |
| **Platt scaling** (Platt 1999) | σ(aΔ + b): scale + offset | yes | yes | Temperature is Platt with b = 0. The gateway's noul fit is this, with a = 1/T: one `b` per profile and layout |
| **Vector / matrix scaling** (Guo et al.) | softmax(w ⊙ z + b), or softmax(Wz + b) | yes | yes | Multi-option Platt; matrix has K² parameters and overfits with many options |
| **Contextual calibration** (Zhao et al. 2021) | Divide by the probabilities for a content-free input ("N/A") | **no**, one extra row | yes | = a per-option offset of −log p_baseline. Up to 30 points accuracy gained on GPT-3/GPT-2 |
| **Option-order averaging** ([`orders.py`](../../gateway/orders.py)) | Nothing: ask `no`-first and `yes`-first, average | no | yes | 2× rows. Cancels a lean to a position or letter, not to the word "no" |
| Noul wording ([`decider_chat.toml`](../../prompts/decider_chat.toml)) | New `noul_question` or labels | to evaluate | yes | Needs rebuilt labels and a refit T |

The noul layout always shows `no` first as `(A)`, so a lean to position A and a lean to the
word "no" are mixed together; the option-order experiment would separate them. An offset
can trade false "no" for false "yes", so judge it on held-out rows, never on its fit rows.

## 7. The phase-2 plan (DS-002)

Spec: [phase-2 design](../superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md).
Items 2, 3 and 5 are done ([report](../results/archive/qwen3.6-27b/2026-10-03T003833Z-calibrate/summary.md)):

1. **Labelled data only:** JevBench gold plus Decision Index, DecisionBench and
   typed-decisions, with a **calibration split** kept apart from the evaluation rows.
2. **Done: fit T per question type,** per profile and layout, by NLL (`calibrate.py`;
   qwen3.6 fitted, §2). Per type because the direction differs: Jev was underconfident on
   noul (refit T = 0.66) but overconfident on choice and score (1.30, 1.92)
   ([jev-notes.md §5](../appendix/jev-notes.md)).
3. **Done: fit a noul offset** (Platt-style) on the same split, per profile and layout.
   It ships only when the eval split shows a gain (qwen3.6: `question_first` only).
4. **Run the option-order experiment** (flip rate, accuracy, ECE) before changing the
   `identity` default.
5. **Done: stamp `calibration.json`** with tokenizer hash, layout hash, model revision and
   prefix padding; the gateway refuses stale files as it does for `labels.json`.

**Never calibrate on Jev's outputs:** TypeSafe's terms forbid it
([1-what-is-jev.md](../1-what-is-jev.md)). Jev's per-row answers stay in `.cache/jev-results/`.

**Refit after any model, precision or layout change.** NVFP4 made reflex's calibration ~50%
worse ([5-combined-server.md](../5-combined-server.md)), so FP8/NVFP4 profiles (DS-005) or
DS-008's prompt padding would each need their own fit.

## Caveats

- **JevBench runs before 2026-10-02 used decider's T = 1.943 (qwen3.6) or T = 1.** Offline
  index-dev transfer checks (§2) cover all three profiles; eval-split offline reruns cover
  qwen3.6 `decider_chat` only.
- **Eval is now a selection set.** The b rule and the T gate both chose on eval, so the
  eval "after" numbers in §2 are mildly optimistic. M3 must not treat eval as untouched;
  index-dev is the cleaner held-out check.
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
