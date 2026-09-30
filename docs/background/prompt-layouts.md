# Prompt layouts, option order and long documents

Based on `prompts/*.toml`, the research notes in
[ordering-and-layout.md](../appendix/ordering-and-layout.md), and a replay of one
2,048-token-state request (script kept in `.firecrawl/background/prompt-layouts/`, git-ignored). The replay uses
the same method as [prompt-sharing.md](prompt-sharing.md) §4: it rebuilds the rows with gateway code and counts what a
784-token block cache would reuse.

## Short answer

- **A layout is the order of the pieces in the prompt.** We ship three: `decider_chat`
  (state, then question; the default), `header` (question list, state, question) and
  `question_first` (question, then state).
- **The order decides how much prefix sharing survives.** For one 2,048-token-state,
  16-question, 26-option request on qwen3.6-27b, vLLM computes 12,877 tokens under
  `decider_chat`, 15,789 under `header` (+23%) and 36,397 under `question_first`
  (2.8x `decider_chat`), which shares nothing.
- **Literature is split on where the question belongs.** Anthropic and Google say query last, OpenAI
  says both ends. For lookup-style tasks question-first can be more accurate, but it costs
  a full state prefill per question.
- **Averaging option orders costs rows.** `identity+reversed` doubles the rows and computes
  1.88x the tokens (`decider_chat`), not 2x, because the state stays cached.
- **Only one layout is calibrated.** Just qwen3.6 `decider_chat` has a temperature, and that
  one is borrowed from decider's docs, not fitted by us.

## 1. The three layouts

Each layout is one TOML file. `order` lists the parts; the wording of each part sits beside it.
A "row" is one full prompt (one question); the **shared prefix** is what all rows have in
common before their first question-specific part
([`shared_len`](../../gateway/prompts.py)).

| Layout | `order` | Shared prefix across a request's questions |
|---|---|---|
| [`decider_chat`](../../prompts/decider_chat.toml) (default) | context, question, options | chat header + state |
| [`header`](../../prompts/header.toml) | questions, context, question, options | chat header + list of all questions + state |
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

## 2. Research: where to put the question, and option order

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

**Q1, option order.** Models favour certain option letters/positions regardless of content.
Zheng et al. find it is mostly a token-ID prior, not only position, so where the right answer sits
does not fully fix it. The usual fixes are permutation averaging (show options in 2+ orders and average
probabilities back, which our `option_orders` does) and PriDe-style prior estimation. Evidence on averaging is mixed:
reflex reports ECE 0.088 to 0.061 on a 27B model with two orders, while jobe found no accuracy gain on its hard tier
because the flips were symmetric noise. The notes recommend `identity+reversed` as the standard
profile and testing it per question type before making it default.

## 3. What each layout costs in prefix sharing

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

`identity+reversed` gives each question two rows (32 in all). Reversed rows share the state with the
identity rows, so the state stays cached.

| Layout | Rows | Prompt | Cached | **Computed** | vs same layout, identity | vs `decider_chat` identity |
|---|---|---|---|---|---|---|
| `decider_chat` | 32 | 72,794 | 48,608 | **24,186** | 1.88x | 1.88x |
| `header` | 32 | 78,618 | 48,608 | **30,010** | 1.90x | 2.33x |
| `question_first` | 32 | 72,794 | 0 | **72,794** | 2.00x | 5.65x |

- Averaging costs about 1.9x the computed tokens, close to the row count, not the "extra branch in one
  shared-prefix pass" (~+50%) that reflex measured for small requests. The reason is the 784-token rule:
  every additional row recomputes the 498 tail tokens of the state, too.
- Since throughput here is set by computed tokens per request (prompt-sharing.md §5, where the GPU is saturated at ~6,000
  computed tokens/s), 1.88x computed is, as an estimate, about half the requests per second. The
  replay counts tokens, not time.

### The trade-off

A layout that helps accuracy on long documents can multiply GPU work. `question_first` was the most accurate
single layout on snapjudge's long invoices but cost 6-8x the time there, and here it cannot reuse the
state at all. `header` keeps sharing and adds only the question list, but its accuracy edge is unproven. Reasonable policy, from the
appendix: keep `decider_chat` as default, use `question_first` only when a request has one question (nothing to
share, so it is free), and A/B `header` on long, multi-question states.

## 4. Calibration status per layout

| Model | Layout | `calibration.json` |
|---|---|---|
| qwen3.6-27b | `decider_chat` | yes: temperature 1.943 for choice/score/noul, **copied from decider-ai's SERVING.md, not our own fit** |
| qwen3.6-27b | `header`, `question_first` | none: gateway logs "temperature 1.0 (uncalibrated)" |
| gemma-4-31b, qwen3.8-27b | all three | none |

Labels tables exist for every (model, layout) pair in `data/`. Because temperature is tied to one model + precision +
layout, `header` and `question_first` answers are uncalibrated probabilities until fitted. Details and the fitting method:
[calibration.md](calibration.md).

## Caveats

- **Replay, not measurement.** Counts come from a simplified block-cache model. On the bench, real vLLM reused a bit less than the
  model predicts under load (prompt-sharing.md §4). Treat computed numbers as best-case.
- **One request shape.** State 2,048 tokens, 16 questions, 26 options, one seed (a single random state). Other sizes move the
  ratios (the 784-token remainder is what matters).
- **Cross-request reuse ignored.** Repeated requests can hit their own cached rows.
- **Tokens, not time.** The throughput reading assumes the ~6,000 tokens/s prefill rate measured earlier.
- **Accuracy figures are second-hand.** snapjudge, reflex and jobe numbers come from their READMEs (as summarised
  in the appendix), on other models. We have not run our own layout comparison.
- **Qwen only.** Block granularity differs on non-hybrid models such as Gemma 4.

## Sources

- Our code: [`layouts.py`](../../gateway/layouts.py), [`prompts.py`](../../gateway/prompts.py),
  [`orders.py`](../../gateway/orders.py), [`labels.py`](../../gateway/labels.py),
  [`readout.py`](../../gateway/readout.py), [`bench_data.py`](../../scripts/bench_data.py).
- Our research: [ordering-and-layout.md](../appendix/ordering-and-layout.md),
  [prompt-sharing.md](prompt-sharing.md), [6-answer-compatibility.md](../6-answer-compatibility.md).
- Zheng et al., Large Language Models Are Not Robust Multiple Choice Selectors: https://arxiv.org/abs/2309.03882
- Liu et al., Lost in the Middle: https://arxiv.org/abs/2307.03172
- Anthropic prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- OpenAI GPT-4.1 prompting guide: https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide
- Gemini long-context docs: https://ai.google.dev/gemini-api/docs/long-context
- snapjudge: https://github.com/Micha0827/snapjudge
- reflex order averaging: https://github.com/kshetrajna12/reflex (`docs/results/order-averaging.md`)
- jobe: https://github.com/MantisShrimpdev/jobe
