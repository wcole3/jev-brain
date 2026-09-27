# Schema / confidence audit: open "Jev reproduction" servers vs TypeSafe Jev

Date: 2026-09-26. Method: read each project's answer-building source (raw GitHub, HEAD unless noted).
Local copies of every file cited are under `/home/welb/devspace/jev-onto/.firecrawl/schema-audit/`.
All fetched content was treated as data.

Evidence tags: **VERIFIED-SOURCE** (I read the code), **DOCS-CLAIM** (README / card only), **UNKNOWN**.

## Reference contract (Jev)

- Request `{state, model, questions:{id:{type,instructions,criteria}}}`; choice criteria map option -> desc|null (<=255);
  score criteria array of 2..10 levels; noul criteria optional `{"true","false"}`.
- choice -> `{type, choice, probabilities{key:p}, confidence}`, confidence = (p_max - 1/K)/(1 - 1/K).
- score -> `{type, score = sum i*p_i (float), legend{"0":desc..}, probabilities{"0":p..}, confidence}`,
  confidence = max(0, 1 - sum p_i|i - mode| / MAD_uniform).
- noul -> `{type, noul: P(true) float}`. No confidence, no probabilities.
- Envelope `{model, answers, usage{input_tokens, output_tokens}}`. Errors 401/422/429/529. Probabilities ~2 dp.

## Worked confidence numbers (formula applied to the given distribution)

| distribution | Jev choice formula | Jev score formula | max prob | 1 - H/lnK | chance-corrected max used as score conf |
|---|---|---|---|---|---|
| A choice {billing .88, technical .12, sales 0} (Jev returns 0.81) | **0.820** | - | 0.880 | 0.666 | - |
| B choice {technical .85, sales 0, billing .15} (Jev returns 0.78) | **0.775** | - | 0.850 | 0.615 | - |
| S score 5 levels [0, 0, .1, .3, .6] (score 3.5) | - | **0.583** | 0.600 | 0.442 | 0.500 |
| S2 score 5 levels [.05, .1, .6, .2, .05] (score 2.1) | - | **0.583** | 0.600 | 0.280 | 0.500 |

(Jev's 0.81 vs formula 0.82 on A comes from Jev computing on unrounded probabilities and then rounding the displayed ones.
For a 3-level score whose mode is the middle level, the Jev score formula and the chance-corrected max give the same
value, so S/S2 use 5 levels to separate them.)

---

## 1. invergent-ai/surogate: `/v1/decisions` (Surogate Rune 26B-A4B v3)

Files: `csrc/src/serve/serve/decisions_schema.cpp`, `decisions_schema.h`, `http_server.cpp`, `serve_options.cpp`
(local: `schema-audit/surogate_*`).

- a. Types: choice / noul / score (`parse_question`, cpp:259-341). **Noul criteria is REQUIRED** and must be exactly
  `{"true","false"}` (cpp:303-307: "criteria must be an object with exactly the keys true and false"). Jev makes it
  optional, so a bare noul that Jev accepts gets a **400** here. Choice option values must be non-null (`require_text_value`,
  cpp:231-235). Jev allows `null` descriptions, so `{"a": null}` is rejected. Score levels go from 2 up to **255**
  (`kDecisionMaxOptions` applies to every type, h:91-92). Jev caps score at 10. VERIFIED-SOURCE.
- b. Choice: `choice = option_keys[first_argmax]`, `probabilities` keyed by the caller's keys, a softmax over the candidate
  label logits only, so it sums to 1 (`resolve_decision_answer`, cpp:647-667; `decision_probabilities`, cpp:617-637).
  VERIFIED-SOURCE.
- c. Score: `score = sum i*p_i` (float, expected level), `legend` = caller's level values keyed "0".."n-1", `probabilities`
  keyed "0".."n-1" (cpp:673-686). VERIFIED-SOURCE.
- d. Noul: `noul = probabilities[1]` with key order `false,true` = P(true), float, with no confidence and no probabilities
  (cpp:309, 668-670). VERIFIED-SOURCE.
- e. Confidence: `decision_choice_confidence` = (max - 1/K)/(1 - 1/K), and `decision_score_confidence` =
  max(0, 1 - sum p_i|i-mode|/uniform_MAD) (cpp:594-615). The header says these are "TypeSafe's confidence metrics: its
  published formulas" (h:190-195). **Exact Jev formulas**, giving A=0.82 and B=0.775. VERIFIED-SOURCE.
- f. Temperature: `--decision-temperature T`, **default 1.0 = raw softmax** (h:200 `kDecisionDefaultTemperature = 1.0`).
  The Rune card *recommends* `--decision-temperature 2` because v3 is overconfident at T=1 (DOCS-CLAIM, HF card lines
  74-83), but the server does not apply it unless you pass the flag. VERIFIED-SOURCE (default) / DOCS-CLAIM (recommendation).
- g. Envelope (http_server.cpp:1428-1443): `{id, model (echo of request), provider:"surogate", answers, usage{input_tokens,
  output_tokens, [reasoning_tokens if thinking], cost:0}}`. The extras are `id`, `provider`, `usage.cost` and
  `usage.reasoning_tokens`. Nothing is rounded (full doubles). Path is **`/v1/decisions`**, with aliases `/api/alpha/decisions` and
  `/api/v1/decisions` (http_server.cpp:450-457); there is **no `/v1/systemone`**. Bad requests return **400**
  `invalid_decisions_request`, not 422, and engine faults return 500 (cpp `classify_decisions_fault`). Optional `thinking:true`
  re-asks questions whose one-pass top prob is below 0.7. Their answers still go through `resolve_decision_answer`
  (decisions_thinking.h:35-39, 106). VERIFIED-SOURCE.
- Doc nit: the example in `docs/inference/decisions.md` has score confidence 0.62 for probabilities {.03,.23,.74}. The code
  formula gives 0.565 there. The choice example (0.93 for .95 of 3) matches.
- **Verdict: same answer types, fields and confidence semantics as Jev.** The differences are the endpoint path, 400
  instead of 422, required noul criteria, null choice descriptions rejected, and score levels allowed above 10.

## 2. EldanRing/winnow-inference: `/v1/systemone` (Winnow-12B, patched llama.cpp)

Files: `native/protocol.h` (`compile`, `answer`), `native/bridge.cpp`, `native/engine.h`, `patches/llama-winnow-server.patch`
(local: `schema-audit/winnow/`).

- a. choice / noul / score (protocol.h:87-131). Noul criteria is optional and honoured: each side is rendered as
  `true: desc` / `false: desc` (protocol.h:87-102). Null choice/score descriptions are allowed. Options run **2..64**
  (labels capped at 64, engine.h:295-300; protocol.h:132-133 "Questions require 2-64 alternatives"). That is under Jev's
  255 for choice, and score is not capped at 10. VERIFIED-SOURCE.
- b. Choice: `choice = keys[argmax]`, `probabilities` keyed by the caller's keys, softmax over candidate logits, sums to 1
  (protocol.h:143-177). VERIFIED-SOURCE.
- c. Score: `score = sum i*p_i` float, `legend` keyed "0".. with the raw criterion value, probabilities keyed "0"..
  (protocol.h:118-123, 156-176). VERIFIED-SOURCE.
- d. Noul: `noul = p[1]` with keys `{false,true}` = P(true), and no confidence or probabilities (protocol.h:166-167).
  VERIFIED-SOURCE.
- e. Confidence (choice and score): **`clamp(1 - entropy/ln K, 0, 1)`** (protocol.h:170). The diagnostics label calls it
  `"confidence_method": "normalized_inverse_entropy"` (protocol.h:182), and docs/API.md:51 says the same. This is **not Jev's formula**
  and gives A=0.666 and B=0.615. The score answer uses the same entropy formula, not Jev's MAD formula (S=0.442).
  VERIFIED-SOURCE.
- f. Temperature from a request extension `winnow.temperature`, **default 1 (raw)** (protocol.h:49-51). VERIFIED-SOURCE.
- g. Envelope `{model: <server model name>, answers, usage{input_tokens = prefix+suffix tokens, output_tokens: 0}}`,
  plus a `winnow` diagnostics block when `winnow.diagnostics` is set (bridge.cpp:142-161). Values are not rounded. Request
  `model` must be the configured name, `Winnow-12B` or `jev-latest`. Errors come back as **400** `invalid_request_error`
  (bridge.cpp:163-170), not 422. `/v1/winnow/inspect` is an extra route. VERIFIED-SOURCE.
- **Verdict: shapes match Jev, confidence does not (entropy-based on both choice and score).**

## 3. razorback16/openjev: `/v1/systemone` (DiffusionGemma 26B-A4B NVFP4 on vLLM; also CLM/JevK5/Laya/Verdict backends)

Files: `openjev/engine.py` (`build_schema`, `slot_distribution`, `confidence`, `to_answer`, `read_group`),
`openjev/api.py`, `openjev/encoders.py` (local: `schema-audit/openjev/`).

- a. choice / noul / score (engine.py:109-151). Noul criteria is optional and honoured (labels yes/no with the true/false
  descriptions, engine.py:118-121, 159-160). Choice allows up to 255 options (`MAX_CHOICES = 255`) and null descriptions.
  Score allows 1..10 levels (`len(crit) > 10` -> 422). A 1-option choice and a 1-level score are answered as "forced" with
  confidence 1.0. VERIFIED-SOURCE.
- b. Choice: `choice = key of argmax`, `probabilities` keyed by the caller's keys. It is a softmax over exact label logprobs
  (`logprob_token_ids`), sums to 1, and is **averaged over re-reads** (engine.py:341-357, 421-448). VERIFIED-SOURCE.
- c. Score: `score = sum i*p_i` float, `legend` "0".. -> caller level, probabilities "0".. (engine.py:449-451). VERIFIED-SOURCE.
- d. Noul: `noul = p[0]` where label 0 = "yes" = P(true), float, with no confidence (engine.py:443-444). VERIFIED-SOURCE.
- e. Confidence: **`1 - H(p)/ln K`**, clamped to [0,1] (engine.py:434-438, "How peaked a distribution is"). It is used for
  choice and score by every backend (encoders.py imports the same `to_answer`, encoders.py:45, 157). The README states it too
  (README:84). Not Jev's formula: A=0.666, B=0.615, S=0.442. VERIFIED-SOURCE.
- f. The DiffusionGemma backend uses **raw** T=1 logprobs ("Read-only logprobs are at temperature 1", engine.py:422). An
  automatic policy re-reads up to 4 times (`OPENJEV_AUTO_MAX=4`) with fresh noise when the first-read entropy is above 0.1, and
  averages the reads (config.py:32-33, engine.py:352-357). The encoder backends (JevK5, Verdict) carry their own calibration
  temperatures (config.py:53; encoders.py:15-27). VERIFIED-SOURCE.
- g. Envelope `{model: model_version, answers, usage{input_tokens, output_tokens: thought tokens (0 unless think)}}`
  (api.py:273-275). Values are not rounded. Extra request fields: `images`, `steps`, `samples`, `think`, `sequential`.
  Status codes: unknown model -> **400** `api_usage_error`, schema -> 422, overloaded -> 529, backend down -> 503. VERIFIED-SOURCE.
- **Verdict: shapes match Jev, confidence does not (entropy). Probabilities can be multi-read averages.**

## 4. vLLM example `examples/features/structured_diffusion/structured_server.py` (vllm-project/vllm main)

Local: `schema-audit/vllm/structured_server.py`.

- a. choice / noul / score (`jev_schema`, :1071-1117; `parse_schema`, :128-200). Noul criteria is optional and honoured
  (:149-153). **At most 26 alternatives** per question (:173-174). Score is not capped at 10. Extensions: `depends_on`,
  `ask_if`, `alone`. A question skipped by `ask_if` comes back as **`null`** in `answers` (:1169-1171). VERIFIED-SOURCE.
- b. Choice: `choice = name of argmax of mean`, `probabilities` keyed by the caller's option names, mean over reads of a
  label softmax (:990-1003, `slot_distribution` :578-593). VERIFIED-SOURCE.
- c. Score: `jev_answer` recomputes `score = sum i*p_i` 0-based (internally it is `(i+1)`-based, :1005, and the Jev wrapper
  fixes this, :1182-1185). Probabilities are keyed "0"... **`legend` values are `str(level)`**, the Python `str()` of each criterion
  (:164, 1186), so an object or array level shows up as a Python repr instead of the JSON value. VERIFIED-SOURCE.
- d. Noul: `noul = mean[0]` ("yes") = P(true), float, with no confidence (:1001, 1172-1173). VERIFIED-SOURCE.
- e. Confidence: **`mean[top]` = the maximum probability** for both choice and score (:997; passed through at :1179, 1188).
  Not Jev's formula: A=0.88, B=0.85, S=0.60. VERIFIED-SOURCE.
- f. Raw T=1 logprobs ("Read-only logprobs are at temperature 1", :580-581). Default policy is auto re-read (up to 4 when
  entropy > 0.1), then averaged (:218-221, 957-981). VERIFIED-SOURCE.
- g. Envelope `{model: --model arg, answers, usage{input_tokens, output_tokens}, diagnostics{...}}`. **`diagnostics` is always
  present** (:1350-1365). Values are not rounded. Schema errors return 422 `validation_error`. VERIFIED-SOURCE.
- **Verdict: shapes largely match. Confidence = max prob; 26-option cap; `legend` stringified; null answers possible.**

## 5. Davipar/djev-dev: `/v1/request` (DiffusionGemma on vLLM)

Files: `djev/contracts.py` (`answer_from_probabilities`, `_entropy_concentration`), `djev/engine.py`, `djev/app.py`
(local: `schema-audit/djev/`).

- a. choice / noul / score (contracts.py:35-57). Noul criteria is optional and honoured (engine.py:268). Choice takes
  1..255 options, score 2..10 levels, null descriptions allowed. VERIFIED-SOURCE.
- b. Choice: `choice = argmax key`, `probabilities` keyed by the caller's keys, validated to sum to 1. They are exact label
  logprobs renormalised (`normalize_logprobs`, engine.py:~423), averaged over `options.samples` reads (default 1)
  (contracts.py:244-262; engine.py:698-706). VERIFIED-SOURCE.
- c. Score: `score = fsum(i*p_i)` float, `legend` "0".. -> caller level, probabilities "0".. (contracts.py:264-271). With the
  opt-in `score_mode: independent_levels`, the distribution comes from per-level yes/no odds (`truth-odds-v1`,
  engine.py:575-596). VERIFIED-SOURCE.
- d. Noul: `noul = values[1]` of [false,true] = P(true), float, with no confidence (contracts.py:250-252). VERIFIED-SOURCE.
- e. Confidence: **`1 - H/ln K`** (`_entropy_concentration`, contracts.py:237-241). The module docstring says "Confidence
  is normalized entropy concentration, not empirical calibration." A=0.666, B=0.615, S=0.442. VERIFIED-SOURCE.
- f. Raw: request `temperature: 1.0`, `top_k: -1` to vLLM (engine.py:346-356). No calibration. Diagnostics say
  `"calibration": "unvalidated"`. VERIFIED-SOURCE.
- g. Envelope `{model: "djev-0.1" (hard-coded; ignores the request model), answers, usage{input_tokens, output_tokens =
  vLLM completion tokens}}`, plus `diagnostics` if `options.diagnostics` (engine.py:601-610, 668-676, 715-717). Path is **`/v1/request`**,
  not `/v1/systemone`. Extra request fields: `options{samples,steps,diagnostics,seed,isolation,score_mode}` and `images` (max 1).
  Status codes: 422 validation, capacity **503** (not 529), 502 backend, 504 timeout, 401, 413, 415 (app.py:111-166).
  VERIFIED-SOURCE.
- **Verdict: shapes match. Confidence is entropy-based. Different path. Model name fixed.**

## 6. JoshuaSP/open-jev: research harness (DiffusionGemma, Modal)

Files: `inference.py` (`prepare`, `DiffusionHarness.predict`), `parallel_canvas.py` (`decode`), `constraints.py`,
`public_eval_benchmark.py`, `modal_app.py` (local: `schema-audit/openjev_jsp/`).

- **Not a Jev-API server.** Its input format is `{document, questions:{key:{question, options:[str|int|bool...]}}}`
  (inference.py:8-30). Output is `{answers:[{key: value}], steps, seed, request_seconds, input_tokens, ...}`: one **decoded
  hard value per field** from constrained diffusion (inference.py:120-133; parallel_canvas.py:105-113). VERIFIED-SOURCE.
- Mapping of Jev types in the public-eval runner (public_eval_benchmark.py:44-52): noul -> options `[False, True]`, so
  the answer is a **JSON boolean**. Score -> options `[0..n-1]`, so the answer is an **integer level (argmax/decoded)**, not an
  expected value. Choice -> key string. VERIFIED-SOURCE.
- **No `probabilities`, no `confidence`** on the harness output. The only probabilities are
  `uncalibrated_choice_probabilities` in a Modal smoke test (modal_app.py:227-229). The README says restricted-softmax scores
  are "uncalibrated" (README:126). VERIFIED-SOURCE.
- **Verdict: different answer types (bool/int/str values), no confidence, no Jev envelope.**

## 7. getainode/jebadiah: `jebadiah-serve` `/v1/systemone` (Jebadiah 27B)

Files: `server/src/jebadiah_server/app.py` (`systemone`, `decision_entry`), `ainode_routes.py` (`answer_from_decision`,
`normalized_confidence`, `read_temperatures`), `model_scripts/ainode_prompt_verbatim.py` (`translate_one`, `noul_options`,
`score_options`, `choice_options`), `model_scripts/jebadiah_model.py` (local: `schema-audit/jebadiah/`).

- a. choice / noul / score. Noul criteria is optional, may describe one side, and is honoured (verbatim.py:196-220).
  **Choice is capped at 20 options** (`MAX_CRITERIA = TOP_LOGPROBS = 20`, verbatim.py:31,123,186-191). More than that is
  refused with 422. Score takes 2..10 levels as **non-empty strings only** (object/array levels are rejected, verbatim.py:231-237).
  An object-form score criteria `{level: desc}` is also accepted. `instructions` must be a non-empty string (verbatim.py:271-273),
  whereas Jev accepts object/array. VERIFIED-SOURCE.
- b. Choice: `choice = caller key`, `probabilities` keyed by the caller's keys, **rounded to 6 dp**, softmax over candidate
  logits after temperature (app.py:73-86; ainode_routes.py:262-296; jebadiah_model.py:116-117). VERIFIED-SOURCE.
- c. Score: `score = round(sum i*p_i, 6)` float, `legend` "0".. -> level name, probabilities "0".. (ainode_routes.py:279-291).
  VERIFIED-SOURCE.
- d. Noul: `noul = P(true)` float, with no confidence (ainode_routes.py:273-277). VERIFIED-SOURCE.
- e. Confidence: `normalized_confidence(p_picked, n) = (n*p_max - 1)/(n - 1)` (ainode_routes.py:225-243), which is
  **algebraically identical to Jev's choice formula** (A=0.82, B=0.775). **The same formula is used for score**
  (ainode_routes.py:270-271, 290), **not Jev's MAD-based score confidence**: S=0.50 vs Jev 0.583. The docstring says it was
  "INFERRED, not specified". VERIFIED-SOURCE.
- f. **Temperature-scaled by default.** `temperatures.json` in the model dir is applied per type unless the body sends
  `"calibration": "raw"` (app.py:156-161; ainode_routes.py:147-185; jebadiah_model.py:116). For jebadiah-27b the fetched file
  holds **choice 1.2321, noul 1.297, score 0.7558** (HF `temperatures.json`, refit 2026-09-26). VERIFIED-SOURCE + fetched file.
- g. Envelope `{model, answers, usage{input_tokens, output_tokens = number of answers}, latency_ms, calibration{applied,
  temperatures}}` (app.py:213-218). The extras are `latency_ms` and `calibration`. Rounded to 6 dp. Status codes: 422 bad request,
  503 model failure. `/v1/decide` is an AINode-shaped extra route. VERIFIED-SOURCE.
- **Verdict: choice confidence equals Jev's; score confidence does not. 20-option cap. Calibrated by default.**

## 8. denis-pplx/autojev: `autojev-serve` `/v1/systemone` (AutoJev-27B)

Files: `src/autojev/server.py` (`EvaluationRequest`, `predict`, `system_one`), `src/autojev/model.py` (`options`, `answer`)
(local: `schema-audit/autojev/`; identical to the cached `trained/autojev/`).

- a. choice / noul / score (server.py:55-68). Noul criteria is optional (`dict[Literal["true","false"], Content|None]`) and
  honoured (model.py:55-56). Choice takes 1..255 options with null allowed, score 2..10 levels. VERIFIED-SOURCE.
- b. Choice: `choice = keys[argmax]`, `probabilities` keyed by the caller's keys, renormalised to sum 1 (model.py:76-92).
  VERIFIED-SOURCE.
- c. Score: `score = sum i*p_i` float, `legend` "0".. -> caller level, probabilities "0".. (model.py:53-54, 93-100).
  VERIFIED-SOURCE.
- d. Noul: `noul = values[1]` with keys [false,true] = P(true), with no confidence (model.py:85-86). VERIFIED-SOURCE.
- e. Confidence: choice `(p_max - 1/K)/(1 - 1/K)` clamped to [0,1]. Score `max(0, 1 - sum p_i|i-best|/baseline)`
  with baseline = uniform MAD (model.py:90-100). **Exact Jev formulas** (A=0.82, B=0.775, S=0.583). VERIFIED-SOURCE.
- f. **Temperature-scaled by default.** `softmax(logits / model.temperature)` (server.py:187), with the temperature loaded from
  `decision_config.json`, **T = 2.2076** in the published checkpoint (model.py:175; cached decision_config.json). VERIFIED-SOURCE.
- g. Envelope `{model: service.name, answers, usage{input_tokens, output_tokens: 0}}` (server.py:191). Values are not rounded.
  Request `model` must be the service name or `jev-latest`. Extra request field: `images` (max 4). Status codes: 422 validation,
  503 not ready, **529 when another request is in flight** (non-blocking lock, server.py:199-200). VERIFIED-SOURCE.
- **Verdict: same types, fields and confidence formulas as Jev. Probabilities are temperature-calibrated (T~2.21).**

## 9. jaredpalmer/kev: `kev.serve` `/v1/systemone` (Kev 0.8B/4B/9B/27B, pointer head)

Files: `kev/api.py` (`to_record`, `choice_confidence`, `score_confidence`, `round_prob`, `to_answers`), `kev/serve.py`
(`_body`), `kev/model.py` (head temperature) (local: `schema-audit/kev/`).

- a. choice / noul / score (api.py:17-46). Noul criteria is optional and honoured (api.py:108-110). Choice takes 1..255 options,
  **score takes 1..255 levels** (Jev 2..10). Null descriptions are allowed. `model` defaults to `kev-latest`. VERIFIED-SOURCE.
- b. Choice: `choice = keys[argmax]`, `probabilities` keyed by the caller's keys, **rounded to 4 dp** (api.py:154-156, 143-146).
  VERIFIED-SOURCE.
- c. Score: `score = round(sum i*p_i, 4)`, probabilities "0".. rounded. `legend` "0".. -> **rendered text** of each level:
  `render()` flattens object levels to text, so an object level becomes a string (api.py:111-115, 157-159). VERIFIED-SOURCE.
- d. Noul: `noul = round(p[1], 4)` = P(true), with no confidence (api.py:152-153). VERIFIED-SOURCE.
- e. Confidence: `choice_confidence` = (max - 1/K)/(1 - 1/K). `score_confidence` = max(0, 1 - E|level - mode|/D), with D the
  uniform MAD. The comment says both "mirror TypeSafe's reference adapter, system-one-adapter 0.2.1 ... confidence_metrics.py"
  (api.py:120-140). **Exact Jev formulas**, rounded to 4 dp (A=0.82, B=0.775, S=0.5833). VERIFIED-SOURCE.
- f. **Temperature-scaled by default.** The head divides logits by `head.temperature` in eval mode (model.py:188-200). The
  checkpoint's head.pt carries **T = 2.30** for kev-9b (DOCS-CLAIM: HF card line 77). `KEV_TEMPERATURE=1.0` gives raw logits.
  VERIFIED-SOURCE (mechanism) / DOCS-CLAIM (value).
- g. Envelope `{model: request model echo, answers, usage{input_tokens, output_tokens = tokens of serialised answers},
  latency_ms}` (serve.py:183-185). The extra is `latency_ms`. Extra routes: `/v1/systemone/permute` and `/v1/systemone/separate`.
  Optional `date_facts` state preprocessing (serve.py:188-190). VERIFIED-SOURCE.
- **Verdict: same types, fields and confidence formulas as Jev (4-dp rounding). Calibrated by default (T=2.30).**

## 10. bespokelabsai/nimble: `ParallelScorer` and Modal/SGLang server

Files: `nimble/scoring/parallel_scorer.py` (`score`), `nimble/scoring/calibration.py`, `nimble/serving/server.py`,
`nimble/serving/compiler.py`, `deploy/modal_app.py`. The served answer shaping comes from the pinned dependency
`ekzhang/openjev-sglang@7f84bedc` `src/openjev/scoring.py` (local: `schema-audit/nimble/`, `schema-audit/sglang/`).

- **`ParallelScorer.score()` (library, MLX)** returns `{model, revision, backend, temperature, temperature_fitted, context,
  output{name: value}, fields{name:{value, scores{key:p}, logits, candidate_token_ids, code_to_choice}}, metrics}`
  (parallel_scorer.py:172-193). This is **not Jev-shaped**: the value is a hard argmax, noul is modelled as `choices=[False, True]`
  and so comes back as a **Python bool**, and there is **no confidence**. VERIFIED-SOURCE.
- **A server does exist.** `nimble/serving/server.py` mounts openjev-sglang's `create_app`, which gives `/v1/systemone` with
  the Nimble prompt compiler, SGLang backend and Modal deploy (server.py:15-49; modal_app.py:63-67). Through it:
  - a. choice / noul / score. Noul criteria is honoured (compiler.py:22-25). **26 candidates max** (server description
    "26 candidates"). VERIFIED-SOURCE.
  - b/c/d. `openjev.scoring.answer`: choice = argmax key with probabilities keyed by the caller's keys. Score = sum i*p_i
    with `legend` "0".. and probabilities "0"... Noul = `distribution["true"]` float with no confidence (sglang/scoring.py:25-40).
    VERIFIED-SOURCE.
  - e. Confidence: **`1 - H/ln K`**. The docstring says "Normalized negative entropy; TypeSafe's exact statistic is not
    published" (sglang/scoring.py:18-21). The server description says "Confidence is entropy concentration, not calibrated
    accuracy" (server.py:39-40). A=0.666, B=0.615. VERIFIED-SOURCE.
  - f. Temperature: `served_temperature(READY.json)`. It is **2.179** for the original v1 revision and for v2, and **1.0 for the
    latest Bespoke-Nimble-9B release** (`latest-12026-unfitted`) (calibration.py:5-63; README:27 "Its default is T=1.0").
    VERIFIED-SOURCE.
  - g. openjev-sglang envelope `{model, answers, usage}`. I did not check it field by field (UNKNOWN beyond that).
- **Verdict: the library output is not Jev-shaped (bool/str values, `scores`, no confidence). The server output is Jev-shaped
  with entropy confidence.**

## 11. togethercomputer/tev1: Tev1-4B-experimental

Files: `examples/decide.py`, `examples/*.json` (local: `schema-audit/tev1/`).

- **No `/v1/systemone` wrapper** anywhere in the repo tree (71 files, no server module). Inference goes through Together's
  OpenAI `/v1/chat/completions` with a regex-constrained letter (`(A|B|...)`), `temperature 0`, `top_logprobs 5`
  (decide.py:14-41). VERIFIED-SOURCE.
- Output of the example: `{label: "A", key: "<option key>", logprobs: <raw OpenAI top-5 logprobs>}` (decide.py:44-51, 78-80).
  There is no probabilities map, no confidence, and no score/noul types. Yes/no is expressed as a 2-option choice
  (examples/yes-no.json), and 2..24 options are allowed. The README says "Logprobs are model preferences, not calibrated
  confidence" (README:85). VERIFIED-SOURCE.
- **Verdict: letter-only, not Jev-compatible without writing your own wrapper.**

## 12. Optional: Hanno-Labs/jev-compatible-server (Bosun backend)

Files: `src/jev_compatible_server/protocol.py`, `bosun.py`, `causal_options.py`, `laya.py` (local: `schema-audit/bosun/`).

- Routes `/v1/systemone` and `/systemone` (app.py:128-129).
- Bosun `_answer` (bosun.py:171-213): choice `confidence = probabilities[choice]` = **max prob**. Score `confidence =
  max(probabilities.values())` (max prob) and **`legend = question.criteria` as a LIST**, not a `{"0":...}` object
  (protocol.py:71-76). Noul = P(true) float. `usage` defaults to 0/0. There is also an `UnsupportedAnswer` type
  `{type:"unsupported", ...}` for models that lack a question type (protocol.py:84-90). VERIFIED-SOURCE.
- The `causal_options` backends use max prob, or 1 - H/lnK under the `system_one_sg` profile (causal_options.py:436-440).
  The `laya` backend passes through whatever confidence the upstream Laya server returns (laya.py:70-98). VERIFIED-SOURCE.
- convaiinnovations/laya and NandhaKishorM/laya: not audited separately (time). The Laya model served through razorback16/openjev
  uses openjev's `to_answer`, so its confidence is 1 - H/lnK (see section 3).

---

## Compatibility matrix

| Project (endpoint) | choice | score semantics | noul semantics | confidence formula (choice / score) | A / B / S | matches Jev conf? | probs default | evidence |
|---|---|---|---|---|---|---|---|---|
| **Jev** (`/v1/systemone`) | key + probs, <=255 | E[i] float, legend{"0"}, 2..10 | P(true) float, no conf | chance-corr max / MAD score | .82(.81) / .775(.78) / .583 | - | calibrated, ~2 dp | docs + adapter |
| Surogate Rune v3 (`/v1/decisions`) | yes, <=255, null desc rejected | E[i] float, legend{"0"}, 2..255 | P(true) float; **criteria required** | **Jev / Jev** | .82 / .775 / .583 | **Yes** | raw T=1 (card recommends T=2) | VERIFIED-SOURCE |
| Winnow-12B (`/v1/systemone`) | yes, <=64 | E[i] float, legend{"0"}, 2..64 | P(true) float | 1-H/lnK / 1-H/lnK | .666 / .615 / .442 | No | raw T=1 | VERIFIED-SOURCE |
| razorback16 openjev (`/v1/systemone`) | yes, <=255 | E[i] float, legend{"0"}, 1..10 | P(true) float | 1-H/lnK / 1-H/lnK | .666 / .615 / .442 | No | raw, multi-read mean | VERIFIED-SOURCE |
| vLLM structured_server (`/v1/systemone`) | yes, **<=26** | E[i] float, legend{"0": str(level)}, <=26 | P(true) float; skipped -> null | **max prob** / max prob | .88 / .85 / .60 | No | raw, multi-read mean | VERIFIED-SOURCE |
| djev-dev (`/v1/request`) | yes, <=255 | E[i] float, legend{"0"}, 2..10 | P(true) float | 1-H/lnK / 1-H/lnK | .666 / .615 / .442 | No | raw T=1 | VERIFIED-SOURCE |
| JoshuaSP open-jev (harness) | decoded value | **int level (decoded)** | **bool** | none | - | No (absent) | n/a | VERIFIED-SOURCE |
| Jebadiah 27B (`/v1/systemone`) | yes, **<=20** | E[i] float (6 dp), legend{"0"}, 2..10 str | P(true) float | Jev / **chance-corr max** | .82 / .775 / .50 | choice yes, score **no** | **T per type (1.23/1.30/0.76)** | VERIFIED-SOURCE |
| AutoJev-27B (`/v1/systemone`) | yes, <=255 | E[i] float, legend{"0"}, 2..10 | P(true) float | **Jev / Jev** | .82 / .775 / .583 | **Yes** | **T=2.21** | VERIFIED-SOURCE |
| Kev (`/v1/systemone`) | yes, <=255, 4 dp | E[i] 4 dp, legend{"0": rendered text}, 1..255 | P(true) 4 dp | **Jev / Jev** | .82 / .775 / .5833 | **Yes** | **T=2.30** (card) | VERIFIED-SOURCE (+DOCS for T) |
| Nimble ParallelScorer (lib) | argmax value + `scores` | argmax value | **bool** | none | - | No (absent) | T 2.18 or 1.0 | VERIFIED-SOURCE |
| Nimble server (openjev-sglang `/v1/systemone`) | yes, <=26 | E[i] float, legend{"0"} | P(true) float | 1-H/lnK / 1-H/lnK | .666 / .615 / .442 | No | T 2.18 (v1/v2) or 1.0 (latest) | VERIFIED-SOURCE |
| Tev1 (Together chat) | letter + raw top-5 logprobs | n/a | n/a (2-way choice) | none | - | No (absent) | n/a | VERIFIED-SOURCE |
| Bosun (jev-compatible-server) | yes | E[i] float, **legend as list** | P(true) float | max prob / max prob | .88 / .85 / .60 | No | backend-dependent | VERIFIED-SOURCE |

Where every project agrees with Jev: the noul answer is a float P(true) with no confidence (every Jev-shaped server; only the
non-server harnesses return booleans); choice probabilities are keyed by the caller's option keys; and score is the
probability-weighted expected level (float) with "0".."n-1" keys. None of the servers round to 2 dp as Jev does. Surogate,
Winnow, openjev, vLLM, djev and AutoJev return full floats, Kev rounds to 4 dp and Jebadiah to 6 dp.
