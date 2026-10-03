# Remote GPU runbook (vast.ai)

Run a profile's long jobs (host comparison, Index runs, collect) on a rented RTX PRO 6000
box, and pull the results back here. Scripts live in `scripts/remote/`.

## Short answer

```bash
vastai search offers '<filter below>' -o 'dph'              # pick an offer
scripts/remote/rent.sh OFFER_ID qwen3.6-27b                 # prints the instance id
vastai ssh-url ID                                           # once it is running
scripts/remote/push.sh ssh://root@HOST:PORT qwen3.6-27b     # code, data, start the queue
scripts/remote/pull.sh ssh://root@HOST:PORT qwen3.6-27b --loop 1800   # until the queue is done
git add docs/results/qwen3.6-27b/<complete dirs>            # commit results (explicit paths; also archive/)
vastai destroy instance ID                                  # owner only, after the final pull
```

- One box per profile. Profiles: `qwen3.6-27b`, `qwen3.8-27b`, `gemma-4-31b`.
- No secrets go on the box. Ports stay on `127.0.0.1`.
- A box can die at any time. Pulled state lets a new box resume (see Recovery).

## Why a container instance, not compose

vast.ai standard instances are Docker containers with Docker-in-Docker disabled, so
`docker compose` cannot run on them. VM instances support compose, but on 2026-10-01 only
1 of ~40 RTX PRO 6000 offers was VM-capable. So the box runs the compose file's own vLLM
image directly, and `scripts/remote/stack.sh` does what compose does (vLLM, then the
gateway).

- Image (the compose digest, pinned in `rent.sh`):
  `vllm/vllm-openai:v0.30.0@sha256:8a69ffad015f138d7170c4ddc429e230a3bc1c1719f67e14324749df200a4b90`
- Ubuntu 24.04, python3.12, uv, curl, pip. No git, rsync, tmux or ssh client; `push.sh`
  and `bootstrap.sh` apt-install `rsync tmux git`. vast injects its own sshd (`--ssh`).
- Sources: [vast FAQ](https://docs.vast.ai/guides/reference/faq/technical),
  [VM instances](https://docs.vast.ai/guides/instances/virtual-machines).
- **`--shm-size` is not passed.** The vast CLI rejects it (argparse; `parse_env` keeps only
  `-e/-p/-h/-v/-n`). A local rehearsal in the exact image with Docker's default 64 MB
  `/dev/shm` brought vLLM up and passed a live test, so it is not needed.

## Picking an offer

Filter used on 2026-10-02:

```bash
vastai search offers 'gpu_name=RTX_PRO_6000_WS num_gpus=1 rentable=true reliability>0.98 cuda_vers>=13.0 disk_space>=250 inet_down>=500 duration>=2 direct_port_count>=2 geolocation in [US,CA]' -o 'dph'
```

| Term | Why |
|---|---|
| `RTX_PRO_6000_WS`, `num_gpus=1` | The card we built on (96 GB). |
| `reliability>0.98`, `duration>=2` | Fewer dead boxes; at least 2 days of rental. |
| `cuda_vers>=13.0` | The vLLM image needs it. |
| `disk_space>=250` | Weights (~55-60 GB) plus the suite, runs and venvs. Disk cannot grow later. |
| `inet_down>=500`, `direct_port_count>=2` | Fast weight download; direct ssh (`--direct`). |
| `geolocation in [US,CA]` | Close to us, fast to HF. |

Then choose by hand from the list:

- `gpu_max_power=600`. Offers of the same card range 400-600 W, and that changes speed.
- At least 16 CPU cores and 90 GB RAM (the gateway and harness are CPU-heavy).
- PCIe 5.

## Cost

| Item | Typical |
|---|---|
| GPU | $1.25-2.00/h |
| Bandwidth | ~$0.003-0.04/GB |
| Storage | Billed while the instance exists, also when stopped (at a higher rate) |

- Disk cannot grow; set `--disk` at rent time (default 250).
- A stopped instance may not get its GPU back. Do not stop to save money; pull and destroy.
- At $0 credit instances are stopped and scheduled for deletion. Keep credit above the
  expected run cost.

## Steps

### 1. Rent

```bash
scripts/remote/rent.sh OFFER_ID PROFILE [--disk GB] [--dry-run]
```

Runs `vastai --raw create instance` with the pinned image, `--ssh --direct`, label
`jev-PROFILE`, `--cancel-unavail`, and onstart command `bash /workspace/jev-brain/scripts/remote/start.sh`.
It prints the instance id. `--dry-run` prints the command only. Never pass `-p`.

### 2. Wait for running

`vastai show instances` until the instance is `running`. The onstart command exits quietly
until a profile is pushed.

### 3. ssh-url

```bash
vastai ssh-url ID     # ssh://root@HOST:PORT
```

### 4. Push

```bash
scripts/remote/push.sh ssh://root@HOST:PORT PROFILE [--restore] [--dry-run]
```

- **Refuses a dirty tree**, so box and local run the same commit.
- Installs rsync/tmux/git if missing, then rsyncs the repo to `/workspace/jev-brain`
  (excluding `.cache .venv .firecrawl .superpowers .env .vscode`, caches, and `secrets/`
  except its tracked, empty `.gitkeep`).
- **Checks the box tree**: `git status --porcelain` there must be empty outside
  `docs/results` (the rule results use to stamp a commit `-dirty`), or push prints the
  differences and stops before the queue starts. Results the box wrote don't count, so a
  re-push mid-run works. It also adds the repo to root's git `safe.directory`.
- Also pushes the suite export, so nothing is rebuilt on the box:
  `.cache/decision-index/rows-0.2.1.jsonl.gz`, `.cache/decision-index/suite-0.2`,
  `.cache/jevbench`.
- `--restore` (a replacement box): see Recovery.
- Writes `.cache/remote/profile`, then starts `start.sh` detached.
- Needs the pushed files to exist locally. `--dry-run` prints every command.
- Each profile keeps its own `known_hosts` in `.cache/remote-boxes/PROFILE/` (vast reuses
  HOST:PORT across boxes).
- Re-pushing to a running box updates its files, but running jobs keep the code they started
  with. Only later jobs run the new commit, so that box's results can mix commits.

On the box, `start.sh` (safe to rerun and run at every boot):

1. imports variables missing from its environment from `/proc/1/environ` (the image's Docker
   ENV: CUDA paths, `VLLM_*`, `CONTAINER_ID`), so a start over ssh sees what onstart sees.
   Variables already set are kept; `PATH` keeps its order and gets the image's missing dirs
   appended;
2. takes a lock and logs to `.cache/remote/logs/start.log`;
3. writes the run tag `<UTC timestamp>-vast` once to `.cache/remote/run_tag`;
4. runs `bootstrap.sh PROFILE` once (marker `.cache/remote/state/bootstrap.done`): apt tools,
   `uv sync --frozen`, harness venv, `suite verify` (hash must match), `fetch_model.py`
   (models are ungated; no token), `uv run pytest -q`.
   - The harness setup is redone from scratch when its venv cannot `import decision_index`
     (an earlier setup was cut off).
   - `fetch_model.py` and `pytest` get 3 tries, 60 s apart (transient HF errors; the download
     resumes).
   - A failed bootstrap writes `state/bootstrap.failed`; the next `start.sh` clears it;
5. opens tmux session `jev` with window `telemetry` (`gpu_telemetry.py sample`, every 5 s, to
   `.cache/remote/telemetry.csv`) and window `queue` (`queue.sh jobs/PROFILE.txt`). It reopens
   whichever window is missing.

Bootstrap takes a while (the weight download dominates).

### 5. Watch

```bash
ssh -p PORT root@HOST tail -f /workspace/jev-brain/.cache/remote/logs/start.log   # bootstrap
ssh -p PORT -t root@HOST tmux attach -t jev                                       # queue + telemetry
scripts/remote/pull.sh ssh://root@HOST:PORT PROFILE --loop 1800                  # keep a local copy
```

Reach the gateway from here with a tunnel, never a published port:

```bash
ssh -p PORT -L 9000:127.0.0.1:9000 root@HOST
```

`push.sh` prints these commands with the right options.

Each pull pass ends with one status line, for example
`bootstrap: done; job: index; failed: none`:

- `bootstrap`: `done`, `running` or `FAILED`. On `FAILED` the last 5 lines of `start.log` follow.
- `job`: the job running now (the last one started in `queue.log` without a `done` or
  `FAILED` line after it).
- `failed`: jobs with a `NAME.failed` marker.

Pull drops its local copies of `*.failed` and `bootstrap.done`/`bootstrap.failed` before
each fetch, so a failure the box has since retried away stops showing.

### 6. Final pull

`pull.sh ... --loop SECONDS` repeats until `QUEUE_DONE` appears in the pulled state, then
does one more pass and exits. A failed pass (box down, rebooting) warns and retries. With a
failure on the box it keeps looping and shows the failure every pass. Without `--loop` it
pulls once and exits 3 when bootstrap or a job failed.

What it copies (rsync, never deletes local files; `--update` keeps a newer local copy):

| From the box | To here |
|---|---|
| `docs/results/PROFILE` | `docs/results/PROFILE` |
| `docs/results/archive/PROFILE` | same path |
| `.cache/collect/PROFILE` | same path |
| `.cache/index-runs/PROFILE` | same path |
| `.cache/remote/{logs,state,telemetry.csv,run_tag}` | `.cache/remote-boxes/PROFILE/` |

`logs/` holds `start.log` and `state/` holds `bootstrap.done`/`bootstrap.failed`.

### 7. Commit results

Check `.cache/remote-boxes/PROFILE/logs/queue.log` ends with `PROFILE queue done` and no
`FAILED`. Then commit `docs/results/PROFILE/...` and `docs/results/archive/PROFILE/...` by explicit path (never `git add -A`).
Commit only complete result dirs: a `*-host` dir without `host.json` is a cut-off run.
Results carry the repo commit and a host fingerprint. Jev's own per-row answers are not
involved: nothing here trains on Jev API outputs.

### 8. Owner destroys

Scripts never destroy. After the final pull and the commit, the owner runs:

```bash
vastai destroy instance ID
```

## What runs

`queue.sh` runs the job file's `name: command` lines in order from the repo root.

| Profile | Jobs |
|---|---|
| `qwen3.6-27b` | stack, host-compare, collect-calib, collect-eval, collect-index-dev |
| `qwen3.8-27b`, `gemma-4-31b` | stack, host-compare, index (4 shards), collect-calib, collect-eval, collect-index-dev |

- Collect runs with `--concurrency 4`.
- Index runs use `--run-dir .cache/index-runs/PROFILE/$(cat .cache/remote/run_tag)`, so a
  restart resumes the same run.
- Index runs use `--strict`: after writing the summary, the job fails if any row is an
  `error` or the harness calls the run incomplete. So `index` is never marked done with
  holes, and its retry (same run dir) reruns only those rows.
- The `stack` job is `stack.sh up PROFILE`: vLLM (`docker/vllm-entrypoint.sh`, 1800 s to
  healthy) then the gateway, both on `127.0.0.1`, logs `logs/vllm.log` and `logs/gateway.log`.
  `stack.sh status` and `stack.sh down` also exist. A no-op when already healthy.
- Every GPU job (host-compare, index, collect) starts with `stack.sh up PROFILE &&`. A vLLM
  crash fails the job, and its retry brings the stack back.
- Per job: log `.cache/remote/logs/PROFILE/NAME.log`, marker `.cache/remote/state/PROFILE/NAME.done`.
  Done jobs are skipped on a rerun. Overall log: `.cache/remote/logs/queue.log`. All done:
  `QUEUE_DONE`.
- A failed job is retried once (`NAME retry (exit N)` in `queue.log`). Each try is appended
  to the job log under a `== <UTC> attempt N` header. A second failure writes `NAME.failed`
  (exit code, time) and stops the queue.
- Retry after that: fix the cause on the box, then `bash scripts/remote/start.sh`; the queue
  resumes at that job. start.sh prints nothing to the terminal, so follow it with
  `tail -f .cache/remote/logs/start.log`.
- The long-row study is not queued: commit `df845b6` found 0 Index rows reach the 32k decision
  cap.

## Recovery: a box dies

Pulled data is the backup. Pull often (`--loop 1800`). If the box rebooted rather than
died, it needs nothing: onstart reruns `start.sh`.

1. Pull the old box once more if it still answers.
2. Rent a new box (steps 1-3). If it comes back on the old HOST:PORT with a new host key, ssh
   refuses it: delete `.cache/remote-boxes/PROFILE/known_hosts` first.
3. Push with `--restore`:

   ```bash
   scripts/remote/push.sh ssh://root@HOST:PORT PROFILE --restore
   ```

   Before it writes the profile and starts the queue, it copies the pulled state back:

   | From here | To the box |
   |---|---|
   | `.cache/index-runs/PROFILE/` | same path |
   | `.cache/collect/PROFILE/` | same path |
   | `.cache/remote-boxes/PROFILE/run_tag` | `.cache/remote/run_tag` |
   | `.cache/remote-boxes/PROFILE/state/PROFILE/{index,collect-*}.done` | `.cache/remote/state/PROFILE/` |

   It refuses to start without a pulled `run_tag`.

Then the queue runs on the new box:

- `stack` and `host-compare` run again: their markers are never copied back, and the new host
  has a new fingerprint.
- A finished `index` stays done. Rerunning it would be a no-op resume that overwrites its good
  `-index` summary.
- An unfinished `index` or `collect` continues from the pushed runs.
- An Index run spread over two boxes reports only the last session's wall time and host in
  its summary.

## Security

- No secrets on the box: no HF token (models are ungated, the suite export is pushed, not
  rebuilt), no vast API key, no GitHub credentials (code goes over rsync).
- vLLM and the gateway bind `127.0.0.1`. Use `ssh -L`. Never pass `-p` to vast.
- `push.sh` excludes `secrets/` (except its empty, tracked `.gitkeep`) and `.env`.
- Optional check once the stack is up: `ssh -p PORT root@HOST ss -ltn` shows 8000 and 9000
  on `127.0.0.1` only (`apt-get install -y iproute2` if `ss` is missing).
- Destroying a box is an owner action, only after the final pull.

## Rehearse locally first

Test harness changes before paying: run the exact image locally (compose stack down: they
share the GPU), mount a fresh clone of this commit at `/workspace/jev-brain` and the HF
cache, write `.cache/remote/profile`, and run `start.sh`. The snippet removes an earlier
`/tmp/jev-box` first (the chown at its end makes that possible):

```bash
IMAGE=vllm/vllm-openai:v0.30.0@sha256:8a69ffad015f138d7170c4ddc429e230a3bc1c1719f67e14324749df200a4b90
rm -rf /tmp/jev-box                                                           # a fresh clone of this commit
git clone -q . /tmp/jev-box && mkdir -p /tmp/jev-box/.cache/decision-index   # .git: results need the commit
cp -r .cache/decision-index/{rows-0.2.1.jsonl.gz,suite-0.2} /tmp/jev-box/.cache/decision-index/
cp -r .cache/jevbench /tmp/jev-box/.cache/                                    # the suite export, as push.sh sends it
docker run --rm -it --gpus all \
  -v /tmp/jev-box:/workspace/jev-brain -v ~/.cache/huggingface:/root/.cache/huggingface \
  --entrypoint bash "$IMAGE"
# inside:
apt-get update -qq && apt-get install -y -qq git rsync tmux
git config --global --add safe.directory /workspace/jev-brain                # files are yours, git runs as root
cd /workspace/jev-brain && mkdir -p .cache/remote && echo qwen3.6-27b > .cache/remote/profile
bash scripts/remote/start.sh; tail -f .cache/remote/logs/start.log
# afterwards, here: the container wrote as root into the HF cache and the clone
for d in ~/.cache/huggingface /tmp/jev-box; do
  docker run --rm -v "$d":/d --entrypoint chown "$IMAGE" -R "$(id -u):$(id -g)" /d
done
```

This is the same process that showed the default 64 MB `/dev/shm` is enough.

## Reading the host comparison

The `host-compare` job runs `scripts/host_compare.py run PROFILE`: latency, a quick bench
and an Index subset (`data/splits/compare-2k.json`, ~2000 rows, 4 shards) against the live
stack, with `gpu_telemetry.py` sampling alongside. It writes
`docs/results/archive/PROFILE/<UTC>-host/`:

| File | Content |
|---|---|
| `host.json` | profile, repo commit, fingerprint, per-phase start/end/wall/dir/telemetry, latency median/p95, throughput by workers, Index rows and rows/min |
| `summary.md` | the fingerprint line, then the metrics table |
| `telemetry.csv` | raw samples: util, SM and mem clock, power draw/limit, temp, throttle bitmask |

Put hosts side by side (any number of dirs, local and remote):

```bash
uv run python scripts/host_compare.py report docs/results/archive/PROFILE/<local>-host docs/results/archive/PROFILE/<remote>-host
```

Columns are named by hostname. Rows: GPU, power limit, latency, throughput at x1/x4/x16,
Index rows/min, and per phase the median SM clock and throttled share.

Fields that explain a difference (fingerprint in `host.json`, from `host_info.py`):

| Field | Why it matters |
|---|---|
| `power_limit_w` (and default/max) | Same card runs 400-600 W; lower limit, lower clocks. |
| `<phase> throttled` | Share of samples with any of: SW power cap, HW slowdown, SW or HW thermal. To split power from thermal, read the `throttle` hex bitmask in `telemetry.csv` (0x4 SW power cap, 0x8 HW slowdown, 0x20 SW thermal, 0x40 HW thermal). |
| `<phase> sm clock` | Median SM clock (`sm_clock_max_mhz` is the ceiling); also `median_power`, `median_temp`, `median_util` in `host.json`. |
| `cpu_model`, `cpu_cores`, `ram_gb` | Gateway, tokenizing and the harness are CPU-bound at times. |
| `pcie_gen_max`, `pcie_width_max` | Weight load and host-side transfers. |
| `wsl`, `kernel`, `driver` | The local box is WSL2; remote is native Linux. |
| `vast_instance` | Set on vast boxes. |

Compare only runs from the same repo commit and profile; `host.json` records the commit.

Make the local reference the way the box makes its run, or the comparison measures the setup
rather than the host:

- Use the rehearsal container above at the same commit, but instead of `start.sh` run
  `bash scripts/remote/bootstrap.sh PROFILE`, then
  `bash scripts/remote/stack.sh up PROFILE && uv run python scripts/host_compare.py run PROFILE`.
  This gives a fresh `stack.sh up` in the pinned image.
- Not the compose stack: it runs warm (caches, compiled graphs), and a new box never does.
- `host_compare.py` always uses the same `compare-2k` ids and 4 shards. Copy the
  `docs/results/archive/PROFILE/<UTC>-host/` dir out of `/tmp/jev-box` after the chown.
Accuracy should not change between hosts. Speed will, and bf16 noise (~0.03 in decision
probabilities under load) is expected.
