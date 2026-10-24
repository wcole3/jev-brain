# CLAUDE.md

**jev-brain:** one vLLM process serves OpenAI chat and a Jev-compatible `/v1/systemone`
decision endpoint from the same model, behind a small FastAPI gateway.

- **Running, models, results, security:** `README.md`. **Tests, benchmarks, evaluation:**
  `docs/development.md`.
- **Deep dives** (how things work, with our measurements): `docs/background/`.
- **Research:** `docs/README.md`. Jev wire format in `docs/1-what-is-jev.md`, answer
  semantics and `confidence` formulas in `docs/6-answer-compatibility.md`.
- **Tickets:** DoStuff (`dostuff-tickets` skill).
- **Specs:** `docs/superpowers/specs/`.

## Working conventions (from the repo owner)

- Code reads like a tutorial: small focused files, obvious names, a flow that can be
  explained quickly. Never trade correctness or performance for this.
- Comments: at most two lines. Needing more means the code is too complex; simplify it.
- Commits:
  - caveman style (`caveman:caveman-commit` skill), Conventional Commits, subject ≤ 50
    chars;
  - stage explicit paths, never `git add -A`: label tables and bench results are committed
    deliberately per profile.
- Ask the owner when unsure or when a decision is theirs to make.
- Orchestration: the main agent plans, delegates and reviews all code. Routine tasks go to
  Sonnet subagents; complex or subtle work goes to Opus subagents.
- Web research: Firecrawl CLI; raw output goes in `.firecrawl/` (git-ignored).

## Commands

`uv run pytest -q` (unit), `uv run pytest tests/parity -q`, `uv run pytest -m live tests/live -v`
(stack up and idle), `uv run ruff check .`. `make help` lists the make targets. Everything else is
in `README.md` and `docs/development.md`.

## Architecture

- `gateway/decide.py` is the whole `/v1/systemone` flow, one module per step:
  1. `questions.render_question`
  2. `orders.option_orders`
  3. `prompts.build_rows` (token ids built piecewise, like decider)
  4. `readout.Readout` (vLLM `/v1/completions`, `max_tokens=1`, `logprob_token_ids`)
  5. `orders.average_back` (raw logprobs, caller order)
  6. `decide.probabilities` (combine: one softmax at per-type T, noul offset b, from the calibration file)
  7. `answers.answer`
- **Prompt wording** lives only in `prompts/<layout>.toml`. Editing it means rebuilding
  label tables and rerunning `scripts/calibrate.py` (the gateway refuses stale hashes and
  stale calibration stamps).
- **Other gateway pieces:**
  - `chat.route()` is the phase-3 hook where systemone answers will steer chat;
  - `disconnect.py` cancels abandoned work so vLLM aborts it.

## Easy to get wrong

- **Never train, calibrate or tune on Jev API outputs** (TypeSafe's terms forbid it).
  - Use JevBench gold labels or our own data.
  - Jev's per-row answers stay in `.cache/jev-results/`.
- **Calibration** (`data/<profile>/<layout>/calibration.json`, or
  `calibration-<prefix_block>.json` when present) is valid for one model + precision +
  layout + option-order setting.
  - With the reads fixed, T never changes the top answer (logprobs are averaged first), but it
    moves `score` values (expected level). A `top_p` gate uses the identity fit's T to pick which
    questions get a second read, so that T can change answers.
  - T can't fix a yes/no bias; the noul offset b can, and can flip a close noul answer.
  - Fits use the calib split; eval picks what ships, so eval is not untouched.
  - A stale stamp stops the gateway, not collect: move the file aside, recollect, recalibrate.
- **Label letters** must be single tokens *in context*. `scripts/build_labels.py` checks
  this; gateway startup only checks hashes.
- **vLLM limits and bugs:**
  - `logprob_token_ids` takes ≤128 ids per request;
  - MTP with label scoring needs our patched rejection sampler (`docker/vllm/`, DS-004;
    upstream PR #61219 open): stock v0.32 returns HTTP 500 on `/v1/completions` and top-k
    instead of the label ids on `/inference/v1/generate` for label-id rows batched with drafts;
  - co-batched top-k logprobs can be `-inf` (#51789);
  - LoRA can be a silent no-op on Qwen hybrids (#49354);
  - `--max-num-seqs 256` is required for hybrid Qwen (Mamba cache blocks);
  - vLLM 0.32 streams thinking in the delta key `reasoning`;
  - `/inference/v1/generate` logprobs carry integer `token_id`s since 0.32 (#58181).
- **vLLM image:** v0.32.0 pinned by digest, with `docker/vllm/*.py` mounted over it. Each
  `.diff` beside them is the change; an image bump means rebasing both files.
- **SGLang:** don't use it for mixed chat + decision traffic (#34719).
- **bf16 noise:** decision probabilities move ~0.03/T under load. The stability test warns
  above 0.05 and fails only if the top answer flips when the top-two gap > 0.10.
- **Chat contention:** decision prefill starves chat decode (DS-007). A long chat prefill
  stalls decisions unless `--long-prefill-token-threshold` is set; on hybrid Qwen keep
  budget − threshold > one block or a decision blocks the queue (DS-025). Since 0.31 stock
  vLLM skips the cap for a lone request (#57951; gemma: a decision behind a lone 24k chat
  prefill waits 4.1 s, not 0.67 s); `docker/vllm/scheduler.py` restores it (#60476).
- **Prefix cache:** hybrid Qwen caches in 784-token blocks, 800 with MTP; the Qwen profiles
  pad to 800 and cap prefill at 800, or prompts ≥ 784 tokens take an extra step (DS-008, DS-004).
- **Tokenizer calls:** encode many short texts in one call (`prompts.encode_each`); the
  per-call overhead in transformers dominates.
- **Abort metrics:** client aborts don't appear in vLLM's `request_success_total`; watch
  the `num_requests_running`/`waiting` gauges.
- **Gemma 4 31B** is KV-bound: ~9,950 blocks, ~144k tokens for one prompt, with or without
  the vision tower. vLLM's logged "KV cache size" moves with `MAX_MODEL_LEN` (DS-026). An
  fp8 KV cache is the lever (DS-005).

## Environment

- 1× RTX PRO 6000 Blackwell (96 GB, sm_120), WSL2, CUDA 13.x.
- Weights are fetched on the host (`scripts/fetch_model.py`). Containers mount the HF
  cache read-only and offline.
- Ports bind to `127.0.0.1`. vLLM's `/health`, `/metrics`, `/version` and `/tokenize` stay
  open even with `VLLM_API_KEY`, so port 8000 must never be published (DS-012 waiver;
  `scripts/check_bind.py` refuses it). vLLM 0.32 also serves its own uncalibrated
  `/v1/systemone` on 8000, behind `VLLM_API_KEY`.
