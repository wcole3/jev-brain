# 3. How the open models compare to Jev

**Short answer:** the best open models now score within about half a point of Jev
on the community benchmark, and one of them uses no training at all: it is a
decoding trick on a stock Gemma 4 31B. Jev still leads on knowledge and reasoning.
Many open models are *better calibrated* than Jev on this benchmark.

## The benchmark: Jev Decision Index 0.2.1

- **Who runs it:** the community Hugging Face Space
  [multimodalart/jev-decision-index](https://huggingface.co/spaces/multimodalart/jev-decision-index)
  (unofficial, not affiliated with TypeSafe). Harness:
  [apolinario/decision-index](https://github.com/apolinario/decision-index).
- **What it runs:** ~120,000 decision requests from 38 benchmarks in 5 areas
  (Knowledge & Reasoning, Language, Retrieval & Classification, Tools, Arts & Taste).
- **Score:** "skill", corrected for chance. **0 = random guessing, 100 = perfect.**
  Areas are weighted (Knowledge 25.8%, Language 25.8%, Retrieval 20%, Tools 18.3%, Arts 10%).
- **Fairness rules:** each model uses its own published prompts and readout. No prompt
  tuning, no truncation, no pruning of options. A request a model cannot answer
  (too long, too many options) counts as wrong.
- **Hardware:** every open model ran on **1 × NVIDIA RTX PRO 6000 (96 GB)**, the same
  card as yours, so the latency numbers below are what you should expect locally.
  Jev (version `jev-1.13.0`) ran through TypeSafe's hosted API.

> Data snapshot: 2026-09-26/27. The board updates often.

## Top of the board

Area columns are skill scores (0–100). ECE = calibration error (lower is better; see below).
Latency = median ms per request, on-card for open models, over HTTPS for Jev.

| # | Model | Kind | Base | Size | **Index** | Know. | Lang. | Retr. | Tools | Arts | ECE | ms |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| – | **Jev** (closed) | hosted API | ? | ? | **57.9** | **51** | 62 | 55 | 75 | 38 | 0.074 | 524* |
| 1 | Surogate Rune 26B-A4B v3 | full fine-tune | Gemma 4 26B-A4B (MoE) | 26B | **57.4** | 43 | **63** | **64** | 71 | **42** | 0.120 | 121 |
| 2 | Decider chat · Gemma-4-31B | **inference technique** | Gemma 4 31B (stock) | 33B | **57.3** | 44 | 60 | 63 | 76 | 38 | 0.047 | 109 |
| 3 | AutoJev-27B | full fine-tune | Qwen3.8-27B | 28B | **56.4** | 41 | **63** | 55 | **79** | 39 | 0.018 | 101 |
| 4 | simple-jev · Qwen3.8-27B | **inference technique** | Qwen3.8-27B (stock) | 28B | **55.7** | 37 | 62 | 63 | 76 | 36 | 0.113 | 373 |
| 5 | Jebadiah 27B | LoRA | Qwen3.8-27B | 28B | **54.7** | 39 | 61 | 54 | 78 | 39 | **0.014** | 110 |
| 6 | reflex 27B | **inference technique** | Qwen3.8-27B (stock) | 28B | **52.2** | 35 | 54 | 58 | 74 | 40 | 0.024 | 108 |
| 7 | Decider chat · Qwen3.6-27B | **inference technique** | Qwen3.6-27B (stock) | 28B | **51.4** | 37 | 57 | 52 | 71 | 35 | 0.021 | 84 |
| 8 | Winnow-12B | LoRA | Gemma 4 12B | 12B | **50.0** | 34 | 56 | 54 | 71 | 30 | 0.168 | 73 |
| 9 | open-jev (JoshuaSP) | inference technique (diffusion) | DiffusionGemma 26B-A4B | 26B | **49.5** | 33 | 54 | 58 | 70 | 27 | 0.216 | 260 |
| 10 | Jevfire | **inference technique** | Qwen3.8-27B-FP8 (stock) | 28B | **49.4** | 30 | 53 | 56 | 72 | 32 | 0.052 | 90 |
| 11 | Decider 35B-A3B | full fine-tune | Qwen3.5-35B-A3B (MoE) | 36B | **47.1** | 32 | 56 | 55 | 57 | 33 | 0.023 | 101 |
| 12 | JPT-9B | LoRA | Qwen3.5-9B | 10B | **46.9** | 32 | 57 | 45 | 67 | 29 | 0.077 | 149 |

\* Jev latency includes the network round-trip to TypeSafe's API, so it is not
directly comparable with the on-card numbers.

67 open entries are on the board. The rest score lower; see the Space for the full list.

## What the numbers say

**1. The gap to Jev is nearly closed on this benchmark.** Three open models sit within
1.5 points of Jev. None of them is Jev: they copy its *interface* (state + typed
options in, probabilities out), not its weights or training.

**2. At ~30B, a decoding trick on a stock model is as good as fine-tuning.**
Decider chat on stock Gemma 4 31B (57.3) ties the best fine-tune (57.4). Four of the
top ten are pure inference techniques. This is good news for a combined chat +
decisions server: the model stays a normal chat model.

**3. At small sizes, training matters more.** Best by size:

| Size | Best open model | Index | Best inference technique at that size |
|---|---|---|---|
| 25–36B | Surogate Rune 26B-A4B v3 | 57.4 | Decider chat · Gemma-4-31B, 57.3 |
| 5–13B | Winnow-12B | 50.0 | — (none entered) |
| 1.5–5B | Decider 4B | 40.7 | Jobe (Qwen3.5-4B), 32.4 |
| < 1.5B | JPT-0.8B | 19.2 | — |

At 4B the trained models lead the stock-model tricks by about 8 points.

**4. Where Jev still wins, and where it loses.**

- Jev leads clearly on **Knowledge & Reasoning** (51 vs best open 44).
- Open models already beat Jev on **Retrieval & Classification** (64 vs 55),
  **Tools** (AutoJev 79 vs 75) and **Arts & Taste** (Rune 42 vs 38).

**5. Small encoders are not general decision models.** GLiNER, ModernBERT and similar
encoders (Laya, Verdict, jeff, Decision 1.0 Kai/Lex) score 2–11 here, close to
chance. They can still be fast and useful for a narrow, fixed task you train them
on, but not as a general Jev replacement.

## Calibration: can you trust the probabilities?

Jev's main selling point is *calibrated* probabilities: when it says 80%, it should
be right about 80% of the time. **ECE** (expected calibration error) measures the gap
between stated confidence and actual accuracy. Lower is better; 0 is perfect.

- Jev on this benchmark: **ECE 0.074** (says 81% confident on average, is right 74%).
- **17 open models have a lower ECE than Jev here**, e.g. Jebadiah 27B 0.014,
  Xor 0.015, AutoJev-27B 0.018, Decider chat · Qwen3.6-27B 0.021, reflex 27B 0.024.
- Techniques that read raw logits without any calibration step tend to be poorly
  calibrated (openvons 0.37, mini-jev 0.35, diffusion routes 0.20–0.23).

Caveats from independent studies:

- Confidence does not reliably flag *individual* errors, even when the average
  calibration looks good ([jev-on-a-laptop](https://github.com/rorshopping/jev-on-a-laptop)).
- Jev itself is less calibrated on unseen tasks: a refit temperature of 2.7 on
  unseen tickets vs 0.96–1.35 on public benchmarks
  ([jev-ood-calibration](https://github.com/scienthoon/jev-ood-calibration)).

## Other head-to-head numbers

These use smaller, different test sets, so they do not line up with the index:

| Study | Result |
|---|---|
| [snapjudge](https://github.com/Micha0827/snapjudge) on TypeSafe's 20 public cases (373 decisions) | stock Qwen3.8-27B 81.2% vs Jev 87.7%; level on short texts, behind on invoices |
| [jev-on-a-laptop](https://github.com/rorshopping/jev-on-a-laptop) | stock Qwen 7B 73.8% agreement vs Jev 86.6% |
| [Bespoke Nimble](https://github.com/bespokelabsai/nimble) (LoRA on Qwen3.5-9B) | 90.1% agreement with Jev vs 66.4% for base Qwen |
| [Kev](https://github.com/jaredpalmer/kev) | Kev-8B 79.6% vs Jev 85.7% out of domain |

## Limits of this comparison

- It is one community benchmark. Scores shift between editions (0.1 → 0.2 → 0.2.1
  changed benchmarks and weights within a week).
- Six interactive environments (games, web tasks) were dropped for everyone,
  because no open model has run them yet.
- Jev is a moving target: its API answers drifted between runs.
- Latency for Jev is measured over the internet; open models on a local GPU.
