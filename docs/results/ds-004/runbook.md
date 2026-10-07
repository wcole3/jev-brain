# DS-004 runbook: patched rejection sampler on Qwen3.6-27B

Goal: show that label-id reads (`logprob_token_ids`) stay exact with MTP on once the
rejection sampler gets the normal sampler's label-id path, and that the patched path really
ran. GPU time is approved for the spike. Three stack bring-ups, five JevBench runs (~5 min
each), roughly 1.5 h with model loads.

## Pieces

| file | role |
|---|---|
| `docker/spike/vllm/rejection_sampler.py` | v0.30.0 file + fix + `JEV-SPIKE` counter |
| `docker/spike/vllm/rejection_sampler.upstream.diff` | the fix only (upstream candidate) |
| `docker/spike/vllm/rejection_sampler.diff` | what is mounted (fix + counter) |
| `docker/spike/vllm/model_runner.diff` | TP gather change, not mounted (no effect on 1 GPU) |
| `compose.spike.yaml` | mounts the patched file read-only, sets `JEV_SPIKE_LOG=1` |
| `profiles/spike/qwen3.6-27b-mtp.env` | shipped Qwen3.6 profile + `--speculative-config` MTP 3 |
| `scripts/spike_chat_load.py` | 4 streaming chats through the gateway, tokens/s, acceptance |

## Arms

| arm | image | MTP | load | expect |
|---|---|---|---|---|
| A | stock | off | idle | baseline |
| A′ | stock | off | chat | bf16 noise floor under load |
| E | stock | on | chat | errors on decision rows (the bug) |
| P | patched | on | idle | ≈ A; spike counter silent (decisions never draft) |
| P′ | patched | on | chat | ≈ A′, no errors; spike counter climbing |

## Shell setup (repo root)

```bash
STOCK="docker compose --env-file profiles/qwen3.6-27b.env"
MTP="docker compose --env-file profiles/spike/qwen3.6-27b-mtp.env"
PATCHED="docker compose -f compose.yaml -f compose.spike.yaml --env-file profiles/spike/qwen3.6-27b-mtp.env"
BENCH="uv run python scripts/bench.py --profile qwen3.6-27b --jevbench-only"
OUT=docs/results/ds-004/qwen3.6-27b/runs
# bench.py writes docs/results/qwen3.6-27b/<UTC stamp>-jevbench/; move it next to the spike results.
keep() { src=$(ls -d docs/results/qwen3.6-27b/*-jevbench | sort | tail -1); mkdir -p "$OUT/$1"; mv "$src"/* "$OUT/$1/"; rmdir "$src"; }
# Chat load in the background; plain python so $! is the load itself (not a uv wrapper).
load_on() { mkdir -p "$OUT/$1"; .venv/bin/python scripts/spike_chat_load.py --seconds 3600 --vllm http://127.0.0.1:8000 \
  --out "$OUT/$1/chat-load.jsonl" > "$OUT/$1/chat-load.txt" 2>&1 & LOAD=$!; sleep 60; }
load_off() { kill -TERM $LOAD; wait $LOAD; cat "$OUT/$1/chat-load.txt"; }
```

With `GATEWAY_API_KEY`/`VLLM_API_KEY` set, export them in this shell (or add
`--env-file .env` to the three compose commands).

Optional preflight (CPU only, no GPU): the image's file must match the one the patch is based
on.

```bash
docker run --rm --entrypoint sha256sum \
  vllm/vllm-openai:v0.30.0@sha256:8a69ffad015f138d7170c4ddc429e230a3bc1c1719f67e14324749df200a4b90 \
  /usr/local/lib/python3.12/dist-packages/vllm/v1/worker/gpu/spec_decode/rejection_sampler.py
# expect 030db5bfca162cc1f305112f299de5d6d61c59d3ed0807fee46575441ca4086d
```

## 1. Stock, MTP off: A and A′

```bash
$STOCK up -d --build --wait --wait-timeout 1800    # waits for both healthchecks
$BENCH && keep A
load_on Aprime; $BENCH && keep Aprime; load_off Aprime
$STOCK down
```

## 2. Stock, MTP on: E (short is fine)

```bash
$MTP up -d --wait --wait-timeout 1800
$MTP logs vllm | grep -iE "speculative|mtp" | head    # MTP really loaded
load_on E; $BENCH; load_off E; keep E                 # failed rows are recorded, not fatal
grep -c '"error"' $OUT/E/raw.jsonl                    # > 0 expected
$MTP logs gateway vllm | grep -E "IndexError|Traceback" | head
$MTP down
```

To cut E short, Ctrl-C the bench: it writes `raw.jsonl` in a `finally`.

## 3. Patched, MTP on: P and P′

```bash
$PATCHED up -d --wait --wait-timeout 1800
$PATCHED exec vllm grep -c JEV-SPIKE \
  /usr/local/lib/python3.12/dist-packages/vllm/v1/worker/gpu/spec_decode/rejection_sampler.py   # > 0: mounted
$BENCH && keep P
$PATCHED logs vllm | grep JEV-SPIKE | tail -3          # P: expect none (decision rows never carry drafts)
load_on Pprime; $BENCH && keep Pprime; load_off Pprime
$PATCHED logs vllm | grep JEV-SPIKE | tail -5          # P′: step 1, 200, 400, ... with N rows each
$PATCHED down
```

The counter logs the first and every 200th rejection-sampler step that carried label-id rows.
No `JEV-SPIKE` line in P′ means the patched path never ran: the run proves nothing.

## 4. Compare

```bash
C="uv run python scripts/compare_runs.py"
$C $OUT/A      $OUT/Aprime >> $OUT/../comparisons.md   # noise floor under load
$C $OUT/A      $OUT/P      >> $OUT/../comparisons.md        # MTP on, idle
$C $OUT/Aprime $OUT/Pprime >> $OUT/../comparisons.md  # the claim: patched == stock under load
$C $OUT/A      $OUT/Pprime >> $OUT/../comparisons.md   # total drift vs production
grep -c '"error"' $OUT/*/raw.jsonl                             # only E may be non-zero
```

Read it as: P′ vs A′ and P′ vs A should look like A′ vs A (max |Δp| a few hundredths, flips
only where the baseline top-two gap is small). A flip with a gap > 0.10, an error row, or a
max |Δp| far above A′ vs A is a bug signal. Chat side: compare `runs/*/chat-load.txt` (p50 decode
tok/s, TTFT, acceptance) for A′ vs P′.
