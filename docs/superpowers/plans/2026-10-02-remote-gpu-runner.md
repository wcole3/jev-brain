# Remote GPU runner (vast.ai) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Run the remaining phase-2 GPU work on rented vast.ai boxes (one per profile), robustly, and pull the results back. Also run a host-comparison suite that answers "is a rented RTX PRO 6000 faster or slower than the local one, and why".

**Architecture:**
- Each box is a vast.ai **container instance** running the pinned vLLM image. There is no Docker-in-Docker, and VM hosts are rare.
- vLLM starts from the same `docker/vllm-entrypoint.sh` with the same profile env as compose. The gateway runs with `uv` in the repo venv, and both bind 127.0.0.1.
- A resumable job queue runs under tmux and is relaunched by the instance's onstart.
- The local machine pushes the code and suite export, and pulls results every 30 min. All state lives in files the existing scripts already resume from, so a dead box is replaced, not repaired.

**Tech stack:** bash, Python 3.12, uv, rsync over ssh, vastai CLI (local only).

**Spec:** DS-019 (DoStuff) plus the phase-2 spec `docs/superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md`.

## Global Constraints

- Code reads like a tutorial: small files, comments ≤ 2 lines. Shell scripts use `set -euo pipefail` and pass `bash -n`. Python is ruff-clean with unit tests.
- **No secrets on rented boxes.** No HF token (the models aren't gated and the suite export is pushed, not rebuilt). No vast API key on the box. No GitHub credentials (code goes over rsync).
- vLLM and the gateway bind **127.0.0.1** on boxes. Reach them only through `ssh -L`. Never pass `-p` port mappings.
- Same commit everywhere: `push.sh` refuses a dirty tree. Results carry the repo commit and a **host fingerprint**.
- The vLLM image must be exactly `vllm/vllm-openai:v0.30.0@sha256:8a69ffad015f138d7170c4ddc429e230a3bc1c1719f67e14324749df200a4b90`, the compose digest.
- Box layout: repo at `/workspace/jev-brain`, HF cache at `/root/.cache/huggingface`, remote state at `.cache/remote/` (logs, state, telemetry, run_tag, profile).
- The image is Ubuntu 24.04 with python3.12, uv, curl and pip. It has **no** git, rsync, tmux or ssh client. vast.ai injects its own sshd in `--ssh` mode.
- Never destroy instances from scripts. Destroying is an owner action.
- Commits: caveman Conventional Commits, subject ≤ 50 chars, explicit paths only, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Do not run anything against live servers or vast.ai in unit tests.

## File map

| File | Responsibility |
|---|---|
| `docker/vllm-entrypoint.sh` (modify) | `--host "${VLLM_HOST:-0.0.0.0}"`, so boxes can bind 127.0.0.1. Compose keeps 0.0.0.0 |
| `scripts/profile_env.py` | prints `export K=V` lines (shell-quoted) for a profile, plus `K=V` overrides |
| `scripts/host_info.py` | host fingerprint dict (GPU, driver, power limits, clocks, PCIe, CPU, RAM, kernel, WSL, vast ids) |
| `scripts/gpu_telemetry.py` | samples nvidia-smi every N s into CSV; summarises a CSV (median clock, power, temp, util, throttle share) |
| `scripts/host_compare.py` | `run PROFILE`: latency-v1 + bench --quick + fixed Index subset + telemetry, written to `docs/results/<profile>/<ts>-host/`. `report DIR...`: side-by-side table |
| `data/splits/compare-2k.json` | fixed 2,000 Index ids (every k-th row of index-dev, linked groups whole) |
| `scripts/remote/stack.sh` | `up PROFILE [K=V...]`, `down`, `status`: vLLM and the gateway as background processes with pidfiles, logs and a health wait |
| `scripts/remote/bootstrap.sh` | on the box: apt (rsync, tmux, git), `uv sync --frozen`, harness setup, fetch model, unit tests |
| `scripts/remote/queue.sh` | runs `name: command` lines from a job file, with done/failed markers and per-job logs; skips done jobs on restart |
| `scripts/remote/start.sh` | onstart entry, idempotent: no-op until the repo is pushed; otherwise starts telemetry + queue in tmux |
| `scripts/remote/jobs/<profile>.txt` | the per-box job lists |
| `scripts/remote/rent.sh` | local: `vastai create instance` with the pinned image, disk, `--ssh --direct` and onstart; prints the ssh command |
| `scripts/remote/push.sh` | local: clean-tree check, install rsync/tmux/git over ssh, rsync the repo, suite export and jevbench cache, write `.cache/remote/profile` |
| `scripts/remote/pull.sh` | local: rsync results back (once, or `--loop SECONDS`) |
| `docs/remote-gpu.md` | runbook: offer filter, cost, steps, monitoring, recovery, teardown |
| `tests/unit/test_profile_env.py`, `test_host_info.py`, `test_gpu_telemetry.py`, `test_host_compare.py`, `test_remote_scripts.py` | tests |

## Box job lists

A box's run tag is `<UTC timestamp>-vast`, written once by `start.sh` to `.cache/remote/run_tag`. Index runs use `--run-dir .cache/index-runs/<profile>/$(cat .cache/remote/run_tag)`, so a restart resumes the same run.

- `qwen3.6-27b.txt`: stack, host-compare, collect calib, collect eval, collect index-dev.
- `qwen3.8-27b.txt` and `gemma-4-31b.txt`: stack, host-compare, index (4 shards), collect calib, collect eval, collect index-dev.

Collect runs with `--concurrency 4`. There is no long-row study: commit `df845b6` showed 0 Index rows reach the 32k cap.

---

### Task R1: profile env, host fingerprint, telemetry (Python, tested)

**Files:**
- Create: `scripts/profile_env.py`, `scripts/host_info.py`, `scripts/gpu_telemetry.py`
- Create: tests `tests/unit/test_profile_env.py`, `tests/unit/test_host_info.py`, `tests/unit/test_gpu_telemetry.py`
- Modify: provenance in `scripts/evaluate.py` (index, offline), `scripts/latency.py` and `scripts/bench.py`, to add `host_info.summary_line()` as a `host` key

**Interfaces:**
- **`profile_env.exports(profile, overrides: list[str]) -> str`:**
  - uses `gateway.config.read_env_file`;
  - overrides are `K=V` and replace or add keys;
  - each line is `export K=<shlex.quote(V)>`;
  - the CLI is `python scripts/profile_env.py PROFILE [K=V ...]`.
- **`host_info.collect() -> dict`.** Keys:
  - `hostname`;
  - GPU: `gpu_name`, `driver`, `power_limit_w`, `power_default_w`, `power_max_w`, `sm_clock_max_mhz`, `pcie_gen_max`, `pcie_width_max`;
  - host: `cpu_model`, `cpu_cores`, `ram_gb`, `kernel`, `wsl` (bool, "microsoft" in /proc/version);
  - vast: `vast_instance` (env `CONTAINER_ID` or `VAST_CONTAINERLABEL`, else None).

  It parses one `nvidia-smi --query-gpu=... --format=csv,noheader,nounits` call. A missing nvidia-smi gives None values and must not raise. `host_info.summary_line(d) -> str` is short, e.g. `RTX PRO 6000 … 600/600 W, drv 610.62, PCIe 5x16, Ryzen 7 3800X (16 thr), 94 GB, WSL`. Parsing is a pure function tested on canned output.
- **`gpu_telemetry`:**
  - `python scripts/gpu_telemetry.py sample --out CSV --interval 5` loops until killed and appends rows: utc, util, sm_clock, mem_clock, power_draw, power_limit, temp, throttle_reasons_hex.
  - `summarize(csv_path, since=None, until=None) -> dict` returns median sm clock, power, temp and util, the sample count, and the share of samples where SW power cap or thermal throttling was active (bits 0x4 = sw power cap, 0x20 = sw thermal, 0x40 = hw thermal, 0x8 = hw slowdown).
  - Tests use a canned CSV.

### Task R2: host-comparison suite (Python, tested)

**Files:**
- Create: `scripts/host_compare.py`, `data/splits/compare-2k.json` (generated by a `make-ids` subcommand and committed), `tests/unit/test_host_compare.py`

**What it does:**
- **`make-ids`:** takes 2,000 ids from `data/splits/index-dev.json` deterministically (every k-th linked group, whole groups; nearest to 2,000 is fine) and writes `{"meta": {...}, "ids": [...]}`.
- **`run PROFILE [--gateway URL] [--vllm URL]`:**
  1. starts a telemetry sampler subprocess;
  2. runs `scripts/latency.py --profile P`;
  3. runs `scripts/bench.py --profile P --quick`;
  4. runs `scripts/evaluate.py index --profile P --ids data/splits/compare-2k.json --shards 4`;
  5. stops the sampler.

  It records each phase's wall start and end, then writes `docs/results/<P>/<ts>-host/`:
  - `host.json`: fingerprint, the phases with their result-dir paths and walls, rows/min for the subset, the latency median and p95 (read from the latency `raw.jsonl`), the bench throughput x1/x4/x16 (read from bench's `raw.jsonl` records with `test == "throughput"`), and a telemetry summary per phase;
  - `summary.md`;
  - `telemetry.csv`.

  Use `subprocess.run(check=True)`. Find the newest result dir each step created by globbing `docs/results/<P>/*-latency` and so on, newest first.
- **`report DIR [DIR...]`:** prints a markdown side-by-side table (rows are metrics, columns are hosts).
- Tests: `make-ids` determinism and group-wholeness; `report` on two canned `host.json` files; the parsers for the latency and bench raw files. Mock subprocesses; nothing is run live.

### Task R3: remote shell harness (stack, bootstrap, queue, start, jobs) + entrypoint host

**Files:**
- Modify: `docker/vllm-entrypoint.sh` (`--host "${VLLM_HOST:-0.0.0.0}"`) and `tests/unit/test_entrypoint.py`, to assert the default and the override
- Create: `scripts/remote/stack.sh`, `scripts/remote/bootstrap.sh`, `scripts/remote/queue.sh`, `scripts/remote/start.sh`, `scripts/remote/jobs/{qwen3.6-27b,qwen3.8-27b,gemma-4-31b}.txt`, `tests/unit/test_remote_scripts.py`

**Behaviour:**
- **`stack.sh up PROFILE [K=V...]`:**
  - If the gateway `/health` is already ok for this profile, exit 0. That makes it idempotent.
  - Otherwise eval `uv run python scripts/profile_env.py PROFILE VLLM_HOST=127.0.0.1 VLLM_URL=http://127.0.0.1:8000 HF_HUB_OFFLINE=1 "$@"`.
  - Start `bash docker/vllm-entrypoint.sh` with nohup to `.cache/remote/logs/vllm.log`, pid to `.cache/remote/vllm.pid`.
  - Wait up to 1,800 s for `curl -sf 127.0.0.1:8000/health`, failing early if the pid dies (print the log tail).
  - Then start the gateway: `uv run --frozen uvicorn gateway.app:app --host 127.0.0.1 --port 9000` with nohup to `logs/gateway.log`, pid file. Wait for `127.0.0.1:9000/health` `status == ok`.
- **`stack.sh down`:** kills both pids (TERM, wait, KILL). **`stack.sh status`:** prints both health results.
- **`bootstrap.sh PROFILE`:**
  1. `apt-get update && apt-get install -y rsync tmux git`, only if any is missing;
  2. `uv sync --frozen` (dev deps too: pytest, pyarrow);
  3. `uv run python scripts/index_suite.py setup`, skipped if `.cache/decision-index-venv/bin/python` exists;
  4. harness `suite verify` against `.cache/decision-index/suite-0.2`, through the harness venv;
  5. `uv run python scripts/fetch_model.py --profile PROFILE`;
  6. `uv run pytest -q`.

  Markers in `.cache/remote/state/bootstrap.done`.
- **`queue.sh JOBFILE`:** for each non-blank, non-# line `name: command`:
  - skip it if `.cache/remote/state/<name>.done` exists;
  - otherwise run `bash -c "command"` with output to `.cache/remote/logs/<name>.log`;
  - on success touch `.done`; on failure write `<name>.failed` (exit code and UTC time) and exit non-zero, so nothing after it runs on bad state.

  Before each job it echoes `== <name> start` and `== <name> done|FAILED` lines with UTC times to `.cache/remote/logs/queue.log`. At the end it touches `.cache/remote/state/QUEUE_DONE`. A rerun resumes at the first job that isn't done. A failed job is retried on the next start: remove the stale `.failed` before running.
- **`start.sh`** (the onstart entry; must be safe at every boot):
  - `cd /workspace/jev-brain` or exit 0 (not pushed yet);
  - read the profile from `.cache/remote/profile` or exit 0;
  - create `run_tag` if it is missing;
  - if the tmux session `jev` exists, exit 0;
  - otherwise run `bootstrap.sh` (idempotent through its marker), then start tmux session `jev` with two windows: telemetry (`uv run python scripts/gpu_telemetry.py sample --out .cache/remote/telemetry.csv --interval 5`) and queue (`bash scripts/remote/queue.sh scripts/remote/jobs/$PROFILE.txt`).
  - Log to `.cache/remote/logs/start.log`.
- **Jobs:** use the run tag through `$(cat .cache/remote/run_tag)`.
- **Tests (`test_remote_scripts.py`):**
  - `bash -n` on every script;
  - the job files parse (each line `name: cmd`, unique names, the first job is `stack`);
  - `queue.sh` behaviour in a temp dir with a fake job file (`ok: true`, `bad: false`, `never: true`): `ok` done, `bad` failed, `never` not run, and a rerun skips `ok`. Make queue.sh's state and log root overridable through env `REMOTE_STATE` so the test can use tmp_path.

### Task R4: local side: rent, push, pull

**Files:**
- Create: `scripts/remote/rent.sh`, `scripts/remote/push.sh`, `scripts/remote/pull.sh`; extend `tests/unit/test_remote_scripts.py`, at least `bash -n`, plus argument checks run with `--dry-run`

**Behaviour:**
- **`rent.sh OFFER_ID PROFILE [--disk 250] [--dry-run]`:** runs
  ```
  vastai create instance OFFER_ID \
    --image vllm/vllm-openai:v0.30.0@sha256:8a69ffad... \
    --disk N --ssh --direct --label jev-PROFILE \
    --env '--shm-size=16g' --cancel-unavail \
    --onstart-cmd 'bash /workspace/jev-brain/scripts/remote/start.sh'
  ```
  It prints the instance id, then tells the owner to run `vastai ssh-url ID` when it's ready. `--dry-run` prints the command only.
- **`push.sh SSH_URL PROFILE`** (`ssh://root@host:port`, as printed by `vastai ssh-url`):
  1. refuse unless `git status --porcelain` is empty;
  2. ssh `mkdir -p /workspace/jev-brain` and install rsync/tmux/git if missing (apt);
  3. rsync the repo (exclude `.cache .venv .firecrawl secrets .superpowers .pytest_cache .ruff_cache __pycache__`, keep `.git`);
  4. rsync `.cache/decision-index/rows-0.2.1.jsonl.gz`, `.cache/decision-index/suite-0.2/` and `.cache/jevbench/`;
  5. write PROFILE to `.cache/remote/profile`;
  6. run `bash scripts/remote/start.sh` once over ssh (nohup, detached), so the first boot doesn't wait for a reboot.

  ssh options: `-o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30`.
- **`pull.sh SSH_URL PROFILE [--loop SECONDS]`:** rsync from the box:
  - `docs/results/PROFILE/` into the local `docs/results/PROFILE/`;
  - `.cache/collect/PROFILE/` into local `.cache/collect/PROFILE/`;
  - `.cache/index-runs/PROFILE/` into local `.cache/index-runs/PROFILE/`;
  - `.cache/remote/{logs,state,telemetry.csv,run_tag}` into local `.cache/remote-boxes/PROFILE/`.

  Never delete local files (no `--delete`). Each pass prints `queue.log`'s last 3 lines. With `--loop`, repeat until `QUEUE_DONE` has been pulled, then do one final pass and exit.

### Task R5: runbook

**Files:**
- Create: `docs/remote-gpu.md`
- Modify: README, adding one line in the Phase 2 section that points to it

**Content:** why container, not compose; the offer filter (the exact `vastai search offers` query used, and why: WS edition at 600 W, reliability, cores, RAM, download, PCIe, US/CA); cost; and the steps:
1. rent;
2. wait for running;
3. ssh-url;
4. push;
5. watch (`ssh … tmux attach -t jev`, `pull.sh --loop 1800`);
6. final pull;
7. commit results;
8. owner destroys.

Then recovery (a box dies: rent a new one, push, then push the pulled `.cache/index-runs`/`.cache/collect` state back and start; the resumable steps continue); security notes; and the host-comparison read-out.

---

## Self-review notes

- The long-row study is dropped (data shows 0 over-cap rows), so DS-016/017 verification stays local and separate.
- `collect --concurrency 4` and `--shards 4` follow the owner's 4-concurrency choice.
- rows/min on the 2k subset, latency-v1 and bench --quick together cover the latency and throughput sides of the comparison. Telemetry plus the fingerprint explain differences (power cap, clocks, CPU, PCIe, WSL).
