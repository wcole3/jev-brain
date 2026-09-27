# Jev (TypeSafe AI): research notes

Compiled 2026-09-26. Every fact carries a URL. Raw fetches are in `/home/welb/devspace/jev-onto/.firecrawl/jev/`.
Labels: **[OFFICIAL]** means TypeSafe's own site, docs, press release, or its CEO's own comments. **[INDEPENDENT]** means a third-party measurement. **[SPECULATION]** means inference by a third party. **[DERIVED]** means my own arithmetic from cited numbers.

Key source shorthands:
- BLOG = https://typesafe.ai/blog/introducing-system-one-models-and-jev (launch post, Sep 15, 2026)
- HOME = https://typesafe.ai/
- API = https://docs.typesafe.ai/api
- MODELS = https://docs.typesafe.ai/models
- LLMSFULL = https://docs.typesafe.ai/llms-full.txt (a single-file dump of all docs; saved as `jev/docs_llms_full.md`)
- EVALS = https://evals.typesafe.ai/
- PR = https://finance.yahoo.com/technology/ai/articles/typesafe-ai-emerges-stealth-40m-190000776.html (Business Wire, also at https://www.businesswire.com/news/home/20260915525333/en/)
- HN = https://news.ycombinator.com/item?id=49717558
- HUME = https://archerhume.com/posts/jevs-architecture-unmasked/

---

## 1. What Jev is (plain language)

Jev is a hosted, closed AI model that **makes decisions and does not write text**. You send it a piece of context (the "state": a string, a JSON object, or an array) together with a set of named, typed questions. It returns one typed answer per question, with probabilities. There are three answer types:
- **choice**: pick one option from your list.
- **score**: a rating on an ordered rubric you define.
- **noul**: a yes/no probability.

All the questions are answered in parallel, in a single request, in roughly 0.1–0.5 s, at a price of $0.042 per million input tokens. Output tokens are free. The output always matches the requested schema. TypeSafe calls this class of model a "System One model" (after Kahneman) and pitches it as a "frontier-intelligence function call: unstructured state in, typed probabilistic decisions out". Sources: [BLOG], [API], https://docs.typesafe.ai/introduction. Jev is not a chat or code model and cannot replace the LLM inside a coding agent (https://docs.typesafe.ai/introduction/coding-agents).

## 2. Company & release

- **Company.** TypeSafe AI, based in San Francisco and founded in 2024. On Sep 15, 2026 it came out of stealth with **$40M in seed funding led by DCVC**. The founders are **Diogo Almeida** (co-founder and CEO, formerly an OpenAI researcher, described as a "co-inventor of RLHF/ChatGPT"), **Erik Gafni**, and **Sasha Sheng**. [OFFICIAL, PR] The Register gives the same $40M figure: https://www.theregister.com/ai-and-ml/2026/09/16/typesafe-ai-debuts-model-for-machines-that-plays-doom/5296711
- The launch post is signed "Diogo Almeida, founder" and says the company spent "two years in stealth". [BLOG] The docs say Almeida co-invented RLHF, which was used for InstructGPT and ChatGPT (https://docs.typesafe.ai/introduction/machine-learning-primer).
- The user brief called the company "System One". That is actually TypeSafe's name for the model class. The company is **TypeSafe AI** and the product is **Jev**. [BLOG]
- **Release date.** The launch post and press release are both dated **Tuesday, Sep 15, 2026**. [BLOG][PR] At launch Jev was "early access", with developers let in from a waitlist. [BLOG][PR] An unofficial list says "Public access opened 21 September 2026" (https://github.com/AnotiaWang/awesome-jev). However, the homepage on 2026-09-26 reads **"TYPESAFE IS INVITE-ONLY AGAIN"** with a waitlist form. [HOME]
- **Model version.** The current model is `jev-1.13.0`. The aliases `jev-latest` and `jev-preview` both point to it, and there is no preview build yet. [MODELS] The "jaggedness" page was last reviewed 2026-09-17 (https://docs.typesafe.ai/model-jaggedness/jev-1.13).
- **Name.** "System One" comes from Kahneman's *Thinking, Fast and Slow*. "Jev" is after William Stanley Jevons (the Jevons paradox). [BLOG]
- **Other places to access Jev:**
  - Vercel AI Gateway, model id `typesafe-ai/jev`, through AI SDK `experimental_evaluate`. The gateway uses `type: 'boolean'` for Noul and lists the price as "$0.04 per 1M" input. (https://vercel.com/ai-gateway/models/jev)
  - OpenRouter, which calls it a "Decisions API" (https://openrouter.ai/blog/insights/jev-vs-claude-opus-5-classification/).
- **SDKs.** The Python SDK is `pip install typesafe-sdk`: v0.5.7 on 2026-09-14, v0.6.0 on 09-15, v0.7.0 on 09-18 (switched to pydantic and added `response_model`), and v0.7.1 on 09-21 (https://docs.typesafe.ai/sdk/python/changelog). The JS SDK is `npm install @typesafe-ai/sdk`: v0.5.7 on 09-11 and v0.6.0 on 09-15 (https://docs.typesafe.ai/sdk/javascript/changelog). There is also an official "System One adapter" that lets LLMs answer the same API shape (https://github.com/typesafe-ai/system-one-adapter-python).
- **Launch reception.** The Hacker News launch thread had 1,981 points as of 2026-09-26 [HN]. The CEO posted there as `CompleteSkeptic`.

## 3. API

### Endpoint [OFFICIAL, API]
```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <API_KEY>
Content-Type: application/json
```
There is also `GET /v1/models`. It returns `{"models":[{"name","description","release_date"}]}` and lists the aliases. Versioned IDs are accepted even if they are not listed. [MODELS]

### Request body [OFFICIAL, API]
The docs dump drops parameter names, so the names below are taken from the examples.

- `state`: `string | object | array`. This is the content to evaluate. The JS SDK also allows `null` (https://docs.typesafe.ai/sdk/javascript/api/interfaces/SystemOneRequestPayload).
- `model`: `string`, for example `"jev-latest"`. The SDKs use this as the default. [API][https://docs.typesafe.ai/sdk/python/api/constants]
- `questions`: `map<string, Question>`, which must not be empty (JS SDK). You choose the keys, and answers come back under the same keys. The key "is not sent to the underlying model and is not used in inference." [API]

`Question` is a union selected by its `type` field. Every question has `type` and `instructions` (a string, object, or array). Each type then has its own `criteria` [API]:

| type | `criteria` | Limits |
|---|---|---|
| `"noul"` | optional object `{ "true": <desc>, "false": <desc> }`, where each desc is a string, object, or array | yes/no |
| `"choice"` | `map<option, string\|object\|array\|null>`, an option-to-rubric map (use null for no description) | **maximum 255 options** per Choice |
| `"score"` | ordered `array<string\|object\|array>` of level descriptions | "should have at least two levels; the API accepts up to 10" |

Structured instructions are supported. For example, `"instructions": {"potential_duplicate": {...}, "question": "Is the resume for the same person as `potential_duplicate`?"}`. [API]

"Noul" is "short for bernoulli", per the CEO. Choice "maps to [a] 'match' statement", score "maps to sorting", and noul "maps to if-statements". [HN, comment https://news.ycombinator.com/item?id=49718407]

### Verbatim example request (Quickstart) [OFFICIAL, https://docs.typesafe.ai/introduction/quickstart]
```json
{
  "state": "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.",
  "model": "jev-latest",
  "questions": {
    "department": {
      "type": "choice",
      "instructions": "Which team should handle this",
      "criteria": {
        "billing": "Payment or subscription issues",
        "technical": "Bugs or integration problems",
        "sales": "Pricing or account questions"
      }
    },
    "frustration": {
      "type": "score",
      "instructions": "How frustrated the customer appears",
      "criteria": [
        "Calm, just stating facts",
        "Frustrated but civil",
        "Very angry, strong language"
      ]
    },
    "is_urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time-sensitivity"
    }
  }
}
```
### Verbatim example response (Quickstart) [OFFICIAL]
```json
{
  "model": "jev-1.13.0",
  "answers": {
    "department": {
      "type": "choice",
      "choice": "technical",
      "confidence": 0.78,
      "probabilities": { "technical": 0.85, "sales": 0.0, "billing": 0.15 }
    },
    "frustration": {
      "type": "score",
      "score": 1.0,
      "confidence": 1.0,
      "legend": { "0": "Calm, just stating facts", "1": "Frustrated but civil", "2": "Very angry, strong language" },
      "probabilities": { "0": 0.0, "1": 1.0, "2": 0.0 }
    },
    "is_urgent": { "type": "noul", "noul": 1.0 }
  },
  "usage": { "input_tokens": 392, "output_tokens": 65 }
}
```

### Response schema [OFFICIAL, API]
- Top level: `model` (the versioned ID that answered), `answers` (`map<id, Answer>`), and `usage` (`{input_tokens, output_tokens}`).
- **Noul answer:** `{type:"noul", noul: number 0..1}`. There is **no confidence field**. [API][https://docs.typesafe.ai/confidence]
- **Choice answer:** `{type:"choice", choice: <highest-prob option>, probabilities: map<option, float summing to 1>, confidence: 0..1}`.
- **Score answer:** `{type:"score", score: <probability-weighted level index; can land between levels>, legend: map<"0".."n", description>, probabilities: map<level-index-string, float>, confidence}`.
- **Errors:**
  - `401` means a bad or missing key.
  - `422` means validation failed.
  - `429` means a rate limit was hit.
  - `529 Overloaded` means TypeSafe is overloaded.
  - The SDKs retry 429 and 529 with exponential backoff and honor `retry-after`. [API][MODELS]
  - The SDK default timeout is 10 s. The environment variables are `TYPESAFE_API_KEY`, `TYPESAFE_BASE_URL`, and `TYPESAFE_DEFAULT_MODEL`. (https://docs.typesafe.ai/sdk/python/api/constants)

### Limits & modalities [OFFICIAL, MODELS]
- **Context:** "64k tokens per request; 32k tokens for `state` plus the longest question". The state is ingested once. The 64k limit covers the state plus all questions, and the 32k limit covers the state plus the single longest question.
- **Rate limits:** "250,000 tokens per second / 1,200 requests per minute", "adjusting dynamically ... can change without notice". Higher limits are available on enterprise plans.
- **Input:** text only. "String, JSON object, or array of text values. No image, audio, or video input." The docs say images are "not supported (yet)" (https://docs.typesafe.ai/concepts/state). The Doom demo ran on structured game state, "not on images (yet…)". [BLOG]
- **Language:** English is the primary language. Other languages, including CJK, are "handled but not equally well". [MODELS]
- **Customization:** no fine-tuning or LoRA. "the same weights serve every account". Jev is not trained on customer requests. ZDR (zero data retention) is available for enterprise. [MODELS]
- **Max questions per request:** there is **no documented count cap**. Only the token budgets apply. [MODELS] The docs recommend "speculative fan-out", meaning you pack every question you might need into one call (https://docs.typesafe.ai/patterns/fan-out).
  - [INDEPENDENT, HUME] Archer Hume sent up to 1,500 questions per request, which returned in a few hundred ms (median 610 ms at 1,500). A 23k-token state with 5,000 questions fit. He measured the limits as about 32,768 tokens per branch and about 65,536 per request.
- **Max options:** 255 per Choice. [API] For larger candidate sets, TypeSafe itself uses a two-stage process: score each candidate independently, then make an explicit choice. [BLOG] Hume notes 255 = 2^8 − 1 and that the cap is enforced by request validation. [HUME]
- **Precision:** probabilities come back at two decimals and are often exactly 0 or 1. [INDEPENDENT: HUME Methods; https://github.com/scienthoon/jev-ood-calibration]
- **Determinism:** small differences appear between identical repeated requests, and between duplicate questions in the same request. Do not assume determinism. [INDEPENDENT, HUME §7]

### The "20 cases" example set
- EVALS publishes four workflows: Security Incidents, Agent Trace Observability, Invoice Processing, and Customer Service. Each workflow page shows a handful of example cases (the Security Incidents page shows 5) with every model's answers (https://evals.typesafe.ai/security_incidents.html).
- [INDEPENDENT] The jev-on-a-laptop repo rebuilt "**all public example cases of all four TypeSafe workflows — 20 cases, 373 reference question-pairs**" (https://github.com/rorshopping/jev-on-a-laptop). So "20 cases" = 4 workflows × 5 public examples on evals.typesafe.ai.

## 4. Pricing & latency claims

### Pricing [OFFICIAL]
- **$0.042 per MTok of input ($42 per billion tokens). Output tokens are free.** [BLOG][MODELS][HOME]
- The homepage claims "238x lower input price than Claude Fable 5.1". [HOME]
- The blog is candid on sustainability: "We can't prove it isn't subsidized; ... we expect [pricing] to go down". [BLOG]
- The Doom demo made 10 queries per second at "~$7/hour". [BLOG]
- **"$15.6 per 1M requests" is NOT an official figure.** It comes from a community news item on the HF Space "jev-decision-index / jev-reproductions-tracker". That item compares Logan Markewich's "jeff" 400M encoder clone ("~$2.6 per 1M requests against jev's ~$15.6"). (https://huggingface.co/spaces/multimodalart/jev-decision-index ; https://huggingface.co/spaces/multimodalart/jev-reproductions-tracker)
  - [DERIVED] $15.6 per 1M requests works out to about 371 input tokens per request at $0.042/MTok.
  - [DERIVED] Measured request sizes vary a lot. A minimal single-noul request is about 268 input tokens (HUME), or about $11.3 per 1M requests. The fixed overhead is about 261 tokens per request (jev-fanout-bench, listed at https://github.com/AnotiaWang/awesome-jev). OpenRouter's Banking77 run averaged 2,605 input tokens, or $0.11 per 1k requests (https://openrouter.ai/blog/insights/jev-vs-claude-opus-5-classification/).
- **What `output_tokens` means.** The usage object still reports `output_tokens`. Hume shows this is a billing/serialization count computed after inference: 4 shared tokens + 15 per answer + the length of the question ID. It "tells us nothing about whether Jev generates text". [INDEPENDENT, HUME §1]

### Latency claims [OFFICIAL], not all mutually consistent
- "End-to-end response time is **70ms-500ms** ... 40x-200x faster" than frontier LLMs. The published evals were run from laptops on the US West Coast, where the service is hosted. [BLOG]
- The homepage headline is "**193.6x Faster, 444.6x Cheaper**", "based on workflows for System One tasks". The blog says these figures come from the workflow evals and "are on the higher end of real world gains". The homepage demo shows TypeSafe at $0.000081 in 0.114 s versus an LLM at $0.013880 in 8.566 s. [HOME][BLOG]
- The docs say "Most queries complete in about 100 ms" (https://docs.typesafe.ai/concepts/how-to-build-with-system-one) and "real-time speeds (150ms)" (https://docs.typesafe.ai/concepts/use-case-map).
- The press release says "less than 100 milliseconds of latency" and "up to 100 times faster and less expensive". [PR]
- The docs say "Adding questions barely changes the response time" (https://docs.typesafe.ai/introduction).

### Independent latency measurements
- **HUME** (server-side upstream time):
  - A 360-token state took a median of 57.5 ms. A ~30k-token state took about 218 ms.
  - From 1 to 100 questions, time stayed around 72–87 ms. 500 questions took a median of 181 ms and 1,500 questions a median of 610 ms.
  - Question text costs roughly twice as much time per token as state text.
- **OpenRouter**, Banking77 (77-way Choice): p50 175 ms, p95 270 ms, p99 353 ms, versus Opus 5 at a p50 of 2,266 ms. (https://openrouter.ai/blog/insights/jev-vs-claude-opus-5-classification/)
- **jev-benchmarks**, called from France: p50 of 236–256 ms (https://github.com/AbdelStark/jev-benchmarks).

## 5. Calibration claims and independent findings

### Official claims [OFFICIAL]
- RLCD optimizes for "answers with epistemically honest probabilities". Jev "Always communicates confidence ... Calibrated: higher confidence means higher accuracy. More consistent". [BLOG]
- "Outcomes assigned a probability of 0.8 should occur about 80% of the time". The docs add that this describes groups of predictions, not a guarantee for any single answer. (https://docs.typesafe.ai/introduction/machine-learning-primer)
- **No official ECE, reliability diagram, or public-benchmark number is published.**
  - The launch FAQ item "How does Jev perform against public benchmarks?" is collapsed and did not render when scraped. [BLOG]
  - A TypeSafe post from 2026-09-11, "Lies, Damned Lies, and Benchmarks" (https://typesafe.ai/blog/antibenchmaxxing), reportedly commits to "no standard benchmark table in our model releases". This is secondary: it comes from a summary at https://jevwiki.ai/wiki/entities/blog-antibenchmaxxing.md and was not fetched directly.
- **The `confidence` field is not a probability of being correct.** It is "a statistic computed from the probability distribution". Noul has none. (https://docs.typesafe.ai/confidence)
  - The official adapter code computes Choice confidence as `(p_max − 1/K)/(1 − 1/K)`.
  - It computes Score confidence as `1 − E|level − mode| / MAD_uniform`.
  - (https://github.com/typesafe-ai/system-one-adapter-python, file `src/system_one_adapter/_utils/confidence_metrics.py`)
  - [DERIVED] Both formulas reproduce the doc examples exactly: 0.88/0.12/0 → 0.82 (the doc shows 0.81), 0.85 → 0.78, and a score of 0/0.95/0.05 → 0.925 (the doc shows 0.92).
- **Official workflow evals** (EVALS):
  - Setup: four workflows. The reference labels are the average of GPT-6 Astra and Claude Fable 5.1 at high thinking. Other models run at their default reasoning setting.
  - **Jev: 67.8% mean accuracy, $0.0004 per case, 0.4 s per case.** Per workflow it scored 61.7%, 61.8%, 71.6%, and 76.0%.
  - Comparison models, workflow mode:

    | Model | Accuracy | Cost per case | Time per case |
    |---|---|---|---|
    | Opus 5 | 73.1% | $0.1761 | 37.8 s |
    | Sol | 74.1% | $0.0836 | 23.3 s |
    | Terra | 67.9% | $0.0304 | 10.1 s |
    | Sonnet 5 | 67.8% | $0.1174 | 78.1 s |
    | Luna | 66.8% | $0.0033 | 12.9 s |
    | DS v4 pro | 65.5% | — | — |
    | DS v4 flash | 64.4% | — | — |
    | Haiku 4.5 | 53.6% | — | — |

  - TypeSafe's caveats: the workflows were built by its own team (so bias is possible), and the reference labels favor OpenAI and Anthropic. [BLOG]

### Independent findings
- **Archer Hume** [HUME], a 17 Sep 2026 study of jev-1.13.0:
  - MMLU sample of 1,200 items: 10-bin **ECE 0.0313**. 990 of the items fell in the 0.9–1.0 bin, predicted at 98.7% and correct 96.3% of the time.
  - MMLU-Pro accuracy: 84.6%.
  - Freshly generated maths problems were mostly calibrated. The exception was modular exponents: 56% correct at a mean probability of 35%.
  - Data: https://archerhume.com/research/jev/calibration.json and https://archerhume.com/research/jev/evidence.json
- **scienthoon/jev-ood-calibration** (via Vercel Gateway, 2026-09-19) (https://github.com/scienthoon/jev-ood-calibration):
  - Public benchmarks (15-bin ECE): OpenBookQA 0.024 at 94.2% accuracy, CommonsenseQA 0.032 at 88.1%, HellaSwag 0.029 at 86.1%. These datasets are probably in the training data.
  - Synthetic tickets the model cannot have seen (n=900): **ECE 0.107** overall, which is 4.4× the noise floor.
  - On a "priority" label defined by a policy that is absent from the text, accuracy was 44.7% with a mean stated probability of 0.74 and ECE 0.325. **The model is confidently wrong when the answer is unknowable.**
  - The direction of miscalibration depends on the question type. Noul is underconfident (refit temperature T = 0.66). Choice and Score are overconfident (T = 1.30 and 1.92 after the author's 2026-09-22 correction; originally reported as 3.29 and 3.40).
  - The `confidence` field is worse than the max probability: ECE 0.035 / 0.078 / 0.18 on its three sets. The author's advice: "Don't threshold on the confidence field".
  - There were 0 schema violations in 4,621 calls.
- **"Jev Does Not Play Dice"** (Kanta Hayashi, Sep 20) (https://kantahayashiai.github.io/posts/jev-does-not-play-dice/):
  - Asked to call a hidden roll of a fair die as a 6-way Choice, Jev picked "1" in all 400 trials, with a **mean reported probability of 83% and 19% accuracy**.
  - Asked as a Noul instead, it was closer to the truth: 19.2% against the true 16.7%.
- **OpenRouter**, Banking77 (3,080 test utterances, 77-way Choice) (https://openrouter.ai/blog/insights/jev-vs-claude-opus-5-classification/):
  - Accuracy: Jev 1.13 81.0% versus Claude Opus 5 84.4%. Cost per 1,000 requests: $0.11 versus $2.42.
  - Their verdict on confidence: "not a calibrated probability ... it ranks well". The 58% of utterances with confidence ≥ 0.99 were 96.3% accurate.
  - Routing low-confidence items to Opus recovers Opus-level accuracy at about half the cost.
- **AbdelStark/jev-benchmarks**, versus GLiNER2.5 (https://github.com/AbdelStark/jev-benchmarks):
  - Jev accuracy was 0.910 on AG News, 0.870 on Banking77, and 0.480 on DAIR Emotion.
  - On Emotion it was badly calibrated: Brier 0.846 versus 0.668, NLL 5.588, and zero probability on the true label for 16% of items.
- **Other studies, cited by the OOD repo:**
  - jev-phishing-bench: ECE 0.154, versus Claude Haiku 4.5 at 0.097.
  - jev-exploration (Samuel Sacco): ECE 2.1–2.5× the noise floor, but p ≥ 0.9 gave a 100% hit rate. Recommendation: "treat the output as a monotone score, not a probability, and calibrate locally".
- **arXiv 2609.29429**, "Just Ask Jev" (Sep 24) (https://arxiv.org/abs/2609.29429):
  - RLCDAlignBench covers 10 alignment-failure types across 44 benchmarks.
  - One generic question reached a **median AUROC of 0.886 zero-shot**, beat supervised baselines on most benchmarks, and cost 63× less than LLM-judge scorers.
- **Behaviour quirks** (https://github.com/RINNECODER/jev-behavior-study, 11,621 requests on Sep 16–17):
  - Option order matters. An arithmetic question was answered correctly 88% of the time when the correct answer was listed first, versus 59–62% when it was later. Hume also found order effects.
  - Letter counting: 117/216 correct.
  - The "car wash" prompt got the answer "walk" in all 1,000 calls.
  - Mid-position conflicting facts failed at 512+ records.
  - A 3D driving pilot completed 0/12 tasks.

## 6. Architecture: official statements vs speculation

### Official statements [OFFICIAL]
- The stack has "a new model architecture, parallel sampler for maximum efficiency, and training method we call ... RLCD". [BLOG] The homepage repeats "new architecture, a new sampler, and a new training algorithm". [HOME]
- "Jev outputs all probabilities in parallel instead of autoregressively generating by token." [BLOG]
- "Jev is neither small nor an LLM." (from the launch FAQ; this answer rendered after expanding the collapsed item). [BLOG]
- Jev ingests the state once and evaluates every question against it in parallel. Questions are evaluated independently and in isolation. [MODELS][https://docs.typesafe.ai/introduction]
- The question key is not sent to the model. [API]
- The same weights serve all accounts. [MODELS]
- CEO on HN:
  - "architecture is close to the chest for now, but we have talked about writing a paper" (https://news.ycombinator.com/item?id=49718824)
  - "strings (and all sequential data structures) are not allowed at all - this is how we make sure all outputs can be computed in parallel (thus no output token cost)" (https://news.ycombinator.com/item?id=49719122)
  - "technically not a language model (it doesn't generate language)" (https://news.ycombinator.com/item?id=49718437)
  - "yes a general model ... no training at all" [for new tasks] "focused on 'System 1' tasks" (https://news.ycombinator.com/item?id=49719245)
- The docs' primer diagram shows "Pretrained language models branch into ... an emphasized RLCD decision-model path". This implies Jev is post-trained from a pretrained LM (https://docs.typesafe.ai/introduction/machine-learning-primer).

### Speculation [SPECULATION, HUME, based on about 10k API probes]
- A **causal transformer decoder** backbone. This is assumed, not proven: the probes cannot tell a decoder from an encoder.
- **Shared state prefix** (a KV cache computed once) plus **isolated per-question suffix branches**. Evidence:
  - A secret placed in a sibling question was invisible, while the same secret in the state was visible.
  - Token accounting is exactly additive.
  - Latency stays flat up to about 100 questions.
  - Both context limits fit this model.
- **Listwise option processing.** Adding an irrelevant fifth option shifted the log-odds between two existing options by −0.28 in all 10 blocks.
- **Direct numerical readout** from a head (option-slot or pointer style) followed by a softmax, rather than decoded text.
- Training with a proper scoring rule (log loss or Brier). **Sparse MoE** (about 10B active parameters) is "an inference, not a measurement".
- The tokenizer matches none of 192 public tokenizers. It is closest to o200k and Qwen (348/415 probes) and splits every digit individually.
- Hume's final reconstruction: "a causal transformer with a shared state prefix, isolated question suffixes, listwise option processing, typed numerical readouts, and training directed at predictive distributions".

### Community reproductions [INDEPENDENT]
These are not TypeSafe's model.
- jev-on-a-laptop reproduces "parallel constrained decoding": prefill once, broadcast the KV cache to one batch row per field, and read candidate logits in one forward pass. A local Qwen2.5-7B scored 73.8% agreement on the 20 public cases, versus Jev's published 86.6% (297/343), Opus 89.8%, and Sol 89.2%. The repo's verdict on Jev-style "calibrated" confidence from raw logits: it is "a proxy, not trained calibration". (https://github.com/rorshopping/jev-on-a-laptop)
- Many open clones serve a `/v1/systemone`-compatible API, including Kev, Laya, NanoJev, LitJev, and jev-style (https://github.com/AnotiaWang/awesome-jev).

## 7. RLCD: what is actually disclosed

- **The name.** Reinforcement Learning for Calibrated Decisions. It is presented as a third post-training path alongside RLHF (which made chatbots) and RLVR (which made reasoning models). (https://docs.typesafe.ai/introduction/machine-learning-primer)
- **The objective.** RLCD "trains TypeSafe to return decisions and calibrated probabilities instead of generated text". The output contract is:
  - the model does not generate text;
  - it returns decisions and probabilities;
  - higher probability should mean a greater chance of being correct.
  (same URL)
- **The motivation.** RLHF rewards sycophancy and confident hallucination and causes "mode dropping". TypeSafe says "Human preference and machine trustworthiness are different optimization targets". (same URL; also [HOME])
- **Training data.** "TypeSafe is primarily a data research lab ... We make all the data ourselves. We wouldn't train on your data ... if you want to find out more, we'd have to hire you." (launch FAQ answer, rendered after expanding) [BLOG] Jev is "not trained on customer requests or responses". [MODELS] The CEO says "data is probably far most interesting than architecture" and points to https://typesafe.ai/blog/bitterest-lesson. That post argues "doing the right task > data > compute > algorithms" and contains no RLCD detail.
- **Not disclosed:** the loss or reward, the RL algorithm, the base model, the parameter count, and whether post-hoc calibration is used. HUME §5 says "The exact recipe is unpublished." The Register loosely calls RLCD an "architecture", which is inaccurate by TypeSafe's own description. The launch FAQ item "Why was a new training algorithm needed?" did not render.

## 8. Use cases pitched

- **Launch post** [BLOG]:
  - "AI-Powered Workflows / smart if-statements" (classify, route, score, extract, branch).
  - "Map-reducing over big data".
  - "Real-time applications" (100 ms UX).
  - "Verify everything": score, judge, verify, guardrail, and detect jailbreaks in LLM prompts, reasoning traces, and outputs.
  - Demos: a race against GPT-5.6 Terra, **Doom** (a bot reacting to structured game state), and **Wikiracing** (choosing among hundreds to thousands of links).
- **Docs use-case map** (https://docs.typesafe.ai/concepts/use-case-map):
  - AI automation software, real-time applications, AI map-reduce, universal verification, and "Harness Engineering" (model routing, guardrails, reasoning-trace classification).
  - Industry accordions: search and retrieval, scientific discovery, model routing, LLM guardrails, semantic code linting, feature extraction, recruiting, lead generation, customer support, insurance claims, financial crime, legal and compliance, e-commerce, moderation and trust and safety, advertising, gaming, risk assessment, demand forecasting, and knowledge graphs.
- **Cookbooks** (https://docs.typesafe.ai/llms.txt): reranking, guardrails, citation checking, function calling, skill suggestion for agents, entity alignment, RAG passage filtering, date and value extraction, hierarchical classification, and SDE cascades.
- **Press release:** "can process hundreds of outputs in parallel from a single prompt". [PR]
- **The Register:** sorting customer-service problems, real-time apps, map-reduce, verifying AI inputs, and model harnesses. It also noted the Doom demo. (theregister URL above)
- **CEO:** coding use cases are not tried yet, and "coding themed releases soon" (https://news.ycombinator.com/item?id=49718867).
- **What the community built** (https://github.com/hellogumbo/awesome-jev, https://github.com/AnotiaWang/awesome-jev): browser and computer-use agents, model routers (LangChain routing middleware: https://www.langchain.com/blog/building-a-harness-with-jev), moderation and spam filters, game bots (Doom, Snake, StarCraft, Minecraft), and agent safety monitors.

## 9. Open questions

1. The backbone, parameter count, and whether it is MoE. The CEO says details are "close to the chest", and a paper is only "talked about". [HN]
2. The actual RLCD algorithm and loss, and whether post-hoc temperature or type-specific calibration is applied. Independent evidence shows the direction of miscalibration flips by question type (scienthoon), which hints at per-type post-processing.
3. Whether calibration holds out of distribution. Evidence says it does not when the answer is unknowable (dice, policy-defined labels), even though it looks good on MMLU. The official claims give no population-level ECE.
4. Server-side confidence formula. It matches the adapter formula on the doc examples, but TypeSafe does not document it explicitly.
5. Maximum number of questions per request. None is documented beyond the 64k-token budget. Rate limits are "dynamic".
6. Access status. The launch was waitlisted, a community list says it went public on Sep 21, and on Sep 26 the homepage says "INVITE-ONLY AGAIN".
7. Image or multimodal input ("not supported (yet)") and a roadmap for non-English languages.
8. Determinism and option-order sensitivity, which matter for threshold-based automation (HUME, RINNECODER).
9. Whether pricing is sustainable: "can't prove it isn't subsidized". [BLOG]
10. The collapsed launch FAQ answers on public benchmarks and "how is it possible" were not retrievable by scraping.
