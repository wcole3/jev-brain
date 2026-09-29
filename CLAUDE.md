# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

**jev-brain**: a single-GPU inference server where one vLLM process serves normal OpenAI chat **and**
a Jev-compatible `/v1/systemone` decision endpoint from the same loaded model, plus
scripts to calibrate, evaluate and benchmark the decision path.

Background research (read before designing anything): `docs/README.md`. Key docs:
- `docs/1-what-is-jev.md`: the Jev wire format we must match.
- `docs/5-combined-server.md`: chosen architecture and engine pitfalls.
- `docs/6-answer-compatibility.md`: exact answer semantics and `confidence` formulas.

Plan and task tracking live in DoStuff tickets (use the `dostuff-tickets` skill).
Design specs go in `docs/superpowers/specs/`.

## Commands

- Install: `uv sync`
- Unit tests (CPU): `uv run pytest -q`; a single test: `uv run pytest tests/unit/test_prompts.py::test_rows_share_the_reported_prefix -q`
- Parity with decider: `uv run pytest tests/parity -q` (fixtures from `scripts/decider_fixtures.py`, run in `.cache/decider-venv`)
- Live tests (stack running): `uv run pytest -m live tests/live -v`
- Lint: `uv run ruff check .`
- Label tables (after any tokenizer or `prompts/*.toml` change): `uv run python scripts/build_labels.py --profile <p>`
- Run a model: `docker compose --env-file profiles/<p>.env up -d --build` (compose project is pinned to `jev-brain`; gateway :9000, vLLM :8000). Switching models: `docker compose --env-file profiles/<old>.env down` first.
- Benchmark: `uv run python scripts/bench.py --profile <p> [--quick] [--jevbench-only] [--chat]` — the default measures only `/v1/systemone`; `--chat` adds chat alone + chat under systemone load (on demand until DS-007 is fixed).
- Jev reference: `uv run python scripts/bench.py --target jev` (key from `TYPESAFE_API_KEY` or `secrets/.jev-key`). Jev per-row answers stay in `.cache/jev-results/`; never use them for calibration or prompt tuning.
- Stage explicit paths when committing (`git add <paths>`), never `git add -A` — generated label tables and bench results are committed deliberately per profile.

## Architecture

- `gateway/decide.py` is the whole `/v1/systemone` flow, in order:
  1. `questions.render_question` turns each question into option texts;
  2. `orders.option_orders` chooses the option orders;
  3. `prompts.build_rows` builds the token ids piecewise (chat frame + layout parts);
  4. `readout.Readout` asks vLLM `/v1/completions` with `max_tokens=1` and `logprob_token_ids`;
  5. `calibration.softmax` applies the temperature;
  6. `orders.average_back` maps probabilities back to the caller's options;
  7. `answers.answer` builds the Jev answer.
- Prompt wording lives only in `prompts/<layout>.toml`. Editing it requires rebuilding the labels (the gateway refuses stale hashes) and refitting temperatures.
- `chat.route()` is the phase-3 hook where systemone answers will steer chat requests.

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
- **Letters must be single tokens *in context*:** `scripts/build_labels.py` checks that
  `encode(prompt + "A") == encode(prompt) + [id_A]`. Gateway startup only verifies the
  stored tokenizer and layout hashes, not this in-context property.
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
- `--max-num-seqs 256` is required: vLLM's default 1024 exceeds the hybrid Qwen models'
  Mamba cache blocks (638 at 0.90) and startup fails.
- vLLM 0.30 streams thinking tokens in the delta key `reasoning` (older versions
  `reasoning_content`).
- Systemone decisions are bf16-noisy under load: probabilities can move ~0.03 (one bf16
  logit step); the live stability test allows 0.05 and requires the top answer to hold
  when the top-two gap > 0.10.
- Decision prefill starves chat decode on the shared GPU (DS-007); priority scheduling
  alone fixes TTFT, not decode — see `docs/appendix/ds007-scheduling.md`.
- Hybrid Qwen prefix caching is 784-token block granular (DS-008).
- Gemma 4 31B with the vision tower resident leaves only ~50k KV tokens (1.5x
  concurrency at 32k).

## Environment

- 1× RTX PRO 6000 Blackwell (96 GB, sm_120), WSL2, CUDA 13.x.
- Owner's other projects run vLLM via Docker Compose on `vllm/vllm-openai` images, with
  ports bound to `127.0.0.1` and the HF token passed as a secret.
- vLLM's port 8000 is unauthenticated even when `GATEWAY_API_KEY` is set; loopback-only
  binding is the protection.
