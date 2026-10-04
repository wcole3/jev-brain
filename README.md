# jev-brain

One GPU, one model, two APIs. A single vLLM process serves normal OpenAI-style chat,
and a small gateway adds a Jev-compatible `/v1/systemone` decision endpoint from the
same loaded model.

- **Chat:** `POST /v1/chat/completions` (thinking on by default).
- **Decisions:** `POST /v1/systemone`, TypeSafe's Jev wire format. Typed `choice`,
  `score` and `noul` questions about a shared `state`, answered with probabilities.

Background research is in [docs/README.md](docs/README.md), the design in
[docs/superpowers/specs/](docs/superpowers/specs/2026-09-28-systemone-server-design.md).

## Where it stands

JevBench, all 1682 gold rows, 2026-09-30. Stock models, bf16, before our own fit (qwen3.6 at
decider's T = 1.943). Accuracy in %; ECE is calibration error (lower is better):

| Model | Overall | Choice | Noul | ECE | p50 latency |
|---|---|---|---|---|---|
| Jev (`jev-1.13.0`, hosted API) | 91.2 | 92.0 | 95.7 | 0.028 | 152 ms (network included) |
| gemma-4-31b | 87.0 | 91.9 | 87.5 | 0.126 | 63 ms |
| qwen3.8-27b | 86.4 | 90.4 | 86.2 | 0.033 | 81 ms |
| qwen3.6-27b | 84.3 | 91.9 | 83.5 | 0.053 | 83 ms |

Since then `header` is the default layout for all three profiles (owner, 2026-10-04; full Index
confirmation in [docs/results/archive/m3-recommendations.md](docs/results/archive/m3-recommendations.md)).
Choice is level with Jev; most of the gap is in noul and score. Details and caveats:
[docs/results/archive/jevbench-vs-jev.md](docs/results/archive/jevbench-vs-jev.md).

Phase 2, decision index. Our latest full Index and latency run per profile, next to the
matching Decision Index 0.2.1 board entries (`scripts/phase2_report.py --readme` rebuilds
the table). ECE and latency are measured differently from the board's; see the run summaries:

<!-- phase2-table -->
| entry | Index | ECE | coverage | median ms | p95 ms | run layout / orders | run calibration | shipped now | latency run |
|---|---|---|---|---|---|---|---|---|---|
| **qwen3.6-27b** | 55.92 | 0.042 | 1.000 | 95.7 | 583.2 | header / identity | T=1.63/1.96/1.28 | header / identity / v6 | 2026-10-03T142353Z-latency |
| Decider chat · Qwen3.6-27B | 51.35 | 0.021 | board | 83.6 | n/a | | | | |
| **gemma-4-31b** | 60.61 | 0.122 | 1.000 | 105.7 | 614.8 | header / identity | T=4.26/5.6/7.61 | header / identity / v3 | 2026-10-04T014354Z-latency |
| Decider chat · Gemma-4-31B | 57.33 | 0.047 | board | 108.5 | n/a | | | | |
| **qwen3.8-27b** | 56.01 | 0.023 | 1.000 | 94.2 | 580.3 | header / identity | T=1.54/1.78/0.963 | header / identity / v3 | 2026-10-04T024731Z-latency |
| simple-jev · Qwen3.8-27B | 55.70 | 0.113 | board | 373.0 | n/a | | | | |
| reflex 27B | 52.20 | 0.024 | board | 108.0 | n/a | | | | |
| Jevfire (Qwen3.8-27B-FP8) | 49.40 | 0.052 | board | 89.6 | n/a | | | | |

- Calibration T is listed as choice/score/noul; b is the noul yes-offset.
<!-- /phase2-table -->

## Requirements

- An NVIDIA GPU with ~96 GB of memory (built on an RTX PRO 6000 Blackwell) and a recent
  driver, plus Docker with the NVIDIA container toolkit.
- [uv](https://docs.astral.sh/uv/) for the Python side (tests, scripts). Python 3.12 is
  pinned in `.python-version`.
- Disk for model weights in `~/.cache/huggingface` (~55–60 GB per model). You download them
  on the host; the containers mount this cache read-only, so they never write there.

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
uv run python scripts/fetch_model.py --profile qwen3.6-27b        # once per model: the pinned revision, ~55–60 GB
docker compose --env-file profiles/qwen3.6-27b.env up -d --build
docker compose --env-file profiles/qwen3.6-27b.env logs -f vllm   # watch the model load
curl -s localhost:9000/health                                     # {"status":"ok","profile":"qwen3.6-27b",...}
```

- The gateway listens on `127.0.0.1:9000` and vLLM on `127.0.0.1:8000`. Clients talk to
  the gateway.
- A start takes up to ~10 minutes (weight load and graph capture); about 4 when the
  weights are still in memory from a recent run.
- To switch models, stop the running profile first:

  ```bash
  docker compose --env-file profiles/qwen3.6-27b.env down
  docker compose --env-file profiles/gemma-4-31b.env up -d --build
  ```

- **Decision length cap:** `SYSTEMONE_MAX_LEN` (default 32,768, or `MAX_MODEL_LEN` if smaller)
  caps `/v1/systemone` prompts separately from chat. Long decisions compete with chat and
  coding agents for KV cache and prefill, so keep it below `MAX_MODEL_LEN` unless you need
  them. Over the cap is a 422 "maximum context length".
- `HF_TOKEN` in your shell raises Hugging Face rate limits for `fetch_model.py`.
- If host tools report `Permission denied` in the HF cache (older setups let the vLLM
  container write there as root), fix it once with `sudo chown -R $USER: ~/.cache/huggingface`.

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

```python
TypeSafeClient(api_key="local", base_url="http://127.0.0.1:9000", timeout=120)
```

- **Timeout:** the SDK's default is 10 s, and it retries twice on timeouts and 5xx
  errors. Large requests (many questions × many options, long states) can take longer,
  so raise `timeout`.
- **Abandoned requests:** when a client gives up, the gateway cancels its work and vLLM
  stops too, so retries don't pile up on the GPU.

### Errors

Every error body is `{"error": {"message": "..."}}`.

| Status | When |
|---|---|
| 400 | Chat body is not a JSON object |
| 401 | Missing or wrong gateway key (with `WWW-Authenticate: Bearer`) |
| 404 / 405 | Unknown path or method |
| 422 | Invalid request, or over a capacity limit (too many options, levels or tokens) |
| 499 | The client disconnected; the work was cancelled (nobody receives this) |
| 500 | Unexpected error; the message carries a `request_id` for the gateway log |
| 503 / 504 | vLLM is unreachable / timed out |

## Security

The defaults suit a single workstation: both ports bind to `127.0.0.1` and no keys are
needed.

- **`GATEWAY_API_KEY`:** requires `Authorization: Bearer <key>` on the gateway's `/v1/*`.
  `/health` stays open.
- **`VLLM_API_KEY`:** vLLM then requires that key on its own `/v1/*`, and the gateway sends
  it automatically. vLLM's `/health`, `/metrics`, `/version` and `/tokenize` stay open,
  so never publish port 8000 beyond loopback.
- **Where to set them:** in your shell, or in a git-ignored `.env` passed as a second env
  file. A `.env` alone is ignored when `--env-file` is given:

  ```bash
  docker compose --env-file profiles/qwen3.6-27b.env --env-file .env up -d --build
  ```

- **Already in place:**
  - API docs (`/docs`, `/openapi.json`) are off.
  - The passthrough never forwards the client's `Authorization` to vLLM.
  - Keys never appear in logs.
  - Images are pinned by digest.
  - Both services restart on failure (up to 3 times). A clean Docker restart leaves them
    stopped, but after a crash (e.g. WSL going down mid-run) Docker brings a running stack
    back on its own. Run `docker compose ... down` if you need the GPU free.
- **Before exposing the gateway beyond localhost:**
  - set both keys;
  - publish only the gateway port (edit its `127.0.0.1:9000:9000` binding);
  - put a TLS proxy in front, since the gateway speaks plain HTTP.

## Tests

| What | Command | Needs |
|---|---|---|
| Unit tests | `uv run pytest -q` | CPU only. Downloads tokenizers once. |
| One test | `uv run pytest tests/unit/test_prompts.py::test_rows_share_the_reported_prefix -q` | CPU |
| Parity with decider | `uv run pytest tests/parity -q` | CPU. Committed fixtures. |
| Live end-to-end | `uv run pytest -m live tests/live -v` | A running, idle stack |
| Lint | `uv run ruff check .` | |

- **Live tests cover:**
  - the official SDK quickstart;
  - capacity limits (422 errors);
  - streaming chat with reasoning;
  - answer stability under chat load;
  - prefix-cache hits;
  - vLLM stopping work when a client gives up.
- **Targets:** `GATEWAY_URL` (default `http://127.0.0.1:9000`) and `VLLM_URL` (default
  `http://127.0.0.1:8000`). The tests skip if the gateway isn't up, and send
  `GATEWAY_API_KEY` when it is set.
- **Parity test:** proves the `decider_chat` prompt layout reproduces decider's
  tokens exactly. To regenerate its fixtures (rarely needed), use a separate venv, because
  decider pins `numpy<2`:

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
- **vLLM's view of each phase:** the bench samples vLLM's `/metrics` (`--vllm`, default
  `VLLM_URL` or `http://127.0.0.1:8000`) and adds one table row per phase:
  - KV cache peak and mean use, waiting-queue peak, preemptions;
  - prompt tokens, how many came from the prefix cache, generation tokens;
  - the Jev-style `usage.input_tokens` the gateway reported.

  Computed (uncached) tokens close to usage means prefix sharing works; far above it
  means cache misses. vLLM's counters are server-wide, so run on an otherwise idle
  stack. Gauge samples go to `raw.jsonl` for plots.
- **`--profile` must match the running gateway**; the bench refuses otherwise. It sends
  `GATEWAY_API_KEY` when set.
- **Results** go to `docs/results/<profile>/<UTC timestamp>[-jevbench]/` (full runs) or
  `docs/results/archive/<profile>/<UTC timestamp>-quick/` (`--quick`), so several runs a day
  never collide:
  - `raw.jsonl` with every request;
  - `summary.md` with provenance (commit, model revision, layout, vLLM version, JevBench
    SHA) and the tables.

### Against the official Jev API

`--target jev` runs only JevBench, with the same request mapping and scoring as the
gateway runs.

- **Key:** from `TYPESAFE_API_KEY`, else `secrets/.jev-key` (git- and docker-ignored).
- **Cost:** a full pass is ~0.9M input tokens, about $0.04. The summary reports the
  actual tokens and estimated cost.
- **Outputs:** the summary goes to `docs/results/jev/`. Jev's per-row answers stay in
  `.cache/jev-results/`.
- **Terms:** TypeSafe's terms forbid using Jev outputs to train or calibrate a similar
  model. Never feed them into calibration or prompt tuning.

## Phase 2: evaluation (DS-002)

Design: [docs/superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md](docs/superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md).
Long runs (suite rebuild, collect, full Index) take hours; plan them.
To run them on a rented GPU box (vast.ai), see [docs/remote-gpu.md](docs/remote-gpu.md).

```bash
uv run python scripts/index_suite.py setup     # pinned harness clone + venv in .cache/
uv run python scripts/index_suite.py rebuild   # ~7 GB download, 17 GB scratch; HF token in secrets/.hf-token (HLE is gated)
uv run python scripts/index_suite.py export    # scoreable 0.2.1 rows -> .cache/decision-index/rows-0.2.1.jsonl.gz
uv run python scripts/splits.py                # data/splits/*.json (committed)

uv run python scripts/collect.py --profile qwen3.6-27b --split eval       # raw letter logprobs, stack up
uv run python scripts/calibrate.py --profile qwen3.6-27b                  # fit T (+ noul offset) on calib, judge on eval; CPU only
uv run python scripts/evaluate.py offline --profile qwen3.6-27b --split eval --orders identity+reversed
uv run python scripts/evaluate.py index --profile qwen3.6-27b             # full Index via the upstream harness, 8 shards
uv run python scripts/evaluate.py replace --profile qwen3.6-27b --base RUN_DIR --override RUN_DIR  # swap re-run rows into an Index run
uv run python scripts/latency.py --profile qwen3.6-27b                    # latency-v1 design, one sequential client
uv run python scripts/evaluate.py lengths --profile qwen3.6-27b --baseline RUN_DIR  # rows the decision cap refuses
```

- **Data:**
  - **Index rows are never used for fitting.**
  - Calibration and evaluation splits come from JevBench gold and filtered DecisionBench
    (public gold only), 50/50 by hash; all questions about one state go to the same split.
  - Jev's outputs are never read.
- **Offline vs live:** `collect.py` uses the gateway's own code, so offline answers equal
  live ones within bf16 noise (`tests/live/test_offline_matches_live.py`).
- **Results:** top level of `docs/results/<profile>/` holds only benchmark runs: bench full and
  `-jevbench` runs, and full `<timestamp>-index` runs. Everything else (`offline-...`,
  `calibrate`, `latency`, `lengths`, `m3-*`, subset Index runs, host compares, experiments,
  reports) goes to `docs/results/archive/<profile>/<timestamp>-.../summary.md`.
  Large run data stays in `.cache/` (`collect/`, `index-runs/`).

## When you change prompts or tokenizers

Prompt wording lives only in `prompts/<layout>.toml`. Label tables in
`data/<profile>/<layout>/labels.json` are tied to the exact tokenizer and layout text, and
the gateway refuses to start if they don't match. After editing a layout, rebuild the
tables for every profile and restart:

```bash
uv run python scripts/build_labels.py --profile qwen3.6-27b   # repeat per profile
```

A layout change also invalidates its calibration
(`data/<profile>/<layout>/calibration.json`); the gateway refuses the stale file and names
the changed field. Move the stale file aside (the gateway then runs that layout at T = 1),
recollect the calib and eval splits (`collect.py` ignores calibration files), then rerun
`uv run python scripts/calibrate.py --profile <profile>`.

## Repository map

| Path | What |
|---|---|
| `gateway/` | FastAPI gateway: `/v1/systemone` flow (`decide.py`), chat proxy (`chat.py`), disconnect cancellation (`disconnect.py`) |
| `prompts/` | Prompt layouts (`header` default for all profiles, `decider_chat`, `question_first`) |
| `profiles/` | One env file per model |
| `data/` | Label tables and calibration per profile/layout; benchmark corpus |
| `scripts/` | `fetch_model.py`, `build_labels.py`, `bench.py` (+ `bench_data.py`, `bench_report.py`), `decider_fixtures.py`; phase 2: `index_suite.py`, `splits.py`, `collect.py`, `calibrate.py` (+ `fit.py`, `calibrate_report.py`), `evaluate.py`, `latency.py` (+ helpers) |
| `data/splits/` | Committed calibration, evaluation, index-dev and latency-v1 row ids |
| `tests/` | `unit/`, `parity/`, `live/` |
| `docker/`, `compose.yaml` | vLLM entrypoint, gateway image, stack definition |
| `docs/` | Research, spec, plan, benchmark results |
