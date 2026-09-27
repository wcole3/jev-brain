# Do the open "Jev reproduction" servers return the same answers as Jev?

Audited 2026-09-26, from source code. The question: do the open inference servers return the same question
types, answer fields and meanings, and the same `confidence` as TypeSafe's Jev?

Source locations:
- Projects 1-5: cached files in `.firecrawl/infer/` (`<owner>_<repo>__<path>`). The key files were fetched again
  from `raw.githubusercontent.com/.../HEAD` on 2026-09-26. They were byte-identical to the cache: reflex
  readout/schema/server/stable.json, simple-jev response_scoring/hf_prompt_policies, decider systemone,
  openjev scoring and jevfire core. The copies are in `.firecrawl/schema-audit/recheck/`.
- Projects 6-12: full tarballs from codeload.github.com, unpacked under `.firecrawl/schema-audit/src/<owner>_<repo>/`.
  These are the HEAD commits:
  - litjev `e7fb109a`
  - jobe `0382f204`
  - snapjudge `80012ca2`
  - openvons `c2683c45`
  - snellingio/system-one `8ca10fd7`
  - jevmlx `7e0d7460`
  - daseinlabs/open-jev `6cb37c3c`

Evidence tags:
- **[SRC]**: I read the code.
- **[DOC]**: taken from a README or other docs only.
- **[UNK]**: unknown.

## Reference: Jev contract (official adapter `confidence_metrics.py`)

**Choice.** The answer is `{type, choice, probabilities{key:p}, confidence}`.
- The probabilities sum to 1.
- `confidence = (p_max − 1/K)/(1 − 1/K)`, called "chance-corrected max" below.

**Score.** The answer is `{type, score, legend{"0":desc..}, probabilities{"0":p..}, confidence}`.
- `score = Σ i·p_i`, a float.
- `confidence = max(0, 1 − Σ p_i·|i − mode| / MAD_uniform)`, where `MAD_uniform = mean_i |i − (n−1)/2|`.

**Noul.** The answer is `{type, noul}`.
- `noul` is P(true), a float. It is not a bool.
- There is no `confidence` and no `probabilities`.

**Envelope and limits.**
- The envelope is `{model, answers, usage{input_tokens, output_tokens}}`.
- Choice accepts up to 255 options. Score accepts 2-10 levels.
- Observed: Jev rounds probabilities to about 2 decimal places.

## Worked confidence example (same probabilities through every formula)

| distribution | Jev returns | chance-corrected max (Jev choice) | Jev score formula | p_max | 1 − normalised entropy | Gini concentration | margin p1−p2 |
|---|---|---|---|---|---|---|---|
| A choice {billing .88, technical .12, sales 0} | 0.81 | **0.820** | (0.820) | 0.880 | 0.666 | 0.683 | 0.760 |
| B choice {technical .85, sales 0, billing .15} | 0.78 | **0.775** | (0.550) | 0.850 | 0.615 | 0.618 | 0.700 |
| S score {0:.65, 1:.30, 2:.05} | - | 0.475 | **0.400** | 0.650 | 0.280 | 0.273 | 0.350 |
| S2 score5 {.1,.2,.4,.2,.1} | - | 0.250 | **0.333** | 0.400 | 0.086 | 0.075 | 0.200 |
| N noul p(true)=0.9 | none (no field) | 0.800 | - | 0.900 | 0.531 | 0.640 | 0.800 |

- Jev's 0.81 on distribution A matches the chance-corrected formula applied to its unrounded p_max, which is about 0.873.
- openjev-sglang's own docs example gives `confidence` 0.2799 for distribution S. That confirms its entropy formula.
- The script is at `.firecrawl/schema-audit/confidence_formulas.py`.
- These numbers hold the probabilities fixed. In practice the probabilities also differ between servers (different
  model, prompt, temperature and readout), so real gaps are usually larger.

---

## 1. Mapika/decider (`decider/systemone.py`, `decider/serve.py`, `decider/serve_vllm.py`)

**a. Types.** [SRC]
- choice, score and noul are supported, and `bool` is accepted as an alias for noul (`render_question`, systemone.py:40).
- Noul criteria are honoured. The options are rendered as `"no: <false desc>"` and `"yes: <true desc>"`.
- A noul question may omit `instructions`.
- Choice accepts 2..255 options (`MAX_CHOICE`). Score accepts 2..10 levels. A list is accepted as choice criteria.

**b. Choice.** [SRC]
- `choice` is the caller's key (`rq["names"][j]`).
- `probabilities` are keyed by the caller's keys, normalised, then rounded to 4 dp (`format_answer`, systemone.py:176).

**c. Score.** [SRC]
- `score = round(Σ i·p_i, 2)`, a float, as in Jev.
- `legend` is `{"0": desc, ...}` and `probabilities` are keyed `"0".."n-1"`.
- If the config sets `isolated_levels`, each level is scored as its own yes/no row, the results are renormalised,
  and two extra fields are added: `level_fit` and `fit_mass` (`assemble`, systemone.py:127). The default is False
  (serve.py `ISOLATED = False`).

**d. Noul.** [SRC]
- The answer is `{"type":"noul","noul": round(P(yes),4)}`, a float.
- There is no confidence field and no probabilities field.

**e. Confidence.** [SRC]
- On `/v1/systemone`, **Jev's exact formulas** are used, ported from the adapter:
  - `choice_confidence` (systemone.py:155) is `(n·p_max − 1)/(n − 1)`.
  - `score_confidence` (systemone.py:162) is the MAD formula.
  - This has been the case since v1.3.0 (CHANGELOG line 103).
- **Matches Jev**: 0.82, 0.775 and 0.40 on the worked examples.
- Extra fields `x_p_max` (p_max, which was `confidence` before 1.3.0) and `certainty` (1 − normalised entropy).
- The separate legacy `/decide` route still reports `confidence = p_max` (serve.py `_format_decide`).

**f. Calibration.** [SRC]
- The output is `softmax(logits/T)`.
- T comes from `decider_config.json`: `temperature` or `temperature_by_type`. Trained checkpoints ship fitted values.
- A stock checkpoint with no config uses T = 1.0 unless `DECIDER_TEMPERATURE` is set. The serve_vllm docstring
  example uses 1.943 for Qwen3.6-27B.

**g. Envelope.** [SRC]
- `model` is `"decider-<version>"` (or `"decider"`). The request's `model` is ignored.
- `usage` is `{input_tokens (shared prefix counted once), output_tokens: 0}`. The schema-cache path adds `cached_tokens`.
- Rounding: probabilities and confidence to 4 dp, score to 2 dp.
- Errors: 422 (validation), 413 (size), 503 (queue full).

## 2. featherless-ai/simple-jev (`common/response_scoring.py`, `hf-server/hf_server.py`, `hf_prompt_policies.py`)

**a. Types.** [SRC]
- choice (2..255 options), score (2..**50** levels; Jev allows 10) and noul (`request_schema.py`:92/107).
- Noul criteria are honoured. The baseline prompt includes a "Truth rubric"; the binary policies use the true/false
  descriptions as the yes/no options.

**b. Choice.** [SRC]
- `choice` is the argmax.
- `probabilities` are keyed by the caller's keys, as an unrounded float32 softmax (`_assemble`, response_scoring.py:230).

**c. Score.** [SRC]
- `score = p·[0..n-1]`, the mean, a float.
- `legend` is `{"0": desc}` and `probabilities` are keyed `"0".."n-1"`.

**d. Noul. The value depends on the prompt policy chosen at startup.** [SRC]
- **baseline** policy: the policy used for any unrecognised model architecture (`resolve_prompt_policy`).
  - The model rates on a 1..9 scale.
  - `noul = clip(0.01 + (E[rating]/10 − 0.1)·0.98/0.8, 0.01, 0.99)` (response_scoring.py:257-281).
  - This is a mapped expected rating clamped to [0.01, 0.99]. It is not a softmax P(true).
- **shared_examples_binary / shared_repeat_state** policies: these are auto-selected for the known Qwen3.5 4B/27B,
  Qwen MoE and Gemma 4 profiles.
  - The noul question is turned into a yes/no Choice.
  - `restore_binary_noul` then returns `{"type":"noul","noul": P(yes)}` (hf_prompt_policies.py:182).
- Either way, the public answer is `{type, noul}` with no confidence field.

**e. Confidence.** [SRC]
- `confidence = p_max` on both choice and score (`"confidence": float(p[winner])`). The docs say the same:
  API_REFERENCE:223/235 describe it as "Winning candidate's softmax probability".
- **Does not match Jev**: 0.88 and 0.85 against Jev's 0.81 and 0.78; 0.65 against Jev's 0.40 on score.

**f. Calibration.** [SRC]
- Raw softmax: "No temperature or other completion setting participates in v1 scoring".
- `calibrated: false`.

**g. Envelope.** [SRC]
- `model` echoes the request (checked against aliases).
- `usage` is `{input_tokens (unique prefix union), output_tokens (branch outputs, normally 0)}`.
- By default only `PUBLIC_FIELDS` are returned.
- `ENABLE_OPEN_JEV_ADVANCED_METRICS=1` adds `margin`, `ties`, `calibrated`, `scoring`, `variance`, `rating`,
  `metadata` and `metrics`.
- No rounding: full float32 values such as 0.8807970285.

## 3. kshetrajna12/reflex (`src/reflex/schema.py`, `readout.py`, `engine.py`, `server.py`)

**a. Types.** [SRC]
- choice (2..**26** options, `MAX_CHOICE_OPTIONS = 26`), score (2..10) and noul.
- Noul criteria are honoured (`prompt.py`:207-209, with defaults "The statement is true/false.").
- The schema is strict (`extra="forbid"`), plus one extension field, `permutations`.

**b. Choice.** [SRC]
- `probabilities` are keyed by `str(caller key)` and averaged over the permuted option orders (`merge_branches`).
- `choice` is the argmax.
- Rounded to 6 dp.

**c. Score.** [SRC]
- `score = Σ level·p`, a float rounded to 6 dp.
- `legend` is `{"0": text}` and `probabilities` are keyed `"0".."n-1"` (`to_answer`, readout.py:93).

**d. Noul.** [SRC] The answer is `NoulAnswer(noul=round(P(True),6))`, with no confidence.

**e. Confidence.** [SRC]
- `confidence = 1 − H(p)/ln n`, one minus normalised entropy (readout.py:61), on both choice and score.
- The docstring calls it "the default statistic".
- **Does not match Jev**: 0.666 and 0.615 on choice (Jev 0.81/0.78); 0.28 on score (Jev 0.40).

**f. Calibration.** [SRC]
- `Calibration()` defaults to T = 1.0 for every type. An optional fitted per-type T or a per-question "calibration
  head" can be loaded.
- `serving/stable.json` sets `calibration: null`, which means raw softmax.
- Option-order averaging: `--permutations` defaults to 1; `--stable` uses 2.

**g. Envelope.** [SRC]
- `model` is `engine.model_name`, which is `--served-name` or the HF id. It does not echo the request.
- `usage` adds `state_tokens`, `question_tokens`, `state_cache_hit` and `images`.
- Errors: 422, 502 (backend) and 529 (OOM).

## 4. ekzhang/openjev-sglang (`src/openjev/models.py`, `scoring.py`, `service.py`)

**a. Types.** [SRC]
- choice (2..**64** options), score (2..**64** levels) and noul. The limit comes from `MAX_ANSWERS = 64`.
- Noul criteria are honoured: `NoulCriteria` aliases `true`/`false` and renders them as option descriptions
  (prompts.py:51-55).
- `instructions` is optional for all types.

**b. Choice.** [SRC] `probabilities` are keyed by the caller's keys and sum to 1. `choice` is the argmax.

**c. Score.** [SRC]
- `score = fsum(i·p_i)`, a float.
- `legend` is `{"0": desc}` and `probabilities` are keyed `"0".."n-1"`.

**d. Noul.** [SRC] The answer is `NoulAnswer(noul=distribution["true"])`, a float, with no confidence.

**e. Confidence.** [SRC]
- `confidence = 1 − normalised entropy` (scoring.py:18). The docstring says "TypeSafe's exact statistic is not published".
- **Does not match Jev**: 0.666 and 0.615; 0.28 on score, which matches the project's own docs example of 0.2799.

**f. Calibration.** [SRC] `OPENJEV_TEMPERATURE` defaults to 1.0, which means raw softmax.

**g. Envelope.** [SRC]
- `model` echoes the request (the `jev-latest` alias is accepted).
- `usage.output_tokens = N + 1` (one warm-up token plus one per question). Jev-style clients may read this as billable output.
- No rounding.

## 5. kikoncuo/jevfire (`jevfire/models.py`, `core.py`, `app.py`): not Jev wire format

**Request.** `POST /v1/decisions` takes:
- `{context: str, schema: {name: {type: "boolean"|"enum", description, choices?: [str]}}, strategy, score_temperature, min_probability, cache_salt}`.
- `context` is a string only; no object or array state.
- Choices are a plain list with **no per-option descriptions**.
- There is **no score type** and no instructions/criteria structure.

**Response** (`classify`, core.py:267). The top level is:
- `{model, mode, strategy, requested_strategy, parsed_json{name: value}, fields{...}, scores_are_calibrated: false,
  abstained_fields, elapsed_ms, backend_requests, scored_fields, max_prompt_tokens, cache_block_tokens, usage{prompt_tokens, completion_tokens, total_tokens}}`.

Each field in `fields` is:
- `{value (True/False, the enum string, or None if abstained), selected_value, probability (= p_max), abstained,
  candidate_probability_mass, candidates[{value, label, probability, logprob}]}` (`decode_choice`, core.py:155).

How it differs from Jev: [SRC]
1. **Boolean fields return an actual bool** (the argmax of True vs False) plus `probability`, which is p_max of the
   winner, not P(true). To get P(true) you have to find it in `candidates`.
2. There is **no `confidence` field**. The closest thing is `probability` (p_max): 0.88 and 0.85 on the examples.
3. There is no score/ordinal type, no `legend`, and no expected value.
4. Probabilities are a list of `candidates`, not a map keyed by option.
5. There is an abstention mechanism: if `min_probability` is set and not met, `value` is null.
6. Usage uses OpenAI names (`prompt_tokens`, `completion_tokens`), not `input_tokens`/`output_tokens`.

Calibration: `score_temperature` is set per request, default 1.0, which means raw softmax.

## 6. zhengxuyu/litjev (`src/litjev/schema.py`, `decision.py`, `scoring.py`, `api.py`)

**a. Types.** [SRC]
- choice (**1**..255 options), score (2..10) and noul.
- Noul criteria (`true`/`false`) are honoured as candidate descriptions.
- Also serves `/v1/systemtwo`, which can escalate to thinking, and `/debug` variants of both routes.

**b. Choice.** [SRC] `probabilities` are keyed by the caller's keys and sum to 1. `choice` is the argmax.

**c. Score.** [SRC] `score = Σ int(k)·p`, a float. `legend` is `{"0": desc}` and `probabilities` are keyed `"0".."n-1"`.

**d. Noul.** [SRC] The answer is `NoulAnswer("noul", probabilities["true"])`, a float, with no confidence.

**e. Confidence.** [SRC]
- `concentration`, the normalised Gini: `(n·Σp² − 1)/(n − 1)` (decision.py:77, `CONFIDENCE_METHOD = "normalized_gini_concentration_v1"`).
- The docs call it "explicitly a LitJev approximation" (docs/jev-schema.md:29).
- If a trained decision head is loaded (`--decision-head`), `confidence` is instead the head's predicted
  P(fast answer correct) (`fast_confidence`, routing.py:37). After escalation it is P(slow answer correct).
- **Does not match Jev**: 0.683 and 0.618; 0.273 on score.

**f. Calibration.** [SRC] T = 1.0 unless a `--calibration` profile is given; the profile holds one fitted T for every type.

**g. Envelope.** [SRC]
- `model` is the loaded HF id. The request's `model` must be `"litjev"` or that id, otherwise 422.
- `usage.output_tokens` is 0, or the number of thinking tokens on systemtwo.
- No rounding.

## 7. MantisShrimpdev/jobe (`src/jobe/server.py`, `readout.py`, `slots.py`)

**a. Types.** [SRC]
- choice, score and noul, with a **16-option cap** (`LETTERS = "A".."P"`). Beyond that the server returns 422 unless
  it is started with `--wide`.
- Noul criteria are honoured (`options_for`, server.py:99).

**b. Choice.** [SRC] `probabilities` are keyed by the caller's keys and sum to 1 (`restricted_softmax`). `choice` is the argmax.

**c. Score. There is no `score` field and no `legend`.** [SRC]
- The answer is `{"type":"score","probabilities":{"0":..}, "confidence", "_meta"}` (server.py:214-215).
- A client that reads `answer["score"]` gets a KeyError.

**d. Noul.** [SRC]
- The answer is `{"type":"noul","noul": P("true")}` **plus `confidence`** (chance-corrected over 2 options, which is
  `|2p − 1|`) and `_meta`.
- Jev has no confidence field on noul.

**e. Confidence.** [SRC]
- The chance-corrected max `(p_max − 1/K)/(1 − 1/K)` (`Readout.confidence`, readout.py:71) is applied to every type.
- **Matches Jev for choice** (0.82 and 0.775).
- **Does not match for score**: 0.475 against Jev's 0.40. The noul confidence is extra.

**f. Calibration.** [SRC] Raw restricted softmax with no temperature. Order averaging exists but is off by default.

**g. Envelope.** [SRC]
- `model` is the backbone name.
- Each answer carries a `_meta` object: `{input_tokens, n_options, narrowed, ...}`.
- The top level adds `latency_s`.
- A single-option question returns a degenerate `{"type": <type>, "choice": id, "probabilities": {id: 1.0}, "confidence": 1.0}`,
  even when the type is score or noul.
- Errors: 400, 404, 422 and 500. No rounding.

## 8. Micha0827/snapjudge (`snapjudge/engine.py`, `prompts.py`, `server.py`), MLX

**a. Types.** [SRC]
- choice (2+ options, no maximum), score (2+ levels) and noul.
- Noul criteria are honoured ("yes means / no means").
- The model emits the option key text itself. It is scored over a multi-token prefix trie, not letter codes.

**b. Choice.** [SRC] `probabilities` are keyed by the caller's keys, rounded to 4 dp. `choice` is the argmax.

**c. Score.** [SRC]
- `score = Σ lvl·p`, a float rounded to 4 dp.
- `legend` is `{"0": str(desc)}`: a structured description becomes a Python `str()` repr, not JSON.
- `probabilities` are keyed `"0".."n-1"`.

**d. Noul.** [SRC] The answer is `{"type":"noul","noul": round(P(yes),4)}`, with no confidence.

**e. Confidence.** [SRC]
- `1 − normalised entropy` (`_confidence`, engine.py:421).
- The docstring claims it "matches the example in the TypeSafe quickstart". **It does not**: it gives 0.666 where
  Jev gives 0.81, and 0.615 where Jev gives 0.78.

**f. Calibration.** [SRC] Per-type T from the `SO_CALIBRATION` JSON if that is set, otherwise 1.0 (engine.py:390).

**g. Envelope.** [SRC]
- `model` is the local model directory name, plus the adapter name if one is loaded.
- `usage.output_tokens` is the number of scored rows, not 0.
- Extension fields `debug` and `layout`. Setting `debug: true` adds a `debug` block with raw_probabilities,
  coverage and timings.
- Errors: 401 and 422.

## 9. genai-craft/openvons (`openvons/lm/api/systemone.py`, `server.py`, `lm/backends/llm_backend.py`)

**a. Types.** [SRC]
- choice (no option cap on this route), score (2..10) and noul.
- Noul criteria are honoured as option descriptions.

**b. Choice.** [SRC]
- `probabilities` are keyed by the caller's keys. `choice` is the argmax.
- The probabilities come from the LLM backend (default mode `logprob`):
  - The backend reads vLLM `top_logprobs` over letter labels with guided choice and temperature 0.
  - A label missing from the top-k gets −inf, so its probability is **exactly 0**.
  - With more than 26 options it **switches to sampling**: 20 samples, so the probabilities are multiples of 0.05.
  - If no logprobs come back, the result is one-hot.

**c. Score.** [SRC] `score = Σ i·p`, a float. `legend` is `{"0": desc}` and `probabilities` are keyed `"0".."n-1"`.

**d. Noul.** [SRC] The answer is `{"type":"noul","noul": probs[0]}`, where `probs[0]` is P("true"). No confidence.

**e. Confidence.** [SRC]
- **The margin `p1 − p2`** (systemone.py:55). The source comment (in Japanese) says confidence is only defined
  as a concentration squashed to 0-1, so they chose the margin.
- **Does not match Jev**: 0.76 and 0.70; 0.35 on score.

**f. Calibration.** [SRC]
- By default the probabilities are a softmax over the vLLM label logprobs, with no temperature.
- If `DM_CKPT` is set, a trained openvons DecisionModel answers instead of the stock LLM.

**g. Envelope.** [SRC]
- `model` is `"open-jev/llm"` or `"open-jev/model"`. The request's `model` is ignored.
- **`usage.input_tokens = len(state)//3`**: a character-count estimate that also leaves out the questions (server.py:107).
- Errors: 422 and 529. No rounding.

## 10. snellingio/system-one (`server/src/system_one_lite/api.py`, `prompts.py`, `engine.py`), MLX

**a. Types.** [SRC]
- choice (1+ options, up to 578 single-token answer codes), score (2..10) and noul.
- Noul criteria are honoured ("yes — <true>", "no — <false>").

**b. Choice.** [SRC] `probabilities` are keyed by the caller's keys. `choice` is the argmax.

**c. Score.** [SRC] `score = Σ i·p`, a float. `legend` is `{"0": level}` and `probabilities` are keyed `"0".."n-1"`.

**d. Noul.** [SRC] The answer is `NoulAnswer(noul=probabilities[0])`, where index 0 is P(yes). No confidence.

**e. Confidence.** [SRC]
- The chance-corrected max `(p_max − 1/n)/(1 − 1/n)` (prompts.py:29) is applied to both choice **and score**.
- **Matches Jev for choice** (0.82 and 0.775).
- **Does not match for score**: 0.475 against Jev's 0.40; 0.25 against 0.333 on the 5-level example.

**f. Calibration.** [SRC] **A fixed temperature of 0.7** (engine.py:34), so every distribution is *sharpened*. It cannot be configured.

**g. Envelope.** [SRC]
- `model` is the HF id; the default is `mlx-community/Qwen3-1.7B-4bit`.
- `usage` is `{input_tokens, 0}`.
- Also served at `/evaluate`. Returns 503 when busy, because only one request runs at a time. No rounding.

## 11. bnsd55/jevmlx (`jevmlx/serve.py` `_systemone_to_schema` / `_format_systemone_response`, `engine.py`), MLX

This is the least compatible of the servers. [SRC, serve.py:300-420]

**a. Types.** choice becomes `enum`, noul becomes `boolean`, and score becomes an ordered `enum`.
- **Choice descriptions are dropped**: only `list(criteria.keys())` is passed.
- **Noul criteria are dropped**: only `instructions` is passed.
- **Score levels become the enum values themselves.** The model scores the *description text* as the label.

**b. Choice.**
- `probabilities` are built from `top_choices`, which the engine **truncates to the top 5** (engine.py:2160/3052 `[:5]`).
- With more than 5 options, `probabilities` is missing options and no longer sums to 1.

**c. Score.**
- `score = Σ i·p`, but only over the top-5 levels, so it is biased when there are more than 5 levels.
- `probabilities` are **keyed by the level description text**, not `"0".."n-1"`.
- Adds **`argmax_level`**, which is the description text.
- `legend` is `{"0": desc}`.
- **There is no `confidence` field on score.**

**d. Noul.** The answer is `{"type":"noul","noul": P("true"), "confidence": margin}`, an extra field.

**e. Confidence.**
- The margin `top1 − top2` (`_probability_margin`) on choice and noul.
- **Does not match Jev**: 0.76 and 0.70.

**f. Calibration.**
- The request's `temperature` (default 1.0) is applied to the "labels" scoring, which scores multi-token label phrases.
- The serve path passes no calibration bundle.

**g. Envelope.**
- **`usage` is `{prompt_tokens, computed_positions}`. There is no `input_tokens` or `output_tokens`.**
- `model` is the model id.
- Validation errors return **400**, not 422. Also 413, 429 and 503. No rounding.

## 12. daseinlabs/open-jev (`openjev/systemone.py`, `scorer.py`, `server.py`)

**a. Types.** [SRC]
- choice (2..255 options), score (2+ levels, no maximum) and noul.
- Noul criteria are honoured ("Answer yes when: ... / Answer no when: ...").

**b. Choice.** [SRC]
- `probabilities` are keyed by the caller's keys.
- **Each full option key is scored as a continuation**, using the sum of log-probs over its tokens (`norm="sum"`).
  Longer or multi-token keys are therefore penalised.

**c. Score.** [SRC] `score = Σ i·p`, a float. `legend` is `{"0": desc}` and `probabilities` are keyed `"0".."n-1"`.

**d. Noul.** [SRC] The answer is `NoulAnswer(noul=probs[0])`, where index 0 is P("yes"). No confidence.

**e. Confidence.** [SRC]
- `1 − normalised entropy` (systemone.py:150). The docstring calls it "an approximation".
- **Does not match Jev**: 0.666, 0.615 and 0.28.

**f. Calibration.** [SRC] Raw softmax over the summed sequence log-probs, with no temperature.

**g. Envelope.** [SRC]
- `model` echoes the request `model`, or else the basename of the model path.
- `usage.output_tokens` is the number of option tokens scored.
- A `ValueError` returns **400**. Pydantic validation errors return 422. Returns 503 while loading.

---

## Compatibility matrix

| # | project | choice | score semantics | noul semantics | confidence formula (choice / score) | matches Jev confidence? | other wire deviations | evidence |
|---|---|---|---|---|---|---|---|---|
| - | **Jev** | key + probs{key} | E[level] float, legend, probs{"0"..} | float P(true), no conf | chance-corrected max / MAD score formula | - | probs about 2 dp | adapter src |
| 1 | Mapika/decider | ✓ (≤255) | ✓ E[level] (2 dp) | ✓ float P(yes) | **Jev's formulas (ported)** | **Yes, both** | +`x_p_max`, +`certainty`; model ignores the request; 4 dp | SRC |
| 2 | featherless simple-jev | ✓ (≤255) | ✓ E[level] (≤50 levels) | ⚠ baseline: 9-bin mean mapped to [0.01, 0.99]; binary policies: P(yes) | p_max / p_max | No | unrounded float32 | SRC |
| 3 | reflex | ✓ but ≤26 options | ✓ E[level] | ✓ float P(true) | 1 − normalised entropy / same | No | usage extras; 6 dp | SRC |
| 4 | openjev-sglang | ✓ ≤64 | ✓ E[level] (≤64) | ✓ float P(true) | 1 − normalised entropy / same | No | output_tokens = N+1 | SRC |
| 5 | jevfire | ✗ different API (`/v1/decisions`, enum list, no descriptions) | ✗ none | ✗ **bool value** + p_max | none (`probability` = p_max) | No | whole envelope differs | SRC |
| 6 | litjev | ✓ (1..255) | ✓ E[level] | ✓ float P(true) | normalised Gini / same (or a trained head) | No | model must be "litjev" or the id | SRC |
| 7 | jobe | ✓ ≤16 | ✗ **no `score`, no `legend`** (probabilities only) | ⚠ float P(true) **+ confidence** | chance-corrected max / same | Choice yes; score no | +`_meta`, +`latency_s` | SRC |
| 8 | snapjudge | ✓ | ✓ E[level] | ✓ float P(yes) | 1 − normalised entropy / same | No (despite its claim) | output_tokens = rows; 4 dp | SRC |
| 9 | openvons | ✓ (sampling above 26 options) | ✓ E[level] | ✓ float P(true) | margin p1−p2 / same | No | usage = chars/3; model "open-jev/llm" | SRC |
| 10 | snellingio/system-one | ✓ | ✓ E[level] | ✓ float P(yes) | chance-corrected max / same | Choice yes; score no | **fixed T = 0.7** | SRC |
| 11 | jevmlx | ⚠ descriptions dropped; probs top-5 only | ⚠ probs keyed by level text; +argmax_level; **no confidence** | ⚠ criteria dropped; float + confidence | margin / (none) | No | usage {prompt_tokens, computed_positions}; 400 errors | SRC |
| 12 | daseinlabs/open-jev | ✓ (full-key sequence scoring) | ✓ E[level] | ✓ float P(yes) | 1 − normalised entropy / same | No | 400 on ValueError | SRC |

## Key takeaways for a combined server

1. **Only decider reproduces Jev's `confidence`.**
   - It has used Jev's chance-corrected choice formula and MAD score formula since v1.3.0.
   - jobe and snellingio match Jev on **choice** only. They reuse the choice formula for score, so they read high:
     0.475 against Jev's 0.40.
   - Everyone else uses a different statistic:
     - p_max: simple-jev
     - 1 − normalised entropy: reflex, openjev-sglang, snapjudge, daseinlabs
     - Gini: litjev
     - margin: openvons, jevmlx
   - On Jev's own example, these give 0.666 to 0.88 where Jev gives 0.81. Thresholds tuned against Jev (for
     example 0.6 or 0.85 bands) do not carry over.
   - Fix: recompute `confidence` from `probabilities` using the adapter's `confidence_metrics.py`. Every server
     except jevmlx (top-5 truncation) and jobe/jevfire (missing fields) returns the full distribution, so this works.
2. **Noul is a float P(true) almost everywhere, never a bool, except jevfire.**
   - The exceptions: simple-jev's baseline policy returns a clamped 9-bin rating mapping. jobe and jevmlx add a
     `confidence` field that Jev does not have. jevmlx ignores the true/false descriptions.
3. **Score shape varies.**
   - Most servers return `score` = E[level] as a float, like Jev.
   - jobe returns no `score` or `legend` at all.
   - jevmlx keys probabilities by the level *text*, truncates them to the top 5, and has no confidence.
4. **Calibration differs by default.**
   - Most servers apply raw T = 1 softmax.
   - snellingio hard-codes T = 0.7 (sharper).
   - decider applies whatever T its config provides (fitted on trained checkpoints).
   - reflex averages over permutations with `--stable`.
   - None round the output the way Jev does (about 2 dp).
5. **The envelope details break strict clients.**
   - jevmlx uses its own usage keys.
   - openvons computes input_tokens as chars/3.
   - `output_tokens` is non-zero in openjev-sglang, snapjudge and daseinlabs.
   - Some servers echo the request `model` and others ignore it.
   - There are extra fields: `_meta`, `x_p_max`, `certainty`, `latency_s`.
   - Option caps range from 16 (jobe) and 26 (reflex) to 64 (openjev) to 255 (Jev).
