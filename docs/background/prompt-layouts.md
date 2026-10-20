# Prompt layouts and long documents

Based on `prompts/*.toml`, the research notes in
[ordering-and-layout.md](../appendix/ordering-and-layout.md), and a replay of one
2,048-token-state request (script kept in `.firecrawl/background/prompt-layouts/`, git-ignored). The replay uses
the same method as [prompt-sharing.md](prompt-sharing.md) §4: it rebuilds the rows with gateway code and counts what a
784-token block cache would reuse.

## Short answer

- **A layout is the order of the pieces in the prompt.** We ship three: `decider_chat`
  (state, then question), `header` (question list, state, question; the default) and
  `question_first` (question, then state).
- **The order decides how much prefix sharing survives.** `decider_chat` and `header` keep each
  row's question outside the shared prefix; `question_first` shares nothing. With today's padding
  and warm-up, `header` computes 1.02–1.09× the minimum on Qwen (1.34 for a tiny 256-token × 4 request: the pad) and ~1.0× on gemma for multi-question
  requests (§3, measured 2026-10-15). Before padding it cost +23% over `decider_chat` (§3, replay).
- **Literature is split on where the question belongs.** Anthropic and Google say query last, OpenAI
  says both ends. For lookup-style tasks question-first can be more accurate, but it costs
  a full state prefill per question.
- **Option order** (bias, averaging and its cost) has its own doc: [option-ordering.md](option-ordering.md).
- **Every profile has a calibration file for all three layouts** (`data/<profile>/<layout>/calibration.json`, §4).
  Experiment layouts have none.
- **An intro blurb** (one sentence before the prompt, round 4) moves text accuracy by +0.2 to +1.0 points; only
  gemma's `decider_chat` gain has a CI above 0. No image CI excludes 0. `decider_chat` trails `header` on text by
  1.5–3.6 points on both models, with or without the blurb (§5).

## 1. The three layouts

Each layout is one TOML file. `order` lists the parts; the wording of each part sits beside it.
A "row" is one full prompt (one question); the **shared prefix** is what all rows have in
common before their first question-specific part
([`shared_len`](../../gateway/prompts.py)).

| Layout | `order` | Shared prefix across a request's questions |
|---|---|---|
| [`decider_chat`](../../prompts/decider_chat.toml) | context, question, options | chat header + state |
| [`header`](../../prompts/header.toml) (default) | questions, context, question, options | chat header + list of all questions + state |
| [`question_first`](../../prompts/question_first.toml) | question, options, context | chat header only (3 tokens) |

A tiny request rendered with each layout (state "Order 17: 3 widgets shipped on Monday.", first
question a two-option choice), decoded from the token ids the gateway builds for qwen3.6. The
`<think></think>` block is the chat template's thinking-off tail:

```
decider_chat                    header                              question_first
<|im_start|>user                <|im_start|>user                    <|im_start|>user
Context:                        Questions that will be asked        Question: When did it ship?
Order 17: 3 widgets ...          about the context:                 Options:
                                - When did it ship?                 (A) monday: Shipped Monday
Question: When did it ship?     - The order shipped late            (B) friday: Shipped Friday
Options:
(A) monday: Shipped Monday      Context:                            Context:
(B) friday: Shipped Friday      Order 17: 3 widgets ...             Order 17: 3 widgets ...
<|im_end|>                                                          <|im_end|>
<|im_start|>assistant           Question: When did it ship?         <|im_start|>assistant
<think></think>                 Options:                            <think></think>
Answer: (                       (A) ... (B) ...<|im_end|> ...       Answer: (
```

All three end at `Answer: (`; the model's next token is the option letter, which we read as logprobs
(see [decision-readout.md](decision-readout.md)). `question_first` puts the state last, right before the
reply, and `header` shows the model every question before the state.

Images sit inside `Context:` with no wording change: the layout files are the same, and the image tokens replace
nothing in the text. With `header` the questions still come before the context, so the image comes after them. See
[images.md](images.md).

### How layouts are loaded and hashed

[`gateway/layouts.py`](../../gateway/layouts.py) reads every `prompts/*.toml`, checks the required
keys and placeholders (`{state}`, `{question}`, `{label}`...), and stores a SHA-256 of the **raw file bytes**
as `Layout.sha256`. Any edit, even a comment, changes it. The token ids are then built part by part
in [`build_rows`](../../gateway/prompts.py) so shared parts are encoded once and match exactly across rows.

### Why editing a layout forces rebuilds and refits

```
edit prompts/x.toml -> sha256 changes -> labels.json stale -> gateway refuses to start
                                     \-> old temperature no longer describes this prompt
```

1. **Label tables.** `data/<profile>/<layout>/labels.json` stores `layout_sha256` and
   `tokenizer_sha256`. [`load_labels`](../../gateway/labels.py) refuses a mismatch ("layout changed, rerun
   scripts/build_labels.py"). The rebuild also re-checks that every option letter is a single token right
   after the layout's answer slot.
2. **Temperature.** A fitted temperature is valid for one model, precision and prompt layout
   (see CLAUDE.md, "Hard-won facts"). New wording shifts the logits, so the fit must be redone. Nothing in code
   detects this; the hash check covers labels only.

## 2. Research: where to put the question

Depth and sources are in [ordering-and-layout.md](../appendix/ordering-and-layout.md). The short version:

**Q2, where the question goes for long documents**

| Source | Advice / finding |
|---|---|
| Anthropic prompting docs | Long documents first, query at the end; "up to 30 percent" better in their tests |
| Google Gemini docs | Query at the end for long contexts |
| OpenAI GPT-4.1 guide | Best: instructions at both ends; if only once, before the context |
| Liu et al., Lost in the Middle | Accuracy is best at context start or end. Repeating the query before and after fixes key-value retrieval but barely helps multi-document QA |
| snapjudge (Jev-compatible, 35B-A3B) | Short state: question-first was more accurate and faster (89% to 97-100%). 8,000-token invoices: 41/75 state-first, 45 `header`, 50 question-first; question-first was 6-8x slower. The authors call the 4-item `header` gain "a hint rather than proof" |

Take-away: there is no universal answer, and the accuracy gain from question-first appears on
retrieval-shaped questions. It is the layout that loses sharing (section 3).

**Q1, option order:** moved to [option-ordering.md §2](option-ordering.md#2-position-and-letter-bias).

## 3. What each layout costs in prefix sharing

### Measured with today's settings (2026-10-15)

Fresh requests (`synthetic_request`, 26 options, mixed types, a new state per request), `header`, rows built by
gateway code and sent straight to vLLM; 3 repeats per cell (`share_probe.py`, raw data in `.cache/share-spike/`).
Computed ÷ usage, where usage is the state once plus each question once:

| State × questions | qwen3.8-27b (pad to 800, row warm-up, MTP) | gemma-4-31b, all rows together | gemma-4-31b, prefix alone first |
|---|---|---|---|
| 256 × 4 | 1.34 (the pad itself) | 1.00 | 0.98 |
| 256 × 16 | 1.09 | 0.92 | 0.92 |
| 2,048 × 4 | 1.09 | 1.22 | 0.99 |
| 2,048 × 16 | 1.03 | 1.07 | 0.95 |
| 8,000 × 4 | 1.02 | **2.78** (5,976 ms) | **1.00** (2,312 ms) |
| 8,000 × 16 | 1.05 | **2.90** (8,201 ms) | **0.99** (3,112 ms) |

- **Qwen:** with front padding each row's question starts a fresh block, so `header` shares almost everything.
  Live benches agree: 1.02 in the throughput phases (2026-10-04, both Qwen profiles). Sending the prefix alone
  first is worse on Qwen in every cell (1.03–1.92), as DS-008 found.
- **Gemma:** with `--long-prefill-token-threshold 1024` (DS-025) every prefill advances 1,024 tokens a step, so rows
  sent together prefill side by side and each computes its own copy of the state. Sending the shared prefix alone
  first fixes it; for short prefixes it only adds a round trip (+60 ms at 256 × 4). Gemma now uses
  `WARM_UP=prefix` with `WARM_MIN_PREFIX_TOKENS=4096`, where the gain is large (prompt-sharing.md §7). Ratios below 1 come from template text cached by earlier
  requests.

### Before padding: the 2026-09-29 replay

This replay predates front padding and explains why Qwen needs it; its `header` cost is no longer current.
Same request as in prompt-sharing.md: `synthetic_request` with a 2,048-token state, 16 questions, 26 options
(mixed choice, score, noul types). The replay applies the same rules as before: only whole 784-token
blocks are reused, rows sent together cannot reuse each other, and row 1 goes first alone when the shared prefix is at
least 512 tokens (`WARM_MIN_PREFIX_TOKENS`).

### One request, `option_orders = identity`

| Layout | Rows | Shared prefix | Prompt tokens | Cached | **Computed** | vs `decider_chat` computed |
|---|---|---|---|---|---|---|
| `decider_chat` | 16 | 2,066 | 36,397 | 23,520 | **12,877** | 1.00x |
| `header` | 16 | 2,248 | 39,309 | 23,520 | **15,789** | 1.23x |
| `question_first` | 16 | 3 | 36,397 | 0 | **36,397** | 2.83x |

- **`decider_chat`:** 2,066 = 2 x 784 + 498, so 15 rows reuse 1,568 tokens each (23,520). This is the 2.4x waste
  from prompt-sharing.md. The ideal (state once + each question once, "usage") is 5,407, so computed
  divided by usage is **2.38**.
- **`header`:** the extra 182 tokens of question list are shared too, but 2,248 is still 2 x 784 + 680, so the
  same two blocks are reused (23,520). The longer tail is recomputed 15 times. Computed / usage is **2.83**
  (usage itself is 5,589).
- **`question_first`:** each row begins with its own question and options, so no two rows share more than the
  3-token chat header. Nothing is cached and **computed equals the full prompt**. Its own computed / usage prints as
  1.00 because "usage" there also has no shared part (36,352); that ratio is misleading. Against the
  ideal state-first work (5,407) it is **6.7x**.

```
decider_chat    [ chat+state 2066 : cached 1568 | recompute 498 ][ q + options ]   x16
header          [ chat+questions+state 2248 : cached 1568 | recompute 680 ][ q ]  x16
question_first  [ q + options ][ state 2,0xx ]  every row unique from token 4 -> all computed
```

### Adding option-order averaging

Moved, with the same replay's token table: [option-ordering.md §1](option-ordering.md#what-a-second-order-costs-in-tokens).

### The trade-off

A layout that helps accuracy on long documents can multiply GPU work. `question_first` was the most accurate
single layout on snapjudge's long invoices but cost 6-8x the time there, and here it cannot reuse the
state at all. `header` keeps sharing and adds only the question list, but its accuracy edge is unproven. Reasonable policy, from the
appendix: keep `decider_chat` as default, use `question_first` only when a request has one question (nothing to
share, so it is free), and A/B `header` on long, multi-question states.

Update 2026-10-03: M3 measured `header` and the owner made it qwen3.6's default layout; qwen3.8 and gemma kept
`decider_chat`.

Update 2026-10-04: `header` ships for all three profiles. Full Decision Index runs beat `decider_chat` by 3.4 to 4.5
points on each (the offline index-dev and eval splits had understated it), at +10–17 ms median latency and 7–11
refused rows per profile ([m3-recommendations.md](../results/archive/m3-recommendations.md)).

## 4. Calibration status per layout

Files in `data/<profile>/<layout>/` (date of the current fit):

| Profile | `calibration.json` | Also |
|---|---|---|
| qwen3.6-27b | all three layouts (2026-10-07) | `calibration-784.json`, all three (2026-10-03), for `PREFIX_BLOCK=784` |
| qwen3.8-27b | all three layouts (2026-10-08) | `calibration-784.json`, all three (2026-10-03) |
| gemma-4-31b | all three layouts (2026-10-03) | — |
| gemma-4-31b-fp8, qwen3.6-27b-fp8, qwen3.8-27b-fp8, qwen3.8-27b-nvfp4 | all three layouts (2026-10-09) | — |

- T per type in every file. A noul offset b ≠ 0 only in gemma's `decider_chat` and `question_first` (bf16 and fp8)
  and qwen3.6's `question_first`.
- Experiment layouts (`prompts/experiments/`) have no file; round 4 fits each arm on calib-600 instead (§5).

Labels tables exist for every (model, layout) pair in `data/`. Because temperature is tied to one model + precision +
layout, each (model, layout) pair needs its own fit. Details and the fitting method:
[calibration.md](calibration.md).

## 5. Intro blurb (round 4)

Round 4 (DS-043, 2026-10-19/20) asked whether one sentence before the prompt changes accuracy or calibration, on
`header` and on `decider_chat`, for gemma-4-31b and qwen3.8-27b. Design:
[the spec](../superpowers/specs/2026-10-19-layouts-and-blurb-design.md). The order grids of the same round are in
[option-ordering.md §10](option-ordering.md#10-round-4-decider_chat-and-the-blurb). This section reports; the owner
picks.

### Wording, placement, cost

[`blurb-header.toml`](../../prompts/experiments/blurb-header.toml) and
[`blurb-decider.toml`](../../prompts/experiments/blurb-decider.toml) copy their served layout and put one line and a
blank line before the first part: before `Questions that will be asked about the context:` on `header`, before
`Context:` on `decider_chat`. Nothing else changes, and the gateway never loads them.

```
You will be asked questions about the following context. Answer each with the letter of the best option.
```

- **Prefix cost.** The blurb sits in the shared prefix, so a request pays it once, not per question. It adds 21
  input tokens per image row on both models: image dev's mean goes 719 → 740 on gemma and 1,117 → 1,138 on qwen3.8.
  Text records hold no token counts.
- **Arms.**

  | Arm | Layout | Blurb | Collect label |
  |---|---|---|---|
  | H | `header` | no | `letters` (round 3's fresh collects) |
  | D | `decider_chat` | no | `decider` |
  | HB | `header` | yes | `blurb-header` |
  | DB | `decider_chat` | yes | `blurb-decider` |

- **Screen.** Identity + reversed reads on text calib-600 and index-dev-2k (3,728 questions: 3,690 choice, 38 noul)
  and image dev (1,462 rows). [`layout_screen.py`](../../scripts/layout_screen.py) pairs two arms on the questions
  both answered, as round 3's label screen does ([answer-labels.md §2](answer-labels.md#2-mechanics)):
  - T per type on each arm's calib-600 identity reads (mean-prob, b = 0); image rows use the choice T;
  - text: M3's paired bootstrap; images: `vision_compare`, paired group bootstrap (10,000 resamples, seed 0).
- **Calib rows.** gemma fits on 600 calib questions (its profile's max_len 65,536); qwen3.8 on 590 (32,768: 10
  entity-alignment rows are too long).

### Screen results

Text, index-dev-2k. Δ is arm − control, 95% paired CI; accuracy in points. The control column is its absolute
accuracy (%). Flip rate: share of questions whose top answer changes between the identity and the reversed read.

| Pair | Effect | Profile | control | Δ accuracy | Δ ECE | Δ NLL | flip rate, control → arm |
|---|---|---|---|---|---|---|---|
| HB vs H | blurb on `header` | gemma-4-31b | 80.2 | +0.4 [-0.0, +0.9] | -0.0004 [-0.0055, +0.0040] | +0.0112 [+0.0003, +0.0217] | 0.074 → 0.070 |
| DB vs D | blurb on `decider_chat` | gemma-4-31b | 76.6 | +1.0 [+0.4, +1.6] | -0.0121 [-0.0184, -0.0057] | -0.0516 [-0.0658, -0.0380] | 0.085 → 0.082 |
| D vs H | layout, no blurb | gemma-4-31b | 80.2 | -3.6 [-4.4, -2.8] | +0.0226 [+0.0133, +0.0299] | +0.1385 [+0.1124, +0.1664] | 0.074 → 0.085 |
| DB vs HB | layout, with blurb | gemma-4-31b | 80.6 | -3.0 [-3.8, -2.2] | +0.0109 [+0.0029, +0.0188] | +0.0757 [+0.0498, +0.1028] | 0.070 → 0.082 |
| HB vs H | blurb on `header` | qwen3.8-27b | 78.2 | +0.4 [-0.1, +0.9] | +0.0128 [-0.0007, +0.0185] | -0.0197 [-0.0260, -0.0132] | 0.098 → 0.094 |
| DB vs D | blurb on `decider_chat` | qwen3.8-27b | 76.7 | +0.2 [-0.3, +0.8] | -0.0014 [-0.0128, +0.0089] | -0.0270 [-0.0338, -0.0205] | 0.105 → 0.107 |
| D vs H | layout, no blurb | qwen3.8-27b | 78.2 | -1.5 [-2.2, -0.8] | +0.0014 [-0.0098, +0.0120] | +0.0360 [+0.0266, +0.0447] | 0.098 → 0.105 |
| DB vs HB | layout, with blurb | qwen3.8-27b | 78.6 | -1.7 [-2.4, -0.9] | -0.0128 [-0.0207, +0.0011] | +0.0287 [+0.0182, +0.0388] | 0.094 → 0.107 |

Image dev, Δ index with `vision_compare`'s CI. Agreement is the share of rows with the same top answer.

| Pair | Profile | control index | Δ index [95% CI] | Δ ECE | Δ NLL | agreement | flip rate, control → arm | mean input tokens, control → arm |
|---|---|---|---|---|---|---|---|---|
| HB vs H | gemma-4-31b | 77.09 | +1.16 [-0.28, +2.63] | -0.0066 | -0.0108 | 0.945 | 0.127 → 0.120 | 719 → 740 |
| DB vs D | gemma-4-31b | 77.96 | -0.83 [-2.18, +0.50] | +0.0044 | +0.0034 | 0.950 | 0.134 → 0.117 | 672 → 693 |
| D vs H | gemma-4-31b | 77.09 | +0.87 [-0.77, +2.46] | -0.0150 | -0.0126 | 0.934 | 0.127 → 0.134 | 719 → 672 |
| DB vs HB | gemma-4-31b | 78.25 | -1.12 [-2.82, +0.48] | -0.0041 | +0.0016 | 0.930 | 0.120 → 0.117 | 740 → 693 |
| HB vs H | qwen3.8-27b | 73.49 | +0.17 [-1.53, +1.89] | +0.0232 | +0.0059 | 0.936 | 0.204 → 0.172 | 1,117 → 1,138 |
| DB vs D | qwen3.8-27b | 72.45 | +0.51 [-1.46, +2.48] | -0.0113 | -0.0244 | 0.917 | 0.198 → 0.174 | 1,070 → 1,091 |
| D vs H | qwen3.8-27b | 73.49 | -1.04 [-2.89, +0.80] | +0.0608 | +0.0578 | 0.923 | 0.204 → 0.198 | 1,117 → 1,070 |
| DB vs HB | qwen3.8-27b | 73.66 | -0.70 [-2.58, +1.17] | +0.0262 | +0.0275 | 0.925 | 0.172 → 0.174 | 1,138 → 1,091 |

- **Blurb on `header`.** +0.4 points on text on both models, CIs touching 0. ECE does not move on gemma; on qwen3.8 it
  is +0.013, CI [−0.001, +0.019]. NLL goes up on gemma (+0.011) and down on qwen3.8 (−0.020), both CIs excluding 0.
  Images: +1.16 (gemma) and +0.17 (qwen3.8), CIs include 0; qwen3.8's image ECE rises 0.023.
- **Blurb on `decider_chat`.** gemma text +1.0 [+0.4, +1.6], with ECE −0.012 and NLL −0.052 (CIs below 0). qwen3.8
  +0.2, CI includes 0, NLL −0.027. Images: −0.83 (gemma) and +0.51 (qwen3.8), CIs include 0.
- **Layout.** `decider_chat` trails `header` on text on both models, with or without the blurb (−3.6 and −3.0 on
  gemma, −1.5 and −1.7 on qwen3.8, all CIs below 0), as M3 found (§3 updates). No layout pair separates on images.
- **Survivors.** The spec runs the order grid on a blurb arm unless its screen is significantly worse than its
  control. HB and DB both passed on both models. The owner ran the grid on HB only (2026-10-19): DB trails HB on
  text on both models, CIs below 0 ("the others seem worse, but we should still record them"). DB has the screen
  results above and no grid.

### `decider_chat` on images

Round 4 collected `decider_chat` on images for the first time. From the D vs H pairs (each arm's calib-600 choice T):

| Profile | Layout | index | accuracy | ECE | NLL | mean input tokens | flip rate |
|---|---|---|---|---|---|---|---|
| gemma-4-31b | `header` | 77.09 | 80.2 | 0.0921 | 0.6260 | 719 | 0.127 |
| gemma-4-31b | `decider_chat` | 77.96 | 80.5 | 0.0770 | 0.6135 | 672 | 0.134 |
| qwen3.8-27b | `header` | 73.49 | 77.0 | 0.0399 | 0.5999 | 1,117 | 0.204 |
| qwen3.8-27b | `decider_chat` | 72.45 | 76.5 | 0.1007 | 0.6577 | 1,070 | 0.198 |

- `decider_chat` drops the question list: 47 fewer tokens per image row.
- Δ index +0.87 [−0.77, +2.46] on gemma and −1.04 [−2.89, +0.80] on qwen3.8. qwen3.8's ECE is 2.5× `header`'s at the
  text-fitted T (1.471).
- The `decider_chat` image order grids: [option-ordering.md §10](option-ordering.md#decider_chat-image).

### Runs

Text `summary.md` (per type, per option count, position histograms) and image `summary.md` (per benchmark under
`*-compare-all/`), per pair:

| Pair | gemma-4-31b | qwen3.8-27b |
|---|---|---|
| D vs H | [text](../results/archive/2026-10-19T153546Z-r4-pair-decider-vs-letters-gemma-4-31b/summary.md), [image](../results/vision-experiments/2026-10-19T153546Z-r4-pair-decider-vs-letters-gemma-4-31b/summary.md) | [text](../results/archive/2026-10-19T181818Z-r4-pair-decider-vs-letters-qwen3.8-27b/summary.md), [image](../results/vision-experiments/2026-10-19T181818Z-r4-pair-decider-vs-letters-qwen3.8-27b/summary.md) |
| HB vs H | [text](../results/archive/2026-10-19T162701Z-r4-pair-blurb-header-vs-letters-gemma-4-31b/summary.md), [image](../results/vision-experiments/2026-10-19T162701Z-r4-pair-blurb-header-vs-letters-gemma-4-31b/summary.md) | [text](../results/archive/2026-10-19T185753Z-r4-pair-blurb-header-vs-letters-qwen3.8-27b/summary.md), [image](../results/vision-experiments/2026-10-19T185753Z-r4-pair-blurb-header-vs-letters-qwen3.8-27b/summary.md) |
| DB vs D | [text](../results/archive/2026-10-19T171451Z-r4-pair-blurb-decider-vs-decider-gemma-4-31b/summary.md), [image](../results/vision-experiments/2026-10-19T171451Z-r4-pair-blurb-decider-vs-decider-gemma-4-31b/summary.md) | [text](../results/archive/2026-10-19T193524Z-r4-pair-blurb-decider-vs-decider-qwen3.8-27b/summary.md), [image](../results/vision-experiments/2026-10-19T193524Z-r4-pair-blurb-decider-vs-decider-qwen3.8-27b/summary.md) |
| DB vs HB | [text](../results/archive/2026-10-19T171521Z-r4-pair-blurb-decider-vs-blurb-header-gemma-4-31b/summary.md), [image](../results/vision-experiments/2026-10-19T171521Z-r4-pair-blurb-decider-vs-blurb-header-gemma-4-31b/summary.md) | [text](../results/archive/2026-10-19T193554Z-r4-pair-blurb-decider-vs-blurb-header-qwen3.8-27b/summary.md), [image](../results/vision-experiments/2026-10-19T193554Z-r4-pair-blurb-decider-vs-blurb-header-qwen3.8-27b/summary.md) |

### Blurb caveats

- **A screen, not a confirm.** One wording, one position; index-dev-2k only (no eval, no full Index run), with 38 noul
  and no score questions, so the text results speak for choice.
- **Many comparisons.** 4 pairs × 2 models × text and image; the CIs are not corrected.
- **Fits.** Each arm is refitted on calib-600, so ECE differences include fit noise. gemma's score T fits to 19.999,
  at [`fit.py`](../../scripts/fit.py)'s upper bound of 20, for H and HB (the summaries' Fits tables); index-dev-2k
  has no score questions, so no number above depends on it.
- **The H arm is round 3's fresh `letters` collects**, not the old full collects round 3's order grid read.
- **Keyed image options.** Reversed image reads show labels that disagree with the options' own keys
  ([option-ordering.md, Caveats](option-ordering.md#caveats)), so the image flip rates carry that clash.
- **`-dirty` provenance.** The image compare summaries record b953b23-dirty; the results were committed right after
  as 438d4b5, which changes no code. The check also counts uncommitted results and untracked files.

## Caveats

- **Replay, not measurement.** Counts come from a simplified block-cache model. On the bench, real vLLM reused a bit less than the
  model predicts under load (prompt-sharing.md §4). Treat computed numbers as best-case.
- **One request shape.** State 2,048 tokens, 16 questions, 26 options, one seed (a single random state). Other sizes move the
  ratios (the 784-token remainder is what matters).
- **Cross-request reuse ignored.** Repeated requests can hit their own cached rows.
- **Tokens, not time.** The throughput reading assumes the ~6,000 tokens/s prefill rate measured earlier.
- **Accuracy figures are second-hand.** snapjudge numbers come from its README (as summarised in the appendix), on
  other models. M3 later ran our own layout comparison (§3, updates).
- **Qwen only.** Block granularity differs on non-hybrid models such as Gemma 4.

## Sources

- Our code: [`layouts.py`](../../gateway/layouts.py), [`prompts.py`](../../gateway/prompts.py),
  [`orders.py`](../../gateway/orders.py), [`labels.py`](../../gateway/labels.py),
  [`readout.py`](../../gateway/readout.py), [`bench_data.py`](../../scripts/bench_data.py),
  [`layout_screen.py`](../../scripts/layout_screen.py).
- Our results: M3 ([m3-recommendations.md](../results/archive/m3-recommendations.md)) and the round 4 pair runs (§5).
- Our research: [ordering-and-layout.md](../appendix/ordering-and-layout.md),
  [prompt-sharing.md](prompt-sharing.md), [6-answer-compatibility.md](../6-answer-compatibility.md).
- Liu et al., Lost in the Middle: https://arxiv.org/abs/2307.03172
- Anthropic prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- OpenAI GPT-4.1 prompting guide: https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide
- Gemini long-context docs: https://ai.google.dev/gemini-api/docs/long-context
- snapjudge: https://github.com/Micha0827/snapjudge
