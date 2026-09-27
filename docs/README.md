# Jev and its open reproductions

Research snapshot, **26 September 2026**. This area changes daily; check dates before
relying on the numbers.

## TL;DR

- **Jev** (TypeSafe AI, launched 15 Sep 2026) is a closed, hosted *decision* model. You
  send a piece of context plus many typed questions. It returns a probability for every
  answer in ~100 ms, for $0.042 per million input tokens. It cannot chat or write text.
- **Open reproductions copy the interface, not the model.** Jev's weights and its RLCD
  training method are not public. Most projects speak Jev's `/v1/systemone` wire
  format, so the official SDKs work against them.
- **The best open models roughly tie Jev** on the community
  [Decision Index](https://huggingface.co/spaces/multimodalart/jev-decision-index):
  57.4 and 57.3 vs Jev's 57.9. Jev still leads on knowledge/reasoning and on long
  documents. Many open models are *better calibrated* than Jev on that benchmark.
- **The "inference technique" needs no training.** A stock LLM is stopped right before
  it writes an answer letter, and the probabilities of `A`, `B`, `C`… are read off. It
  ties Jev at ~30B (stock Gemma 4 31B: 57.3) but falls behind trained models at 4B.
- **One server for chat and decisions: yes, on your 96 GB GPU.** Recommended:
  - **vLLM** serving a stock **Qwen3.6-27B** (or Gemma 4 31B), which handles chat;
  - a small **gateway** that adds `/v1/systemone` using the letter-probability trick.

  The model is unchanged, so chat quality is unaffected.
- **Same answer types, mostly different confidence.** Most Jev-style servers return
  the same `choice` / `score` / `noul` shapes. `noul` is a probability, not a boolean,
  as in Jev. But only 4 of ~25 audited servers (decider, Kev, AutoJev, surogate) compute
  `confidence` with Jev's formula. Recompute it yourself from `probabilities`.
- **Watch-outs:**
  - Calibrate on your own labelled data. TypeSafe's terms forbid training on Jev's outputs.
  - Avoid SGLang for mixed chat + decision traffic (open crash bug).
  - Don't enable speculative decoding on the shared vLLM server.

## Documents

| # | Doc | Read it for |
|---|---|---|
| 1 | [What is Jev?](1-what-is-jev.md) | The idea, the API, limits, calibration findings, what's known about how it works |
| 2 | [The open reproductions](2-open-reproductions.md) | The five kinds of project and the strongest of each |
| 3 | [How they compare to Jev](3-leaderboard.md) | Scores, calibration and latency vs Jev, on your GPU model |
| 4 | [The inference technique](4-inference-technique.md) | How the no-training trick works, the projects, pitfalls |
| 5 | [One server for chat + decisions](5-combined-server.md) | Options ranked, and a step-by-step build for your RTX PRO 6000 |
| 6 | [Same answers as Jev?](6-answer-compatibility.md) | Source-code audit of answer shapes, `noul`, and `confidence` across ~25 servers |
| – | [Sources](sources.md) | Links, plus open engine bugs to track |
| – | [Appendix](appendix/) | Detailed research notes with citations |

## Glossary

| Term | Meaning |
|---|---|
| **State** | The input to decide about: a ticket, a document, game state as JSON |
| **choice / score / noul** | Jev's three question types: pick one option / rate on a scale / yes-no probability |
| **Wire format** | The exact JSON request/response shape of Jev's `/v1/systemone` API |
| **Calibration** | Whether stated probabilities match reality (80% confident → right 80% of the time) |
| **ECE** | Expected calibration error: the average gap between confidence and accuracy. Lower is better; 0 is perfect |
| **Temperature (T)** | One number that softens or sharpens probabilities (`softmax(logits / T)`), fitted on labelled data to fix calibration. It never changes which answer wins |
| **Skill score** | The Decision Index score: 0 = random guessing, 100 = perfect |
| **Prefill / KV cache** | Processing the input once and keeping the result, so many questions can reuse it |
| **Logits / logprobs** | The model's raw scores / log-probabilities for each possible next token |
| **Sidecar** | A small program next to an inference server that adds an API without loading its own copy of the model |
| **LoRA** | A small trainable add-on to a frozen model; can be switched on per request |
| **RLCD** | "Reinforcement Learning for Calibrated Decisions", TypeSafe's unpublished training method |
