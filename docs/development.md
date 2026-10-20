# Development

Tests, benchmarks, evaluation, prompt changes and the repository map. For running a model and
using the API, see [README.md](../README.md).

## Tests

| What | Command | Needs |
|---|---|---|
| Unit tests | `make test` or `uv run pytest -q` | CPU only. Downloads tokenizers once. |
| One test | `uv run pytest tests/unit/test_prompts.py::test_rows_share_the_reported_prefix -q` | CPU |
| Parity with decider | `make parity` or `uv run pytest tests/parity -q` | CPU. Committed fixtures. |
| Live end-to-end | `make live` or `uv run pytest -m live tests/live -v` | A running, idle stack |
| Lint | `make lint` or `uv run ruff check .` | |

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

Run these against a running stack (`make bench PROFILE=<profile>` runs the full benchmark;
`make bench PROFILE=<profile> ARGS=--quick` the smaller grid). The benchmark measures through the gateway, so it sees
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
- **Results** go to `results/<profile>/<UTC timestamp>[-jevbench]/` (full runs) or
  `results/archive/<profile>/<UTC timestamp>-quick/` (`--quick`), so several runs a day
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
- **Outputs:** the summary goes to `results/jev/`. Jev's per-row answers stay in
  `.cache/jev-results/`.
- **Terms:** TypeSafe's terms forbid using Jev outputs to train or calibrate a similar
  model. Never feed them into calibration or prompt tuning.


## Phase 2: evaluation (DS-002)

Design: [docs/superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md](superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md).
Long runs (suite rebuild, collect, full Index) take hours; plan them.
Shortcuts: `make latency PROFILE=<profile>`, `make index PROFILE=<profile> [SHARDS=4] [RUN_DIR=<dir>]`
(runs `evaluate.py index --shards N --strict`; `RUN_DIR` resumes a run) and `make report`
(`scripts/phase2_report.py --readme`, rebuilds the README results table).
To run them on a rented GPU box (vast.ai), see [docs/remote-gpu.md](remote-gpu.md).

```bash
uv run python scripts/index_suite.py setup     # pinned harness clone + venv in .cache/
uv run python scripts/index_suite.py rebuild   # ~7 GB download, 17 GB scratch; HF token in secrets/.hf-token (HLE is gated)
uv run python scripts/index_suite.py export    # scoreable 0.3 rows -> .cache/decision-index/rows-0.3.jsonl.gz
uv run python scripts/splits.py                # data/splits/*.json (committed)

uv run python scripts/collect.py --profile qwen3.6-27b --split eval       # raw letter logprobs, stack up
uv run python scripts/calibrate.py --profile qwen3.6-27b                  # fit T (+ noul offset) on calib, judge on eval; CPU only
uv run python scripts/calibrate.py --profile qwen3.6-27b --orders identity+reversed --collect-label L  # a setting's fit from <split>-L.jsonl.gz; writes that setting's file
# gated settings (top_p:<tau>+reversed) gate on the identity fit: gemma runs --orders identity first, then --orders top_p:0.9+reversed
uv run python scripts/evaluate.py offline --profile qwen3.6-27b --split eval --orders identity+reversed
uv run python scripts/evaluate.py index --profile qwen3.6-27b             # full Index via the upstream harness, 8 shards
uv run python scripts/evaluate.py replace --profile qwen3.6-27b --base RUN_DIR --override RUN_DIR  # swap re-run rows into an Index run
uv run python scripts/latency.py --profile qwen3.6-27b                    # latency-v1 design, one sequential client
uv run python scripts/evaluate.py lengths --profile qwen3.6-27b --baseline RUN_DIR  # rows the decision cap refuses
uv run python scripts/collect.py --profile gemma-4-31b --split calib-600 --layout-file prompts/experiments/labels-lower.toml --label lower  # experiment layout -> calib-600-lower.jsonl.gz
uv run python scripts/label_screen.py screen --profile gemma-4-31b --set lower  # a label set vs letters, text + image (CPU); `check` first
uv run python scripts/layout_screen.py --profile gemma-4-31b --arm blurb-header --control letters  # two collected prompt arms, paired, text + image (CPU)
uv run python scripts/r3_orders.py --profile qwen3.8-27b --layout-file prompts/experiments/blurb-header.toml \
  --calib .cache/collect/qwen3.8-27b/calib-600-blurb-header-all.jsonl.gz \
  --dev .cache/collect/qwen3.8-27b/index-dev-2k-blurb-header-all.jsonl.gz  # order grid on collect files (CPU); --layout NAME alone: a served layout's full collects
uv run python scripts/r3_orders.py --profile qwen3.8-27b --layout header --calib .cache/collect/qwen3.8-27b/calib.jsonl.gz \
  --dev .cache/collect/qwen3.8-27b/index-dev.jsonl.gz  # served-layout control: full collects, restricted to the calib-600 / index-dev-2k rows
```

- **Data:**
  - **Index rows are never used for fitting.**
  - Calibration and evaluation splits come from JevBench gold and filtered DecisionBench
    (public gold only), 50/50 by hash; all questions about one state go to the same split.
  - Jev's outputs are never read.
- **Offline vs live:** `collect.py` uses the gateway's own code, so offline answers equal
  live ones within bf16 noise (`tests/live/test_offline_matches_live.py`).
- **Results:** top level of `results/<profile>/` holds only benchmark runs: bench full and
  `-jevbench` runs, and full `<timestamp>-index` runs. Everything else (`offline-...`,
  `calibrate`, `latency`, `lengths`, `m3-*`, subset Index runs, host compares, experiments,
  reports) goes to `results/archive/<profile>/<timestamp>-.../summary.md`.
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
(`data/<profile>/<layout>/calibration.json`, or `calibration-<prefix_block>.json` when that
exists for the gateway's `PREFIX_BLOCK`); the gateway refuses the stale file and names the
changed field. Move the stale file aside (the gateway then runs that layout at T = 1),
recollect the calib and eval splits (`collect.py` ignores calibration files), then rerun
`uv run python scripts/calibrate.py --profile <profile>`.


## Run a vision experiment

Method and how to read the output: [background/vision-experiments.md](background/vision-experiments.md).
The splits (`data/splits/vision-{dev,holdout,latency}.json`) are committed; `vision_splits.py write` only
regenerates them. Start vLLM with the config's settings, idle, then:

```bash
# 1. collect raw letter logprobs on dev (add --env KEY=VALUE for mm kwargs; --holdout only for finalists)
uv run python scripts/vision_collect.py --profile gemma-4-31b --label base
# 2. re-score offline (CPU); repeat per arm: text, fit-T, fit-T-bench, pride
uv run python scripts/vision_offline.py --collect .cache/vision-collect/gemma-4-31b/base/dev.jsonl.gz \
  --arm fit-T --orders identity --out .cache/vision-arms/gemma-4-31b/base-fit-T
# 3. latency through the gateway (320 rows, 20 warm-up dropped; needs nvidia-smi)
uv run python scripts/vision_run.py --profile gemma-4-31b --gateway http://127.0.0.1:9000 \
  --ids vision-latency --workers 1
# 4. paired compare on vision-dev (--ids); --baseline is one config, the rest are positional; never picks
uv run python scripts/vision_compare.py --baseline text=.cache/vision-arms/gemma-4-31b/base-text \
  fitT=.cache/vision-arms/gemma-4-31b/base-fit-T --out-label gemma-base
```

Every holdout touch needs `--holdout` and is logged; on a holdout collect, fitted arms also need
`--fit-on <dev collect>`. Configs that need a vLLM restart get
A-B-A latency runs, and `--latency NAME=DIR` attaches a run's `summary.json` to compare.

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
| `Makefile` | Entry point: `make help` lists fetch, up, down, try, test, bench, index and report targets |
| `docker/`, `compose.yaml` | vLLM entrypoint, gateway image, stack definition |
| `docs/` | Research, spec, plan, benchmark results (this file is `docs/development.md`) |

## Earlier results

JevBench, all 1682 gold rows, 2026-09-30. Stock models, bf16, before our own fit (qwen3.6 at
decider's T = 1.943). Accuracy in %; ECE is calibration error (lower is better):

| Model | Overall | Choice | Noul | ECE | p50 latency |
|---|---|---|---|---|---|
| Jev (`jev-1.13.0`, hosted API) | 91.2 | 92.0 | 95.7 | 0.028 | 152 ms (network included) |
| gemma-4-31b | 87.0 | 91.9 | 87.5 | 0.126 | 63 ms |
| qwen3.8-27b | 86.4 | 90.4 | 86.2 | 0.033 | 81 ms |
| qwen3.6-27b | 84.3 | 91.9 | 83.5 | 0.053 | 83 ms |

Since then `header` is the default layout for all three profiles (owner, 2026-10-04; full Index
confirmation in [docs/results/archive/m3-recommendations.md](results/archive/m3-recommendations.md)).
Choice is level with Jev; most of the gap is in noul and score. Details and caveats:
[docs/results/archive/jevbench-vs-jev.md](results/archive/jevbench-vs-jev.md).
