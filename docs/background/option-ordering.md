# Option ordering

How the gateway shows a question's options in more than one order and averages the answers back, why that can help
(position and letter bias), and what our measurements found: M3 on text (2026-10-03), round 1 and round 2 on images
(2026-10-16/17) and round 3 on both (2026-10-18/19, DS-041). Round 3's design is
[the spec](../superpowers/specs/2026-10-17-orders-and-labels-design.md). This doc reports; the owner picks.

## Short answer

- **Today every profile reads one order (`identity`).** The owner kept it after M3 (a second order was not worth 2×
  reads, 2026-10-03) and after round 1 on images (2026-10-16).
- **A second order is one more row per question.** `average_back` maps each order's probabilities back to the
  caller's positions and takes the mean. On a 16-question request a token replay computed 1.88–1.90× the tokens (§1).
- **Text, round 3:** a second order on every question adds 0.4–0.7 accuracy points on index-dev on both models.
  On eval, always reversed adds 1.5 points on gemma and 0.2 on qwen3.8 (CI includes 0). Gating the second read on a
  low top probability keeps most of gemma's gain at 1.2–1.4 reads per question. Selective reads by option count keep
  less (§8).
- **Image, round 3:** on gemma no arm separates from identity; the best is +0.37 index [−0.12, +0.87] at 1.19 reads.
  On qwen3.8 the only CIs above 0 (4 of 82 arms) add the reversed read when a question has ≥ 3 or ≥ 4 options. The
  largest is `min_n 4 reversed/mean-logprob`, +2.04 [+0.67, +3.42] at 1.56 reads, with ECE 0.042 → 0.070. The CIs
  are not corrected for the comparisons (§9).
- **`tn-prob` is a calibration effect, not an order effect.** On gemma it cuts text ECE by 0.04–0.05 on index-dev
  in every arm. It does so even when only 4% of questions pay a second read. Round 2 saw the same with one read (§6).
- **PriDe never helped.** It is a per-letter prior subtracted before the softmax. Its accuracy change was 0 or
  negative on text and −0.26 index on images, and the gateway cannot serve it (§3).

## 1. How the gateway shows and averages orders

[`orders.py`](../../gateway/orders.py) shows each question with one or more orderings of its options. `perm[j]` is
the caller's option shown at position `j`. Models lean toward some positions (often the first); averaging over
orders spreads that lean across options.

| Setting | Orders for 3 options |
|---|---|
| `identity` (default, `OPTION_ORDERS`) | `[0,1,2]` |
| `identity+reversed` | `[0,1,2]`, `[2,1,0]` |
| `cyclic:<k>` | `k` evenly spaced rotations, at most one per option |

- **Rotations.** `cyclic:k` uses the shifts `round(i·n/k) mod n` for i < min(k, n). Python rounds halves to even, so
  `cyclic:2` on 3 options shifts by 2, and `cyclic:4` on 5 options shifts by 1, 2 and 4.
- **Rows.** Each order is its own row, so 2 orders means twice the rows.
  [decision-readout.md](decision-readout.md)'s example was built with `identity+reversed`: 3 questions gave 6 rows.
- **Averaging.** [`blend`](../../gateway/decide.py) applies a softmax to each order at T (the noul offset b is added
  per order), then `average_back` takes the mean per caller position. For `[.7,.2,.1]` in identity and `[.5,.3,.2]`
  in reversed order the result is `[.45, .25, .30]`.
- **Overrides.** A request may set `option_orders` (and `layout`); both are experiment hooks, not Jev API.
- **Calibration.** A fit holds for one option-order setting (`fit.orders`, `identity` today). Startup and
  `evaluate.py offline` warn when another setting uses it ([calibration.md](calibration.md)).

**Temperature and averaging.** Averaging happens *after* the softmax. For noul the "T never changes the winner" rule
still holds: two orders average above 0.5 exactly when their two Δs sum above 0, whatever T is. With 3+ options it
can break: a check on random synthetic logprobs found cases where T changed the averaged winner. Today's default is
one order (`identity`), so current runs are unaffected. Why T alone never moves an answer:
[calibration.md §3](calibration.md#3-why-temperature-never-changes-the-winner).

### What a second order costs in tokens

A 2026-09-29 replay ([prompt-layouts.md §3](prompt-layouts.md#3-what-each-layout-costs-in-prefix-sharing) has the
method; it predates front padding): `synthetic_request` with a 2,048-token state, 16 questions, 26 options.
`identity+reversed` gives each question two rows (32 in all). Reversed rows share the state with the identity rows,
so the state stays cached.

| Layout | Rows | Prompt | Cached | **Computed** | vs same layout, identity | vs `decider_chat` identity |
|---|---|---|---|---|---|---|
| `decider_chat` | 32 | 72,794 | 48,608 | **24,186** | 1.88x | 1.88x |
| `header` | 32 | 78,618 | 48,608 | **30,010** | 1.90x | 2.33x |
| `question_first` | 32 | 72,794 | 0 | **72,794** | 2.00x | 5.65x |

- Averaging costs about 1.9x the computed tokens, close to the row count. That is far from the "extra branch in
  one shared-prefix pass" (~+50%) that reflex measured for small requests. The reason is the 784-token rule:
  every extra row also recomputes the 498 tail tokens of the state.
- Throughput here is set by computed tokens per request (prompt-sharing.md §5: the GPU saturates at ~6,000 computed
  tokens/s). So 1.88x computed is, as an estimate, about half the requests per second. The replay counts tokens,
  not time.
- Round 3 counts cost per question: mean reads on text (text records hold no token counts), plus extra suffix tokens
  and mean input tokens on images (§7).

## 2. Position and letter bias

Research depth and sources are in [ordering-and-layout.md](../appendix/ordering-and-layout.md). Models favour
certain option letters and positions regardless of content. Zheng et al. find it is mostly a token-ID prior, not only
position, so where the right answer sits does not fully fix it. The usual fixes are:

- permutation averaging: show the options in 2+ orders and average the probabilities back, as `option_orders` does;
- PriDe-style prior estimation (§3).

Evidence on averaging is mixed. reflex reports ECE 0.088 to 0.061 on a 27B model with two orders. jobe found no
accuracy gain on its hard tier because the flips were symmetric noise. The notes recommended `identity+reversed` as
the standard profile, tested per question type before it became a default.

**Our flip rates.** The share of questions whose top answer changes between the identity and the reversed read (noul
left out), M3 on `header`:

| Profile | Split | All | 2 options | 3-5 | 6-26 | 27+ |
|---|---|---|---|---|---|---|
| gemma-4-31b | index-dev | 0.073 | 0.031 | 0.078 | 0.175 | 0.290 |
| gemma-4-31b | eval | 0.071 | 0.009 | 0.076 | 0.118 | 0.073 |
| qwen3.8-27b | index-dev | 0.093 | 0.039 | 0.116 | 0.229 | 0.289 |
| qwen3.8-27b | eval | 0.090 | 0.021 | 0.126 | 0.067 | 0.046 |

On image dev the flip rate is 0.124 on gemma and 0.202 on qwen3.8 (round 3 label screens, letters arm). Round 3 also
separated the letter from the alphabet: the `shuffled` label sets keep the letter tokens in a non-alphabetical order
([answer-labels.md](answer-labels.md)).

## 3. PriDe

PriDe (Zheng et al.) estimates a prior over option letters from a small sample read in cyclic orders. It then
subtracts that prior from each read's logprobs before the softmax. It needs one read per question once the prior is
known.

- **The gateway cannot serve it:** there is no `OPTION_ORDERS` value for it. M3 reported it as a diagnostic only.
- **M3, text (2026-10-03).** On `header`, gemma index-dev Δ accuracy −0.000 [−0.001, −0.000], eval ΔECE +0.022
  [+0.011, +0.030]. qwen3.8 eval Δ accuracy −0.007 [−0.011, −0.004]. qwen3.6 `decider_chat` eval
  −0.010 [−0.015, −0.006] ([m3-recommendations.md](../results/archive/m3-recommendations.md)).
- **Round 1, image (2026-10-16):** −0.26 index with identity reads, −0.09 with cyclic reads; neither separates (§6).
- **Identity reads mix two effects.** With identity orders only, PriDe mixes the gold-position skew with the letter
  bias. Cyclic orders put each option in every position and separate them. `vision_offline.py` needs at least 30
  reads per option count, else that option count is left undebiased.

## 4. Noul: order and the yes/no lean

The noul layout always shows `no` first as `(A)`, so a lean to position A and a lean to the word "no" are mixed
together ([noul-bias.md](noul-bias.md)). `identity+reversed` shows `yes` as `(A)` in the second row and averages both
back. It swaps position and letter together, so it separates the word from the slot, not the letter from the slot.

M3 measured p(yes) under both orders on `header`. If p(yes) moves with the order, the lean is to a position. If it
stays put, the lean is to the word.

| Profile | Split | Noul questions | p(yes), identity | p(yes), reversed | Gold yes |
|---|---|---|---|---|---|
| gemma-4-31b | index-dev | 143 | 0.502 | 0.510 | 0.399 |
| gemma-4-31b | eval | 666 | 0.367 | 0.346 | 0.359 |
| qwen3.8-27b | index-dev | 143 | 0.581 | 0.589 | 0.399 |
| qwen3.8-27b | eval | 666 | 0.329 | 0.360 | 0.359 |

p(yes) moves by at most 0.031 when the order flips, so the measured lean on these splits is mostly to the word, not
the slot. A noul-only second order would need a per-type setting; `option_orders` is one global setting today.

Round 3's text summaries break each policy down per type. Always reversed (`mean-prob`) against identity, noul
questions only, Δ accuracy in points:

| Profile | index-dev (154) | eval (666) |
|---|---|---|
| gemma-4-31b | +0.6 [+0.0, +1.9] | +3.2 [+1.8, +4.7] |
| qwen3.8-27b | −2.6 [−5.8, +0.0] | +0.8 [−0.6, +2.1] |

## 5. M3: text arms (2026-10-03)

M3 scored identity, `identity+reversed`, `cyclic:2/3/4` and PriDe on the index-dev and eval collects. Each arm used
its own calib-fitted T (b = 0). Accuracy change against identity
([m3-recommendations.md](../results/archive/m3-recommendations.md)):

| Profile | On `decider_chat` | On `header` |
|---|---|---|
| qwen3.6-27b | identity+reversed: +0.003 (index-dev), +0.011 (eval); 2 reads | cyclic:4: +0.003 / +0.007; 2.7–3.2 reads. identity+reversed fails on eval |
| qwen3.8-27b | keep identity: only cyclic:2 on eval | cyclic:2: +0.003 / +0.007; 2 reads |
| gemma-4-31b | identity+reversed: +0.007 / +0.008; 2 reads | identity+reversed: +0.005 / +0.015; 2 reads |

The owner kept `identity` for every profile: two orders were not worth 2× reads. qwen3.8's first-option bias
(DS-020): averaging recovers about +0.3 points on index-dev, far short of the 4.3-point gap to simple-jev.

## 6. Image orders, rounds 1 and 2

### Round 1, E5 (gemma-4-31b, 2026-10-16)

Baseline `fitT_id`, dev, 1,462 rows. Results:
[`2026-10-16T223919Z-r1-gemma-orders`](../results/vision-experiments/2026-10-16T223919Z-r1-gemma-orders/summary.md).

| config | index | Δ index [95% CI] | ECE | NLL | mean input tokens |
|---|---|---|---|---|---|
| fitT_id | 77.02 | baseline | 0.0407 | 0.5742 | 719 |
| pride_id | 76.76 | -0.26 [-1.07, +0.54] | 0.0406 | 0.5740 | 719 |
| fitT_cyc | 77.00 | -0.02 [-1.23, +1.21] | 0.0340 | 0.5783 | 966 |
| pride_cyc | 76.93 | -0.09 [-1.30, +1.15] | 0.0362 | 0.5776 | 966 |

Cyclic orders read 966 tokens per row against 719 (+247, about +34%). No arm separates from the baseline. The owner
kept identity orders ([vision-experiments.md §9](vision-experiments.md#9-round-1-results-gemma-4-31b)).

### Round 2, CPU (both models, 2026-10-17)

- **Reversed read only on many-option rows**
  ([`r2-cpu-orders`](../results/vision-experiments/2026-10-17T013235Z-r2-cpu-orders/summary.md)). All arms used the
  shipped text T. On gemma no arm separates (ge8: +0.11 [−0.02, +0.24]). On qwen3.8 ge4 is +1.46 [+0.12, +2.78] at
  0.56 second reads, with ECE +0.033 [+0.011, +0.039]. Round 3 repeats this as `min_n`.
- **T per option count** ([`r2-cpu-calibration`](../results/vision-experiments/2026-10-17T013235Z-r2-cpu-calibration/summary.md)).
  T(n) = α + β ln n fitted on text calib. On gemma image dev with one read, it moves ECE from 0.0808 to 0.0420.
  On qwen3.8 the text eval check got slightly worse (ECE 0.045 → 0.050). Round 3's `tn-prob` combine rule is this
  fit.

## 7. Round 3: the policies

Every policy reads only orders a collect already holds: the M3 text collects (`.cache/collect/{profile}/`, identity,
reversed and cyclic:2/3/4 reads) and two image dev collects per model (DS-034 identity+reversed, plus a new
`cyclic:4` collect). Scripts: [`order_policies.py`](../../scripts/order_policies.py) (policies, combine rules, fits),
[`r3_orders.py`](../../scripts/r3_orders.py) (text) and [`vision_orders.py`](../../scripts/vision_orders.py)
(image, paired by `vision_compare.py`).

| Family | Rule |
|---|---|
| Baselines | identity; always + second order; cyclic:2, cyclic:3, cyclic:4 |
| Gated (`top_p τ`) | identity first; add the second order only when the identity read's top probability < τ, τ ∈ {0.5, 0.6, 0.7, 0.8, 0.9} |
| Selective (`min_n k`) | add the second order only when the question has n ≥ k options, k ∈ {3, 4, 5, 6, 8} |
| Aleria (`aleria half`) | identity + the half turn; when their top answers differ and n ≥ 3, add the quarter turns |

- **Second order.** Reversed on text. On images both reversed and `half` (cyclic:2's second order) are scored.
- **Shifts (ruling R6).** `half` and Aleria's turns are the collected `cyclic:2`/`cyclic:4` shifts, round(i·n/k), not
  the literal n//2, n//4, 3n//4. The half turn differs from n//2 when n ≡ 3 (mod 4) (n = 3, 7, 11 …). The quarter
  turns differ at more counts (n = 5: 1, 2, 4 instead of 1, 2, 3).
- **Gates** read the identity read at the shipped T, so a gate never depends on the arm's own fit.
- **Combine rules.**
  - `mean-prob`: softmax each order at T and average the probabilities (today's `blend`).
  - `mean-logprob`: average the orders' letter logprobs per option, then softmax at T.
  - `tn-prob`: as `mean-prob` with T(n) = α + β ln n (round 2's fit; floor 0.05).
- **Fits (ruling R2).** Each policy's T, or α and β, is fitted per question type on text calib, b = 0, as M3 did.
  Image arms use the choice parameters, since image rows are all choice.
- **Image `half` arms (ruling R3)** borrow the text fit of the same family with second = reversed, because the text
  collects hold no half-turn reads. A 2-fold group cross-fit on image dev (`xfit`) is reported beside them as a
  reference only.
- **cyclic:3 is not scored on images (ruling R7).** n = 5 needs shift 3, which neither image collect holds.
- **Cost.**
  - Text: mean reads per question and the share paying a second read.
  - Images: the same, plus extra suffix tokens (the suffixes of every read after the first) and mean input tokens.
- **Metrics.**
  - Text: accuracy, ECE and NLL with M3's paired bootstrap, plus "approx skill": chance-corrected accuracy per
    source family, unweighted.
  - Images: the dev index with `vision_compare` (paired group bootstrap, 10,000 resamples, seed 0).

## 8. Round 3: text results

Runs:
[gemma-4-31b](../results/archive/2026-10-18T021201Z-r3-orders-text-gemma-4-31b/summary.md),
[qwen3.8-27b](../results/archive/2026-10-18T023336Z-r3-orders-text-qwen3.8-27b/summary.md).
Every policy is scored under all three combine rules; they also break each policy down per type and per option count.

The tables below are `mean-prob`. "reads" is mean reads per question; for a two-order policy the share paying a
second read is reads − 1. Δ is policy − identity with a 95% paired-bootstrap CI; the identity row shows absolute
accuracy (%), ECE and approx skill. Columns 2–5 are index-dev (15,635 questions), columns 6–9 are eval (2,827).

**gemma-4-31b** (`header`):

| policy | reads | Δ accuracy (pts) | Δ ECE | approx skill | reads | Δ accuracy (pts) | Δ ECE | approx skill |
|---|---|---|---|---|---|---|---|---|
| identity | 1.00 | 80.0 | 0.120 | 0.620 | 1.00 | 81.1 | 0.097 | 0.779 |
| always reversed | 2.00 | +0.5 [+0.2, +0.7] | -0.013 [-0.016, -0.010] | 0.640 | 2.00 | +1.5 [+0.9, +2.2] | +0.011 [-0.000, +0.020] | 0.813 |
| cyclic:2 | 2.00 | +0.5 [+0.2, +0.7] | -0.011 [-0.014, -0.008] | 0.636 | 2.00 | +1.3 [+0.7, +1.9] | +0.002 [-0.006, +0.010] | 0.811 |
| cyclic:3 | 2.39 | +0.7 [+0.4, +0.9] | -0.009 [-0.012, -0.006] | 0.637 | 2.65 | +0.9 [+0.2, +1.6] | +0.002 [-0.008, +0.009] | 0.812 |
| cyclic:4 | 2.73 | +0.6 [+0.3, +0.8] | -0.011 [-0.013, -0.008] | 0.635 | 3.17 | +1.1 [+0.5, +1.8] | +0.002 [-0.006, +0.011] | 0.814 |
| top_p 0.5 reversed | 1.04 | -0.0 [-0.2, +0.1] | -0.000 [-0.002, +0.001] | 0.623 | 1.02 | +0.2 [-0.1, +0.5] | +0.002 [-0.002, +0.005] | 0.781 |
| top_p 0.6 reversed | 1.06 | +0.1 [-0.0, +0.3] | -0.002 [-0.004, -0.000] | 0.626 | 1.05 | +0.6 [+0.2, +1.1] | -0.000 [-0.006, +0.005] | 0.788 |
| top_p 0.7 reversed | 1.09 | +0.2 [-0.0, +0.4] | -0.004 [-0.006, -0.002] | 0.630 | 1.10 | +1.0 [+0.5, +1.6] | +0.004 [-0.005, +0.010] | 0.795 |
| top_p 0.8 reversed | 1.14 | +0.4 [+0.2, +0.6] | -0.007 [-0.009, -0.004] | 0.639 | 1.19 | +1.3 [+0.7, +2.0] | +0.003 [-0.005, +0.010] | 0.806 |
| top_p 0.9 reversed | 1.22 | +0.4 [+0.2, +0.7] | -0.009 [-0.011, -0.006] | 0.640 | 1.36 | +1.6 [+1.0, +2.2] | +0.002 [-0.006, +0.011] | 0.814 |
| min_n 3 reversed | 1.39 | +0.2 [-0.0, +0.4] | -0.006 [-0.008, -0.004] | 0.633 | 1.65 | +0.8 [+0.2, +1.3] | +0.012 [+0.002, +0.019] | 0.782 |
| min_n 4 reversed | 1.34 | +0.1 [-0.0, +0.4] | -0.005 [-0.008, -0.003] | 0.633 | 1.52 | +0.8 [+0.2, +1.3] | +0.014 [+0.003, +0.020] | 0.782 |
| min_n 5 reversed | 1.19 | -0.0 [-0.2, +0.1] | -0.000 [-0.002, +0.001] | 0.621 | 1.24 | +0.6 [+0.2, +0.9] | +0.003 [-0.004, +0.008] | 0.783 |
| min_n 6 reversed | 1.18 | -0.0 [-0.2, +0.1] | -0.001 [-0.002, +0.001] | 0.619 | 1.22 | +0.5 [+0.2, +0.9] | +0.004 [-0.003, +0.009] | 0.783 |
| min_n 8 reversed | 1.18 | -0.0 [-0.2, +0.1] | -0.001 [-0.003, +0.001] | 0.619 | 1.20 | +0.5 [+0.2, +0.9] | +0.004 [-0.003, +0.009] | 0.783 |
| aleria half | 2.10 | +0.6 [+0.4, +0.8] | -0.009 [-0.012, -0.006] | 0.635 | 2.10 | +1.3 [+0.6, +1.9] | +0.004 [-0.006, +0.010] | 0.814 |

**qwen3.8-27b** (`header`):

| policy | reads | Δ accuracy (pts) | Δ ECE | approx skill | reads | Δ accuracy (pts) | Δ ECE | approx skill |
|---|---|---|---|---|---|---|---|---|
| identity | 1.00 | 78.6 | 0.023 | 0.557 | 1.00 | 81.0 | 0.093 | 0.789 |
| always reversed | 2.00 | +0.4 [+0.2, +0.7] | +0.000 [-0.004, +0.005] | 0.557 | 2.00 | +0.2 [-0.5, +0.9] | -0.012 [-0.022, +0.000] | 0.796 |
| cyclic:2 | 2.00 | +0.5 [+0.3, +0.8] | -0.000 [-0.005, +0.005] | 0.561 | 2.00 | +0.7 [+0.1, +1.3] | -0.008 [-0.018, +0.004] | 0.793 |
| cyclic:3 | 2.39 | +0.5 [+0.3, +0.8] | -0.001 [-0.005, +0.005] | 0.560 | 2.65 | -0.1 [-0.8, +0.6] | -0.014 [-0.024, -0.001] | 0.790 |
| cyclic:4 | 2.73 | +0.6 [+0.3, +0.9] | +0.001 [-0.004, +0.006] | 0.558 | 3.17 | +0.5 [-0.2, +1.2] | -0.011 [-0.021, +0.002] | 0.793 |
| top_p 0.5 reversed | 1.12 | +0.4 [+0.2, +0.6] | -0.002 [-0.005, +0.001] | 0.559 | 1.11 | +0.2 [-0.3, +0.7] | -0.002 [-0.008, +0.004] | 0.793 |
| top_p 0.6 reversed | 1.21 | +0.5 [+0.2, +0.7] | -0.003 [-0.007, +0.001] | 0.557 | 1.23 | +0.2 [-0.5, +0.8] | -0.009 [-0.017, +0.000] | 0.796 |
| top_p 0.7 reversed | 1.29 | +0.4 [+0.2, +0.7] | -0.003 [-0.007, +0.001] | 0.557 | 1.34 | +0.2 [-0.5, +0.8] | -0.013 [-0.022, -0.001] | 0.796 |
| top_p 0.8 reversed | 1.37 | +0.4 [+0.2, +0.7] | +0.000 [-0.005, +0.005] | 0.556 | 1.44 | +0.2 [-0.5, +0.9] | -0.014 [-0.024, -0.001] | 0.796 |
| top_p 0.9 reversed | 1.48 | +0.4 [+0.2, +0.7] | +0.002 [-0.003, +0.007] | 0.557 | 1.56 | +0.2 [-0.5, +0.9] | -0.012 [-0.021, +0.002] | 0.796 |
| min_n 3 reversed | 1.39 | +0.3 [+0.1, +0.5] | +0.001 [-0.004, +0.005] | 0.557 | 1.65 | +0.1 [-0.5, +0.6] | -0.014 [-0.021, -0.002] | 0.793 |
| min_n 4 reversed | 1.34 | +0.2 [+0.1, +0.4] | +0.001 [-0.003, +0.005] | 0.556 | 1.52 | +0.1 [-0.5, +0.6] | -0.013 [-0.020, -0.002] | 0.792 |
| min_n 5 reversed | 1.19 | +0.2 [+0.0, +0.3] | +0.004 [-0.001, +0.008] | 0.556 | 1.24 | -0.1 [-0.4, +0.2] | -0.008 [-0.013, -0.002] | 0.789 |
| min_n 6 reversed | 1.18 | +0.2 [+0.1, +0.3] | +0.004 [-0.002, +0.007] | 0.557 | 1.22 | -0.1 [-0.4, +0.1] | -0.008 [-0.014, -0.002] | 0.787 |
| min_n 8 reversed | 1.18 | +0.2 [+0.0, +0.3] | +0.004 [-0.002, +0.007] | 0.557 | 1.20 | -0.1 [-0.4, +0.1] | -0.009 [-0.014, -0.002] | 0.787 |
| aleria half | 2.13 | +0.6 [+0.3, +0.9] | +0.001 [-0.004, +0.006] | 0.558 | 2.09 | +0.6 [-0.0, +1.2] | -0.009 [-0.019, +0.003] | 0.792 |

- **Gated reads.** On gemma, `top_p 0.9 reversed` is within 0.1 point of always reversed on both splits (+0.4 /
  +1.6) at 1.22 / 1.36 reads. On qwen3.8, `top_p 0.5 reversed` matches it on index-dev (+0.4 at 1.12 reads). On qwen3.8
  eval only cyclic:2 has a CI above 0 (+0.7 [+0.1, +1.3]).
- **Selective reads** (`min_n`) gain less than gating at similar cost. On gemma eval `min_n 3`/`4` raise ECE
  (+0.012, +0.014, CIs above 0).
- **Combine rules.** Against `mean-prob`, `mean-logprob` moves accuracy by at most 0.3 point and ECE by at most
  0.005, and `tn-prob` moves accuracy by at most 0.04 point. On gemma `tn-prob` cuts index-dev ECE by 0.042–0.053
  and eval ECE by 0.009–0.024 in every policy, `top_p 0.5` (4% second reads) included. On qwen3.8 its index-dev ECE
  change is −0.003 to +0.005.
- **Fits.** Each policy's T is refitted on calib, so the identity row is not the shipped file. gemma's identity score
  T fits to 19.999, the search edge, against the shipped pooled 5.603 (the summaries' Fits tables).

## 9. Round 3: image results

Dev, 1,462 rows, Δ index against identity with a 95% paired group-bootstrap CI. Runs (orders.md has cost and fit per
arm; summary.md is the `vision_compare` table):
[gemma-4-31b](../results/vision-experiments/2026-10-19T010142Z-r3-orders-gemma-4-31b/orders.md),
[qwen3.8-27b](../results/vision-experiments/2026-10-19T010703Z-r3-orders-qwen3.8-27b/orders.md). These supersede the
2026-10-18T0255* runs, which had only the baseline reads. `cyclic:2` scores the same index as `always half` in every
combine rule and is left out below.

**gemma-4-31b** (identity: index 77.06, ECE 0.0808, NLL 0.6072, 719 input tokens):

| policy | mean reads | extra suffix tokens | mean input tokens | Δ index, mean-prob | Δ index, mean-logprob | Δ index, tn-prob |
|---|---|---|---|---|---|---|
| always reversed | 2.000 | 96.8 | 816 | -0.27 [-1.51, +0.96] | -0.27 [-1.55, +0.96] | -0.39 [-1.62, +0.79] |
| always half | 2.000 | 96.8 | 816 | -0.38 [-1.56, +0.81] | -0.38 [-1.57, +0.82] | -0.34 [-1.53, +0.87] |
| cyclic:4 | 3.191 | 247.1 | 966 | +0.12 [-1.06, +1.28] | +0.13 [-1.02, +1.27] | +0.20 [-0.95, +1.35] |
| aleria half | 2.196 | 135.1 | 854 | +0.12 [-1.04, +1.24] | +0.03 [-1.11, +1.14] | +0.10 [-1.06, +1.23] |
| top_p 0.5 reversed | 1.066 | 10.3 | 730 | -0.07 [-0.58, +0.41] | -0.05 [-0.55, +0.42] | -0.07 [-0.57, +0.41] |
| top_p 0.6 reversed | 1.114 | 17.7 | 737 | +0.07 [-0.68, +0.82] | +0.18 [-0.56, +0.94] | +0.07 [-0.67, +0.83] |
| top_p 0.7 reversed | 1.161 | 25.7 | 745 | -0.05 [-0.95, +0.85] | -0.05 [-0.94, +0.85] | -0.17 [-1.05, +0.69] |
| top_p 0.8 reversed | 1.222 | 35.7 | 755 | -0.41 [-1.49, +0.67] | -0.31 [-1.40, +0.80] | -0.53 [-1.59, +0.52] |
| top_p 0.9 reversed | 1.305 | 44.8 | 764 | -0.15 [-1.35, +1.05] | -0.15 [-1.39, +1.08] | -0.28 [-1.47, +0.91] |
| top_p 0.5 half | 1.066 | 10.3 | 730 | +0.09 [-0.35, +0.55] | +0.04 [-0.40, +0.51] | +0.09 [-0.35, +0.55] |
| top_p 0.6 half | 1.114 | 17.7 | 737 | +0.17 [-0.60, +0.94] | +0.08 [-0.68, +0.86] | +0.12 [-0.64, +0.89] |
| top_p 0.7 half | 1.161 | 25.7 | 745 | +0.03 [-0.93, +1.01] | -0.05 [-1.01, +0.93] | -0.01 [-0.97, +0.97] |
| top_p 0.8 half | 1.222 | 35.7 | 755 | -0.44 [-1.50, +0.63] | -0.43 [-1.52, +0.65] | -0.44 [-1.50, +0.63] |
| top_p 0.9 half | 1.305 | 44.8 | 764 | -0.26 [-1.43, +0.91] | -0.26 [-1.42, +0.92] | -0.26 [-1.42, +0.91] |
| min_n 3 reversed | 1.631 | 77.5 | 797 | +0.03 [-0.93, +0.99] | +0.03 [-0.96, +1.00] | -0.10 [-1.03, +0.82] |
| min_n 4 reversed | 1.560 | 72.8 | 792 | -0.22 [-1.04, +0.61] | -0.22 [-1.09, +0.64] | -0.34 [-1.15, +0.44] |
| min_n 5 reversed | 1.185 | 35.3 | 755 | +0.02 [-0.34, +0.38] | +0.24 [-0.12, +0.61] | +0.02 [-0.34, +0.38] |
| min_n 6 reversed | 1.179 | 34.9 | 754 | +0.02 [-0.34, +0.38] | +0.24 [-0.12, +0.61] | +0.02 [-0.34, +0.38] |
| min_n 8 reversed | 1.077 | 7.9 | 727 | +0.11 [-0.02, +0.24] | +0.11 [+0.00, +0.24] | +0.11 [-0.02, +0.24] |
| min_n 3 half | 1.631 | 77.5 | 797 | -0.08 [-0.98, +0.84] | -0.08 [-0.99, +0.85] | -0.04 [-0.94, +0.88] |
| min_n 4 half | 1.560 | 72.8 | 792 | -0.21 [-1.01, +0.61] | -0.21 [-1.02, +0.61] | -0.16 [-0.98, +0.66] |
| min_n 5 half | 1.185 | 35.3 | 755 | +0.32 [-0.16, +0.82] | +0.35 [-0.14, +0.84] | +0.37 [-0.12, +0.87] |
| min_n 6 half | 1.179 | 34.9 | 754 | +0.20 [-0.23, +0.61] | +0.22 [-0.21, +0.64] | +0.24 [-0.18, +0.67] |
| min_n 8 half | 1.077 | 7.9 | 727 | +0.11 [+0.00, +0.22] | +0.11 [+0.00, +0.22] | +0.11 [+0.00, +0.22] |

**qwen3.8-27b** (identity: index 73.31, ECE 0.0424, NLL 0.6029, 1,117 input tokens):

| policy | mean reads | extra suffix tokens | mean input tokens | Δ index, mean-prob | Δ index, mean-logprob | Δ index, tn-prob |
|---|---|---|---|---|---|---|
| always reversed | 2.000 | 93.8 | 1211 | +0.76 [-1.11, +2.60] | +1.26 [-0.65, +3.14] | +0.76 [-1.11, +2.60] |
| always half | 2.000 | 93.8 | 1211 | +0.38 [-1.59, +2.39] | +0.18 [-1.83, +2.18] | +0.38 [-1.59, +2.39] |
| cyclic:4 | 3.191 | 239.7 | 1357 | +0.68 [-1.34, +2.73] | +0.57 [-1.45, +2.62] | +0.68 [-1.34, +2.73] |
| aleria half | 2.331 | 145.3 | 1262 | +0.78 [-1.23, +2.81] | +0.69 [-1.32, +2.71] | +0.78 [-1.23, +2.81] |
| top_p 0.5 reversed | 1.202 | 34.6 | 1152 | +0.68 [-0.57, +1.93] | +0.95 [-0.26, +2.20] | +0.72 [-0.52, +1.98] |
| top_p 0.6 reversed | 1.298 | 43.5 | 1160 | +0.85 [-0.90, +2.55] | +1.25 [-0.52, +3.00] | +0.90 [-0.86, +2.61] |
| top_p 0.7 reversed | 1.374 | 49.7 | 1167 | +0.66 [-1.20, +2.48] | +1.05 [-0.84, +2.94] | +0.70 [-1.15, +2.53] |
| top_p 0.8 reversed | 1.479 | 58.0 | 1175 | +0.76 [-1.11, +2.60] | +1.26 [-0.65, +3.14] | +0.80 [-1.06, +2.65] |
| top_p 0.9 reversed | 1.611 | 69.2 | 1186 | +0.76 [-1.11, +2.60] | +1.26 [-0.65, +3.14] | +0.80 [-1.06, +2.65] |
| top_p 0.5 half | 1.202 | 34.6 | 1152 | +0.12 [-1.21, +1.44] | +0.08 [-1.27, +1.38] | +0.12 [-1.21, +1.44] |
| top_p 0.6 half | 1.298 | 43.5 | 1160 | +0.45 [-1.39, +2.28] | +0.24 [-1.61, +2.09] | +0.45 [-1.39, +2.28] |
| top_p 0.7 half | 1.374 | 49.7 | 1167 | +0.38 [-1.59, +2.37] | +0.18 [-1.82, +2.17] | +0.38 [-1.59, +2.37] |
| top_p 0.8 half | 1.479 | 58.0 | 1175 | +0.38 [-1.59, +2.39] | +0.18 [-1.83, +2.18] | +0.38 [-1.59, +2.39] |
| top_p 0.9 half | 1.611 | 69.2 | 1186 | +0.38 [-1.59, +2.39] | +0.18 [-1.83, +2.18] | +0.38 [-1.59, +2.39] |
| min_n 3 reversed | 1.631 | 75.2 | 1192 | +1.30 [-0.25, +2.80] | +1.79 [+0.21, +3.37] | +1.30 [-0.25, +2.80] |
| min_n 4 reversed | 1.560 | 70.7 | 1188 | +1.42 [+0.08, +2.74] | +2.04 [+0.67, +3.42] | +1.42 [+0.08, +2.74] |
| min_n 5 reversed | 1.185 | 34.7 | 1152 | +0.16 [-0.37, +0.69] | +0.34 [-0.21, +0.90] | +0.16 [-0.37, +0.69] |
| min_n 6 reversed | 1.179 | 34.3 | 1151 | +0.28 [-0.18, +0.77] | +0.46 [-0.03, +0.97] | +0.33 [-0.14, +0.82] |
| min_n 8 reversed | 1.077 | 7.0 | 1124 | -0.02 [-0.15, +0.11] | -0.02 [-0.15, +0.11] | -0.02 [-0.15, +0.11] |
| min_n 3 half | 1.631 | 75.2 | 1192 | +0.92 [-0.75, +2.64] | +0.71 [-0.98, +2.47] | +0.92 [-0.75, +2.64] |
| min_n 4 half | 1.560 | 70.7 | 1188 | +1.04 [-0.45, +2.60] | +0.84 [-0.69, +2.40] | +1.04 [-0.45, +2.60] |
| min_n 5 half | 1.185 | 34.7 | 1152 | +0.14 [-0.42, +0.68] | +0.05 [-0.53, +0.60] | +0.14 [-0.42, +0.68] |
| min_n 6 half | 1.179 | 34.3 | 1151 | +0.26 [-0.22, +0.76] | +0.17 [-0.34, +0.68] | +0.26 [-0.22, +0.76] |
| min_n 8 half | 1.077 | 7.0 | 1124 | +0.02 [-0.09, +0.13] | +0.02 [-0.11, +0.15] | +0.02 [-0.09, +0.13] |

- **gemma.** No CI excludes 0; `min_n 8`'s lower bounds are 0.00 (+0.11 at 1.08 reads). The largest point estimate
  is `min_n 5 half/tn-prob`, +0.37 [−0.12, +0.87] at 1.19 reads. Aleria is +0.12 [−1.04, +1.24] at 2.20 reads.
- **qwen3.8.**
  - The `min_n 3`/`4` reversed arms lead. `min_n 4 reversed/mean-logprob` is +2.04 [+0.67, +3.42] at 1.56 reads and
    +71 suffix tokens.
  - `min_n 3 reversed/mean-logprob` is +1.79 [+0.21, +3.37]. `min_n 4 reversed/mean-prob` is +1.42 [+0.08, +2.74],
    close to round 2's ge4 (+1.46).
  - The same rule with the half turn is +1.04 [−0.45, +2.60].
- **ECE.**
  - gemma: arms that read two or more orders on every question (always, cyclic, Aleria) lower ECE from 0.0808 to
    0.061–0.068 with `mean-prob` and 0.032–0.044 with `tn-prob`.
  - qwen3.8: the same arms raise it from 0.0424 to 0.066–0.081 with `mean-prob` and 0.077–0.090 with `tn-prob`.
    `min_n 4 reversed/mean-logprob` has 0.0700.
  - The image cross-fit references bring ECE to 0.034–0.041 (gemma) and 0.026–0.044 (qwen3.8): the text fits do not
    transfer exactly.
- **Agreement and per benchmark:** in each run's `summary.md`.

## Caveats

- **Many comparisons.**
  - Text: 45 arms per split and model; image: 82 arms per model. Every CI is unadjusted.
  - At this count, a few CIs that exclude 0 are expected by chance. Dev's minimum detectable Δ index is about 3.5
    points ([vision-experiments.md §5](vision-experiments.md#5-compare-and-how-to-read-it)).
- **Eval is a selection set.** The calibration gate and M3's verdicts chose on eval; index-dev is the cleaner text
  check, and image dev has been compared on many times (the holdout guards it).
- **Each arm's own fit.** Text ECE baselines use each arm's refitted T, not the shipped file. Image `half` arms
  borrow the reversed fit (R3), so their ECE column is biased; their index is not affected by T except in averaged
  or gated rows.
- **qwen3.8 padding.** The profile pads its prefix; image reads were padded for one order, so two-order arms are not
  exactly what live would compute ([vision-experiments.md §3](vision-experiments.md#3-collect)).
- **Cost is reads and tokens, not time.** No latency was measured for any round-3 arm; a second read's live cost
  depends on prefix caching (§1).
- **`tn-prob` on noul.** Noul has one option count, so its β is not identified; only T(2) matters.
- **bf16 noise.** Probabilities move ~0.03 under load ([determinism.md](determinism.md)); offline numbers equal live
  within that noise.
- **Replay, not measurement.** The token table in §1 comes from a simplified block-cache model of one request shape
  (prompt-layouts.md caveats).

## Sources

- Our code: [`orders.py`](../../gateway/orders.py), [`decide.py`](../../gateway/decide.py) (`blend`),
  [`order_policies.py`](../../scripts/order_policies.py), [`order_stats.py`](../../scripts/order_stats.py),
  [`r3_orders.py`](../../scripts/r3_orders.py), [`vision_orders.py`](../../scripts/vision_orders.py),
  [`m3.py`](../../scripts/m3.py), [`vision_offline.py`](../../scripts/vision_offline.py).
- Our results: [m3-recommendations.md](../results/archive/m3-recommendations.md), M3 `header` order runs
  ([gemma](../results/archive/gemma-4-31b/2026-10-03T033153Z-m3-orders-header/summary.md),
  [qwen3.8](../results/archive/qwen3.8-27b/2026-10-03T031727Z-m3-orders-header/summary.md)), the round 1, 2 and 3 runs
  linked above.
- Our research: [ordering-and-layout.md](../appendix/ordering-and-layout.md),
  [vision-research.md](../appendix/vision-research.md).
- Zheng et al., Large Language Models Are Not Robust Multiple Choice Selectors (PriDe): https://arxiv.org/abs/2309.03882
- reflex order averaging: https://github.com/kshetrajna12/reflex (`docs/results/order-averaging.md`)
- jobe: https://github.com/MantisShrimpdev/jobe
