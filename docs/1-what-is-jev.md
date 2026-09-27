# 1. What is Jev?

**In one sentence:** Jev is a hosted AI model that answers many multiple-choice
questions about a piece of text at once, in about a tenth of a second, and returns a
probability for every answer instead of writing text.

## The idea

A normal LLM (a chat model) writes an answer one token at a time. If you use it to make
a decision ("Is this ticket urgent?"), you ask it to write JSON, wait for it, then parse
it. That is slow, costly, and the output can be malformed.

Jev does not write text. You give it:

1. a **state**: the thing to look at (a support ticket, a game screen as JSON, a document);
2. a set of **typed questions** about that state.

It reads the state **once**, answers **all questions in parallel**, and returns a
probability distribution for each one. The output always matches your schema.

TypeSafe calls this kind of model a **"System One" model**, after the fast, intuitive
"System 1" thinking in Kahneman's *Thinking, Fast and Slow*. Chat models with reasoning
are the slow "System 2". The name "Jev" comes from the economist William Stanley Jevons.

| | Chat LLM (System 2) | Jev (System 1) |
|---|---|---|
| Output | Free text, token by token | Typed answers with probabilities |
| Many questions | One long generation, or many calls | One call, answered in parallel |
| Speed | Seconds | ~70–500 ms |
| Can it chat, write code, explain? | Yes | No |

## The three question types

| Type | What it does | Code analogy | Answer |
|---|---|---|---|
| `choice` | Pick one option from your list (up to 255) | `match` | chosen option + probability per option |
| `score` | Rate on an ordered scale you define (2–10 levels) | sorting | weighted level (e.g. `1.3`) + probabilities |
| `noul` | Yes/no (short for *Bernoulli*) | `if` | probability of "true" |

## What a request looks like

Official example from the [TypeSafe quickstart](https://docs.typesafe.ai/introduction/quickstart):

```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <API_KEY>
```

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
      "criteria": ["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"]
    },
    "is_urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time-sensitivity"
    }
  }
}
```

Response:

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "department": {
      "type": "choice", "choice": "technical", "confidence": 0.78,
      "probabilities": { "technical": 0.85, "sales": 0.0, "billing": 0.15 }
    },
    "frustration": {
      "type": "score", "score": 1.0, "confidence": 1.0,
      "legend": { "0": "Calm, just stating facts", "1": "Frustrated but civil", "2": "Very angry, strong language" },
      "probabilities": { "0": 0.0, "1": 1.0, "2": 0.0 }
    },
    "is_urgent": { "type": "noul", "noul": 1.0 }
  },
  "usage": { "input_tokens": 392, "output_tokens": 65 }
}
```

Things worth knowing about the format:

- Question IDs (`department`, …) are yours. They are **not** sent to the model.
- `confidence` is **not** a probability of being right. It is a statistic of the
  distribution, e.g. for choice `(p_max − 1/K) / (1 − 1/K)`
  ([official adapter code](https://github.com/typesafe-ai/system-one-adapter-python)).
  `noul` has no confidence field.
- This request/response shape is the **"wire format"** most open reproductions copy.
  If a server speaks it, the official SDKs work against it by setting
  `TYPESAFE_BASE_URL`.

## Limits, price and speed

| | Official value | Source |
|---|---|---|
| Context | 64k tokens per request; 32k for state + the longest question | [docs/models](https://docs.typesafe.ai/models) |
| Options per choice | 255 max | [docs/api](https://docs.typesafe.ai/api) |
| Questions per request | No fixed cap (one tester ran 1,500 in ~0.6 s) | docs/models, [Hume](https://archerhume.com/posts/jevs-architecture-unmasked/) |
| Input | Text only (string, JSON object or array). No images yet. English first. | [docs/concepts/state](https://docs.typesafe.ai/concepts/state) |
| Customisation | None: no fine-tuning, same weights for everyone | docs/models |
| Price | $0.042 per million input tokens; output is free | [launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev) |
| Latency | "70–500 ms"; docs say "about 100 ms" | launch post, docs |
| Rate limits | 250k tokens/s, 1,200 requests/min (dynamic) | docs/models |

Independent latency measurements agree with the claims: ~60–90 ms server-side for up to
100 questions on a short state, and 175 ms p50 on a 77-way classification task through
OpenRouter.

## Company and release

- **Company:** TypeSafe AI, San Francisco, founded 2024. Came out of stealth on
  **15 September 2026** with a $40M seed round led by DCVC. CEO Diogo Almeida (ex-OpenAI).
- **Current model:** `jev-1.13.0` (`jev-latest` points to it).
- **Access:** waitlist at launch. As of 26 September 2026 the homepage says
  "invite-only again". Also available through Vercel AI Gateway (`typesafe-ai/jev`)
  and OpenRouter.
- **SDKs:** `pip install typesafe-sdk`, `npm install @typesafe-ai/sdk`.

## How good are its probabilities?

"Calibrated" means that when the model says 80%, it is right about 80% of the time.
This is Jev's main selling point. TypeSafe publishes **no calibration numbers** of its own.

Independent tests show a mixed picture:

| Finding | Source |
|---|---|
| Well calibrated on familiar benchmarks (MMLU ECE 0.031; OpenBookQA, HellaSwag ~0.03) | [Hume](https://archerhume.com/posts/jevs-architecture-unmasked/), [jev-ood-calibration](https://github.com/scienthoon/jev-ood-calibration) |
| Worse on unseen tasks (ECE 0.107 on synthetic tickets) | jev-ood-calibration |
| Confidently wrong when the answer is unknowable: 74% average probability at 45% accuracy | jev-ood-calibration |
| Asked to guess a hidden fair die roll, picked "1" in all 400 trials at 83% confidence | ["Jev Does Not Play Dice"](https://kantahayashiai.github.io/posts/jev-does-not-play-dice/) |
| Confidence *ranks* answers well: answers at ≥0.99 were 96% correct | [OpenRouter](https://openrouter.ai/blog/insights/jev-vs-claude-opus-5-classification/) |
| Option order matters: 88% correct when the right answer is listed first, ~60% when later | [jev-behavior-study](https://github.com/RINNECODER/jev-behavior-study) |

**Practical takeaway:** treat Jev's probabilities as a good *ranking* signal and
calibrate thresholds on your own data. The same advice applies to every open alternative.

## How does it work inside?

TypeSafe keeps this private. What is **official**:

- "A new model architecture, parallel sampler, and training method we call RLCD."
- It "outputs all probabilities in parallel instead of autoregressively generating".
- It reads the state once and answers each question **in isolation**.
- It is post-trained from a pretrained language model (per their docs diagram).
- It is "neither small nor an LLM".

What is **speculation** (Archer Hume's
[teardown](https://archerhume.com/posts/jevs-architecture-unmasked/), from ~10k API probes):

- A transformer that encodes the state once (a shared KV cache), then runs a separate
  branch per question.
- Options are read together as a list; probabilities come straight from a small output
  layer, not from generated text.
- Probably a sparse mixture-of-experts model with ~10B active parameters.

**RLCD** ("Reinforcement Learning for Calibrated Decisions") is described only at
blog-post level: a post-training step, like RLHF, that rewards honest probabilities
instead of pleasing answers. The algorithm, loss, data, base model and size are not public.

## Terms of use: one thing to know

TypeSafe's [customer agreement](https://typesafe.ai/legal/mca) forbids using Jev or its
outputs to "perform model distillation, train a model to imitate the output of the
Services, or develop … a similar or competing product". If you have Jev access, do not
use its answers to train or calibrate your own Jev-like server. Calibrate on your own
labelled data instead. (This is a summary, not legal advice.)
