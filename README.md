# jev-brain

One GPU, one model, two APIs. A single vLLM process serves normal OpenAI-style chat,
and a small gateway adds a Jev-compatible `/v1/systemone` decision endpoint from the
same loaded model.

- **Chat:** `POST /v1/chat/completions` (thinking on by default).
- **Decisions:** `POST /v1/systemone`, TypeSafe's Jev wire format. Typed `choice`,
  `score` and `noul` questions about a shared `state`, answered with probabilities.

Background research is in [docs/README.md](docs/README.md), the design in
[docs/superpowers/specs/](docs/superpowers/specs/2026-09-28-systemone-server-design.md).

## Requirements

- An NVIDIA GPU with ~96 GB of memory (built on an RTX PRO 6000 Blackwell) and a recent
  driver, plus Docker with the NVIDIA container toolkit.
- [uv](https://docs.astral.sh/uv/) for the Python side (tests, scripts). Python 3.12 is
  pinned in `.python-version`.
- Disk for model weights in `~/.cache/huggingface` (~55–60 GB per model). The containers
  mount this cache, so weights download once and are shared with the host.

```bash
uv sync      # install the gateway, scripts and test dependencies
```

## Run a model

Each model is a profile in `profiles/`. Only one runs at a time.

| Profile | Model |
|---|---|
| `qwen3.6-27b` | Qwen/Qwen3.6-27B |
| `qwen3.8-27b` | Qwen/Qwen3.8-27B |
| `gemma-4-31b` | google/gemma-4-31B-it |

```bash
docker compose --env-file profiles/qwen3.6-27b.env up -d --build
docker compose --env-file profiles/qwen3.6-27b.env logs -f vllm   # first start downloads and loads the model
curl -s localhost:9000/health                                     # {"status":"ok","profile":"qwen3.6-27b",...}
```

- The gateway listens on `127.0.0.1:9000` and vLLM on `127.0.0.1:8000`. Clients should
  talk to the gateway.
- The first start of a model can take 20–30 minutes: download plus load. Later starts
  take about 10 minutes (weight load and graph capture).
- To switch models, stop the running profile first:

  ```bash
  docker compose --env-file profiles/qwen3.6-27b.env down
  docker compose --env-file profiles/gemma-4-31b.env up -d --build
  ```

- Optional settings:
  - `GATEWAY_API_KEY` (in your shell or a git-ignored `.env`) requires
    `Authorization: Bearer <key>` on the gateway.
  - `HF_TOKEN` raises Hugging Face rate limits.
  - vLLM's own port stays unauthenticated; binding to loopback is the protection.

### Try it

```bash
curl -s localhost:9000/v1/systemone -H 'content-type: application/json' -d '{
  "model": "jev-latest",
  "state": "My card was charged twice for one order, please refund.",
  "questions": {
    "team":   {"type": "choice", "instructions": "Which team should handle this?",
               "criteria": {"billing": null, "technical": null, "sales": null}},
    "urgent": {"type": "noul", "instructions": "Needs a reply today"}
  }}'

curl -sN localhost:9000/v1/chat/completions -H 'content-type: application/json' \
  -d '{"model": "qwen3.6-27b", "messages": [{"role": "user", "content": "Say hi"}], "stream": true}'
```

The official TypeSafe SDK works against the gateway too:
`TypeSafeClient(api_key="local", base_url="http://127.0.0.1:9000")`. Its default 10 s
timeout is short for very large requests (see DS-009), so pass `timeout=` if needed.

## Tests

| What | Command | Needs |
|---|---|---|
| Unit tests | `uv run pytest -q` | CPU only. Downloads tokenizers once. |
| One test | `uv run pytest tests/unit/test_prompts.py::test_rows_share_the_reported_prefix -q` | CPU |
| Parity with decider | `uv run pytest tests/parity -q` | CPU. Committed fixtures. |
| Live end-to-end | `uv run pytest -m live tests/live -v` | A running stack |
| Lint | `uv run ruff check .` | |

- Live tests cover:
  - the official SDK quickstart;
  - capacity limits (422 errors);
  - streaming chat with reasoning;
  - answer stability under chat load;
  - prefix-cache hits.
- Live tests target `GATEWAY_URL` (default `http://127.0.0.1:9000`) and `VLLM_URL`
  (default `http://127.0.0.1:8000`). They skip if the gateway isn't up.
- The parity test proves the default `decider_chat` prompt layout reproduces decider's
  tokens exactly.
- To regenerate its fixtures (rarely needed), use a separate venv, because decider pins
  `numpy<2`:

  ```bash
  uv venv .cache/decider-venv
  uv pip install --python .cache/decider-venv --no-deps decider-ai==1.5.0
  uv pip install --python .cache/decider-venv transformers jinja2 "numpy<2" huggingface_hub
  .cache/decider-venv/bin/python scripts/decider_fixtures.py --profile qwen3.6-27b
  ```

## Benchmarks

Run these against a running stack. The benchmark measures through the gateway, so it sees
what clients see.

```bash
uv run python scripts/bench.py --profile qwen3.6-27b                  # full run, ~25–40 min
uv run python scripts/bench.py --profile qwen3.6-27b --quick          # smaller grid, a few minutes
uv run python scripts/bench.py --profile qwen3.6-27b --jevbench-only  # accuracy only, ~5 min
uv run python scripts/bench.py --profile qwen3.6-27b --chat           # also measure chat alone and under decision load
uv run python scripts/bench.py --target jev                           # JevBench against the official Jev API
```

- **Default run:** only `/v1/systemone`.
  - A cold sweep over state length × questions × options, with a unique state per
    request so it can't reuse another request's cached prefix.
  - A warm run that repeats the same state.
  - Throughput at 1, 4 and 16 clients.
  - The JevBench gold set.
- **JevBench** is pinned to upstream commit `fcec62f` (1682 gold rows). Its table uses the
  upstream board's columns: overall, choice and noul accuracy, plus QWK and MAE for
  ordinal score rows. A failed request counts as a wrong answer, as upstream does.
- **`--chat` is on demand** until chat/decision contention is fixed (DS-007).
- **`--profile` must match the running gateway**; the bench refuses otherwise. It sends
  `GATEWAY_API_KEY` when set, as do the live tests.
- **Results** go to `docs/results/<profile>/<date>[-quick][-jevbench]/`: `raw.jsonl` with
  every request, and `summary.md` with provenance (commit, model revision, layout, vLLM
  version, JevBench SHA) and the tables.

### Against the official Jev API

`--target jev` runs only JevBench, with the same request mapping and scoring as the
gateway runs.

- **Key:** from `TYPESAFE_API_KEY`, else `secrets/.jev-key` (git- and docker-ignored).
- **Cost:** a full pass is ~0.9M input tokens, about $0.04.
- **Outputs:** the summary goes to `docs/results/jev/`. Jev's per-row answers stay in
  `.cache/jev-results/`.
- **Terms:** TypeSafe's terms forbid using Jev outputs to train or calibrate a similar
  model. Never feed them into calibration or prompt tuning.

## When you change prompts or tokenizers

Prompt wording lives only in `prompts/<layout>.toml`. Label tables in
`data/<profile>/<layout>/labels.json` are tied to the exact tokenizer and layout text, and
the gateway refuses to start if they don't match. After editing a layout, rebuild the
tables for every profile and restart:

```bash
uv run python scripts/build_labels.py --profile qwen3.6-27b   # repeat per profile
```

A layout change also invalidates its fitted temperatures
(`data/<profile>/<layout>/calibration.json`). Phase 2 refits them.

## Repository map

| Path | What |
|---|---|
| `gateway/` | FastAPI gateway: `/v1/systemone` flow (`decide.py`), chat proxy (`chat.py`) |
| `prompts/` | Prompt layouts (`decider_chat` default, `header`, `question_first`) |
| `profiles/` | One env file per model |
| `data/` | Label tables and temperatures per profile/layout; benchmark corpus |
| `scripts/` | `build_labels.py`, `bench.py`, `decider_fixtures.py` |
| `tests/` | `unit/`, `parity/`, `live/` |
| `docker/`, `compose.yaml` | vLLM entrypoint, gateway image, stack definition |
| `docs/` | Research, spec, plan, benchmark results |
