# jev-brain

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Decision Index](https://img.shields.io/badge/Decision_Index_Full_(0.4)-65.2-2ea44f)](https://multimodalart-jev-decision-index.static.hf.space/index.html?model=jev-brain-gemma-4-31b)
[![Decision Index Text](https://img.shields.io/badge/Decision_Index_Text_(public)-61.69-2ea44f)](https://huggingface.co/spaces/multimodalart/jev-decision-index)
[![Vision](https://img.shields.io/badge/Decision_Index_Vision_(public,_own_run)-74.18-2ea44f)](docs/results/gemma-4-31b/2026-10-21T080720Z-vision/summary.md)

One GPU serves OpenAI-style chat (`POST /v1/chat/completions`) and Jev-compatible decisions
(`POST /v1/systemone`) at the same time, from one loaded model. A small gateway sits in front
of a single vLLM process.

There are nine ready profiles across Gemma 4 31B and 12B, Qwen3.6 27B and Qwen3.8 27B, in
bf16, FP8, NVFP4 and int4 (QAT). One profile runs at a time; switch with `make up PROFILE=...`. The gemma and
qwen3.8 profiles take text and image decisions.

## Scores

Decision Index scores of the model behind each profile, as served by this repo. The Index columns
come from older runs than the latency column (see the notes below the table).

| Profile | Text Index (0.3 public; `blurb_header`, vLLM 0.30) | Vision Index (public; vLLM 0.30) | Latency ms, median / mean / p80 (current default, vLLM 0.32, 600 W) | Board |
|---|---|---|---|---|
| `gemma-4-31b` | 62.98 | 74.18 | [199.7 / 467.9 / 652.4](docs/results/archive/gemma-4-31b/2026-10-25T131631Z-latency/summary.md) | [Full 65.2 (0.4), earlier run](https://multimodalart-jev-decision-index.static.hf.space/index.html?model=jev-brain-gemma-4-31b) |
| `gemma-4-31b-fp8` | 62.82 | 73.96 | [135.5 / 329.0 / 431.9](docs/results/archive/gemma-4-31b-fp8/2026-10-25T150150Z-latency/summary.md) | — |
| `gemma-4-12b` | 53.58 | 67.56 | [85.9 / 165.9 / 206.0](docs/results/archive/gemma-4-12b/2026-10-25T145052Z-latency/summary.md) | — |
| `gemma-4-12b-qat` | 51.26 | 66.54 | [83.2 / 161.7 / 204.2](docs/results/archive/gemma-4-12b-qat/2026-10-25T150932Z-latency/summary.md) | — |
| `qwen3.6-27b` | 56.82 | — (text only) | [162.8 / 399.8 / 494.1](docs/results/archive/qwen3.6-27b/2026-10-25T141532Z-latency/summary.md) | — |
| `qwen3.6-27b-fp8` | 56.78 | — (text only) | [151.4 / 344.9 / 408.6](docs/results/archive/qwen3.6-27b-fp8/2026-10-25T152157Z-latency/summary.md) | — |
| `qwen3.8-27b` | 57.64 | 71.13 | [287.9 / 622.0 / 822.3](docs/results/archive/qwen3.8-27b/2026-10-25T124823Z-latency/summary.md) | — |
| `qwen3.8-27b-fp8` | 57.58 | 70.67 | [248.4 / 531.1 / 722.5](docs/results/archive/qwen3.8-27b-fp8/2026-10-25T153711Z-latency/summary.md) | — |
| `qwen3.8-27b-nvfp4` | 56.63 | 71.00 | [487.3 / **1,009.5 / 1,272.0**](docs/results/archive/qwen3.8-27b-nvfp4/2026-10-25T160045Z-latency/summary.md) (**fails the gate**) | — |

- **Index columns:** our full text and Vision runs of 2026-10-20/21 with the defaults of that time (`blurb_header`, round 4
  option orders, vLLM 0.30). Profiles now serve `blurb_header_reread` with H1q on vLLM 0.32 (DS-045), which has
  no full Index run yet; a gemma-4-31b full text and Vision rerun is in progress. Estimates of what the new
  default is worth, from index-dev-2k deltas: [experiments vs public](docs/results/2026-10-25-experiments-vs-public.md).
  The board entry (Full 65.2, public 61.69) is an earlier gemma-4-31b run (PR #193).
- **Latency:** the board's design (latency-v1, one client, text decisions), 2026-10-25, on our WSL workstation
  (RTX PRO 6000 at 600 W), under each profile's shipped layout, orders and calibration. The board's gate is median,
  mean and p80 each ≤ 1,000 ms: eight profiles pass; `qwen3.8-27b-nvfp4` fails on mean and p80.
- **Why the Qwen3.8 profiles got slower** than the 2026-10-20 runs (88–156 ms median then): CPU-bound hybrid
  prefill on a slower host CPU plus the extra tokens H1q and `min_n:4+reversed` read; not WSL2 and mostly not
  vLLM 0.32. [qwen3.8 latency note](docs/results/2026-10-25-qwen38-latency.md). See also [Results](#results).

## Versus vLLM's own `/v1/systemone`

vLLM 0.32 ships an uncalibrated `/v1/systemone` (one read per question, at most 26 options; not served for Gemma 4).
We evaluate the same model (qwen3.8-27b) in jev-brain and vLLM's native '/v1/systemone'; same GPU, same 1,994 Decision Index requests (index-dev-2k), 2026-10-25:

| | jev-brain | vLLM native |
|---|---|---|
| Requests answered | 1,994 / 1,994 | 1,787 / 1,994 (207 refused: over 26 options) |
| Accuracy, all questions | **79.7%** | 71.8% |
| Accuracy, questions both answer | **80.9%** | 76.0% |
| Latency ms, median / mean / p80 (latency-v1, 600 W, requests both answer) | 263 / 540 / 598 | **138 / 272 / 276** |

Summary: jev-brain is more accurate, at about twice the latency; both pass the board's 1,000 ms gate. Details and caveats:
[2026-10-25-vs-vllm-native-systemone.md](docs/results/2026-10-25-vs-vllm-native-systemone.md).

As stated above, vLLM is not able to serve Gemma 4 as a decision model even though it is currently (2026-10-25) the best
performing non-finetuned model. A future effort will investigate enabling it.

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
  Clients talk to the gateway. To serve your LAN, see [Security](#security).
- **Start time:** up to ~10 minutes (weight load and graph capture); about 4 when the
  weights are still in memory from a recent run.
- **Switching models:** `make up PROFILE=<other>` replaces the running stack.
- **Passing keys:** `make` also passes a git-ignored `.env` when it exists.

<details>
<summary>Without make</summary>

Each model is a profile in `profiles/`, and only one runs at a time. The raw equivalents:

```bash
uv run python scripts/fetch_model.py --profile qwen3.6-27b        # once per model: the pinned revision
docker compose --env-file profiles/qwen3.6-27b.env up -d --build --wait
docker compose --env-file profiles/qwen3.6-27b.env logs -f vllm   # watch the model load
curl -s localhost:9000/health                                     # {"status":"ok","profile":"qwen3.6-27b",...}
docker compose --env-file profiles/qwen3.6-27b.env down
docker compose --env-file profiles/gemma-4-31b.env up -d --build --wait   # switch: stop first, then start the other
```

</details>

## Pick a model

Nine profiles, none of them a default: pick one with `PROFILE=`. Quantized profiles carry
their own calibration (DS-005 Stage 2). Decisions are capped at 32,768 tokens (`SYSTEMONE_MAX_LEN`),
except the Gemma profiles (31B and 12B) at 65,536 so every Decision Index request fits; the chat context differs.

| Profile | Weights (HF repo @ revision) | Precision (weights / KV cache) | Weights on disk | Chat context | Best for |
|---|---|---|---|---|---|
| `qwen3.6-27b` | `Qwen/Qwen3.6-27B` @ 6a9e13bd | bf16 / bf16 | 52 GB | 262,144 | Reference for Qwen3.6 |
| `qwen3.8-27b` | `Qwen/Qwen3.8-27B` @ 1d4bf0f2 | bf16 / bf16 | 52 GB | 262,144 | Reference for Qwen3.8 |
| `gemma-4-31b` | `google/gemma-4-31B-it` @ 842da379 | bf16 / bf16 | 59 GB | 65,536 | Reference for Gemma, with image chat |
| `qwen3.6-27b-fp8` | `Qwen/Qwen3.6-27B-FP8` @ e89b16eb | FP8 / bf16 | 29 GB | 262,144 | Decision throughput (~1.4x), least drift |
| `qwen3.8-27b-fp8` | `Qwen/Qwen3.8-27B-FP8` @ 017b9c7a | FP8 / bf16 | 29 GB | 262,144 | Decision throughput (~1.4x), least drift |
| `qwen3.8-27b-nvfp4` | `RadixArk/Qwen3.8-27B-NVFP4` @ 319f741c | NVFP4 MLPs + FP8 attention / bf16 | 21 GB | 262,144 | Chat speed (~2.1x); most drift |
| `gemma-4-31b-fp8` | `RedHatAI/gemma-4-31B-it-FP8-block` @ d7242548 | FP8 / fp8 (`fp8_per_token_head`) | 32 GB | 65,536 | KV headroom: 3.3x bf16's KV tokens |
| `gemma-4-12b` | `google/gemma-4-12B-it` @ 707f0a3b | bf16 / bf16 | 23.9 GB | 65,536 | Lower tier: about a third of the 31B's mean latency |
| `gemma-4-12b-qat` | `google/gemma-4-12B-it-qat-w4a16-ct` @ 1d2c2d7f | int4 W4A16 QAT / bf16 | 10.3 GB | 65,536 | Fastest chat (~4× the 31B), int4 QAT; −2.3 text points vs bf16 |

The trade-offs behind the last column are in [Quantization trade-offs](#quantization-trade-offs).

<details>
<summary>Per-profile notes</summary>

Each profile is one command (`make fetch up PROFILE=<name>`); the profile file carries the
flags. Calibration files are in `data/<profile>/<layout>/`; quantized profiles borrow their bf16
base's fit (`scripts/borrow_calibration.py`).

- **qwen3.6-27b:** MTP speculative decoding with our patched rejection sampler, which
  `compose.yaml` mounts over the stock vLLM v0.32.0 image (DS-004; upstream PR #61219). Prefix blocks padded to
  800 tokens; chat prefill capped at 800 a step with `--max-num-batched-tokens 2400`, chat
  first (priority scheduling). Text only. `calibration-784.json` is for MTP off.
- **qwen3.8-27b:** same setup as qwen3.6-27b (MTP with the patched sampler, 800-token blocks,
  chat priority). Vision on. `calibration-784.json` is for MTP off.
- **gemma-4-31b:** vision on for image chat; video is off (a 2,496-token video item never fits,
  images do). Sliding-window layers hash blocks densely only with
  `--prefix-cache-retention-interval 32`. A shared prefix of ≥ 1,024 tokens goes alone first
  (`WARM_UP=prefix`), since chunked prefill otherwise makes each row recompute it. No MTP.
- **qwen3.6-27b-fp8:** base `qwen3.6-27b`; same MTP, 800-token blocks and batch size. DeepGEMM
  off (`VLLM_USE_DEEP_GEMM=0`; it crashes on sm_120). KV forced to bf16: fp8 KV with MTP
  corrupts output on sm_120 (vLLM #49010). Text only.
- **qwen3.8-27b-fp8:** base `qwen3.8-27b`; same MTP, 800-token blocks and batch size. DeepGEMM
  off; KV forced to bf16 (vLLM #49010). Vision on.
- **qwen3.8-27b-nvfp4:** base `qwen3.8-27b`; NVFP4 MLPs plus FP8 attention (RadixArk). MTP,
  800-token blocks and batch size as above. DeepGEMM off. KV forced to bf16: the checkpoint
  declares an fp8 `kv_cache_scheme` that would otherwise pick fp8 (vLLM #49010). Vision on.
- **gemma-4-31b-fp8:** base `gemma-4-31b`; vision on, video off, retention interval 32, no
  MTP; the prefix warm-up still starts at 4,096 tokens (as on both 12B profiles). FP8 block
  weights plus `--kv-cache-dtype fp8_per_token_head` (1.55x KV tokens, no query cast; DS-005).
  DeepGEMM off.
- **gemma-4-12b:** vision on (encoder-free, `gemma4_unified`), `--prefix-cache-retention-interval 64`
  (its scheduler block is 64), bf16 KV, no MTP. Chat is ~49 tok/s single-stream (31B bf16 ~24).
- **gemma-4-12b-qat:** base `gemma-4-12b`; int4 W4A16 QAT weights (compressed-tensors, run by
  the Marlin kernel). Chat is ~103 tok/s single-stream.

</details>

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

Chat has thinking on by default. Decisions use TypeSafe's Jev wire format: typed `choice`,
`score` and `noul` questions about a shared `state`, answered with probabilities.

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

Profiles with `SYSTEMONE_IMAGES=1` (gemma-4-31b, gemma-4-31b-fp8, gemma-4-12b,
gemma-4-12b-qat, qwen3.8-27b, qwen3.8-27b-fp8 and qwen3.8-27b-nvfp4) answer questions about images. Both formats give the
same prompt, with the images inside `Context:`:

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

## Results

Decision Index 0.3. Our latest full Index run per profile (2026-10-20/21, `blurb_header`, vLLM 0.30)
and latest latency run (2026-10-25, the shipped `blurb_header_reread`, vLLM 0.32), next to the
matching Decision Index 0.3 board entries. † and ‡ mark exactly that gap: no Index run under the
current default yet. `make report` regenerates the table (the raw command
is `uv run python scripts/phase2_report.py --readme`). Index is the 0.3 public index; Full adds
the private parts only the maintainers run ([index-0.3-rescore.md](docs/results/index-0.3-rescore.md)).
ECE and latency are measured differently from the board's; see the run summaries:

<!-- phase2-table -->
| entry | Index | Full | ECE | coverage | median ms | p95 ms | run layout / orders | run calibration | shipped now | latency run |
|---|---|---|---|---|---|---|---|---|---|---|
| **qwen3.6-27b** † | 56.82 | — | 0.048 | 1.000 | 162.8 | 901.2 | blurb_header / identity | T=1.63/2.06/1.26 | blurb_header_reread / identity / v1 | 2026-10-25T141532Z-latency ‡ |
| Decider chat · Qwen3.6-27B | 51.57 | 51.25 | 0.021 | board | 83.6 | n/a | | | | |
| **gemma-4-31b** † | 62.98 | — | 0.119 | 1.000 | 199.7 | 1282.6 | blurb_header / top_p:0.9+reversed | T=3.98/5.21/6.74 | blurb_header_reread / top_p:0.9+reversed / v1 | 2026-10-25T131631Z-latency ‡ |
| Decider chat · Gemma-4-31B | 57.79 | 57.62 | 0.047 | board | 108.5 | n/a | | | | |
| **qwen3.8-27b** † | 57.64 | — | 0.024 | 1.000 | 287.9 | 1272.3 | blurb_header / min_n:4+reversed | T=1.64/1/1.21 | blurb_header_reread / min_n:4+reversed / v1 | 2026-10-25T124823Z-latency ‡ |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | board | 373.0 | n/a | | | | |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | board | 108.3 | n/a | | | | |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | board | 89.6 | n/a | | | | |
| **gemma-4-12b** † | 53.58 | — | 0.060 | 1.000 | 85.9 | 397.1 | blurb_header / identity | T=4.035 | blurb_header_reread / identity / v1 | 2026-10-25T145052Z-latency ‡ |
| AJev lora7 (Gemma 4 12B) | 55.17 | 49.11 | 0.082 | board | 69.1 | n/a | | | | |
| decisio 0.4.0 (Gemma 4 12B) | 49.72 | 47.93 | 0.103 | board | 37.8 | n/a | | | | |
| Winnow-12B | 50.66 | 47.07 | 0.168 | board | 72.5 | n/a | | | | |
| **qwen3.6-27b-fp8** † | 56.78 | — | 0.049 | 1.000 | 151.4 | 835.5 | blurb_header / identity | T=1.61/2.04/1.26 | blurb_header_reread / identity / v1 | 2026-10-25T152157Z-latency ‡ |
| Decider chat · Qwen3.6-27B | 51.57 | 51.25 | 0.021 | board | 83.6 | n/a | | | | |
| **qwen3.8-27b-fp8** † | 57.58 | — | 0.024 | 1.000 | 248.4 | 1171.9 | blurb_header / min_n:4+reversed | T=1.59/1/1.11, b=0.14 | blurb_header_reread / min_n:4+reversed / v1 | 2026-10-25T153711Z-latency ‡ |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | board | 373.0 | n/a | | | | |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | board | 108.3 | n/a | | | | |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | board | 89.6 | n/a | | | | |
| **qwen3.8-27b-nvfp4** † | 56.63 | — | 0.025 | 1.000 | 487.3 | 2880.5 | blurb_header / min_n:4+reversed | T=1.68/1.97/1.14 | blurb_header_reread / min_n:4+reversed / v1 | 2026-10-25T160045Z-latency ‡ |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | board | 373.0 | n/a | | | | |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | board | 108.3 | n/a | | | | |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | board | 89.6 | n/a | | | | |
| **gemma-4-31b-fp8** † | 62.82 | — | 0.116 | 1.000 | 135.5 | 789.7 | blurb_header / top_p:0.9+reversed | T=4.06/5.31/6.66 | blurb_header_reread / top_p:0.9+reversed / v1 | 2026-10-25T150150Z-latency ‡ |
| Decider chat · Gemma-4-31B | 57.79 | 57.62 | 0.047 | board | 108.5 | n/a | | | | |
| **gemma-4-12b-qat** † | 51.26 | — | 0.047 | 1.000 | 83.2 | 394.9 | blurb_header / identity | T=3.01/12.9/2.24 | blurb_header_reread / identity / v1 | 2026-10-25T150932Z-latency ‡ |
| AJev lora7 (Gemma 4 12B) | 55.17 | 49.11 | 0.082 | board | 69.1 | n/a | | | | |
| decisio 0.4.0 (Gemma 4 12B) | 49.72 | 47.93 | 0.103 | board | 37.8 | n/a | | | | |
| Winnow-12B | 50.66 | 47.07 | 0.168 | board | 72.5 | n/a | | | | |

- Calibration T is listed as choice/score/noul; b is the noul yes-offset.
- † the run's layout, orders or calibration differ from what ships now (or the calibration file is newer).
- ‡ the latency run's layout, orders or calibration differ from the Index run's.
<!-- /phase2-table -->

<details>
<summary>Latency notes</summary>

- **Latency** is the latency-v1 design with one sequential client, run on 2026-10-25 on our WSL
  workstation (RTX PRO 6000 at 600 W, Ryzen 7 3800X), vLLM 0.32, each profile's shipped layout, orders
  and calibration. The board's gate is median, mean and p80 each ≤ 1,000 ms; qwen3.8-27b-nvfp4 fails it
  (487.3 / 1,009.5 / 1,272.0 ms), the other eight pass. The 2026-10-20/21 runs (old default, vLLM 0.30,
  rented boxes except the 12B) stay in `docs/results/archive/<profile>/`.
- **qwen3.8-27b's row is the local 600 W run** (`2026-10-25T124823Z-latency`). Its newest latency dir,
  which `make report` would pick, is a rented-box run from the investigation below.
- **Qwen is slower on our workstation** than on the 2026-10-20 rented boxes. Not WSL2: a native-Linux
  box with the same CPU generation measures the same. Hybrid-Qwen prefill is CPU-bound, those boxes had
  much faster CPUs, and H1q and `min_n:4+reversed` compute more tokens per row; vLLM 0.32 adds about 5%
  to mean and p80. nvfp4 also loses time in FlashInfer's FP8 kernel for its attention projections.
  Details: [qwen3.8 latency note](docs/results/2026-10-25-qwen38-latency.md) (DS-032).

</details>

<details>
<summary id="quantization-trade-offs">Quantization trade-offs</summary>

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

</details>

## How it works

<details>
<summary><b>Design highlights:</b> how a stock model emulates Jev</summary>

- **Read the answer, don't generate it.** Each question becomes a multiple-choice prompt
  that stops at `Answer: (`. vLLM runs one token (`max_tokens=1`) and returns the
  log-probabilities of the option letters only. The model weights are unchanged, so chat
  still works. [Inference technique](docs/4-inference-technique.md),
  [decision readout](docs/background/decision-readout.md).
- **Prompt format is data, not code.** Wording and part order live in `prompts/<layout>.toml`.
  The default `blurb_header_reread` layout is `header` with an intro blurb: question list, then the
  state, then one question per row, so every row of a request shares one long
  prefix. A one-question request reads the list and state twice and, with up to 32 options,
  its question and labelled options twice too (H1q); a request too long to read twice is read
  once. Option names that only repeat their letter (A, B, …) are dropped (DS-045,
  [read-twice](docs/background/read-twice.md)). Profiles set the orders: gemma `top_p:0.9+reversed` (images `identity`), qwen3.8 `min_n:4+reversed`, qwen3.6 `identity`.
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

The design is in
[docs/superpowers/specs/](docs/superpowers/specs/2026-09-28-systemone-server-design.md).

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
needed. Never publish vLLM's port 8000 beyond loopback.

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

- **Serving the LAN:** set `GATEWAY_BIND` (default `127.0.0.1`; `0.0.0.0` or a LAN IP) and
  optionally `GATEWAY_PORT` (default `9000`) in `.env`. Then:
  - `make up` refuses a non-loopback bind until `GATEWAY_API_KEY` is set;
  - set `VLLM_API_KEY` too, and keep vLLM's port 8000 on loopback;
  - on WSL2, the bind alone doesn't reach the LAN: turn on mirrored networking, or add a
    Windows `netsh interface portproxy` rule and a firewall rule for the port.
- **TLS (planned):** the gateway speaks plain HTTP, so the key and traffic cross the LAN
  in the clear. The intent is a TLS proxy in front (e.g. a Caddy service in compose);
  until then, only bind beyond loopback on a network you trust.
- **Already in place:** API docs (`/docs`, `/openapi.json`) are off; the passthrough never
  forwards the client's `Authorization` to vLLM; keys never appear in logs; images are pinned
  by digest. Both services restart on failure (up to 3 times). A clean Docker restart leaves
  them stopped, but after a crash (e.g. WSL going down mid-run) Docker brings a running stack
  back on its own. Run `make down` if you need the GPU free.

## More

- [docs/development.md](docs/development.md): tests, benchmarks, evaluation, prompt and
  tokenizer changes, the repository map and earlier results.
- [docs/README.md](docs/README.md): background research.
- [docs/background/README.md](docs/background/README.md): deep dives with our measurements.
