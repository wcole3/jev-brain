# The decision readout, end to end

How one `/v1/systemone` request becomes token ids, one vLLM call and a Jev-style answer.
Every value below is real output from the code on `qwen3.6-27b` (tokenizer only, no GPU),
except the probabilities in §7, which are illustrative. The concept is in
[../4-inference-technique.md](../4-inference-technique.md); this doc walks the code.

## Short answer

- **The model never writes an answer.** We show it a multiple-choice prompt that stops at
  `Answer: (`, ask vLLM for **one token** and read the log-probabilities of the option
  letters `A`, `B`, `C`...
- **Everything depends on tokens, not text.** Each letter must be exactly one token in
  that position, and rows are built token by token so the shared prefix is identical.
  That is why there is a label table and piecewise encoding.
- **One row per question per option order.** A row is one prompt. Several option orders
  per question are averaged back to reduce position bias.
- **Log-probabilities become probabilities via a softmax with a fitted temperature**,
  then `answers.py` shapes them into `choice`, `score` or `noul`.

The flow, in the order of [`decide.py`](../../gateway/decide.py):

```
request --> render --> choose orders --> build rows --> vLLM readout --> softmax --> answer
            questions   orders.py        prompts.py     readout.py       calibration  answers.py
                                         (uses the label table loaded at startup)
```

The sections below explain these pieces in teaching order, so labels (§2) and orders (§4)
come before and after the row building they feed into.

The worked example is the quickstart request from
[`tests/helpers.py`](../../tests/helpers.py): the state "Hi, my Stripe integration keeps
failing and I'm losing sales. Please help ASAP." and three questions (`department`
choice, `frustration` score, `is_urgent` noul).

## 1. Rendering: questions become option texts

[`questions.py`](../../gateway/questions.py) turns every question into a `Rendered`: the
question text, the option texts in the caller's order, and what each option reports back.
The text patterns come from the layout, [`prompts/decider_chat.toml`](../../prompts/decider_chat.toml).

| Type | Options shown to the model | Reports back |
|---|---|---|
| choice | `billing: Payment or subscription issues`, ... (`name: description`; just `name` if no description) | the choice keys |
| score | `0: Calm, just stating facts`, `1: ...` (level number plus description, 2 to 10 levels) | level numbers |
| noul | `no`, `yes` (plus descriptions of `false`/`true` if given) | `False`, `True` |

- **noul** is a two-option choice. If it has no `instructions`, the fixed question
  "Which answer fits the context?" is used, and the criteria must describe true or false.
- **State** is used as is when it is a string. A dict or list is dumped to JSON, and
  lists of 8 or more items get an `_index` on each item (`ANNOTATE_MIN`) so a model can
  cite `records[47]`, as decider does.
- Limits: at most 255 options per choice, 2 to 10 score levels; violations are a
  `RequestError` (HTTP 422).

Example, real output:

```
department  choice  'Which team should handle this'
            ['billing: Payment or subscription issues', 'technical: Bugs or integration problems', 'sales: ...']
is_urgent   noul    'The message conveys urgency or time-sensitivity'   ['no', 'yes']
```

## 2. Label tables: which token means "A"?

The readout compares the logprobs of one token per option, so each label must be **one
token**. [`labels.py`](../../gateway/labels.py) builds the table once per tokenizer and layout,
with [`scripts/build_labels.py`](../../scripts/build_labels.py):

- **The list:** `A`..`Z`, then `AA`..`ZZ`, keeping those that encode to a single token,
  and stopping at **255** (`MAX_LABELS`, Jev's option cap). On qwen3.6: `A`=32, `B`=33,
  `Z`=57, `AA`=5840, `AB`=1803, and the 255th label is `JT`. 26 single letters plus 229
  two-letter labels.
- **In context, not just alone.** A letter that is one token alone can merge with its
  neighbour. Real example: `"\n("` then `"A"` encodes to `[198, 7, 32]`, but `"\n(A"`
  encodes to `[198, 4205]`, one token `(A` that is not the id of `A`. The build script
  checks that `encode(answer_slot + "A") == encode(answer_slot) + [id_A]` for `A`..`J`.
  For `Answer: (` it holds: `[15666, 25, 318]` plus `[32]`.
- **Stale-hash refusal.** `labels.json` stores a SHA-256 of the tokenizer (vocabulary and
  chat template) and of the layout file. At startup `load_labels` raises if either
  changed, telling you to rerun the script. Ids from an old tokenizer would silently read
  the wrong tokens.

Only the first 10 letters are checked in context, and the gateway does not recheck at
startup ([CLAUDE.md](../../CLAUDE.md) notes this). More than 10 options never rely on it, see §3.

## 3. Piecewise tokenization: building the row ids

[`prompts.py`](../../gateway/prompts.py) builds the token ids itself instead of sending
text to vLLM. Two reasons:

1. **Tokens merge at boundaries.** Real example: `encode("state\n") + encode("\nQuestion")`
   gives `[2374, 198, 198, 14162]`, but `encode("state\n\nQuestion")` gives
   `[2374, 271, 14162]`: two newlines merged into one token (271). Encode the whole prompt
   and the tokens around the state depend on what follows it.
2. **Rows must share an exact prefix.** If each part is encoded on its own and the ids are
   concatenated, the state part is the same ids in every row, so vLLM's prefix cache can
   match ([prompt-sharing.md](prompt-sharing.md)). This is also how decider does it, so we
   match its token ids exactly:
   [`tests/parity`](../../tests/parity/test_decider_parity.py) compares our rows with
   fixtures made by decider-ai 1.5.0 (`scripts/decider_fixtures.py`), token for token, on
   every profile.

**The chat frame.** `chat_frame` renders the model's chat template for one user turn with
a placeholder, splits at the placeholder into `head` and `tail`, and closes the thinking
block so the model answers directly:

```
head  [248045, 846, 198]                          <|im_start|> user \n
...user content...
tail  [248046, 198, 248045, 74455, 198,           <|im_end|> \n <|im_start|> assistant \n
       248068, 271, 248069, 271]                  <think> \n\n </think> \n\n
```

`CLOSE_THINKING` appends the closing tag when the template leaves thinking open
(`<think>\n`); `chat_frame` also checks that the tail does not merge with the answer slot.

**The rows.** The layout's `order` (default `context, question, options`) lists the
parts. `context` (`Context:\n<state>`) is encoded once and shared. Per question, `question`
(`\n\nQuestion: ...\nOptions:`) and `options` are added, then the tail and `Answer: (`.
Decoded, the first row of the example is:

```
<|im_start|>user
Context:
Hi, my Stripe integration keeps failing and I'm losing sales. Please help ASAP.

Question: Which team should handle this
Options:
(A) billing: Payment or subscription issues
(B) technical: Bugs or integration problems
(C) sales: Pricing or account questions<|im_end|>
<|im_start|>assistant
<think>

</think>

Answer: (
```

Its last tokens are `... ' questions', '<|im_end|>', '\n', '<|im_start|>', 'assistant', '\n', '<think>', '\n\n', '</think>', '\n\n', 'Answer', ':', ' ('`,
and the label ids to read are `[32, 33, 34]`.

**Narrow versus wide options (`option_ids`).**

| Options | How they are encoded | Why |
|---|---|---|
| up to 10 (`NARROW`) | one text encode of `\n(A) text\n(B) text...` | matches decider; in this text `(A` is one merged token, which is fine because the readout token comes after `Answer: (` |
| more than 10 | opening, label **id**, closing are spliced per option; the closings go through `encode_each` (one tokenizer call for all texts) | labels like `AB` must be one token each, so we insert the id instead of trusting the encoder |

Real wide example (12 options): `..., '\n', '(', 'K', ')', ' c', '1', '0', ...`: the
label is its own token `K` (id 42).

`Batch.shared_len` is the number of leading tokens common to all rows (23 in the example:
head plus context). `Batch.input_tokens` counts that prefix once, as Jev counts state once:
`shared_len + sum(len(row) - shared_len)`. For the example that is 6 rows of
73, 73, 80, 80, 58, 58 tokens and `input_tokens` = 307 (with 2 orders, see §4).

## 4. Option orders: fighting position bias

Models lean toward some positions (often the first). [`orders.py`](../../gateway/orders.py)
shows each question with several orderings of its options. `perm[j]` is the caller's option
shown at position `j`.

| Setting | Orders for 3 options |
|---|---|
| `identity` (default, `OPTION_ORDERS`) | `[0,1,2]` |
| `identity+reversed` | `[0,1,2]`, `[2,1,0]` |
| `cyclic:<k>` | `k` evenly spaced rotations, at most one per option |

Each order is its own row, so 2 orders means twice the rows. The example above was built
with `identity+reversed`: 3 questions gave 6 rows. `average_back` puts each row's
probabilities back in the caller's positions and takes the mean; for
`[.7,.2,.1]` in identity and `[.5,.3,.2]` in reversed order, the result is
`[.45, .25, .30]`. A request may override the setting with `option_orders`
(and `layout`); both are experiment hooks, not Jev API.

## 5. Readout: one token, many logprobs

[`readout.py`](../../gateway/readout.py) sends the ids to vLLM `/v1/completions`:

```json
{"prompt": [[ids row 1], [ids row 2], ...], "max_tokens": 1, "temperature": 0, "logprobs": 0,
 "logprob_token_ids": [32, 33, 34], "return_tokens_as_token_ids": true, "add_special_tokens": false}
```

- **One token, no text.** `max_tokens=1` stops after the answer slot, and
  `logprob_token_ids` asks for exactly the label tokens' log-probabilities, not top-k.
- **Where they come back:** `choices[i].logprobs.top_logprobs[0]["token_id:<id>"]`.
  `return_tokens_as_token_ids` makes the keys ids instead of decoded text. Choices are
  sorted by `index` so rows stay aligned.
- **Chunks of 128.** vLLM caps `logprob_token_ids` at 128 per request
  (`MAX_LABEL_IDS`). A 255-option question makes two calls with the same prompts.
- **Warm-up** (`WARM_UP=row` on Qwen; gemma uses `WARM_UP=prefix` and sends the shared prefix alone first,
  see [prompt-sharing.md §7](prompt-sharing.md)). If there is more than one row and `shared_len >= 512`
  (`WARM_MIN_PREFIX_TOKENS`), row 1 goes alone first, so its prefix is cached, then the
  rest go together and reuse it. Details and limits of that cache:
  [prompt-sharing.md](prompt-sharing.md); model-specific reasons:
  [model-architectures.md](model-architectures.md). The example's shared part is only 23
  tokens, so it is sent in one call.
- **Context-length refusals.** `decide.py` refuses before calling vLLM if the longest
  row is `>= max_model_len`; `readout.py` also maps a vLLM 400 "maximum context length"
  to the same 422 `RequestError`.

## 6. Softmax and temperature

The logprobs are of a full-vocabulary softmax, so those of the labels do not sum to 1.
[`calibration.py`](../../gateway/calibration.py) renormalises them over the shown options and
divides by a temperature `T`: `p_i = exp(lp_i / T) / sum_j exp(lp_j / T)`.

Illustrative logprobs `[-0.2, -2.1, -4.0]` for three options:

| T | Probabilities |
|---|---|
| 1.0 | 0.8533, 0.1276, 0.0191 |
| 1.943 | 0.6589, 0.2478, 0.0932 |

`T > 1` flattens an overconfident model. The temperatures live in
`data/<profile>/<layout>/calibration.json`, one per question type plus a noul yes-offset `b`,
and are valid only for that model, precision and layout (the file is stamped; stale ones are
refused). For qwen3.6 and `decider_chat` our fit is T = 1.648 / 1.927 / 1.386 for choice /
score / noul, b = 0. A missing file means `T = 1.0` and a warning. Fits and their
numbers: [calibration.md](calibration.md).

## 7. Answers: the Jev shapes

[`answers.py`](../../gateway/answers.py) receives probabilities in the caller's option order
and builds the answer. The formulas follow TypeSafe's open adapter
([../6-answer-compatibility.md](../6-answer-compatibility.md)). Numbers are rounded to 4
decimals. The values below come from the code, fed with illustrative logprobs and
T = 1.943:

| Type | Shape | Value in the example |
|---|---|---|
| choice | `choice`, `confidence`, `probabilities` | `billing`, confidence 0.4884, p = 0.6589 / 0.2478 / 0.0932 |
| score | `score`, `confidence`, `legend`, `probabilities` | 1.1669, confidence 0.3196 |
| noul | `noul` only (P(true), no confidence) | 0.7563 |

- **choice confidence:** `(p_max - 1/K) / (1 - 1/K)`: 0 for a uniform guess, 1 when certain.
  Here `(0.6589 - 1/3) / (2/3) = 0.4884`.
- **score:** `sum(i * p_i)`, the probability-weighted level, with a `legend` of the
  level descriptions. Its confidence is `1 - expected distance from the mode / the same
  for a uniform guess` (mode-distance based).
- **noul:** the probability of the second option (`yes`); `no` is the first, so
  `noul = p[1]`.
- **`usage`:** `{"input_tokens": Batch.input_tokens, "output_tokens": 0}`, the shared
  state counted once, as in §3.

## Caveats

- **Illustrative answers.** No live response is shown. Token ids, rows and the label table
  are real; the logprobs in §6 and §7 are made up to show the arithmetic.
- **Qwen3.6 ids.** Ids and the 229 two-letter labels are for the qwen3.6
  tokenizer; gemma and qwen3.8 tables differ (`data/<profile>/`).
- **In-context check is partial.** Only `A`..`J` are verified after the answer slot;
  labels beyond 10 are safe because their ids are spliced in, not encoded.
- **Temperature.** The examples use decider's 1.943; our own qwen3.6 fit is in
  [calibration.md](calibration.md).
- **Decider parity** is tested for the `decider_chat` layout; the other layouts
  (`header`, `question_first`) are our own experiments.

## Sources

- Our code: [`gateway/decide.py`](../../gateway/decide.py),
  [`questions.py`](../../gateway/questions.py), [`labels.py`](../../gateway/labels.py),
  [`prompts.py`](../../gateway/prompts.py), [`orders.py`](../../gateway/orders.py),
  [`readout.py`](../../gateway/readout.py), [`calibration.py`](../../gateway/calibration.py),
  [`answers.py`](../../gateway/answers.py), [`scripts/build_labels.py`](../../scripts/build_labels.py).
- Research docs: [../1-what-is-jev.md](../1-what-is-jev.md),
  [../4-inference-technique.md](../4-inference-technique.md),
  [../6-answer-compatibility.md](../6-answer-compatibility.md).
- Decider reference implementation: decider-ai 1.5.0 (`decider/systemone.py`, `decider/prompt.py`),
  as installed in `.cache/decider-venv`; used through the parity fixtures.
- TypeSafe confidence formulas: `typesafe-ai/system-one-adapter-python`, `confidence_metrics.py`
  (as cited in [CLAUDE.md](../../CLAUDE.md)).
