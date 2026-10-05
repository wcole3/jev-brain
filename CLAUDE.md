# CLAUDE.md

**jev-brain:** one vLLM process serves OpenAI chat and a Jev-compatible `/v1/systemone`
decision endpoint from the same model, behind a small FastAPI gateway.

- **Running, testing, benchmarking, security:** `README.md`.
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
(stack up and idle), `uv run ruff check .`. Everything else is in `README.md`.

## Architecture

- `gateway/decide.py` is the whole `/v1/systemone` flow, one module per step:
  1. `questions.render_question`
  2. `orders.option_orders`
  3. `prompts.build_rows` (token ids built piecewise, like decider)
  4. `readout.Readout` (vLLM `/v1/completions`, `max_tokens=1`, `logprob_token_ids`)
  5. `decide.probabilities` (per-type T, noul offset b, from `calibration.json`)
  6. `orders.average_back`
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
- **Calibration** (`data/<profile>/<layout>/calibration.json`) is valid for one model +
  precision + layout + option-order setting.
  - With one option order T keeps the top answer, but it moves `score` values (expected
    level). Averaged orders can flip a close top answer.
  - T can't fix a yes/no bias; the noul offset b can.
  - Fits use the calib split; eval picks what ships, so eval is not untouched.
  - A stale stamp stops the gateway, not collect: move the file aside, recollect, recalibrate.
- **Label letters** must be single tokens *in context*. `scripts/build_labels.py` checks
  this; gateway startup only checks hashes.
- **vLLM limits and bugs:**
  - `logprob_token_ids` takes ≤128 ids per request;
  - no speculative decoding/MTP with label scoring (#42592);
  - co-batched top-k logprobs can be `-inf` (#51789);
  - LoRA can be a silent no-op on Qwen hybrids (#49354);
  - `--max-num-seqs 256` is required for hybrid Qwen (Mamba cache blocks);
  - vLLM 0.30 streams thinking in the delta key `reasoning`.
- **SGLang:** don't use it for mixed chat + decision traffic (#34719).
- **bf16 noise:** decision probabilities move ~0.03/T under load. The stability test warns
  above 0.05 and fails only if the top answer flips when the top-two gap > 0.10.
- **Chat contention:** decision prefill starves chat decode (DS-007). A long chat prefill
  stalls decisions unless `--long-prefill-token-threshold` is set; on hybrid Qwen keep
  budget − threshold > 784 or a decision blocks the queue (DS-025).
- **Prefix cache:** hybrid Qwen prefix caching is 784-token granular (DS-008).
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
  open even with `VLLM_API_KEY`, so port 8000 must never be published (DS-012 waiver).
