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
git add docs/results/qwen3.6-27b ...                        # commit results (explicit paths)
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
scripts/remote/push.sh ssh://root@HOST:PORT PROFILE [--dry-run]
```

- **Refuses a dirty tree**, so box and local run the same commit.
- Installs rsync/tmux/git if missing, then rsyncs the repo to `/workspace/jev-brain`
  (excluding `.cache .venv .firecrawl secrets .superpowers .env .vscode` and caches).
- Also pushes the suite export, so nothing is rebuilt on the box:
  `.cache/decision-index/rows-0.2.1.jsonl.gz`, `.cache/decision-index/suite-0.2`,
  `.cache/jevbench`.
- Writes `.cache/remote/profile`, then starts `start.sh` detached.
- Needs the pushed files to exist locally. `--dry-run` prints every command.
- Each profile keeps its own `known_hosts` in `.cache/remote-boxes/PROFILE/` (vast reuses
  HOST:PORT across boxes).

On the box, `start.sh` (safe to rerun and run at every boot):

1. takes a lock and logs to `.cache/remote/logs/start.log`;
2. writes the run tag `<UTC timestamp>-vast` once to `.cache/remote/run_tag`;
3. runs `bootstrap.sh PROFILE` once (marker `.cache/remote/state/bootstrap.done`): apt tools,
   `uv sync --frozen`, harness venv, `suite verify` (hash must match), `fetch_model.py`
   (models are ungated; no token), `uv run pytest -q`;
4. opens tmux session `jev` with window `telemetry` (`gpu_telemetry.py sample`, every 5 s, to
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

### 6. Final pull

`pull.sh ... --loop SECONDS` repeats until `QUEUE_DONE` appears in the pulled state, then
does one more pass and exits. A failed pass (box down, rebooting) warns and retries. Without
`--loop` it pulls once.

What it copies (rsync, never deletes local files; `--update` keeps a newer local copy):

| From the box | To here |
|---|---|
| `docs/results/PROFILE` | `docs/results/PROFILE` |
| `.cache/collect/PROFILE` | same path |
| `.cache/index-runs/PROFILE` | same path |
| `.cache/remote/{logs,state,telemetry.csv,run_tag}` | `.cache/remote-boxes/PROFILE/` |

### 7. Commit results

Check `.cache/remote-boxes/PROFILE/logs/queue.log` ends with `PROFILE queue done` and no
`FAILED`. Then commit `docs/results/PROFILE/...` by explicit path (never `git add -A`).
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
- Per job: log `.cache/remote/logs/PROFILE/NAME.log`, marker `.cache/remote/state/PROFILE/NAME.done`.
  Done jobs are skipped on a rerun. A failure writes `NAME.failed` (exit code, time) and stops
  the queue. All done: `QUEUE_DONE`. Overall log: `.cache/remote/logs/queue.log`.
- The `stack` job is `stack.sh up PROFILE`: vLLM (`docker/vllm-entrypoint.sh`, 1800 s to
  healthy) then the gateway, both on `127.0.0.1`, logs `logs/vllm.log` and `logs/gateway.log`.
  `stack.sh status` and `stack.sh down` also exist. A no-op when already healthy.
- Retry after a failure: fix the cause on the box, then `bash scripts/remote/start.sh`; the
  queue resumes at that job.
- The long-row study is not queued: commit `df845b6` found 0 Index rows reach the 32k decision
  cap.

## Recovery: a box dies

Pulled data is the backup. Pull often (`--loop 1800`).

1. Rent a new box (steps 1-3) and `push.sh` it. Bootstrap starts at once.
2. While bootstrap runs, put the old run tag and runs back, using the same ssh options as
   `push.sh`:

   ```bash
   P=PROFILE
   S="ssh -p PORT -o UserKnownHostsFile=$PWD/.cache/remote-boxes/$P/known_hosts"
   rsync -az --relative -e "$S" .cache/collect/$P .cache/index-runs/$P root@HOST:/workspace/jev-brain/
   $S root@HOST "cp /dev/stdin /workspace/jev-brain/.cache/remote/run_tag" < .cache/remote-boxes/$P/run_tag
   ```

   Do this before the queue reaches `index` (after `stack` and `host-compare`), which reads
   `run_tag` when it starts.
3. Nothing else: the queue starts fresh on the new box (new host fingerprint, so
   host-compare reruns there on purpose), and `index` and `collect` continue from the pushed
   runs instead of starting over.

Do not copy `state/*.done` markers back; they would skip jobs this box has not done. If the
box rebooted rather than died, it needs nothing: onstart reruns `start.sh`.

## Security

- No secrets on the box: no HF token (models are ungated, the suite export is pushed, not
  rebuilt), no vast API key, no GitHub credentials (code goes over rsync).
- vLLM and the gateway bind `127.0.0.1`. Use `ssh -L`. Never pass `-p` to vast.
- `push.sh` excludes `secrets/` and `.env`.
- Destroying a box is an owner action, only after the final pull.

## Rehearse locally first

Test harness changes before paying: run the exact image locally, mount a `git archive` copy
of the repo at `/workspace/jev-brain` and the HF cache, write
`.cache/remote/profile`, and run `start.sh`:

```bash
mkdir -p /tmp/jev-box && git archive HEAD | tar -x -C /tmp/jev-box
docker run --rm -it --gpus all \
  -v /tmp/jev-box:/workspace/jev-brain -v ~/.cache/huggingface:/root/.cache/huggingface \
  --entrypoint bash vllm/vllm-openai:v0.30.0@sha256:8a69ffad015f138d7170c4ddc429e230a3bc1c1719f67e14324749df200a4b90
# inside:
cd /workspace/jev-brain && mkdir -p .cache/remote && echo qwen3.6-27b > .cache/remote/profile
bash scripts/remote/start.sh
```

This is the same process that showed the default 64 MB `/dev/shm` is enough. Copy the suite
export in too (`.cache/decision-index/...`, `.cache/jevbench`), as `push.sh` would.

## Reading the host comparison

The `host-compare` job runs `scripts/host_compare.py run PROFILE`: latency, a quick bench
and an Index subset (`data/splits/compare-2k.json`, ~2000 rows, 4 shards) against the live
stack, with `gpu_telemetry.py` sampling alongside. It writes
`docs/results/PROFILE/<UTC>-host/`:

| File | Content |
|---|---|
| `host.json` | profile, repo commit, fingerprint, per-phase start/end/wall/dir/telemetry, latency median/p95, throughput by workers, Index rows and rows/min |
| `summary.md` | the fingerprint line, then the metrics table |
| `telemetry.csv` | raw samples: util, SM and mem clock, power draw/limit, temp, throttle bitmask |

Put hosts side by side (any number of dirs, local and remote):

```bash
uv run python scripts/host_compare.py report docs/results/PROFILE/<local>-host docs/results/PROFILE/<remote>-host
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
Accuracy should not change between hosts. Speed will, and bf16 noise (~0.03 in decision
probabilities under load) is expected.
