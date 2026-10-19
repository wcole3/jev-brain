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
- **Only qwen3.6 is calibrated.** All three of its layouts have our own fit; qwen3.8 and
  gemma run uncalibrated until their collects are fitted.

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

| Model | Layout | `calibration.json` |
|---|---|---|
| qwen3.6-27b | all three | yes: our fit, 2026-10-02 (T per type; noul offset only in `question_first`) |
| gemma-4-31b, qwen3.8-27b | all three | none: gateway warns and runs at T = 1, b = 0 |

Labels tables exist for every (model, layout) pair in `data/`. Because temperature is tied to one model + precision +
layout, each (model, layout) pair needs its own fit. Details and the fitting method:
[calibration.md](calibration.md).

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
  [`readout.py`](../../gateway/readout.py), [`bench_data.py`](../../scripts/bench_data.py).
- Our research: [ordering-and-layout.md](../appendix/ordering-and-layout.md),
  [prompt-sharing.md](prompt-sharing.md), [6-answer-compatibility.md](../6-answer-compatibility.md).
- Liu et al., Lost in the Middle: https://arxiv.org/abs/2307.03172
- Anthropic prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- OpenAI GPT-4.1 prompting guide: https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide
- Gemini long-context docs: https://ai.google.dev/gemini-api/docs/long-context
- snapjudge: https://github.com/Micha0827/snapjudge
