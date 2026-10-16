# jev-brain

A setup specifically for users with a single gpu that want to run both chat and
 decision APIs at the same time.

One GPU, one model, two APIs. A single vLLM process serves normal OpenAI-style chat,
and a small gateway adds a Jev-compatible `/v1/systemone` decision endpoint from the
same loaded model.

- **Chat:** `POST /v1/chat/completions` (thinking on by default).
- **Decisions:** `POST /v1/systemone`, TypeSafe's Jev wire format. Typed `choice`,
  `score` and `noul` questions about a shared `state`, answered with probabilities.

Background research is in [docs/README.md](docs/README.md), the design in
[docs/superpowers/specs/](docs/superpowers/specs/2026-09-28-systemone-server-design.md).
Tests, benchmarks, evaluation and the repository map are in
[docs/development.md](docs/development.md).

<details>
<summary><b>Design highlights:</b> how a stock model emulates Jev</summary>

- **Read the answer, don't generate it.** Each question becomes a multiple-choice prompt
  that stops at `Answer: (`. vLLM runs one token (`max_tokens=1`) and returns the
  log-probabilities of the option letters only. The model weights are unchanged, so chat
  still works. [Inference technique](docs/4-inference-technique.md),
  [decision readout](docs/background/decision-readout.md).
- **Prompt format is data, not code.** Wording and part order live in `prompts/<layout>.toml`.
  The default `header` layout puts the question list, then the state, then one question per
  row, so every row of a request shares one long prefix.
  [Prompt layouts](docs/background/prompt-layouts.md).
- **Token-exact rows.** Rows are built piecewise from token ids, and each label letter must
  be one token in context (checked by `scripts/build_labels.py`). Identical prefixes hit the
  prefix cache. [Decision readout](docs/background/decision-readout.md).
- **KV cache padding.** Hybrid Qwen caches its recurrent state only at block boundaries
  (784 tokens, 800 with MTP). The Qwen profiles pad the shared prefix to the block size
  (`PREFIX_PAD=front`, `PREFIX_BLOCK=800`), so each question row reuses the whole state
  instead of recomputing the tail. [KV cache](docs/background/kv-cache.md),
  [prompt sharing](docs/background/prompt-sharing.md).
- **Calibrated probabilities.** A softmax over the letters with a fitted temperature T per
  question type, plus a yes/no offset b for `noul`. Fits use JevBench gold labels, never
  Jev outputs. [Calibration](docs/background/calibration.md),
  [yes/no bias](docs/background/noul-bias.md).
- **Jev-shaped answers.** `choice`, `score` and `noul` with Jev's fields and `confidence`
  formulas. [Answer compatibility](docs/6-answer-compatibility.md).
- **Chat and decisions share one GPU.** Decisions are all prefill and can starve chat
  decode. Every profile caps long prefills; the Qwen profiles also use priority scheduling
  and MTP, which speeds chat and needs our patched vLLM. [Prefill and decode](docs/background/prefill-and-decode.md),
  [speculative decoding](docs/background/speculative-decoding-and-mamba.md).

All deep dives: [docs/background/](docs/background/README.md).

</details>

## Quick start

Requirements:

- An NVIDIA GPU with ~96 GB of memory (built on an RTX PRO 6000 Blackwell) and a recent
  driver, plus Docker with the NVIDIA container toolkit.
- [uv](https://docs.astral.sh/uv/) for the Python side (tests, scripts). Python 3.12 is
  pinned in `.python-version`.
- Disk for model weights in `~/.cache/huggingface` (~55–60 GB per bf16 model; see the
  table below for the quantized ones). You download them on the host; the containers
  mount this cache read-only, so they never write there.

```bash
uv sync      # install the gateway, scripts and test dependencies
```

Then four commands:

```bash
make fetch PROFILE=qwen3.8-27b-fp8   # once per model, ~20-60 GB
make up PROFILE=qwen3.8-27b-fp8      # ~4-10 min; waits until healthy
make try                         # one decision + one streaming chat
make down
```

`make help` lists every target and profile.

- **Ports:** the gateway listens on `127.0.0.1:9000` and vLLM on `127.0.0.1:8000`.
  Clients talk to the gateway. To serve your LAN, see Security.
- **Start time:** up to ~10 minutes (weight load and graph capture); about 4 when the
  weights are still in memory from a recent run.
- **Switching models:** `make up PROFILE=<other>` replaces the running stack.
- **Passing keys:** `make` also passes a git-ignored `.env` when it exists (see Security).
- **Without make:** each model is a profile in `profiles/`, and only one runs at a time.
  The raw equivalents:

  ```bash
  uv run python scripts/fetch_model.py --profile qwen3.6-27b        # once per model: the pinned revision
  docker compose --env-file profiles/qwen3.6-27b.env up -d --build --wait
  docker compose --env-file profiles/qwen3.6-27b.env logs -f vllm   # watch the model load
  curl -s localhost:9000/health                                     # {"status":"ok","profile":"qwen3.6-27b",...}
  docker compose --env-file profiles/qwen3.6-27b.env down
  docker compose --env-file profiles/gemma-4-31b.env up -d --build --wait   # switch: stop first, then start the other
  ```

## Pick a model

Seven profiles, none of them a default: pick one with `PROFILE=`. Quantized profiles carry
their own calibration (DS-005 Stage 2). Decisions are capped at 32,768 tokens (`SYSTEMONE_MAX_LEN`),
except `gemma-4-31b` at 65,536 so every Decision Index request fits; the chat context differs.

| Profile | Weights (HF repo @ revision) | Precision (weights / KV cache) | Weights on disk | Chat context | Best for |
|---|---|---|---|---|---|
| `qwen3.6-27b` | `Qwen/Qwen3.6-27B` @ 6a9e13bd | bf16 / bf16 | 52 GB | 262,144 | Reference for Qwen3.6 |
| `qwen3.8-27b` | `Qwen/Qwen3.8-27B` @ 1d4bf0f2 | bf16 / bf16 | 52 GB | 262,144 | Reference for Qwen3.8 |
| `gemma-4-31b` | `google/gemma-4-31B-it` @ 842da379 | bf16 / bf16 | 59 GB | 65,536 | Reference for Gemma, with image chat |
| `qwen3.6-27b-fp8` | `Qwen/Qwen3.6-27B-FP8` @ e89b16eb | FP8 / bf16 | 29 GB | 262,144 | Decision throughput (~1.4x), least drift |
| `qwen3.8-27b-fp8` | `Qwen/Qwen3.8-27B-FP8` @ 017b9c7a | FP8 / bf16 | 29 GB | 262,144 | Decision throughput (~1.4x), least drift |
| `qwen3.8-27b-nvfp4` | `RadixArk/Qwen3.8-27B-NVFP4` @ 319f741c | NVFP4 MLPs + FP8 attention / bf16 | 21 GB | 262,144 | Chat speed (~2.1x); most drift |
| `gemma-4-31b-fp8` | `RedHatAI/gemma-4-31B-it-FP8-block` @ d7242548 | FP8 / fp8 (`fp8_per_token_head`) | 32 GB | 65,536 | KV headroom: 3.3x bf16's KV tokens |

The trade-offs behind the last column are in [Quantization trade-offs](#quantization-trade-offs).

## Recipes

Each recipe is one command; the profile file carries the flags. Calibration files are in
`data/<profile>/header/`.

### qwen3.6-27b

`make fetch up PROFILE=qwen3.6-27b`

- MTP speculative decoding is on. It needs our patched rejection sampler, which `compose.yaml`
  mounts over the stock vLLM v0.30.0 image (DS-004).
- Prefix blocks are padded to 800 tokens; chat prefill is capped at 800 a step with
  `--max-num-batched-tokens 2400` and chat goes first (priority scheduling).
- Calibration: `data/qwen3.6-27b/header/calibration.json` (`calibration-784.json` is for MTP off).

### qwen3.8-27b

`make fetch up PROFILE=qwen3.8-27b`

- Same setup as qwen3.6-27b: MTP with the patched sampler (DS-004), 800-token prefix blocks,
  `--max-num-batched-tokens 2400`, chat priority.
- Calibration: `data/qwen3.8-27b/header/calibration.json` (`calibration-784.json` is for MTP off).

### gemma-4-31b

`make fetch up PROFILE=gemma-4-31b`

- Vision is kept for image chat; video is off (a video item of 2,496 tokens never fits, images do).
- Sliding-window layers hash blocks densely only with `--prefix-cache-retention-interval 32`;
  the shared prefix goes alone first when it is ≥ 4,096 tokens (`WARM_UP=prefix`), since chunked
  prefill otherwise makes each row recompute it (2026-10-15). No MTP.
- Calibration: `data/gemma-4-31b/header/calibration.json`.

### qwen3.6-27b-fp8

`make fetch up PROFILE=qwen3.6-27b-fp8`

- Base profile: `qwen3.6-27b`. Same MTP, 800-token blocks and `--max-num-batched-tokens 2400`.
- DeepGEMM is off (`VLLM_USE_DEEP_GEMM=0`; it crashes on sm_120).
- The KV cache is forced to bfloat16: fp8 KV with MTP corrupts output on sm_120 (vLLM #49010).
- Calibration: `data/qwen3.6-27b-fp8/header/calibration.json`.

### qwen3.8-27b-fp8

`make fetch up PROFILE=qwen3.8-27b-fp8`

- Base profile: `qwen3.8-27b`. Same MTP, 800-token blocks and `--max-num-batched-tokens 2400`.
- DeepGEMM off on sm_120; KV forced to bfloat16 (fp8 KV + MTP corrupts output, vLLM #49010).
- Calibration: `data/qwen3.8-27b-fp8/header/calibration.json`.

### qwen3.8-27b-nvfp4

`make fetch up PROFILE=qwen3.8-27b-nvfp4`

- Base profile: `qwen3.8-27b`. NVFP4 MLPs plus FP8 attention (RadixArk); MTP, 800-token blocks
  and `--max-num-batched-tokens 2400` as for the other Qwen profiles.
- DeepGEMM off on sm_120. KV forced to bfloat16: the checkpoint declares an fp8
  `kv_cache_scheme` that would otherwise pick fp8, and fp8 KV + MTP corrupts output (vLLM #49010).
- Calibration: `data/qwen3.8-27b-nvfp4/header/calibration.json`.

### gemma-4-31b-fp8

`make fetch up PROFILE=gemma-4-31b-fp8`

- Base profile: `gemma-4-31b`. Vision kept, video off, prefix-cache retention interval 32, no MTP.
- FP8 block weights plus `--kv-cache-dtype fp8_per_token_head` (1.55x KV tokens, no query cast;
  DS-005). DeepGEMM off on sm_120.
- Calibration: `data/gemma-4-31b-fp8/header/calibration.json`.

## Results (last updated 10-09-26)

Decision Index 0.3. Our latest full Index and latency run per profile, next to the
matching Decision Index 0.3 board entries (`make report` rebuilds the table; the raw command is
`uv run python scripts/phase2_report.py --readme`). Index is the 0.3 public index; Full adds the
private parts only the maintainers run ([index-0.3-rescore.md](docs/results/index-0.3-rescore.md)).
ECE and latency are measured differently from the board's; see the run summaries:

<!-- phase2-table -->
| entry | Index | Full | ECE | coverage | median ms | p95 ms | run layout / orders | run calibration | shipped now | latency run |
|---|---|---|---|---|---|---|---|---|---|---|
| **qwen3.6-27b** † | 56.51 | — | 0.047 | 1.000 | 176.0 | 995.1 | header / identity | T=1.63/1.96/1.28 | header / identity / v8 | 2026-10-10T152806Z-latency ‡ |
| Decider chat · Qwen3.6-27B | 51.57 | 51.25 | 0.021 | board | 83.6 | n/a | | | | |
| **gemma-4-31b** | 61.60 | — | 0.119 | 1.000 | 112.7 | 875.3 | header / identity | T=4.26/5.6/7.61 | header / identity / v3 | 2026-10-10T155454Z-latency |
| Decider chat · Gemma-4-31B | 57.79 | 57.62 | 0.047 | board | 108.5 | n/a | | | | |
| **qwen3.8-27b** † | 56.60 | — | 0.024 | 1.000 | 128.9 | 763.9 | header / identity | T=1.54/1.78/0.963 | header / identity / v5 | 2026-10-10T154255Z-latency ‡ |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | board | 373.0 | n/a | | | | |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | board | 108.3 | n/a | | | | |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | board | 89.6 | n/a | | | | |
| **qwen3.6-27b-fp8** | 56.41 | — | 0.047 | 1.000 | 187.6 | 994.5 | header / identity | T=1.63/1.97/1.29 | header / identity / v1 | 2026-10-10T161053Z-latency |
| Decider chat · Qwen3.6-27B | 51.57 | 51.25 | 0.021 | board | 83.6 | n/a | | | | |
| **qwen3.8-27b-fp8** | 56.33 | — | 0.022 | 1.000 | 133.7 | 811.7 | header / identity | T=1.52/1/0.959 | header / identity / v1 | 2026-10-10T165407Z-latency |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | board | 373.0 | n/a | | | | |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | board | 108.3 | n/a | | | | |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | board | 89.6 | n/a | | | | |
| **qwen3.8-27b-nvfp4** | 55.54 | — | 0.021 | 1.000 | 161.6 | 1833.1 | header / identity | T=1.6/1.83/0.963 | header / identity / v1 | 2026-10-10T163037Z-latency |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | board | 373.0 | n/a | | | | |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | board | 108.3 | n/a | | | | |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | board | 89.6 | n/a | | | | |
| **gemma-4-31b-fp8** | 61.56 | — | 0.118 | 1.000 | 72.2 | 623.0 | header / identity | T=4.27/5.57/7.57 | header / identity / v1 | 2026-10-10T164045Z-latency |
| Decider chat · Gemma-4-31B | 57.79 | 57.62 | 0.047 | board | 108.5 | n/a | | | | |

- Calibration T is listed as choice/score/noul; b is the noul yes-offset.
- † the run's layout, orders or calibration differ from what ships now (or the calibration file is newer).
- ‡ the latency run's layout, orders or calibration differ from the Index run's.
<!-- /phase2-table -->

- **Latency** is the latency-v1 design with one sequential client, all seven runs on one box on
  2026-10-10: our WSL workstation (Ryzen 7 3800X, RTX PRO 6000 at 600 W), commit `9409223`.
  The board's gate is median, mean and p80 each ≤ 1,000 ms; every profile passes here.
- **Qwen is slower on this box** than on the rented vast.ai boxes with the same profiles
  (qwen3.6-27b-fp8 median 55 ms there, 187 ms here; qwen3.8-27b-nvfp4 64 vs 161 ms). Its engine
  step is CPU-bound and the cause is still open (DS-032). Gemma matches (gemma-4-31b-fp8 68 vs 72 ms).

### Quantization trade-offs

DS-005: what FP8 / NVFP4 weights and an fp8 KV cache cost and buy, measured on one RTX PRO 6000
with vLLM v0.30.0. Stage 1 columns (flips, req/s, chat, KV) are uncalibrated at T = 1, single run
per arm. ECE columns are Stage 2 on the eval split, before the fit (T = 1) → after. Details:
[docs/results/ds-005/README.md](docs/results/ds-005/README.md).

| profile | weights / KV GiB | KV tokens (× bf16) | JevBench answers flipped vs bf16 (T=1) | req/s at 16 clients | chat tok/s long, alone | calibrated choice ECE | calibrated noul ECE |
|---|---|---|---|---|---|---|---|
| qwen3.6-27b (bf16) | 51.0 / 29.6 | 436,397 | — | 0.9 | 60.7 | 0.079 → 0.033 | 0.040 → 0.024 |
| qwen3.8-27b (bf16) | 51.0 / 29.6 | 436,397 | — | 0.9 | 46.7 | 0.041 → 0.045 | 0.035 → 0.029 |
| gemma-4-31b (bf16) | 59.0 / 24.3 | 86,955 | — | 0.6 | 24.3 | 0.167 → 0.079 | 0.115 → 0.051 |
| qwen3.6-27b-fp8 | 28.1 / 52.6 | 774,967 (1.8×) | 10 (0.6%) | 1.3 | 88.0 | 0.087 → 0.034 | 0.039 → 0.027 |
| qwen3.8-27b-fp8 | 28.1 / 52.6 | 774,967 (1.8×) | 12 (0.7%) | 1.3 | 70.2 | 0.047 → 0.044 | 0.031 → 0.027 |
| qwen3.8-27b-nvfp4 | 19.8 / 60.3 | 888,079 (2.0×) | 43 (2.6%) | 1.4 | 90.1 | 0.063 → 0.026 | 0.036 → 0.033 |
| gemma-4-31b-fp8 | 31.7 / 51.4 | 284,529 (3.3×) | 43 (2.6%) | 0.9 | 41.3 | 0.165 → 0.076 | 0.111 → 0.053 |

- KV tokens are vLLM's startup figure at each profile's `MAX_MODEL_LEN` (65,536 for Gemma,
  262,144 for Qwen), not a measured maximum context.
- The calibrated T, the noul offset b and the score-type results are in the report.

## Use it from a client

`make try` runs both requests below.

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
  -d '{"model": "jev-latest", "messages": [{"role": "user", "content": "Say hi"}], "stream": true}'
```

The official TypeSafe SDK works against the gateway too:

```python
TypeSafeClient(api_key="local", base_url="http://127.0.0.1:9000", timeout=120)
```

The Decision Index kit's `http` engine takes `base_url=http://127.0.0.1:9000` and
`model=jev-latest`; with `GATEWAY_API_KEY` set, put the key in `DECISION_INDEX_API_KEY`.

- **Timeout:** the SDK's default is 10 s, and it retries twice on timeouts and 5xx
  errors. Large requests (many questions × many options, long states) can take longer,
  so raise `timeout`.
- **Abandoned requests:** when a client gives up, the gateway cancels its work and vLLM
  stops too, so retries don't pile up on the GPU.

### Images

Profiles with `SYSTEMONE_IMAGES=1` (gemma-4-31b and qwen3.8-27b) answer questions about
images. Both formats give the same prompt, with the images inside `Context:`:

- top-level `"images": ["data:image/png;base64,..."]`, shown before the `state`;
- `{"image": "..."}` items in a list `state`, to mix text and images:
  `"state": ["Step 3 of checkout", {"image": "data:image/png;base64,..."}]`.

- **Sources:** `data:` URLs or raw base64 of a PNG, JPEG, WEBP or GIF. The gateway never
  fetches a URL.
- **Limits:** 4 images and a 20 MB body per request; at most 50 MP per image and 100 MP per
  request, read from the headers before decoding. Images over 1,638,400 pixels are
  downscaled, keeping the aspect ratio.
- **Errors:** a URL, an undecodable image, more than 4 images, an image over 50 MP or
  100 MP in total, a body over 20 MB, text that contains image placeholder tokens, or
  images sent to a text-only profile give 400. A prompt over `SYSTEMONE_MAX_LEN` once the
  images are counted gives 422.

How it works: [Images](docs/background/images.md).

Vision suite (12,210 rows, Public Vision Index; the stock runs use the kit's `vllm-vl` engine):

| profile | gateway | stock | ECE gateway / stock |
|---|---|---|---|
| gemma-4-31b | 73.70 | 71.81 | 0.090 / 0.191 |
| qwen3.8-27b | 70.55 | 64.62 | 0.034 / 0.038 |

Per-benchmark numbers and runs: [Images, section 6](docs/background/images.md#6-the-vision-suite).

## Settings

- **Decision length cap:** `SYSTEMONE_MAX_LEN` (default 32,768, or `MAX_MODEL_LEN` if smaller)
  caps `/v1/systemone` prompts separately from chat. Long decisions compete with chat and
  coding agents for KV cache and prefill, so keep it below `MAX_MODEL_LEN` unless you need
  them. Over the cap is a 422 "maximum context length".
- **Decision priority:** `SYSTEMONE_PRIORITY` (default 0) sets the vLLM priority of decision requests;
  1 runs them after chat, but vLLM needs `--scheduling-policy priority`. 0 sends no field.
- **Decision governor:** `GOVERNOR_DUTY` (default 1.0 = off) is the share of time decisions may run while a chat
  streams (0.5 = half); `GOVERNOR_WAVE` rows per wave. Only streaming chat counts.
- `HF_TOKEN` in your shell raises Hugging Face rate limits for `fetch_model.py`.
- If host tools report `Permission denied` in the HF cache (older setups let the vLLM
  container write there as root), fix it once with `sudo chown -R $USER: ~/.cache/huggingface`.

## Errors

Every error body is `{"error": {"message": "..."}}`.

| Status | When |
|---|---|
| 400 | Chat body is not a JSON object; a bad image or too many; a decision body over 20 MB; images on a text-only profile; decision text with image placeholder tokens |
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
- **Where to set them:** in your shell, or in a git-ignored `.env`. `make` passes `.env`
  automatically when it exists. Without make, pass it as a second env file; a `.env` alone is
  ignored when `--env-file` is given:

  ```bash
  docker compose --env-file profiles/qwen3.6-27b.env --env-file .env up -d --build --wait
  ```

- **Already in place:**
  - API docs (`/docs`, `/openapi.json`) are off.
  - The passthrough never forwards the client's `Authorization` to vLLM.
  - Keys never appear in logs.
  - Images are pinned by digest.
  - Both services restart on failure (up to 3 times). A clean Docker restart leaves them
    stopped, but after a crash (e.g. WSL going down mid-run) Docker brings a running stack
    back on its own. Run `make down` if you need the GPU free.
- **Serving the LAN:** set `GATEWAY_BIND` (default `127.0.0.1`; `0.0.0.0` or a LAN IP) and
  optionally `GATEWAY_PORT` (default `9000`) in `.env`. Then:
  - `make up` refuses a non-loopback bind until `GATEWAY_API_KEY` is set;
  - set `VLLM_API_KEY` too, and keep vLLM's port 8000 on loopback;
  - on WSL2, the bind alone doesn't reach the LAN: turn on mirrored networking, or add a
    Windows `netsh interface portproxy` rule and a firewall rule for the port.
- **TLS (planned):** the gateway speaks plain HTTP, so the key and traffic cross the LAN
  in the clear. The intent is a TLS proxy in front (e.g. a Caddy service in compose);
  until then, only bind beyond loopback on a network you trust.

## More

Tests, benchmarks, evaluation, prompt and tokenizer changes, the repository map and earlier
results are in [docs/development.md](docs/development.md).
