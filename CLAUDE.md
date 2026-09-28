# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A single-GPU inference server where one vLLM process serves normal OpenAI chat **and**
a Jev-compatible `/v1/systemone` decision endpoint from the same loaded model, plus
scripts to calibrate, evaluate and benchmark the decision path.

Background research (read before designing anything): `docs/README.md`. Key docs:
- `docs/1-what-is-jev.md`: the Jev wire format we must match.
- `docs/5-combined-server.md`: chosen architecture and engine pitfalls.
- `docs/6-answer-compatibility.md`: exact answer semantics and `confidence` formulas.

Plan and task tracking live in DoStuff tickets (use the `dostuff-tickets` skill).
Design specs go in `docs/superpowers/specs/`.

## Working conventions (from the repo owner)

- Code must read like a tutorial: small focused files, obvious names, and a flow that
  can be explained quickly. Never trade correctness or performance for this.
- Comments: at most two lines. Needing more means the code is too complex; simplify it.
- Commit messages: caveman style (`caveman:caveman-commit` skill), Conventional Commits,
  subject ≤ 50 chars.
- Ask the owner when unsure or when a decision is theirs to make.
- Orchestration: the main agent plans, delegates and reviews all code. Routine,
  well-specified tasks go to Sonnet subagents; complex or subtle work goes to Opus
  subagents.
- Web research: Firecrawl CLI; raw output goes in `.firecrawl/` (git-ignored).

## Hard-won facts (verified during research, Sept 2026)

- **Decision readout:** render each question with the model's chat template (thinking
  off), end at the answer slot (`Answer: (`), then call vLLM `/v1/completions` with
  `max_tokens: 1`, `temperature: 0`, `logprob_token_ids: [letter ids]`,
  `return_tokens_as_token_ids: true`. Softmax the returned logprobs over the letters,
  divided by a fitted temperature.
- **Where vLLM returns the label logprobs:**
  `choices[i].logprobs.top_logprobs[0]["token_id:<id>"]`.
- **Letters must be single tokens *in context*:** check that
  `encode(prompt + "A") == encode(prompt) + [id_A]` at startup.
- **Jev answer contract:**
  - `noul` is a float P(true) with no `confidence` field.
  - `score` is the probability-weighted level, with a `legend`.
  - `confidence` uses TypeSafe's formulas: choice `(p_max − 1/K)/(1 − 1/K)`; score is
    mode-distance based. See `typesafe-ai/system-one-adapter-python`, file
    `confidence_metrics.py`.
- **vLLM limits and open bugs:**
  - `logprob_token_ids` is capped at 128 ids per request (`MAX_LOGPROB_TOKEN_IDS`).
  - Speculative decoding plus label scoring can crash vLLM (issue #42592).
  - Top-k logprobs of co-batched requests can become `-inf` (PR #51789).
  - LoRA may be a silent no-op on Qwen3.5/3.6 hybrid models (issue #49354).
- **Do not use SGLang for mixed chat and decision traffic:** its scheduler crashes on
  mixed logprob batches (issue #34719).
- **Temperature is tied to one setup.** A fitted temperature is valid only for one
  model + precision + prompt layout. Refit after any change.
- **Never train or calibrate on Jev API outputs.** TypeSafe's customer agreement forbids
  distillation and imitation. Calibrate on labelled public or our own data.

## Environment

- 1× RTX PRO 6000 Blackwell (96 GB, sm_120), WSL2, CUDA 13.x.
- Owner's other projects run vLLM via Docker Compose on `vllm/vllm-openai` images, with
  ports bound to `127.0.0.1` and the HF token passed as a secret.
