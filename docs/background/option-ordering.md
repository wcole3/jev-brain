# Option ordering

How the gateway shows a question's options in more than one order and averages the answers back, why that can help
(position and letter bias), and what our measurements found: M3 on text (2026-10-03), round 1 and round 2 on images
(2026-10-16/17), round 3 on both (2026-10-18/19, DS-041) and round 4 on `decider_chat` and an intro blurb
(2026-10-19/20, DS-043). Designs: [round 3](../superpowers/specs/2026-10-17-orders-and-labels-design.md),
[round 4](../superpowers/specs/2026-10-19-layouts-and-blurb-design.md). This doc reports; the owner picks.

## Short answer

- **Profiles read their own orders (owner, 2026-10-20).** gemma reads `top_p:0.9+reversed` on text and `identity`
  on images. qwen3.8 reads `min_n:4+reversed` on text and images. qwen3.6 reads `identity`. Every setting combines
  with `mean-logprob`. Before, every profile read `identity`, kept after M3 (2026-10-03) and round 1 on images.
- **A second order is one more row per question.** `average_back` maps each order's probabilities back to the
  caller's positions and takes the mean. On a 16-question request a token replay computed 1.88–1.90× the tokens (§1).
- **Text, round 3:** a second order on every question adds 0.4–0.7 accuracy points on index-dev on both models.
  On eval, always reversed adds 1.5 points on gemma and 0.2 on qwen3.8, whose CI includes 0. Gating the second read
  on a low top probability keeps most of gemma's gain at 1.2–1.4 reads per question. Selective reads by option count
  keep less (§8).
- **Image, round 3:** on gemma no arm separates from identity; the best is +0.37 index [−0.12, +0.87] at 1.19 reads.
  On qwen3.8 the only CIs above 0 (4 of 81 arms) add the reversed read when a question has ≥ 3 or ≥ 4 options. The
  largest is `min_n 4 reversed/mean-logprob`, +2.04 [+0.67, +3.42] at 1.56 reads, with ECE 0.042 → 0.070. The CIs
  are not corrected for the comparisons (§9).
- **On gemma, `tn-prob`'s ECE gain comes from its T(n) fit, not from extra orders.** Against identity (one read at
  its own refit T), it cuts gemma's text ECE by 0.04–0.05 on index-dev in every arm, even when only 4% of questions
  pay a second read; round 2 saw the same with one read (§6). On qwen3.8 it moves text ECE by −0.003 to +0.005 and
  raises image ECE (§8, §9).
- **Round 4, `decider_chat` text:** gemma gains as on `header` on index-dev (+0.4 to +0.5 with a second order on
  every question); on eval always reversed adds +0.8 against `header`'s +1.5. On qwen3.8 only selective reads
  separate on index-dev (+0.2 to +0.3 at 1.13–1.19 reads) (§10).
- **Round 4, images:** on `decider_chat`, no gemma arm separates; on qwen3.8 `min_n 4 reversed` adds +1.36 to +1.40
  (CI lower bounds +0.01, +0.04) and `min_n 6 reversed` +0.43 to +0.50. With the blurb on `header`, gemma's
  `min_n 5 reversed/mean-logprob` adds +0.73 [+0.24, +1.26] and no qwen3.8 arm separates. 10 of 300 image CIs lie
  above 0, none corrected (§10).
- **Round 4, blurb grid:** against its like-for-like `header` control on index-dev-2k, the blurb moves each arm's
  Δ accuracy by −0.21 to +0.16 points (§10).
- **PriDe never helped.** It is a per-letter prior subtracted before the softmax. Its accuracy change was 0 or
  negative on text and −0.26 index on images, and the gateway cannot serve it (§3).
- **Cutdown failed on gemma (negative, 2026-10-20).** Re-asking an uncertain choice question with its weakest options
  removed never beat the first read: −5.7 to +0.7 accuracy points on the re-asked questions, and worse ECE for the
  half and halving cuts. With gold still kept, the re-read picks worse than the first read (§11).

## 1. How the gateway shows and averages orders

[`orders.py`](../../gateway/orders.py) shows each question with one or more orderings of its options. `perm[j]` is
the caller's option shown at position `j`. Models lean toward some positions (often the first); averaging over
orders spreads that lean across options.

| Setting | Orders for 3 options |
|---|---|
| `identity` (default, `OPTION_ORDERS`) | `[0,1,2]` |
| `identity+reversed` | `[0,1,2]`, `[2,1,0]` |
| `cyclic:<k>` | `k` evenly spaced rotations, at most one per option |
| `min_n:<k>+reversed` | `[0,1,2]`, plus `[2,1,0]` when the question has ≥ k options |
| `top_p:<τ>+reversed` | `[0,1,2]`, plus `[2,1,0]` in a second pass when the identity top probability is < τ |

- **Rotations.** `cyclic:k` uses the shifts `round(i·n/k) mod n` for i < min(k, n). Python rounds halves to even, so
  `cyclic:2` on 3 options shifts by 2, and `cyclic:4` on 5 options shifts by 1, 2 and 4.
- **Rows.** Each order is its own row, so 2 orders means twice the rows.
  [decision-readout.md](decision-readout.md)'s example was built with `identity+reversed`: 3 questions gave 6 rows.
- **Averaging.** [`combine`](../../gateway/decide.py) has `average_back` map each order's raw logprobs to caller
  order and take the mean, shifts "yes" by b·T for noul, then takes one softmax at T (mean-logprob). For two orders
  of `[.7,.2,.1]` and `[.5,.3,.2]` that is a geometric, not arithmetic, blend.
- **Overrides.** A request may set `option_orders` (and `layout`); both are experiment hooks, not Jev API.
- **Calibration.** A fit holds for one option-order setting (`fit.orders`); the gateway refuses another setting's file. gemma
  keeps `calibration-identity.json` beside `calibration.json` for its image requests ([calibration.md](calibration.md)).

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
the standard profile, to be tested per question type before making it the default; it never became one.

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
([answer-labels.md](answer-labels.md); on images the labels also clash with the options' own keys, see Caveats).

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
stays put, the lean is to the word. M3's index-dev had 143 noul questions; round 3's has 154, because index-dev was
recollected since (14,680–14,684 → 15,635 questions).

| Profile | Split | Noul questions | p(yes), identity | p(yes), reversed | Gold yes |
|---|---|---|---|---|---|
| gemma-4-31b | index-dev | 143 | 0.502 | 0.510 | 0.399 |
| gemma-4-31b | eval | 666 | 0.367 | 0.346 | 0.359 |
| qwen3.8-27b | index-dev | 143 | 0.581 | 0.589 | 0.399 |
| qwen3.8-27b | eval | 666 | 0.329 | 0.360 | 0.359 |

On index-dev both models say "yes" more often than gold (mean p(yes) 0.50 and 0.58 against 0.40), and flipping the
order moves mean p(yes) by at most 0.008 there, so that yes lean is not a lean to a slot. On any split the order moves
mean p(yes) by at most 0.031. A noul-only second order would need a per-type setting; `option_orders` is one global
setting today.

Round 3's text summaries break each policy down per type. Always reversed (`mean-prob`) against identity, noul
questions only, Δ accuracy in points:

| Profile | index-dev (154) | eval (666) |
|---|---|---|
| gemma-4-31b | +0.6 [+0.0, +1.9] | +3.2 [+1.8, +4.7] |
| qwen3.8-27b | −2.6 [−5.8, +0.0] | +0.8 [−0.6, +2.1] |

A second order raises gemma's eval noul accuracy by 3.2 points [+1.8, +4.7], while its mean p(yes) differs by 0.021
between the two orders.

## 5. M3: text arms (2026-10-03)

M3 scored identity, `identity+reversed`, `cyclic:2/3/4` and PriDe on the index-dev and eval collects. Each arm used
its own calib-fitted T (b = 0). Accuracy change against identity
([m3-recommendations.md](../results/archive/m3-recommendations.md)):

| Profile | On `decider_chat` | On `header` |
|---|---|---|
| qwen3.6-27b | identity+reversed: +0.003 (index-dev), +0.011 (eval); 2 reads | cyclic:4: +0.003 / +0.007; 2.7–3.2 reads. identity+reversed fails on eval |
| qwen3.8-27b | keep identity: only cyclic:2 on eval | cyclic:2: +0.003 / +0.007; 2 reads |
| gemma-4-31b | identity+reversed: +0.007 / +0.008; 2 reads | identity+reversed: +0.005 / +0.015; 2 reads |

The owner kept `identity` for every profile; for gemma the recorded reason is that two orders were not worth 2×
reads. qwen3.8's first-option bias
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
- **Image `half` arms (ruling R3)** use the text fit of the same family with second = reversed. Their own text fit is
  computable (`half` is cyclic:2's second order, and every text collect holds cyclic:2 reads) but was not run. Where
  both fits exist they are close: gemma's always half `mean-prob` used T 4.090 against cyclic:2's 4.053 (the same
  order pair), and `tn-prob` α 7.10 against 6.85; qwen3.8 1.457 against 1.462. A 2-fold group cross-fit on image dev
  (`xfit`) is reported beside them as a reference only.
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
- **Combine rules.** Against each policy's `mean-prob` arm, `mean-logprob` moves accuracy by at most 0.3 point and
  ECE by at most 0.005, and `tn-prob` moves accuracy by at most 0.04 point. On gemma `tn-prob` lowers ECE against
  `mean-prob` by 0.036–0.044 on index-dev and 0.017–0.028 on eval in every policy, `top_p 0.5` (4% second reads)
  included. On qwen3.8 the same difference is −0.003 to +0.005 on index-dev and +0.001 to +0.005 on eval.
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

## 10. Round 4: `decider_chat` and the blurb

Round 4 (DS-043, 2026-10-19/20; [spec](../superpowers/specs/2026-10-19-layouts-and-blurb-design.md)) ran §7's
policies, unchanged, on `decider_chat` (text and image) and on `header` with an intro blurb
([prompt-layouts.md §5](prompt-layouts.md#5-intro-blurb-round-4), which also has the blurb screen). Fits, combine
rules, cost and metrics are as in §7 unless noted.

**Arm counts.** Each text grid scores 45 arms per split (15 policies × 3 combine rules); each image grid 75 policy
arms plus 6 cross-fit references. Round 4 adds 10 text grid-splits and 4 image grids. No CI is corrected for these
comparisons.

### `decider_chat`, text

Same collects and splits as §8: the M3 full collects hold `decider_chat` records beside `header`'s. Gates read the
identity read at the shipped `data/<profile>/decider_chat/calibration.json` T. index-dev has 15,636 questions
(round 3's `header`: 15,635), eval 2,827. Runs:
[gemma-4-31b](../results/archive/2026-10-19T141129Z-r4-orders-text-decider_chat-gemma-4-31b/summary.md),
[qwen3.8-27b](../results/archive/2026-10-19T144419Z-r4-orders-text-decider_chat-qwen3.8-27b/summary.md). Tables as in
§8 (`mean-prob`; columns 2–5 index-dev, 6–9 eval); round 3's `header` tables are in §8.

**gemma-4-31b** (`decider_chat`):

| policy | reads | Δ accuracy (pts) | Δ ECE | approx skill | reads | Δ accuracy (pts) | Δ ECE | approx skill |
|---|---|---|---|---|---|---|---|---|
| identity | 1.00 | 76.7 | 0.142 | 0.596 | 1.00 | 81.4 | 0.095 | 0.772 |
| always reversed | 2.00 | +0.4 [+0.2, +0.7] | -0.013 [-0.016, -0.010] | 0.609 | 2.00 | +0.8 [+0.2, +1.5] | +0.002 [-0.006, +0.011] | 0.795 |
| cyclic:2 | 2.00 | +0.4 [+0.2, +0.7] | -0.012 [-0.015, -0.010] | 0.606 | 2.00 | +1.3 [+0.7, +1.9] | +0.013 [+0.005, +0.023] | 0.796 |
| cyclic:3 | 2.39 | +0.4 [+0.2, +0.7] | -0.012 [-0.015, -0.009] | 0.599 | 2.65 | +0.5 [-0.1, +1.2] | +0.007 [-0.003, +0.015] | 0.792 |
| cyclic:4 | 2.73 | +0.5 [+0.2, +0.7] | -0.012 [-0.015, -0.009] | 0.602 | 3.17 | +0.9 [+0.2, +1.5] | +0.005 [-0.004, +0.014] | 0.794 |
| top_p 0.5 reversed | 1.05 | -0.1 [-0.2, +0.1] | +0.001 [-0.001, +0.002] | 0.600 | 1.02 | +0.3 [+0.0, +0.6] | +0.003 [-0.000, +0.007] | 0.775 |
| top_p 0.6 reversed | 1.07 | +0.1 [-0.1, +0.3] | -0.002 [-0.004, +0.000] | 0.602 | 1.05 | +0.4 [-0.0, +0.8] | +0.002 [-0.003, +0.007] | 0.778 |
| top_p 0.7 reversed | 1.10 | +0.2 [-0.0, +0.4] | -0.003 [-0.005, -0.001] | 0.602 | 1.10 | +0.5 [-0.1, +1.1] | +0.001 [-0.005, +0.007] | 0.786 |
| top_p 0.8 reversed | 1.16 | +0.3 [+0.1, +0.5] | -0.004 [-0.007, -0.002] | 0.604 | 1.19 | +0.7 [+0.0, +1.3] | +0.002 [-0.005, +0.010] | 0.790 |
| top_p 0.9 reversed | 1.25 | +0.4 [+0.2, +0.6] | -0.009 [-0.012, -0.006] | 0.610 | 1.35 | +0.8 [+0.1, +1.5] | -0.000 [-0.008, +0.009] | 0.795 |
| min_n 3 reversed | 1.39 | +0.2 [-0.0, +0.4] | -0.006 [-0.008, -0.004] | 0.606 | 1.65 | +0.5 [-0.1, +1.1] | +0.008 [-0.000, +0.015] | 0.778 |
| min_n 4 reversed | 1.34 | +0.1 [-0.1, +0.3] | -0.005 [-0.007, -0.003] | 0.604 | 1.52 | +0.5 [-0.1, +1.0] | +0.006 [-0.001, +0.013] | 0.778 |
| min_n 5 reversed | 1.19 | -0.0 [-0.2, +0.1] | -0.000 [-0.002, +0.001] | 0.597 | 1.24 | +0.5 [+0.1, +0.8] | +0.000 [-0.005, +0.006] | 0.779 |
| min_n 6 reversed | 1.18 | -0.0 [-0.2, +0.1] | -0.000 [-0.002, +0.001] | 0.596 | 1.22 | +0.4 [+0.1, +0.7] | +0.001 [-0.004, +0.006] | 0.776 |
| min_n 8 reversed | 1.18 | +0.0 [-0.1, +0.2] | -0.001 [-0.002, +0.001] | 0.596 | 1.20 | +0.4 [+0.1, +0.7] | +0.001 [-0.005, +0.006] | 0.776 |
| aleria half | 2.11 | +0.5 [+0.2, +0.7] | -0.011 [-0.014, -0.008] | 0.602 | 2.09 | +1.0 [+0.4, +1.6] | +0.008 [-0.001, +0.017] | 0.795 |

**qwen3.8-27b** (`decider_chat`):

| policy | reads | Δ accuracy (pts) | Δ ECE | approx skill | reads | Δ accuracy (pts) | Δ ECE | approx skill |
|---|---|---|---|---|---|---|---|---|
| identity | 1.00 | 77.6 | 0.024 | 0.531 | 1.00 | 79.6 | 0.073 | 0.780 |
| always reversed | 2.00 | +0.0 [-0.2, +0.3] | +0.001 [-0.005, +0.005] | 0.529 | 2.00 | +0.1 [-0.6, +0.7] | -0.001 [-0.012, +0.010] | 0.785 |
| cyclic:2 | 2.00 | +0.1 [-0.2, +0.4] | +0.002 [-0.004, +0.007] | 0.527 | 2.00 | +1.0 [+0.4, +1.6] | +0.010 [-0.002, +0.021] | 0.785 |
| cyclic:3 | 2.39 | +0.1 [-0.1, +0.4] | +0.002 [-0.004, +0.007] | 0.525 | 2.65 | -0.6 [-1.3, +0.0] | -0.007 [-0.019, +0.004] | 0.778 |
| cyclic:4 | 2.73 | +0.2 [-0.1, +0.5] | +0.001 [-0.005, +0.006] | 0.528 | 3.17 | +0.1 [-0.6, +0.7] | -0.005 [-0.016, +0.007] | 0.778 |
| top_p 0.5 reversed | 1.13 | +0.2 [+0.0, +0.4] | -0.002 [-0.005, +0.001] | 0.529 | 1.12 | +0.1 [-0.4, +0.6] | -0.003 [-0.008, +0.005] | 0.780 |
| top_p 0.6 reversed | 1.22 | +0.0 [-0.2, +0.3] | +0.001 [-0.005, +0.004] | 0.529 | 1.26 | +0.0 [-0.6, +0.6] | -0.006 [-0.016, +0.003] | 0.783 |
| top_p 0.7 reversed | 1.32 | +0.0 [-0.2, +0.3] | -0.003 [-0.008, +0.001] | 0.529 | 1.37 | +0.1 [-0.6, +0.7] | -0.004 [-0.015, +0.007] | 0.785 |
| top_p 0.8 reversed | 1.41 | +0.0 [-0.2, +0.3] | +0.004 [-0.002, +0.008] | 0.529 | 1.47 | +0.1 [-0.6, +0.7] | -0.004 [-0.016, +0.006] | 0.785 |
| top_p 0.9 reversed | 1.55 | +0.0 [-0.2, +0.3] | +0.006 [+0.000, +0.010] | 0.530 | 1.59 | +0.1 [-0.6, +0.7] | +0.001 [-0.011, +0.012] | 0.785 |
| min_n 3 reversed | 1.39 | +0.2 [-0.0, +0.4] | -0.000 [-0.005, +0.004] | 0.529 | 1.65 | -0.0 [-0.6, +0.5] | -0.004 [-0.013, +0.007] | 0.781 |
| min_n 4 reversed | 1.34 | +0.2 [-0.0, +0.4] | +0.001 [-0.003, +0.005] | 0.528 | 1.52 | -0.2 [-0.7, +0.2] | -0.004 [-0.013, +0.006] | 0.780 |
| min_n 5 reversed | 1.19 | +0.2 [+0.1, +0.4] | -0.000 [-0.005, +0.004] | 0.530 | 1.24 | -0.0 [-0.2, +0.2] | -0.000 [-0.007, +0.007] | 0.780 |
| min_n 6 reversed | 1.18 | +0.3 [+0.1, +0.4] | -0.001 [-0.006, +0.004] | 0.532 | 1.22 | -0.0 [-0.2, +0.2] | -0.000 [-0.007, +0.007] | 0.780 |
| min_n 8 reversed | 1.18 | +0.3 [+0.1, +0.4] | -0.000 [-0.005, +0.004] | 0.532 | 1.20 | -0.0 [-0.2, +0.2] | -0.001 [-0.007, +0.007] | 0.780 |
| aleria half | 2.15 | +0.2 [-0.1, +0.4] | +0.003 [-0.002, +0.008] | 0.527 | 2.11 | +0.4 [-0.2, +1.0] | +0.001 [-0.010, +0.013] | 0.779 |

- **Identity.** `decider_chat` against `header`: gemma 76.7 / 81.4 against 80.0 / 81.1 (index-dev / eval); qwen3.8
  77.6 / 79.6 against 78.6 / 81.0.
- **gemma.** A second order on every question adds +0.4 to +0.5 on index-dev (`header`: +0.5 to +0.7). On eval,
  always reversed adds +0.8 [+0.2, +1.5] (`header`: +1.5) and cyclic:2 +1.3 on both layouts. `top_p 0.9 reversed`
  gives +0.4 / +0.8 at 1.25 / 1.35 reads.
- **qwen3.8.** On index-dev no every-question arm separates (+0.0 to +0.2; `header`: +0.4 to +0.6). The CIs above 0
  are `top_p 0.5 reversed` (+0.2 at 1.13 reads) and `min_n 5`/`6`/`8 reversed` (+0.2 to +0.3 at 1.18–1.19 reads). On
  eval only cyclic:2 separates, +1.0 [+0.4, +1.6] (`header`: +0.7).
- **Combine rules.** Against each policy's `mean-prob` arm, `mean-logprob` moves accuracy by at most 0.2 point and
  ECE by at most 0.005; `tn-prob` moves accuracy by at most 0.04 point. Against identity, `tn-prob` cuts gemma's ECE
  by 0.040–0.051 on index-dev and 0.005–0.016 on eval in every policy; on qwen3.8 it changes index-dev ECE by +0.003
  to +0.013.
- **Fits.** gemma's `decider_chat` identity score T is 18.187, below the fit bound (the summaries' Fits tables).

### `decider_chat`, image

Collects: the screen's `r4-decider` identity+reversed dev collect plus an `r4-decider-cyclic4` collect, merged by
`vision_orders.py`. Fits come from the text runs above; gates use the shipped `decider_chat` choice T. Runs
(orders.md has cost and fit per arm):
[gemma-4-31b](../results/vision-experiments/2026-10-19T154110Z-r4-orders-decider_chat-gemma-4-31b/orders.md),
[qwen3.8-27b](../results/vision-experiments/2026-10-19T182347Z-r4-orders-decider_chat-qwen3.8-27b/orders.md). Dev,
1,462 rows; round 3's `header` grids are in §9.

**gemma-4-31b** (identity: index 77.96, ECE 0.0654, NLL 0.6009, 672 input tokens):

| policy | mean reads | extra suffix tokens | mean input tokens | Δ index, mean-prob | Δ index, mean-logprob | Δ index, tn-prob |
|---|---|---|---|---|---|---|
| always reversed | 2.000 | 96.8 | 769 | -0.29 [-1.58, +0.95] | -0.18 [-1.46, +1.08] | -0.33 [-1.63, +0.91] |
| always half | 2.000 | 96.8 | 769 | -0.60 [-1.76, +0.54] | -0.71 [-1.88, +0.46] | -0.65 [-1.82, +0.50] |
| cyclic:4 | 3.191 | 247.1 | 919 | -0.21 [-1.47, +1.00] | +0.00 [-1.25, +1.22] | -0.11 [-1.35, +1.09] |
| aleria half | 2.202 | 136.0 | 808 | -0.29 [-1.51, +0.90] | -0.07 [-1.29, +1.11] | -0.19 [-1.40, +0.99] |
| top_p 0.5 reversed | 1.079 | 12.6 | 685 | +0.05 [-0.52, +0.62] | +0.14 [-0.44, +0.73] | +0.05 [-0.52, +0.62] |
| top_p 0.6 reversed | 1.116 | 18.5 | 691 | -0.10 [-0.82, +0.63] | -0.10 [-0.84, +0.65] | -0.14 [-0.88, +0.59] |
| top_p 0.7 reversed | 1.185 | 30.7 | 703 | -0.01 [-1.04, +0.99] | +0.10 [-0.92, +1.11] | -0.10 [-1.13, +0.90] |
| top_p 0.8 reversed | 1.247 | 38.1 | 710 | -0.00 [-1.16, +1.13] | +0.11 [-1.06, +1.27] | -0.09 [-1.26, +1.05] |
| top_p 0.9 reversed | 1.332 | 48.6 | 721 | -0.14 [-1.38, +1.07] | -0.02 [-1.29, +1.20] | -0.23 [-1.47, +1.00] |
| top_p 0.5 half | 1.079 | 12.6 | 685 | -0.01 [-0.49, +0.47] | -0.04 [-0.52, +0.45] | -0.04 [-0.52, +0.45] |
| top_p 0.6 half | 1.116 | 18.5 | 691 | -0.53 [-1.29, +0.19] | -0.55 [-1.31, +0.17] | -0.55 [-1.31, +0.17] |
| top_p 0.7 half | 1.185 | 30.7 | 703 | -0.32 [-1.22, +0.58] | -0.41 [-1.33, +0.51] | -0.36 [-1.27, +0.54] |
| top_p 0.8 half | 1.247 | 38.1 | 710 | -0.45 [-1.57, +0.65] | -0.54 [-1.68, +0.57] | -0.50 [-1.62, +0.61] |
| top_p 0.9 half | 1.332 | 48.6 | 721 | -0.45 [-1.57, +0.65] | -0.56 [-1.70, +0.56] | -0.50 [-1.62, +0.61] |
| min_n 3 reversed | 1.631 | 77.5 | 750 | +0.11 [-0.96, +1.14] | +0.22 [-0.84, +1.26] | +0.06 [-1.01, +1.11] |
| min_n 4 reversed | 1.560 | 72.8 | 745 | +0.23 [-0.65, +1.12] | +0.34 [-0.55, +1.22] | +0.19 [-0.70, +1.07] |
| min_n 5 reversed | 1.185 | 35.3 | 708 | +0.11 [-0.28, +0.50] | +0.22 [-0.18, +0.63] | +0.07 [-0.34, +0.47] |
| min_n 6 reversed | 1.179 | 34.9 | 707 | +0.11 [-0.28, +0.50] | +0.22 [-0.18, +0.63] | +0.07 [-0.34, +0.47] |
| min_n 8 reversed | 1.077 | 7.9 | 680 | +0.09 [-0.04, +0.22] | +0.11 [-0.02, +0.26] | +0.09 [-0.04, +0.22] |
| min_n 3 half | 1.631 | 77.5 | 750 | -0.21 [-1.10, +0.69] | -0.32 [-1.23, +0.60] | -0.25 [-1.15, +0.65] |
| min_n 4 half | 1.560 | 72.8 | 745 | -0.08 [-0.88, +0.70] | -0.19 [-1.01, +0.61] | -0.13 [-0.93, +0.66] |
| min_n 5 half | 1.185 | 35.3 | 708 | +0.14 [-0.25, +0.52] | +0.02 [-0.40, +0.45] | +0.09 [-0.31, +0.49] |
| min_n 6 half | 1.179 | 34.9 | 707 | +0.14 [-0.25, +0.52] | +0.02 [-0.40, +0.45] | +0.09 [-0.31, +0.49] |
| min_n 8 half | 1.077 | 7.9 | 680 | +0.02 [-0.09, +0.13] | +0.00 [-0.13, +0.13] | +0.02 [-0.09, +0.13] |

**qwen3.8-27b** (identity: index 72.45, ECE 0.1060, NLL 0.6604, 1,070 input tokens):

| policy | mean reads | extra suffix tokens | mean input tokens | Δ index, mean-prob | Δ index, mean-logprob | Δ index, tn-prob |
|---|---|---|---|---|---|---|
| always reversed | 2.000 | 93.8 | 1163 | +0.63 [-1.33, +2.61] | +0.57 [-1.41, +2.56] | +0.67 [-1.31, +2.65] |
| always half | 2.000 | 93.8 | 1163 | +0.63 [-1.54, +2.73] | +0.49 [-1.62, +2.54] | +0.68 [-1.46, +2.76] |
| cyclic:4 | 3.191 | 239.7 | 1309 | +1.10 [-1.06, +3.31] | +0.97 [-1.24, +3.19] | +1.10 [-1.06, +3.31] |
| aleria half | 2.330 | 148.5 | 1218 | +0.98 [-1.04, +3.04] | +0.91 [-1.15, +2.99] | +0.98 [-1.04, +3.04] |
| top_p 0.5 reversed | 1.243 | 37.9 | 1108 | +1.11 [-0.16, +2.40] | +1.09 [-0.22, +2.38] | +1.11 [-0.16, +2.40] |
| top_p 0.6 reversed | 1.387 | 51.5 | 1121 | +0.84 [-1.08, +2.77] | +0.74 [-1.21, +2.68] | +0.84 [-1.08, +2.77] |
| top_p 0.7 reversed | 1.498 | 59.4 | 1129 | +0.67 [-1.31, +2.65] | +0.57 [-1.41, +2.56] | +0.67 [-1.31, +2.65] |
| top_p 0.8 reversed | 1.626 | 69.7 | 1139 | +0.67 [-1.31, +2.65] | +0.57 [-1.41, +2.56] | +0.67 [-1.31, +2.65] |
| top_p 0.9 reversed | 1.825 | 82.8 | 1152 | +0.67 [-1.31, +2.65] | +0.57 [-1.41, +2.56] | +0.67 [-1.31, +2.65] |
| top_p 0.5 half | 1.243 | 37.9 | 1108 | +0.46 [-0.90, +1.80] | +0.60 [-0.73, +1.93] | +0.46 [-0.90, +1.80] |
| top_p 0.6 half | 1.387 | 51.5 | 1121 | +0.65 [-1.44, +2.69] | +0.56 [-1.50, +2.58] | +0.75 [-1.32, +2.78] |
| top_p 0.7 half | 1.498 | 59.4 | 1129 | +0.58 [-1.58, +2.67] | +0.49 [-1.62, +2.54] | +0.68 [-1.46, +2.76] |
| top_p 0.8 half | 1.626 | 69.7 | 1139 | +0.58 [-1.58, +2.67] | +0.49 [-1.62, +2.54] | +0.68 [-1.46, +2.76] |
| top_p 0.9 half | 1.825 | 82.8 | 1152 | +0.58 [-1.58, +2.67] | +0.49 [-1.62, +2.54] | +0.68 [-1.46, +2.76] |
| min_n 3 reversed | 1.631 | 75.2 | 1145 | +1.11 [-0.36, +2.57] | +1.06 [-0.42, +2.54] | +1.16 [-0.32, +2.61] |
| min_n 4 reversed | 1.560 | 70.7 | 1140 | +1.36 [+0.01, +2.70] | +1.30 [-0.07, +2.68] | +1.40 [+0.04, +2.75] |
| min_n 5 reversed | 1.185 | 34.7 | 1104 | +0.31 [-0.10, +0.70] | +0.38 [-0.11, +0.83] | +0.35 [-0.06, +0.75] |
| min_n 6 reversed | 1.179 | 34.3 | 1104 | +0.43 [+0.12, +0.77] | +0.50 [+0.10, +0.90] | +0.48 [+0.16, +0.82] |
| min_n 8 reversed | 1.077 | 7.0 | 1077 | -0.07 [-0.18, +0.04] | -0.04 [-0.17, +0.07] | -0.07 [-0.18, +0.04] |
| min_n 3 half | 1.631 | 75.2 | 1145 | +1.11 [-0.53, +2.76] | +0.98 [-0.64, +2.58] | +1.17 [-0.47, +2.77] |
| min_n 4 half | 1.560 | 70.7 | 1140 | +1.36 [-0.17, +2.87] | +1.23 [-0.26, +2.70] | +1.42 [-0.10, +2.91] |
| min_n 5 half | 1.185 | 34.7 | 1104 | +0.42 [-0.04, +0.90] | +0.44 [-0.02, +0.92] | +0.37 [-0.08, +0.85] |
| min_n 6 half | 1.179 | 34.3 | 1104 | +0.42 [-0.04, +0.90] | +0.44 [-0.02, +0.92] | +0.37 [-0.08, +0.85] |
| min_n 8 half | 1.077 | 7.0 | 1077 | +0.00 [-0.11, +0.11] | +0.02 [-0.09, +0.13] | +0.00 [-0.11, +0.11] |

- **gemma.** No CI excludes 0. The largest is `min_n 4 reversed/mean-logprob`, +0.34 [−0.55, +1.22] at 1.56 reads;
  every-question arms run from −0.71 to +0.00.
- **qwen3.8.** 5 of 75 CIs lie above 0: `min_n 4 reversed` with `mean-prob` (+1.36 [+0.01, +2.70]) and `tn-prob`
  (+1.40 [+0.04, +2.75]) at 1.56 reads, and `min_n 6 reversed` in all three rules (+0.43 to +0.50 at 1.18 reads).
  `header`'s leader, `min_n 4 reversed/mean-logprob` (+2.04 in §9), is +1.30 [−0.07, +2.68] here.
- **ECE.**
  - gemma: every-question arms lower it from 0.0654 to 0.051–0.052 with `mean-prob` and 0.031–0.037 with `tn-prob`.
  - qwen3.8: identity is 0.1060 (`header` 0.0424 in §9); every-question arms raise it to 0.129–0.139 with
    `mean-prob` and 0.146–0.156 with `tn-prob`. The cross-fit references bring it to 0.032–0.045.

### Blurb grids and their controls

The owner ran the grid on HB (`header` + blurb) only, on both models (2026-10-19); DB was screened, not gridded
(prompt-layouts.md §5).

- **Text.** `--orders all` collects of HB on calib-600 and index-dev-2k. `r3_orders.py --calib/--dev` fits each
  policy on calib-600 and scores index-dev-2k (3,728 questions). An experiment layout has no shipped calibration, so
  gates use each run's own identity T.
- **Like-for-like controls.** `header` and `decider_chat` rerun in the same mode on the old full collects, restricted
  to the same rows. The blurb's effect on the grid is HB against the `header` control, not against §8 or the
  full-split `decider_chat` tables above.
  - Caveat: the controls come from the M3-era full collects (older session; gemma with `warm_up` off), while HB ran
    later (gemma with `warm_up` prefix; qwen3.8 `row` in both). Neither `warm_up` nor max len is in the calibration
    stamp, so nothing refuses the mix. HB minus control spreads only ±0.2 points over all arms.
- **Max len.** gemma's three grids ran at systemone_max_len 32,768, as all earlier gemma text grids did (M3, round
  3, the full-split `decider_chat` grid); gemma's profile and the round 4 screens use 65,536.
  - The first HB collect at 65,536 timed out (`httpx.ReadTimeout`): long entity-alignment rows read under every
    order exceed gemma's KV at concurrency 8.
  - Measured effect of the cap: every index-dev-2k row (1,994 of 1,994) is read under both caps, so the scored rows
    are the same; the calib-600 fit drops 10 of 600 rows.
  - qwen3.8 uses 32,768 everywhere.
- **Fits.** gemma's score T fits to 19.999, at [`fit.py`](../../scripts/fit.py)'s upper bound of 20, in the
  `header` and HB runs (each summary's Fits table), as in round 3 (§8). index-dev-2k has no score questions, so no
  number below depends on it.
- **Image.** One `cyclic:4` dev collect of HB, merged with its screen collect and scored with HB's text fit; gates
  at HB's own identity T. No image control was rerun. The nearest are round 3's `header` grids (§9: full-calib fits,
  shipped-T gates, the DS-034 collect) and the `decider_chat` grids above.

Text runs, index-dev-2k: gemma
[`header`](../results/archive/2026-10-19T220419Z-r4-orders-text-header-2k-gemma-4-31b/summary.md),
[HB](../results/archive/2026-10-20T014817Z-r4-orders-text-blurb-header-2k-gemma-4-31b/summary.md),
[`decider_chat`](../results/archive/2026-10-19T220846Z-r4-orders-text-decider_chat-2k-gemma-4-31b/summary.md);
qwen3.8
[`header`](../results/archive/2026-10-19T221421Z-r4-orders-text-header-2k-qwen3.8-27b/summary.md),
[HB](../results/archive/2026-10-20T002658Z-r4-orders-text-blurb-header-2k-qwen3.8-27b/summary.md),
[`decider_chat`](../results/archive/2026-10-19T222025Z-r4-orders-text-decider_chat-2k-qwen3.8-27b/summary.md).
`mean-prob`; Δ against each run's own identity. "reads" is one value when the three runs agree, else `header` / HB /
`decider_chat`. The identity row shows absolute accuracy (%) and ECE.

**gemma-4-31b**, index-dev-2k:

| policy | reads | Δ accuracy, `header` | Δ accuracy, HB | Δ accuracy, `decider_chat` | Δ ECE, `header` | Δ ECE, HB | Δ ECE, `decider_chat` |
|---|---|---|---|---|---|---|---|
| identity | 1.00 | 80.2 | 80.5 | 76.6 | 0.125 | 0.126 | 0.147 |
| always reversed | 2.00 | +0.5 [-0.0, +1.0] | +0.3 [-0.1, +0.8] | +0.3 [-0.2, +0.9] | -0.016 [-0.020, -0.009] | -0.012 [-0.016, -0.005] | -0.011 [-0.017, -0.006] |
| cyclic:2 | 2.00 | +0.4 [-0.1, +0.9] | +0.3 [-0.1, +0.8] | +0.5 [-0.1, +1.0] | -0.010 [-0.015, -0.004] | -0.011 [-0.014, -0.004] | -0.012 [-0.017, -0.006] |
| cyclic:3 | 2.41 | +0.6 [+0.1, +1.1] | +0.5 [+0.1, +1.0] | +0.5 [-0.1, +1.0] | -0.010 [-0.014, -0.003] | -0.009 [-0.014, -0.003] | -0.012 [-0.017, -0.005] |
| cyclic:4 | 2.76 | +0.6 [+0.1, +1.2] | +0.6 [+0.2, +1.1] | +0.6 [+0.1, +1.2] | -0.006 [-0.012, -0.000] | -0.009 [-0.013, -0.002] | -0.009 [-0.015, -0.003] |
| top_p 0.5 reversed | 1.04 / 1.03 / 1.04 | +0.0 [-0.2, +0.2] | -0.2 [-0.4, +0.1] | -0.1 [-0.4, +0.1] | -0.001 [-0.004, +0.002] | -0.001 [-0.003, +0.002] | +0.001 [-0.002, +0.004] |
| top_p 0.6 reversed | 1.06 / 1.05 / 1.07 | +0.2 [-0.1, +0.6] | +0.1 [-0.2, +0.4] | +0.2 [-0.2, +0.5] | -0.004 [-0.007, +0.001] | -0.003 [-0.006, +0.000] | -0.002 [-0.005, +0.002] |
| top_p 0.7 reversed | 1.08 / 1.08 / 1.10 | +0.4 [-0.0, +0.8] | +0.3 [-0.1, +0.7] | +0.1 [-0.3, +0.5] | -0.006 [-0.009, -0.000] | -0.006 [-0.009, -0.001] | -0.002 [-0.006, +0.001] |
| top_p 0.8 reversed | 1.12 / 1.11 / 1.15 | +0.5 [+0.1, +1.0] | +0.3 [-0.1, +0.8] | +0.3 [-0.1, +0.9] | -0.010 [-0.014, -0.004] | -0.009 [-0.012, -0.003] | -0.007 [-0.012, -0.002] |
| top_p 0.9 reversed | 1.21 / 1.20 / 1.24 | +0.6 [+0.1, +1.1] | +0.3 [-0.1, +0.8] | +0.3 [-0.2, +0.8] | -0.012 [-0.017, -0.006] | -0.010 [-0.014, -0.004] | -0.007 [-0.013, -0.002] |
| min_n 3 reversed | 1.41 | +0.2 [-0.2, +0.6] | +0.1 [-0.3, +0.5] | +0.1 [-0.3, +0.5] | -0.009 [-0.013, -0.003] | -0.008 [-0.011, -0.002] | -0.005 [-0.009, -0.000] |
| min_n 4 reversed | 1.35 | +0.3 [-0.1, +0.7] | +0.1 [-0.3, +0.5] | +0.1 [-0.3, +0.5] | -0.009 [-0.013, -0.004] | -0.008 [-0.012, -0.003] | -0.004 [-0.008, +0.001] |
| min_n 5 reversed | 1.20 | +0.1 [-0.2, +0.3] | -0.1 [-0.4, +0.2] | +0.0 [-0.3, +0.3] | -0.003 [-0.006, +0.001] | -0.003 [-0.006, +0.001] | +0.000 [-0.002, +0.004] |
| min_n 6 reversed | 1.19 | +0.1 [-0.2, +0.3] | -0.1 [-0.4, +0.2] | +0.0 [-0.3, +0.3] | -0.003 [-0.006, +0.001] | -0.003 [-0.006, +0.001] | -0.001 [-0.004, +0.003] |
| min_n 8 reversed | 1.18 | +0.1 [-0.2, +0.3] | -0.1 [-0.4, +0.2] | +0.1 [-0.2, +0.4] | -0.003 [-0.007, +0.001] | -0.004 [-0.006, -0.000] | -0.002 [-0.005, +0.001] |
| aleria half | 2.10 / 2.10 / 2.11 | +0.6 [+0.1, +1.1] | +0.6 [+0.1, +1.0] | +0.6 [+0.0, +1.1] | -0.006 [-0.012, -0.001] | -0.010 [-0.013, -0.003] | -0.008 [-0.014, -0.002] |

**qwen3.8-27b**, index-dev-2k:

| policy | reads | Δ accuracy, `header` | Δ accuracy, HB | Δ accuracy, `decider_chat` | Δ ECE, `header` | Δ ECE, HB | Δ ECE, `decider_chat` |
|---|---|---|---|---|---|---|---|
| identity | 1.00 | 78.2 | 78.5 | 76.7 | 0.021 | 0.032 | 0.026 |
| always reversed | 2.00 | +0.3 [-0.2, +0.9] | +0.4 [-0.2, +1.0] | -0.3 [-0.9, +0.3] | +0.007 [-0.005, +0.014] | -0.005 [-0.010, +0.005] | +0.002 [-0.009, +0.014] |
| cyclic:2 | 2.00 | +0.2 [-0.2, +0.8] | +0.3 [-0.2, +0.9] | -0.5 [-1.1, +0.0] | +0.011 [-0.002, +0.019] | -0.002 [-0.009, +0.008] | +0.005 [-0.006, +0.016] |
| cyclic:3 | 2.41 | +0.0 [-0.5, +0.6] | +0.2 [-0.4, +0.7] | -0.5 [-1.1, +0.1] | +0.008 [-0.003, +0.017] | -0.002 [-0.009, +0.008] | +0.006 [-0.005, +0.016] |
| cyclic:4 | 2.76 | +0.2 [-0.4, +0.7] | +0.3 [-0.3, +0.8] | -0.3 [-1.0, +0.3] | +0.014 [+0.000, +0.022] | -0.002 [-0.009, +0.006] | +0.003 [-0.008, +0.015] |
| top_p 0.5 reversed | 1.12 / 1.13 / 1.13 | +0.6 [+0.1, +1.0] | +0.6 [+0.1, +1.0] | +0.4 [-0.1, +0.8] | +0.003 [-0.005, +0.009] | -0.001 [-0.006, +0.004] | +0.002 [-0.005, +0.008] |
| top_p 0.6 reversed | 1.20 / 1.21 / 1.24 | +0.4 [-0.1, +0.9] | +0.5 [-0.1, +1.0] | -0.2 [-0.8, +0.4] | +0.008 [-0.003, +0.013] | -0.001 [-0.007, +0.006] | +0.000 [-0.008, +0.010] |
| top_p 0.7 reversed | 1.31 / 1.27 / 1.33 | +0.3 [-0.2, +0.9] | +0.4 [-0.2, +0.9] | -0.2 [-0.8, +0.3] | +0.009 [-0.003, +0.015] | -0.002 [-0.009, +0.006] | -0.001 [-0.009, +0.009] |
| top_p 0.8 reversed | 1.38 / 1.34 / 1.42 | +0.3 [-0.2, +0.9] | +0.4 [-0.2, +1.0] | -0.2 [-0.8, +0.3] | +0.006 [-0.005, +0.013] | -0.003 [-0.009, +0.006] | +0.007 [-0.005, +0.015] |
| top_p 0.9 reversed | 1.49 / 1.44 / 1.55 | +0.3 [-0.2, +0.9] | +0.4 [-0.2, +1.0] | -0.2 [-0.8, +0.3] | +0.007 [-0.004, +0.015] | -0.003 [-0.009, +0.006] | +0.007 [-0.004, +0.016] |
| min_n 3 reversed | 1.41 | +0.6 [+0.1, +1.0] | +0.5 [+0.1, +1.0] | +0.3 [-0.1, +0.8] | +0.005 [-0.006, +0.012] | -0.002 [-0.008, +0.007] | +0.002 [-0.009, +0.011] |
| min_n 4 reversed | 1.35 | +0.5 [+0.1, +1.0] | +0.5 [+0.1, +0.9] | +0.4 [+0.0, +0.9] | +0.004 [-0.006, +0.011] | -0.000 [-0.006, +0.008] | +0.004 [-0.007, +0.012] |
| min_n 5 reversed | 1.20 | +0.5 [+0.2, +0.9] | +0.4 [+0.1, +0.8] | +0.4 [+0.1, +0.8] | +0.007 [-0.004, +0.014] | +0.002 [-0.004, +0.009] | +0.004 [-0.006, +0.012] |
| min_n 6 reversed | 1.19 | +0.5 [+0.1, +0.9] | +0.4 [+0.1, +0.8] | +0.5 [+0.2, +0.8] | +0.007 [-0.004, +0.013] | +0.003 [-0.003, +0.010] | +0.002 [-0.007, +0.010] |
| min_n 8 reversed | 1.18 | +0.5 [+0.1, +0.8] | +0.4 [+0.1, +0.8] | +0.5 [+0.2, +0.8] | +0.007 [-0.004, +0.013] | +0.003 [-0.003, +0.009] | +0.003 [-0.007, +0.010] |
| aleria half | 2.12 / 2.12 / 2.14 | +0.2 [-0.3, +0.7] | +0.2 [-0.4, +0.8] | -0.4 [-1.0, +0.2] | +0.012 [-0.000, +0.020] | -0.001 [-0.007, +0.009] | +0.004 [-0.006, +0.017] |

- **Identity.** gemma 80.2 (`header`), 80.5 (HB), 76.6 (`decider_chat`); qwen3.8 78.2, 78.5, 76.7. HB's 80.5 / 78.5
  differ from the screen's 80.6 / 78.6 because they are separate collects: bf16 batching noise (net 5 and 4 of
  3,728 questions).
- **The blurb barely moves the grid.** Over all 45 arms, HB's Δ accuracy minus the `header` control's runs from −0.21
  to +0.11 points on gemma and −0.16 to +0.16 on qwen3.8. Arms with a CI above 0: gemma 15 (`header`), 11 (HB) and
  6 (`decider_chat`) of 45; qwen3.8 18, 13 and 8.
- **Largest gains, any combine rule.**
  - gemma: `header` +0.64 with `top_p 0.9 reversed/mean-logprob` (1.21 reads) and `cyclic:4/tn-prob` (2.76 reads);
    HB `cyclic:4/tn-prob` +0.67 [+0.24, +1.15]; `decider_chat` `cyclic:4/mean-logprob` +0.62 [+0.03, +1.21].
  - qwen3.8: `header` `top_p 0.5 reversed` +0.56 [+0.13, +1.02] at 1.12 reads; HB `top_p 0.5 reversed/tn-prob` +0.59
    [+0.16, +1.02] at 1.13 reads; `decider_chat` `min_n 6`/`8 reversed` +0.48 [+0.16, +0.83] at 1.18–1.19 reads.
- **ECE.** gemma's `tn-prob` arms lower ECE from 0.125 to 0.074–0.087 (`header`), 0.126 to 0.087–0.098 (HB) and 0.147
  to 0.100–0.113 (`decider_chat`). qwen3.8's HB identity ECE is 0.032 against `header`'s 0.021.
- **index-dev-2k vs index-dev.** With a quarter of the questions the CIs are about twice §8's width.

Image runs (orders.md has cost and fit per arm):
[gemma-4-31b](../results/vision-experiments/2026-10-20T015305Z-r4-orders-blurb-header-gemma-4-31b/orders.md),
[qwen3.8-27b](../results/vision-experiments/2026-10-20T004117Z-r4-orders-blurb-header-qwen3.8-27b/orders.md).

**gemma-4-31b**, HB (identity: index 78.25, ECE 0.0814, NLL 0.6065, 740 input tokens):

| policy | mean reads | extra suffix tokens | mean input tokens | Δ index, mean-prob | Δ index, mean-logprob | Δ index, tn-prob |
|---|---|---|---|---|---|---|
| always reversed | 2.000 | 96.8 | 837 | -0.81 [-2.09, +0.38] | -0.75 [-2.06, +0.47] | -0.86 [-2.14, +0.34] |
| always half | 2.000 | 96.8 | 837 | -1.15 [-2.46, +0.11] | -0.87 [-2.18, +0.42] | -1.13 [-2.43, +0.13] |
| cyclic:4 | 3.191 | 247.1 | 987 | -0.55 [-1.87, +0.71] | -0.43 [-1.75, +0.84] | -0.55 [-1.87, +0.71] |
| aleria half | 2.192 | 135.1 | 875 | -0.45 [-1.75, +0.78] | -0.34 [-1.65, +0.91] | -0.45 [-1.75, +0.78] |
| top_p 0.5 reversed | 1.062 | 9.6 | 750 | +0.34 [-0.20, +0.90] | +0.36 [-0.18, +0.92] | +0.34 [-0.20, +0.90] |
| top_p 0.6 reversed | 1.103 | 15.6 | 756 | +0.05 [-0.87, +0.94] | +0.07 [-0.86, +0.96] | +0.05 [-0.87, +0.94] |
| top_p 0.7 reversed | 1.154 | 24.1 | 764 | -0.13 [-1.24, +0.94] | +0.03 [-1.09, +1.11] | -0.13 [-1.24, +0.94] |
| top_p 0.8 reversed | 1.218 | 33.4 | 774 | -0.40 [-1.57, +0.72] | -0.34 [-1.55, +0.81] | -0.45 [-1.62, +0.68] |
| top_p 0.9 reversed | 1.287 | 42.5 | 783 | -0.69 [-1.95, +0.48] | -0.64 [-1.93, +0.58] | -0.74 [-2.01, +0.43] |
| top_p 0.5 half | 1.062 | 9.6 | 750 | -0.05 [-0.52, +0.40] | +0.02 [-0.46, +0.47] | -0.03 [-0.49, +0.41] |
| top_p 0.6 half | 1.103 | 15.6 | 756 | -0.40 [-1.29, +0.43] | -0.23 [-1.15, +0.64] | -0.38 [-1.27, +0.45] |
| top_p 0.7 half | 1.154 | 24.1 | 764 | -0.71 [-1.85, +0.41] | -0.47 [-1.64, +0.69] | -0.69 [-1.82, +0.43] |
| top_p 0.8 half | 1.218 | 33.4 | 774 | -0.83 [-2.08, +0.36] | -0.55 [-1.81, +0.68] | -0.81 [-2.05, +0.38] |
| top_p 0.9 half | 1.287 | 42.5 | 783 | -1.03 [-2.31, +0.20] | -0.75 [-2.06, +0.52] | -1.01 [-2.29, +0.22] |
| min_n 3 reversed | 1.631 | 77.5 | 818 | +0.17 [-0.68, +1.01] | +0.23 [-0.66, +1.11] | +0.13 [-0.74, +0.97] |
| min_n 4 reversed | 1.560 | 72.8 | 813 | +0.05 [-0.79, +0.84] | +0.11 [-0.75, +0.94] | +0.00 [-0.84, +0.80] |
| min_n 5 reversed | 1.185 | 35.3 | 776 | +0.55 [+0.08, +1.04] | +0.73 [+0.24, +1.26] | +0.50 [+0.03, +1.02] |
| min_n 6 reversed | 1.179 | 34.9 | 775 | +0.42 [+0.02, +0.85] | +0.60 [+0.17, +1.05] | +0.38 [-0.03, +0.81] |
| min_n 8 reversed | 1.077 | 7.9 | 748 | +0.15 [+0.00, +0.32] | +0.15 [+0.00, +0.32] | +0.15 [+0.00, +0.32] |
| min_n 3 half | 1.631 | 77.5 | 818 | -0.17 [-1.07, +0.74] | +0.12 [-0.83, +1.06] | -0.14 [-1.05, +0.76] |
| min_n 4 half | 1.560 | 72.8 | 813 | -0.17 [-0.91, +0.57] | +0.12 [-0.67, +0.92] | -0.14 [-0.89, +0.59] |
| min_n 5 half | 1.185 | 35.3 | 776 | +0.18 [-0.18, +0.54] | +0.34 [-0.07, +0.75] | +0.18 [-0.18, +0.54] |
| min_n 6 half | 1.179 | 34.9 | 775 | +0.18 [-0.18, +0.54] | +0.34 [-0.07, +0.75] | +0.18 [-0.18, +0.54] |
| min_n 8 half | 1.077 | 7.9 | 748 | +0.04 [-0.09, +0.18] | +0.04 [-0.11, +0.20] | +0.04 [-0.09, +0.18] |

**qwen3.8-27b**, HB (identity: index 73.66, ECE 0.0631, NLL 0.6058, 1,138 input tokens):

| policy | mean reads | extra suffix tokens | mean input tokens | Δ index, mean-prob | Δ index, mean-logprob | Δ index, tn-prob |
|---|---|---|---|---|---|---|
| always reversed | 2.000 | 93.8 | 1232 | +0.46 [-1.26, +2.17] | +0.55 [-1.15, +2.23] | +0.46 [-1.26, +2.17] |
| always half | 2.000 | 93.8 | 1232 | +0.84 [-0.86, +2.58] | +0.92 [-0.79, +2.65] | +0.79 [-0.92, +2.54] |
| cyclic:4 | 3.191 | 239.7 | 1378 | +1.11 [-0.66, +2.89] | +1.09 [-0.66, +2.82] | +1.11 [-0.66, +2.89] |
| aleria half | 2.304 | 145.2 | 1283 | +1.48 [-0.26, +3.20] | +1.48 [-0.23, +3.17] | +1.48 [-0.26, +3.20] |
| top_p 0.5 reversed | 1.211 | 35.7 | 1174 | -0.49 [-1.62, +0.59] | -0.28 [-1.43, +0.85] | -0.45 [-1.57, +0.63] |
| top_p 0.6 reversed | 1.316 | 44.3 | 1182 | +0.19 [-1.50, +1.87] | +0.28 [-1.40, +1.95] | +0.19 [-1.50, +1.87] |
| top_p 0.7 reversed | 1.406 | 52.7 | 1191 | +0.46 [-1.26, +2.17] | +0.55 [-1.15, +2.23] | +0.44 [-1.28, +2.14] |
| top_p 0.8 reversed | 1.505 | 61.3 | 1199 | +0.46 [-1.26, +2.17] | +0.55 [-1.15, +2.23] | +0.44 [-1.28, +2.14] |
| top_p 0.9 reversed | 1.686 | 74.8 | 1213 | +0.46 [-1.26, +2.17] | +0.55 [-1.15, +2.23] | +0.44 [-1.28, +2.14] |
| top_p 0.5 half | 1.211 | 35.7 | 1174 | +0.13 [-0.95, +1.22] | +0.30 [-0.78, +1.38] | +0.13 [-0.95, +1.22] |
| top_p 0.6 half | 1.316 | 44.3 | 1182 | +0.67 [-0.99, +2.35] | +0.80 [-0.88, +2.47] | +0.67 [-0.99, +2.35] |
| top_p 0.7 half | 1.406 | 52.7 | 1191 | +0.89 [-0.80, +2.61] | +1.02 [-0.68, +2.73] | +0.89 [-0.80, +2.61] |
| top_p 0.8 half | 1.505 | 61.3 | 1199 | +0.89 [-0.80, +2.61] | +1.02 [-0.68, +2.73] | +0.89 [-0.80, +2.61] |
| top_p 0.9 half | 1.686 | 74.8 | 1213 | +0.79 [-0.92, +2.54] | +0.92 [-0.79, +2.65] | +0.79 [-0.92, +2.54] |
| min_n 3 reversed | 1.631 | 75.2 | 1213 | +0.01 [-1.29, +1.29] | +0.10 [-1.20, +1.39] | +0.01 [-1.29, +1.29] |
| min_n 4 reversed | 1.560 | 70.7 | 1209 | +0.38 [-0.85, +1.60] | +0.47 [-0.78, +1.70] | +0.38 [-0.85, +1.60] |
| min_n 5 reversed | 1.185 | 34.7 | 1173 | +0.11 [-0.36, +0.56] | +0.32 [-0.19, +0.86] | +0.11 [-0.36, +0.56] |
| min_n 6 reversed | 1.179 | 34.3 | 1172 | +0.11 [-0.36, +0.56] | +0.32 [-0.19, +0.86] | +0.11 [-0.36, +0.56] |
| min_n 8 reversed | 1.077 | 7.0 | 1145 | +0.07 [-0.06, +0.20] | +0.07 [-0.07, +0.20] | +0.07 [-0.06, +0.20] |
| min_n 3 half | 1.631 | 75.2 | 1213 | +0.39 [-0.91, +1.69] | +0.47 [-0.83, +1.75] | +0.34 [-0.96, +1.64] |
| min_n 4 half | 1.560 | 70.7 | 1209 | +0.51 [-0.70, +1.74] | +0.59 [-0.61, +1.81] | +0.47 [-0.75, +1.70] |
| min_n 5 half | 1.185 | 34.7 | 1173 | +0.39 [-0.09, +0.90] | +0.26 [-0.23, +0.77] | +0.35 [-0.14, +0.85] |
| min_n 6 half | 1.179 | 34.3 | 1172 | +0.39 [-0.09, +0.90] | +0.26 [-0.23, +0.77] | +0.35 [-0.14, +0.85] |
| min_n 8 half | 1.077 | 7.0 | 1145 | +0.00 [-0.11, +0.11] | +0.00 [-0.11, +0.11] | +0.00 [-0.11, +0.11] |

- **gemma.** 5 of 75 CIs lie above 0, all selective by option count: `min_n 5 reversed` in all three rules (largest
  `mean-logprob`, +0.73 [+0.24, +1.26] at 1.19 reads) and `min_n 6 reversed` with `mean-prob` and `mean-logprob`
  (+0.42, +0.60). Every-question arms run from −1.15 to −0.34, CIs including 0. In round 3's `header` grid
  `min_n 5 reversed/mean-logprob` was +0.24 [−0.12, +0.61].
- **qwen3.8.** No CI excludes 0. The largest is `aleria half`, +1.48 [−0.26, +3.20] at 2.30 reads.
  `min_n 4 reversed/mean-logprob` is +0.47 [−0.78, +1.70].
- **ECE.** Every-question arms take gemma from 0.0814 to 0.065–0.076 (`mean-prob`) and 0.030–0.041 (`tn-prob`), and
  qwen3.8 from 0.0631 to 0.081–0.095 (`mean-prob`) and 0.092–0.108 (`tn-prob`). Cross-fit references: 0.023–0.032
  (gemma), 0.030–0.046 (qwen3.8).
- **Keyed options.** Reversed and half image reads carry the key/label clash (Caveats).

## 11. Cutdown spike: removing the weakest options (gemma, negative)

A quick spike after round 4 (2026-10-20, owner-approved, gemma-4-31b text only): when the first read is uncertain,
re-ask the question with only its strongest options. Unlike every rule above, this changes the option set, not the
order. Method and full tables: [results](../results/archive/2026-10-20T034116Z-cutdown-spike-gemma-4-31b/summary.md).

- **Rule.** Choice questions with ≥ 3 options whose identity top probability (shipped `header` T) is below τ, at §7's
  gate thresholds τ ∈ {0.5, …, 0.9}. The re-read keeps the first read's top 2, top 3 or top ⌈n/2⌉ options, or
  halves repeatedly while still below τ (`halving`). Kept options keep their order and are relabelled A, B, …; the
  prompt prefix is unchanged, so a re-read costs one question suffix, like a gated order read.
- **Result.** Δ accuracy on the re-asked index-dev-2k questions, 95% paired bootstrap:

| τ | Re-asked | top 2 | top 3 | top half | halving |
|---|---|---|---|---|---|
| 0.5 | 151 | −3.3 [−9.3, +3.3] | +0.7 [−6.6, +7.9] | −5.3 [−12.6, +2.0] | −4.6 [−11.9, +2.6] |
| 0.7 | 285–291 | −4.8 [−9.3, −0.3] | −2.1 [−7.0, +2.5] | −4.5 [−8.9, +0.0] | −5.2 [−10.3, +0.0] |
| 0.9 | 656–693 | −2.5 [−4.8, −0.3] | −1.8 [−4.0, +0.5] | −2.7 [−4.9, −0.6] | −4.2 [−6.8, −1.6] |

- **Calibration.** Top half and halving raise ECE on the re-asked questions by +0.05 to +0.14 and NLL by up to +0.26.
  Top 3 at τ 0.9 is the one ECE gain (−0.040 [−0.065, −0.019]), at −1.8 accuracy.
- **Why.** Dropping gold is only part of it: at τ 0.9 top half keeps gold for 79.5% of re-asked questions, yet the
  re-read is right on 45.0% against the first read's 47.8%. With fewer options gemma moves off a correct first
  choice more often than onto one. Each halving round compounds this (0.47 extra reads per question, averaged over all questions, at τ 0.9).
- **Not tried.** Images (relabelled letters would clash with the options' own keys, Caveats) and qwen3.8.
- **Caveats.** calib-600 looks unlike index-dev-2k here (gold dropped for 0–9% of its gated questions against
  21–54%), so T_cut rests on about 133 calib questions. Some options print their original index (`option_7: …`), so
  a cut list reads non-contiguous; production would send the same.

## Caveats

- **Many comparisons.**
  - Text: 45 arms per split and model; image: 75 policy arms plus 6 cross-fit references per model. Every CI is unadjusted.
  - Round 4 adds 10 text grid-splits of 45 arms and 4 image grids of 75 (§10).
  - At this count, a few CIs that exclude 0 are expected by chance. Dev's minimum detectable Δ index is about 3.5
    points ([vision-experiments.md §5](vision-experiments.md#5-compare-and-how-to-read-it)).
- **Eval is a selection set.** The calibration gate and M3's verdicts chose on eval; index-dev is the cleaner text
  check, and image dev has been compared on many times (the holdout guards it). Round 4's blurb grids have no eval.
- **Each arm's own fit.** Text ECE baselines use each arm's refitted T, not the shipped file. Image `half` arms use
  the reversed policy's text fit, not their own (R3, §7), so their ECE column is slightly off; their index is not
  affected by T except in averaged or gated rows.
- **Image options carry their own letter keys.** Every image dev question has criteria keys `A`, `B`, … with
  descriptions, which the `described` format puts in the option text: the identity read shows `(A) A: 1`. Every
  reversed, half or cyclic image read shows a label that disagrees with the key, e.g. `(A) D: 2`, so a second image
  order changes the key/label agreement as well as the position. On text a quarter of index-dev's gold-labelled
  choice questions are keyed the same way (3,870 of 15,482; eval has none). A CPU-only split of the text results by
  keyed vs unkeyed questions is possible from the existing collects; it has not been run. Round 4's image grids use
  letters too, so their reversed, half and cyclic reads carry the same clash.
- **qwen3.8 padding.** The profile pads its prefix; image reads were padded for one order, so two-order arms are not
  exactly what live would compute ([vision-experiments.md §3](vision-experiments.md#3-collect)).
- **Cost is reads and tokens, not time.** No latency was measured for any round-3 or round-4 arm; a second read's
  live cost depends on prefix caching (§1).
- **`tn-prob` on noul.** Noul has one option count, so its β is not identified; only T(2) matters.
- **bf16 noise.** Probabilities move ~0.03 under load ([determinism.md](determinism.md)); offline numbers equal live
  within that noise.
- **`-dirty` provenance.** The text runs record 9c8945e-dirty: their code was committed together with their results
  as 90196a5. The image runs (§9) record 07cdb4a-dirty, with results committed right after as 849d7df; their check
  also counts uncommitted results and untracked files. Round 4's image grids record b953b23-dirty (`decider_chat`)
  and 438d4b5-dirty (blurb); their results commits, 438d4b5 and 119a5cf, change no code. Its text grids are clean.
- **Replay, not measurement.** The token table in §1 comes from a simplified block-cache model of one request shape
  (prompt-layouts.md caveats).

## Sources

- Our code: [`orders.py`](../../gateway/orders.py), [`decide.py`](../../gateway/decide.py) (`blend`),
  [`order_policies.py`](../../scripts/order_policies.py), [`order_stats.py`](../../scripts/order_stats.py),
  [`r3_orders.py`](../../scripts/r3_orders.py), [`vision_orders.py`](../../scripts/vision_orders.py),
  [`m3.py`](../../scripts/m3.py), [`vision_offline.py`](../../scripts/vision_offline.py).
- Our results: [m3-recommendations.md](../results/archive/m3-recommendations.md), M3 `header` order runs
  ([gemma](../results/archive/gemma-4-31b/2026-10-03T033153Z-m3-orders-header/summary.md),
  [qwen3.8](../results/archive/qwen3.8-27b/2026-10-03T031727Z-m3-orders-header/summary.md)), the round 1–4 runs
  and the cutdown spike linked above.
- Our research: [ordering-and-layout.md](../appendix/ordering-and-layout.md),
  [vision-research.md](../appendix/vision-research.md).
- Zheng et al., Large Language Models Are Not Robust Multiple Choice Selectors (PriDe): https://arxiv.org/abs/2309.03882
- reflex order averaging: https://github.com/kshetrajna12/reflex (`docs/results/order-averaging.md`)
- jobe: https://github.com/MantisShrimpdev/jobe
