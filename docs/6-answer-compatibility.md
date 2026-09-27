# 6. Do the open models give the same kinds of answers as Jev?

**Short answer:** the answer *shapes* mostly match. `confidence` mostly does **not**.

- Most Jev-style servers return the same three answer types with the same fields. The
  yes/no answer (`noul`) comes back as a probability, like Jev's.
- Only **4 of ~25** audited servers compute `confidence` the way Jev does. The rest use
  a different formula, so the same probabilities give a different confidence number.
- Even with the right formula, the **probabilities themselves** come from a different
  model, so the numbers still differ from Jev's.

Method: we read the answer-building source code of each server (26 September 2026),
not just its README. Details: [appendix/schema-audit-inference.md](appendix/schema-audit-inference.md),
[appendix/schema-audit-trained.md](appendix/schema-audit-trained.md).

## What Jev returns (the reference)

From TypeSafe's [API docs](https://docs.typesafe.ai/api) and its
[official adapter code](https://github.com/typesafe-ai/system-one-adapter-python):

| Type | Fields | Meaning |
|---|---|---|
| `choice` | `choice`, `probabilities`, `confidence` | Top option; a probability for every option (keyed by your option names, sums to 1) |
| `score` | `score`, `legend`, `probabilities`, `confidence` | `score` is the probability-weighted level, so it can fall between levels (e.g. `1.3`) |
| `noul` | `noul` | A **probability** that the statement is true (e.g. `0.93`). **Not a boolean.** No `confidence` field. |

`confidence` is calculated from the probabilities. It is not a separate estimate:

- **choice:** `(p_max − 1/K) / (1 − 1/K)`, where K is the number of options.
  0 = uniform guess, 1 = certain.
- **score:** `1 − (expected distance from the most likely level) / (the same distance
  for a uniform guess)`, clipped at 0.

## The results

### Same shapes and same confidence as Jev

| Server | Kind | Notes |
|---|---|---|
| [Mapika/decider](https://github.com/Mapika/decider) `/v1/systemone` | inference technique (and its trained models) | Copies TypeSafe's formulas. Adds extra `x_p_max` and `certainty` fields. |
| [Kev](https://github.com/jaredpalmer/kev) `/v1/systemone` | trained | Code comment cites TypeSafe's adapter. |
| [AutoJev-27B](https://github.com/denis-pplx/autojev) `/v1/systemone` | trained | Handles one request at a time; returns 529 while busy. |
| [surogate](https://github.com/invergent-ai/surogate) (Rune v3) | trained | Path is `/v1/decisions`, not `/v1/systemone`. Requires `noul` criteria; rejects `null` choice descriptions. |

### Same shapes, different confidence

These return `choice` / `score` / `noul` like Jev, but compute `confidence` another way:

| Server | Confidence formula used |
|---|---|
| reflex, openjev-sglang, snapjudge, daseinlabs/open-jev, Winnow-12B, razorback16/openjev, djev | 1 − normalised entropy (reads **lower** than Jev) |
| litjev | Gini concentration (lower) |
| openvons | Gap between the top two probabilities |
| vLLM `structured_server.py` example, Bosun | Top probability (reads **higher** than Jev) |

### Partly compatible

| Server | What differs |
|---|---|
| Jebadiah 27B | Choice confidence matches Jev; score confidence doesn't. Max 20 options. |
| snellingio/system-one | Choice matches; score reuses the choice formula (reads higher). |
| jobe | Choice matches; `score` answers have no `score` or `legend` field; `noul` gets an extra `confidence`. |
| simple-jev | Confidence = top probability. In its default mode `noul` is a 1–9 rating mapped to 0.01–0.99, not a probability. |

### Different format

| Server | What differs |
|---|---|
| jevfire | Own `/v1/decisions` API. Yes/no comes back as a **boolean** plus a probability. No `score` type, no `confidence`. |
| jevmlx | Drops option and true/false descriptions; returns only the top 5 probabilities; no score confidence. |
| JoshuaSP/open-jev, Nimble `ParallelScorer` | Research code, not servers: boolean `noul`, whole-number score, no confidence. |
| Tev1 | Returns one option letter; no Jev-style wrapper. |

## How big is the difference?

The same probabilities, run through each formula:

| Formula | Choice {0.88, 0.12, 0.00} | Choice {0.85, 0.15, 0.00} | Score {0.65, 0.30, 0.05} |
|---|---|---|---|
| **Jev** (decider, Kev, AutoJev, surogate) | **0.82** (Jev API showed 0.81) | **0.78** | **0.40** |
| Top probability | 0.88 | 0.85 | 0.65 |
| Top-two gap | 0.76 | 0.70 | 0.35 |
| Gini | 0.68 | 0.62 | 0.27 |
| 1 − normalised entropy | 0.67 | 0.62 | 0.28 |

So a rule like "act automatically if confidence ≥ 0.8" fires on the first example with
Jev's formula, but not with the entropy formula (0.67).

## Why the numbers still differ with the right formula

`confidence` is only a summary of `probabilities`. The probabilities differ because:

- **Different model.** A stock Qwen or Gemma is not Jev.
- **Different calibration.** Defaults vary:
  - most servers use a plain softmax (T = 1);
  - AutoJev (T = 2.21), Kev (T = 2.30) and Jebadiah (per-type T) apply a fitted temperature;
  - snellingio hard-codes T = 0.7, which makes answers look more certain;
  - surogate defaults to T = 1, though Rune's model card recommends 2.
- **Rounding.** Jev rounds to about 2 decimals, so exact 0s and 1s are common. The
  open servers return 4–6 decimals or full floats.

## What this means for your combined server

1. **Compute `confidence` yourself** from `probabilities`, using TypeSafe's two formulas
   (copy them from the [official adapter](https://github.com/typesafe-ai/system-one-adapter-python),
   `confidence_metrics.py`). The recommended build in [doc 5](5-combined-server.md)
   reuses decider's code, which already does this.
2. **Return `noul` as a float** P(true) with no confidence, and `score` as the weighted
   level, to stay drop-in compatible with the TypeSafe SDK.
3. **Don't reuse Jev's thresholds.** Calibrate your temperature, then choose thresholds
   on your own labelled data.
4. **Test compatibility with the official SDK** against your gateway. Also check the
   edge cases where servers disagree:
   - `null` choice descriptions;
   - `noul` without criteria;
   - more than 26 options;
   - `422` error codes.
