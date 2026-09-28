# Open Jev alternatives: (A) diffusion route, (B) trained open-weight models

Research date: 2026-09-26. Target hardware: 1x RTX PRO 6000 Blackwell (96 GB, sm_120).
Raw material: `.firecrawl/trained/` (HF cards `hf_*`, GitHub READMEs `gh_*`, blogs `web_*`).
Leaderboard figures are from Jev Decision Index 0.2.1 (balanced skill; Jev 1.13 = 57.89, ECE 0.074, p50 524 ms hosted),
leaderboard data in `.firecrawl/space/data/index-v2.json` (run on 1x RTX PRO 6000). Self-reported numbers from
model cards are marked as such. The index counts rows an entrant trained on as wrong.

License check: every model below is Apache-2.0 (weights) except: **Tev1 weights have no license yet** ("being
finalized"), and the **Nimble GitHub code repo has no LICENSE file** (the HF adapter itself is Apache-2.0).
None is non-commercial. DiffusionGemma is Apache-2.0 (Gemma 4 license link).

---------------------------------------------------------------------------------------------------

## A. The diffusion route ("Jev mode" on DiffusionGemma)

### A.1 How it works, in plain language

- A normal (autoregressive) LLM writes one token at a time, left to right. To get a probability for an answer you
  stop at the answer position and read the next-token distribution. One question = one read (or one branch).
- A text-diffusion LLM (Google's `google/diffusiongemma-26B-A4B-it`, 25.2B total / 3.8B active MoE, 256-token
  canvas, released July 2026) works on a *canvas* of token slots at once. An autoregressive encoder prefills the prompt
  into a KV cache; a decoder with **bidirectional attention over the canvas** then starts from noise in every slot and
  repeatedly "denoises": each forward pass outputs a full vocabulary distribution for **every slot simultaneously**,
  and the sampler commits the confident ones. (Normal chat uses ~48 steps with an entropy-bounded sampler.)
  Source: https://huggingface.co/google/diffusiongemma-26B-A4B-it
- The Jev trick: build the answer template for the typed schema, e.g.
  `urgent: @\nteam: @\ntone: @`, and **seed the canvas with it**, leaving only one noised slot per question (`@`).
  Pin the template tokens so they never change. Run **one read-only denoising step**. At each answer slot the model has
  produced a distribution over the whole vocabulary; keep only the allowed single-token labels (`yes`/`no`,
  `A`/`B`/`C`, `0`/`1`/`2`), renormalize, and that **is** the answer distribution: noul = P(yes), choice = argmax +
  probabilities, score = expected level. All questions are read in the same pass, nothing is generated or parsed, and
  an answer cannot go off-schema.
- Optional refinements: re-read with fresh noise and average when a slot's entropy is high (openjev re-reads 3x when
  entropy > 0.1); run 2-8 steps so answers settle against each other; let the model "think" first, then read;
  constrain unembedding/sampling to the label ids (`diffusion_constrained` on vLLM main).
- Limitations (why it trails trained models): labels must be single tokens (multi-token options get relabelled to
  letters); questions in one canvas attend to each other (not Jev's isolated questions); the model was never trained
  for this readout, so probabilities are **poorly calibrated** (leaderboard ECE 0.20-0.23 vs 0.014-0.07 for trained
  models / Jev) and accuracy is lower. DiffusionGemma is also weaker than autoregressive Gemma 4 26B-A4B as a general
  model (MMLU-Pro 77.6 vs 82.6, GPQA 73.2 vs 82.3, BBEH 47.6 vs 64.8 per Google's card).

### A.2 Leaderboard (Decision Index 0.2.1)

| Entry | Skill | ECE | p50 | Notes |
|---|---:|---:|---:|---|
| JoshuaSP/open-jev (bf16, transformers) | 49.47 | 0.216 | 260 ms | best diffusion entry |
| djev (Davipar/djev-dev, bf16 vLLM) | 40.28 | 0.212 | 84 ms | |
| razorback16/openjev (NVFP4, vLLM) | 37.25 | 0.232 | 37.7 ms | fastest entry on the board |
| mmastrac vLLM PR 57250 example server | 32.24 | 0.202 | 127 ms | |
| (for scale) Jev 1.13 | 57.89 | 0.074 | 524 ms hosted | |

### A.3 vLLM PR #57250 (mmastrac): "[Core] structured generation mode for DiffusionGemma model (Jev-like)"

- URL: https://github.com/vllm-project/vllm/pull/57250 (raw: `gh_vllm_pr57250.json`)
- **Status: MERGED 2026-09-22 20:51 UTC**, merge commit `1b3b88ec2b7457aa030db4d0e7d8aaf04f6d0fb8`. vLLM **v0.30.0
  was tagged earlier that same day (05:20 UTC), so the PR is NOT in v0.30.0** - use a nightly / build from main or
  the pinned commit. Prerequisite PRs split out: #57414, #57416, #57417, #57462, #57589.
- Adds per-request `vllm_xargs` for DiffusionGemma: `diffusion_seed_canvas` (token ids replacing the random canvas),
  `diffusion_pinned` (positions held at seed value), `diffusion_max_steps`, `diffusion_read_only` (emit on the
  converging step, skip commit forward, temperature-1 logprobs), `diffusion_canvas_length` (per-request width;
  needs async scheduling), and makes `logprob_token_ids` (exact logprobs for the label ids, up to 128) work on the
  converging step. Also fixes a concurrency bug (HTTP 500 when parallel diffusion requests converge/commit in lockstep).
  Main has since added `diffusion_constrained` (unembed/sample over label ids only).
- Ships a prototype interposer `examples/features/structured_diffusion/structured_server.py` that serves
  `POST /v1/systemone` (Jev wire format, plus extensions `depends_on`, `ask_if`, `alone`, `think`, images via
  multipart or data URLs) and a schema-in-system-prompt `/v1/chat/completions` variant. It is **not** a native vLLM
  endpoint; `vllm serve` itself keeps serving normal OpenAI chat for the same model.
- How to use (from the PR / example README):
  ```bash
  vllm serve nvidia/diffusiongemma-26B-A4B-it-NVFP4 --diffusion-config '{"canvas_length": 32}' \
    --max-logprobs 32 --enable-prefix-caching --async-scheduling --attention-backend TRITON_ATTN --max-num-seqs 32
  python examples/features/structured_diffusion/structured_server.py --upstream http://127.0.0.1:8000 \
    --tokenizer nvidia/diffusiongemma-26B-A4B-it-NVFP4 --canvas 32      # listens on :8011
  ```
  FlashInfer attention is rejected for this model (mixes causal prefill with bidirectional denoising).
- PR test result: DGX Spark, 3 decisions/request: 1-way 8.7 req/s at 0.12 s; 32-way 54 req/s at 0.58 s (~162 decisions/s).
- Example README: https://github.com/vllm-project/vllm/blob/main/examples/features/structured_diffusion/README.md

### A.4 razorback16/openjev (the practical packaged server)

- https://github.com/razorback16/openjev (Apache-2.0, 450 stars, pushed 2026-09-27). Hosted free tier:
  `https://api.codiv.ai/v1/systemone` (Codiv, 100M input tokens free).
- What: Jev-wire-compatible `/v1/systemone` + **`/v1/chat/completions` (model `diffusiongemma-26b`, streaming and
  tools)** + `/v1/models` from **one** DiffusionGemma NVFP4 instance on vLLM. Model ids `openjev-latest`/`openjev-0.1`;
  accepts `jev-latest`/`jev-preview` so the TypeSafe SDK works unchanged (`TYPESAFE_BASE_URL`). Can also route to
  small side models (Laya, Verdict, CLM, JevK5) in sibling containers.
- Weights: `nvidia/diffusiongemma-26B-A4B-it-NVFP4` (~18 GB download; needs >= 24 GB GPU). **Tested on RTX PRO 6000
  Blackwell (sm_120).** MLX backend for Macs (4-bit, ~16 GB).
- Engine: Docker image pins vLLM at the PR merge commit `1b3b88ec` with two patches: label-id logprob cap 128 -> 512
  (choices up to 255) and bidirectional image-token attention (`docker/patches/vision_prefix_lm.py`).
- Launch:
  ```bash
  git clone https://github.com/razorback16/openjev && cd openjev && docker compose up -d   # :8080
  # or
  docker run -d --gpus all --ipc=host -p 127.0.0.1:8080:8080 \
    -v ~/.cache/huggingface:/root/.cache/huggingface razorback16/openjev:0.5.0
  ```
  Without Docker: checkout vLLM `1b3b88ec`, sed `MAX_LOGPROB_TOKEN_IDS = 512`, `pip install -e .`, then
  `vllm serve nvidia/diffusiongemma-26B-A4B-it-NVFP4 --served-model-name dgemma --diffusion-config '{"canvas_length": 64}'
  --max-logprobs 32 --enable-prefix-caching --async-scheduling --attention-backend TRITON_ATTN
  --limit-mm-per-prompt '{"image": 8, "video": 0}' --enable-auto-tool-choice --tool-call-parser gemma4
  --reasoning-parser gemma4 --override-generation-config '{"max_new_tokens": null}'` and `python -m openjev`.
- Perf on RTX PRO 6000 (38% of GPU, 3 q/request): c=1 10.7 req/s p50 94 ms; c=64 57.4 req/s p50 760 ms.
  Single request `samples:1`: 1 q 27 ms, 3 q 31 ms.
- Extensions: `images` (<=8), `steps` 1-8, `samples` 1-32, `think` 0-4096 tokens, `sequential`. Chunks ~12 questions
  per read in parallel. Chat: sampling fields ignored (vLLM refuses them for diffusion models), max 8 concurrent
  generations, `max_tokens` cap 8192.
- Chat? **Yes** - same loaded model serves chat, but it is DiffusionGemma-quality chat.

### A.5 Davipar/djev-dev ("djev")

- https://github.com/Davipar/djev-dev (Apache-2.0, 171 stars). Typed-decision layer + playground on DiffusionGemma via a
  source-pinned, patched vLLM composite (builds on PR 57250). Native image inputs, **images as options**, live camera.
- Reference HW: 1x B200, CUDA 13, **BF16 weights + BF16 KV** (~52 GB weights; fits 96 GB). Compact canvases (16-token
  buckets, `DJEV_CANVAS=128`), exact label logprobs (cap raised to 512), prefix reuse.
- Run: `docker build -f runtime/Dockerfile -t djev-local .` then `docker run ... djev-local` and
  `docker exec -d djev-model python3 -m djev --host 0.0.0.0 --port 8000`; decision endpoint `POST /v1/request`
  (Jev-like body). Docs mention a chat endpoint path with identical image parts inside the runtime.
- Leaderboard 40.28, p50 84 ms. Warns stock vLLM lacks its structured-read and image fixes.

### A.6 JoshuaSP/open-jev

- https://github.com/JoshuaSP/open-jev (MIT). Transformers harness (Modal H100, bf16, transformers 5.11, model rev
  `f7f5b7f5...`), **not a serving stack**. "Denoise freely, then choose the most likely allowed tokens from the final
  logits. No training."
- Method: tokenizes every allowed JSON value, fixes positions shared by all candidates, fills the rest with uniform
  noise, runs N steps on the 256-token canvas, then a trie-constrained final readout picks the highest-logit allowed
  token (handles multi-token options, strings/ints/bools). Output is real JSON. Grouped runner packs questions sharing a
  document into one canvas.
- Results (self-reported): Jev public examples 337 scored: 1-step 88.4% (one q/sequence), grouped 2-step 87.8% vs saved
  Jev 90.8%; grouped is 4.85x faster. Restricted softmax scores are explicitly **uncalibrated**.
- Leaderboard 49.47 (best diffusion), ECE 0.216, p50 260 ms.
- Run: `pip install -e '.[inference]'`; `DiffusionHarness.load().predict([request], steps=1)`; or `modal run infer.py`.

### A.7 githubnext/localjev

- https://github.com/githubnext/localjev (MIT, 781 stars). Bun/TypeScript bridge exposing `/v1/systemone` on top of
  **oMLX** (Mac) chat completions. It **prompts DiffusionGemma to write JSON probabilities** (self-reported, retries on
  malformed JSON) - wire-compatible but *not* a logit read.
- 1,200-request bake-off (M5 Max, 5 x 4-bit models, AG News / BoolQ / SST-5, 2 input lengths):
  short input macro acc: Gemma 4 26B-A4B 75.0%, Qwen3.6-35B-A3B 76.7%, **DiffusionGemma 74.2% and slowest** (p50 1.21 s).
  Conclusion: in this prompted pipeline DiffusionGemma did not win on speed or accuracy; for real probabilities use
  OpenJev's patched vLLM. Also notes LM Studio / llama.cpp could not load `diffusion_gemma` as of 2026-09-18.
  Source: https://github.com/githubnext/localjev/blob/main/docs/evaluation-results-2026-09-18.md

### A.8 Related: trained head on frozen DiffusionGemma

- `EryriLabs/DiffusionGemma-26B-A4B-Hev` (Apache-2.0, 2026-09-24): frozen DiffusionGemma + trained 44.5M-param Hydra
  (bidirectional SSM) head ensemble. **Specialist**: fitted per workflow on LocalLLaMA/typed-decisions; lifts canvas-read
  accuracy 0.708 -> 0.731, Brier 0.304 -> 0.094 on that test split. Needs 80 GB (bf16). Not on the Decision Index.

### A.9 Weights for the diffusion route

`google/diffusiongemma-26B-A4B-it` (bf16 ~51.6 GB), `nvidia/diffusiongemma-26B-A4B-it-NVFP4` (~18.8 GB; ModelOpt),
`RedHatAI/diffusiongemma-26B-A4B-it-NVFP4`, `RedHatAI/diffusiongemma-26B-A4B-it-FP8-dynamic`,
`unsloth/diffusiongemma-26B-A4B-it-GGUF`, `mlx-community/diffusiongemma-26B-A4B-it-{4,5,6,8}bit/bf16`.

### A.10 Practical status of the diffusion route (verdict)

- Works today on your GPU: razorback16/openjev Docker (NVFP4, tested on RTX PRO 6000) gives one server with
  `/v1/systemone` + OpenAI chat. Upstream vLLM support is merged (main/nightly only, not v0.30.0).
- Quality: 32-49 skill vs Jev 57.89 and calibration ~3x worse than Jev. Strength is latency/throughput (tens of ms)
  and zero training. Best accuracy (JoshuaSP, 49.47) comes from a research harness, not a server.
- Chat from the same model is DiffusionGemma chat: fast, but weaker than AR Gemma 4 26B-A4B and ignores sampling params.

---------------------------------------------------------------------------------------------------

## B. Trained open-weight models

### B.0 Summary table

| Model (HF) | Skill / ECE / p50 (index) | Base | Training | License | Size / quants | Serving | Keeps chat? |
|---|---|---|---|---|---|---|---|
| Surogate Rune 26B-A4B v3 (`surogate/rune-26b-a4b-GGUF`) | 57.44 / 0.120 / 120 ms | google/gemma-4-26B-A4B-it | full FT | Apache-2.0 | bf16 safetensors 51.6 GB; **no v3 GGUF** (v1 GGUFs at rev `2a15504`) | `surogate serve` (C++/CUDA): `/v1/decisions` + OpenAI chat + Anthropic; transformers | Chat endpoint works on the same model (generation intact; thinking mode used), chat quality unmeasured |
| AutoJev-27B (`denis-pplx/autojev-27b`) | 56.4 / 0.018 / 101 ms | Qwen/Qwen3.8-27B | full FT backbone + 255-way readout head | weights Apache-2.0, code MIT | bf16 ~49 GiB; community Q4_K_M GGUF (jev.cpp fork only) | `autojev-serve` FastAPI `/v1/systemone` (transformers) | **No** - LM head removed (arch `Qwen3_5Model` + `readout.safetensors`) |
| Jebadiah 27B (`frontier-infra/jebadiah-27b`) | 54.67 / **0.014** / 110 ms | Qwen3.8-27B chat ckpt (thinking off) | LoRA r16 **merged** | Apache-2.0 | bf16 ~56 GB; GGUF Q8_0/Q5_K_M/Q4_K_M; MLX 8/4-bit | `jebadiah-serve` (`/v1/systemone`, `/v1/decide`); AINode (vLLM); llama.cpp + `decide_gguf.py` | LM head intact, generative; chat not evaluated; adapter not published separately |
| Winnow-12B (`EldanRing/Winnow-12B`) | 50.02 / 0.168 / 72.5 ms (Q8) | google/gemma-4-12B-it | LoRA r32 merged | Apache-2.0 (data private) | GGUF Q8_0 12.7 GB / BF16 23.8 GB + mmproj 175 MB | winnow-inference (patched llama.cpp): `/v1/systemone` **and** `/v1/chat/completions`, vision | **Yes, by design** (quality vs base not measured) |
| Decider 35B-A3B (`Mapika/decider-35b-a3b`, `-nvfp4`) | 47.11 (NVFP4) / 0.023 / 101 ms | Qwen/Qwen3.5-35B-A3B-Base | partial full FT (2.45B params; routed experts frozen; Muon) | Apache-2.0 | bf16 65 GB; NVFP4 19.6 GB (vLLM/TRT-LLM); mradermacher GGUF | `decider.serve` `/v1/systemone` (bf16); NVFP4 only via a vLLM Python loop (no ready HTTP server) | **No** - "does not generate text", base (non-chat) model |
| Bespoke Nimble 9B v2 (`bespokelabs/Bespoke-Nimble-9B-v2`) | 39.57 / 0.024 / 77 ms | Qwen/Qwen3.5-9B (post-trained) | **unmerged PEFT LoRA r16 (173 MB)** | adapter Apache-2.0; GitHub code: no license file | base ~19 GB bf16 | `ParallelScorer` (transformers), MLX; hosted on SGLang via `openjev-sglang` (merged weights) | Base keeps chat if the adapter is applied per request; the adapter is decision-only |
| Kev 9B (`jaredpalmer/kev-9b`; also 0.8B/4B/27B) | 38.48 / 0.138 / 51 ms | Qwen3.5-9B-Base (27B: Qwen3.8-27B) | LoRA r16 + pointer head (`head.pt`) | Apache-2.0 | ~17-19 GB (27B: 55 GB, ~66 GB resident); community GGUFs | `kev.serve` `/v1/systemone` (CUDA/ROCm/MLX), Modal deploy | **No** - base model + custom head |
| Tev1-4B-experimental (`togethercomputer/Tev1-4B-experimental`) | 29.24 / 0.104 / 36 ms | Qwen/Qwen3.5-4B | LoRA r8 merged (Together FT; leaderboard labels it full FT) | **weights: no license yet ("being finalized")**; code MIT | ~9.3 GB bf16; bartowski/prithivMLmods GGUF | Any OpenAI server (vLLM/SGLang/llama.cpp): generates one letter; Together serverless | LM head intact but "generic chat is not the intended interface" |

All fit in 96 GB at bf16 (Decider bf16 65 GB is the largest).

### B.1 Surogate Rune 26B-A4B v3 (Invergent)

- Card: https://huggingface.co/surogate/rune-26b-a4b-GGUF ; blog: https://invergent.ai/blog/rune/ ; engine:
  https://github.com/invergent-ai/surogate (Apache-2.0, 823 stars).
- What: decision model for text **and images**, 262k context; choice/noul/score with probabilities in one pass.
  Standard `Gemma4ForConditionalGeneration` bf16 checkpoint (26.5B, 8/128 experts active). Repo name says GGUF but v3
  is **bf16 safetensors only**; "There are no GGUF builds of v3 yet" (v1 Q3/Q4/Q5_K_M GGUFs are at revision `2a15504`).
- Scores: leaderboard 57.44 (0.45 behind Jev). Self-estimated 59.2 with opt-in `"thinking": true` (unsure questions,
  top prob < 0.7, reason up to 512 tokens, ~1 in 10 questions; ~5 s for those). Calibration: T=1 ECE 12.5%; **with
  `--decision-temperature 2` ECE 2.2%** (choice unchanged). Image decisions: 83.4% on a 1,196-item Image JevBench-style
  self-run at 1,120 image tokens.
- Speed (RTX PRO 6000, bf16, surogate 1.5.3, 4 clients): per-request p50 388 ms / p95 2.33 s; one question idle
  0.09-0.18 s.
- Serve (they serve on 96 GB RTX PRO 6000):
  ```bash
  hf download surogate/rune-26b-a4b-GGUF --local-dir rune-v3
  surogate serve ./rune-v3 --host 0.0.0.0 --port 8000 \
    --max-model-len 32768 --max-num-seqs 8 --kv-capacity auto --decision-temperature 2
  curl localhost:8000/api/alpha/decisions -d '{"model":"<id>","state":"...","questions":{...}}'
  ```
  Use a surogate build with MoE router fix #217 (1.5.3 can crash under sustained load) and #240 for thinking. CUDA 13
  required (no CUDA 12 package). `--vision` for images.
- Surogate decisions API (https://github.com/invergent-ai/surogate/blob/main/docs/inference/decisions.md):
  `POST /v1/decisions` (aliases `/api/alpha/decisions`, `/api/v1/decisions`), OpenRouter decisions field names =
  Jev's shape (`state`, `questions{type,instructions,criteria}`), response `answers{choice,confidence,probabilities |
  noul | score,legend}`. **Not at `/v1/systemone`** - a trivial reverse-proxy alias is needed for the TypeSafe SDK.
  Shared state prefilled once; questions continue from it in waves. Works for **any served model or LoRA adapter**
  (generic prompt: SHARED STATE / QUESTION / OPTIONS, letter-logit softmax).
- Same server also serves `/v1/chat/completions`, `/v1/completions`, `/v1/responses`, Anthropic `/v1/messages`;
  **runtime LoRA** (`--enable-lora --lora-modules name=path`, per-request adapter by `model` name, supports Qwen hybrid
  linear-attention modules and Gemma 4, works over NVFP4 bases); **several models on one GPU** in one process
  (`--model name=/path/to/x.sinfer,...`, elastic KV, optional sleep mode). Formats: bf16, FP8, NVFP4, GGUF.
- Chat: Rune is a full FT of the *instruct* Gemma 4 model, keeps the LM head and chat template (thinking off by default);
  its thinking path generates text, so generation survives, but no chat-quality eval is published. Training data /
  recipe: not released on the card (surogate is the training engine).

### B.2 AutoJev-27B (denis-pplx)

- Card: https://huggingface.co/denis-pplx/autojev-27b ; code: https://github.com/denis-pplx/autojev (MIT).
- "Built with autonomous agents" end to end. Multimodal decision model; one forward pass **per question**.
- Architecture: `Qwen3_5Model` backbone (no `lm_head` in the checkpoint) + `readout.safetensors` = Linear(5120 -> 255)
  initialised from the LM-head rows of 255 single-token codes (A..Z, AA..). Fitted scalar temperature 2.21.
- Training: 1x H200, full-weight SFT, cross-entropy, lr 2e-6, eff. batch 256, 73,000 curated rows, checkpoint 200 of
  286. Training code + configs in repo; **exact curated corpus not bundled** (script builds an earlier 96k-row corpus).
- Self-reported: 84.60% acc vs Jev 82.79% on their panel; ECE 0.043. Leaderboard 56.4, ECE 0.018 (best-calibrated
  near the top).
- Serve: `uv run hf download denis-pplx/autojev-27b --local-dir checkpoints/selected; AUTOJEV_CHECKPOINT=... uv run
  autojev-serve` -> `POST /v1/systemone` (choice/noul/score + base64 images), playground at `/`. ~49 GiB bf16 via
  transformers/sdpa (no vLLM). Community GGUF: `thomasgauthier/autojev-27b-GGUF` (Q4_K_M + mmproj) requires the
  `thomasgauthier/jev.cpp` llama.cpp fork (mainline llama.cpp/LM Studio cannot run it).
- Chat: **no** (no LM head). Could only chat by grafting the base LM head onto a fully fine-tuned backbone - untested.

### B.3 Jebadiah 27B (Frontier Infra / AINode)

- Card: https://huggingface.co/frontier-infra/jebadiah-27b ; code: https://github.com/getainode/jebadiah (Apache-2.0).
  Also 9B v2 / 4B v2 (+GGUF/MLX), 27B GGUF (`frontier-infra/jebadiah-27b-GGUF`, Q8_0 260/260 same answers,
  Q4_K_M 258/260) and MLX.
- Base: `Qwen/Qwen3.8-27B` at rev `1d4bf0f2`, the **chat checkpoint, thinking off** (their "chat-checkpoint finding":
  training on the chat checkpoints beat the -Base ones).
- Training: LoRA r16 alpha32 on every linear projection incl. Gated DeltaNet (116.7M trainable), lr 1e-4, 1 epoch,
  1,862 steps, 1x H200 167 min; **public data only**: 11,013 records / 15,813 questions from
  `LocalLLaMA/typed-decisions`, license-permitting Kev v7 sources, HelpSteer2 train, SummEval. Merged into bf16
  (496/496 pairs; merged gives run's pick on 259/260). Full trainer, data builders, run records in the GitHub repo.
- Readout: label-token distribution at last prompt position, fp32, per-type temperatures (choice 1.23, noul 1.30,
  score 0.76). Choice capped at 20 options on `/v1/systemone`. Trained states <= 2,048 tokens. English.
- Scores: leaderboard 54.67, **ECE 0.014 (best on board)**. Self: headline 78.9 on their public suites; JevBench public
  0.866.
- Serve:
  ```bash
  git clone https://github.com/getainode/jebadiah.git && cd jebadiah/server
  uv sync --extra cuda && uv run hf download frontier-infra/jebadiah-27b
  uv run jebadiah-serve --model frontier-infra/jebadiah-27b    # /v1/systemone, /v1/decide, playground
  ```
  ~56 GB bf16. AINode loads it on **vLLM** (`extra_vllm_args: ["--language-model-only"]`), i.e. it is a stock
  Qwen3.8 checkpoint vLLM can serve; the decision readout is done by AINode's renderer + logprobs.
- Chat: LM head intact, generative model, but only the merged checkpoint is published (**no separate adapter**).
  Because it is a rank-16 LoRA merged into a known public base revision, the delta `W_jeb - W_base` is (up to bf16
  rounding) rank 16 and could be re-extracted as a PEFT adapter by SVD (e.g. mergekit `extract-lora`) - my inference,
  untested. Chat quality not evaluated; "the model never refuses" refers to decisions.

### B.4 Winnow-12B (EldanRing)

- Card: https://huggingface.co/EldanRing/Winnow-12B ; server: https://github.com/EldanRing/winnow-inference (MIT,
  builds on pinned llama.cpp). Also Winnow-E4B (39.89).
- Base `google/gemma-4-12B-it` (rev `707f0a3b`); LoRA r32 alpha64 on q/k/v/o/gate/up/down, merged; exported as BF16 and
  Q8_0 GGUF. **Training data private** (synthetic, teacher-supervised, labeled semantic tasks; 26k-example refinement
  with replay; gold CE + teacher CE when teacher agrees).
- Self-reported: JevBench public 231 items: Q8 85.71% = Jev 85.71%; Kev-v9 clean 81.55% vs Jev 87.0%.
  Leaderboard 50.02, **ECE 0.168** (T=1, no fitted calibration).
- Serve (same loaded model serves decisions, chat, vision):
  ```bash
  git clone https://github.com/EldanRing/winnow-inference.git && cd winnow-inference
  python3 scripts/setup.py            # downloads pinned Q8 + mmproj (~12.85 GB), builds server (CUDA >= 12.8 for Blackwell)
  python3 scripts/serve.py            # :8091, profile 5070ti-64k (64K ctx, 4 decision branches, 1 chat slot, q8 KV)
  # explicit: --model .../Winnow-12B-BF16.gguf --mmproj ... --context 65536 --decision-parallel 4 --chat-parallel 1 --cache q8_0 --memory exclusive
  curl localhost:8091/v1/systemone -d @examples/decisions.json
  curl localhost:8091/v1/chat/completions -d '{"model":"Winnow-12B","messages":[...],"stream":true}'
  ```
  Decisions: prefill state once, fork question branches, read answer-token logits (selected-head mode; `--head full`
  reference). In the "exclusive" profile chat and decisions share weights and take turns with KV (switching can evict a
  cached prefix) - on 96 GB you can raise context/parallelism. NVIDIA container needs CUDA 13-compatible driver.
- Chat: **yes**, "Chat uses the preserved Gemma template and the full vocabulary"; a paired chat-quality comparison
  vs the base was not completed.

### B.5 Decider 35B-A3B (Mapika)

- Cards: https://huggingface.co/Mapika/decider-35b-a3b , https://huggingface.co/Mapika/decider-35b-a3b-nvfp4 ;
  code: https://github.com/Mapika/decider (Apache-2.0, 535 stars; data registry + training scripts; family 0.8B/2B/4B/35B/2B-vision).
- Base `Qwen/Qwen3.5-35B-A3B-Base` (34.7B, 3B active; 30 GDN + 10 full-attention layers). One epoch on the public
  mixture (~95 decision datasets, agent trajectories, Mind2Web, games, Jev input shapes; 1.54M items, 463M tokens),
  **routed experts frozen**, 2.45B params trained with Muon + AdamW, 4x B300, 394 min. Temperature 1.08. No RL stage.
  Recipe and data registry are public.
- Readout: prompt `Context: ... Question ... (A) ... Answer: (` -> softmax over option-letter logits; many questions
  read from one pass (slots). 2-255 options.
- Self-reported: regression set 0.855/0.810; Bespoke suite macro 0.774 (Jev 0.760); JevBench hard 0.676.
  Leaderboard (NVFP4) 47.11, ECE 0.023.
- Serve bf16 (>= 80 GB, fits 96 GB): `pip install decider-ai`; `scripts/serve.sh Mapika/decider-35b-a3b 8000`
  (`decider.serve`, `/v1/systemone`, `use_graphs=False` required for this MoE; needs transformers >= 5.17,
  flash-linear-attention, `experts_implementation: grouped_mm`). Speed on B300: 47 ms single 3-q request.
- NVFP4 (19.6 GB, ModelOpt 0.46.1): transformers cannot load it; use vLLM (tested vLLM 0.29 on B300, not on sm_120):
  `LLM(model="Mapika/decider-35b-a3b-nvfp4", logprobs_mode="processed_logits", max_logprobs=256)` +
  `SamplingParams(max_tokens=1, allowed_token_ids=label_ids, logprobs=n)` + package prompt builder; ~1-1.5 points below
  bf16, argmax changes on 3-4% of rows. No packaged HTTP server for NVFP4 ("adapt `system_one` translation").
- Chat: **no** ("A language model that does not generate text ... called from software, not chatted with").
- Note: decider-ai 1.5.0 adds `decider.serve_vllm` (vLLM 0.29.0) for stock chat checkpoints read in the chat layout
  (e.g. Qwen3.6-27B, "Decider chat" leaderboard rows 51.35 / 57.33 for Gemma-4-31B) - that is an inference technique
  on stock models (other agents' scope) but relevant to a chat+decision server.

### B.6 Bespoke Nimble 9B v2 (Bespoke Labs)

- Card: https://huggingface.co/bespokelabs/Bespoke-Nimble-9B-v2 ; code: https://github.com/bespokelabsai/nimble
  (1,847 stars; **no LICENSE file** in repo). Tagline "Data, Model, Recipe for an open Jev".
- **Unmerged PEFT LoRA** (r16, alpha32, dropout 0.05) on `Qwen/Qwen3.5-9B` rev `c2022362` (the post-trained model),
  targets attention + MLP + GDN (`in_proj_qkv/z/a/b`, `out_proj`). Adapter keys use the multimodal prefix
  `base_model.model.model.language_model.layers.*`. 173 MB.
- Recipe (v2): 4,926 rows, 1 epoch, lr 5e-5, eff. batch 8, 8,192 max len, peak 24.5 GiB, 22 min. Original release
  data published: 2,676 train / 324 held-out (contrastive "flip one fact" pairs, synthetic labels, TypeSafe-style
  schemas; no Jev distillation). CE over allowed candidate logits.
- **Temperature T=2.179 must be applied** (`softmax(logits/2.179)`); loading the LoRA elsewhere silently gives T=1.
  Up to 255 choices; 8,192-token context; oversize rejected.
- Scores: leaderboard 39.57, ECE 0.024, p50 77 ms. Self: 90.1% on its 324 held-out vs Jev 93.2%.
- Serve: `ParallelScorer(model_dir)` (transformers, fields sequential on CUDA; MLX processes shared context once);
  hosted deploy (`deploy/modal_app.py`) uses **SGLang 0.5.19 + `ekzhang/openjev-sglang`** on merged weights, H100.
- Chat: the adapter is a pure decision adapter; the **base Qwen3.5-9B keeps chat if you apply the adapter only to
  decision requests** (multi-LoRA). This is the only top trained model published as a separate adapter.

### B.7 Kev (Jared Palmer)

- Code: https://github.com/jaredpalmer/kev (Apache-2.0, 7,224 stars); weights `jaredpalmer/kev-{0.8b,4b,9b,27b}`.
- LoRA r16 (attention, MLP, DeltaNet) **plus a pointer head** trained from scratch; Qwen3.5-*-Base (27B: Qwen3.8-27B
  post-trained, 55 GB bf16, ~66 GB resident, 80 GB GPU). Built-in temperature (9B T=2.30). Questions run as separate
  causal rows continuing from the shared state (GDN layers can't honour block masks). Public data + programmatic policy
  records; full suites and every trial with hashes published.
- Leaderboard Kev 9B 38.48 (ECE 0.138), Kev 4B 34.64, Kev 0.8B 14.6. Self: 9B locked test 0.852 OOD.
- Serve: `uv run --extra serve python -m kev.serve --run jaredpalmer/kev-9b --port 8008` (CUDA/ROCm/MLX), Modal deploy.
- Chat: **no** (Base model + head; LoRA keys are `base_model.model.layers.*` feature-extraction form).

### B.8 Tev1 (Together AI)

- Blog: https://www.together.ai/blog/how-to-train-your-own-jev ("How to train your own Jev for $17", 2026-09-22);
  code: https://github.com/togethercomputer/tev1 (MIT); weights `togethercomputer/Tev1-4B-experimental`, `-0.8B-`.
- Fully open **recipe** (weights license pending): 37,840 examples (MultiNLI, BoolQ, Banking77, AG News, SST-5,
  programmatic policies, routing, research taxonomy), LoRA r8 alpha16 all-linear, 1 epoch, lr 5e-5, on Together
  fine-tuning (~25 min, ~$17), deploy as Together dedicated endpoint.
- Interface: plain chat completion; model returns exactly one option letter (temperature 0, max_tokens 8,
  `enable_thinking: false`); logprobs are "model preferences, not calibrated confidence". Keeps Qwen's LM head.
- Leaderboard: 4B 29.24, 0.8B 12.85. Serve with any OpenAI-compatible engine (vLLM/SGLang/llama.cpp GGUFs by
  bartowski / prithivMLmods) + a small wrapper for `/v1/systemone`.
- Chat: technically a chat model, but "Generic chat is not the intended interface and may produce prose".

### B.9 vLLM multi-LoRA caveat for the Qwen3.5/3.6/3.8 family (important for "base + decision LoRA")

- Open issue https://github.com/vllm-project/vllm/issues/49354 (2026-07-21): on Qwen3.5/3.6 hybrid-GDN models,
  `enable_lora` produced **identical outputs to the base** (silent no-op) while HF PEFT changed labels; Gemma 4 passed
  after #39816. Workaround reported: merge the adapter and serve dense. Proposed shared fix PR #49464 was closed
  unmerged; PR #49525 is still open. Related merged fixes: #37912 (fused `in_qkvz` with LoRA), #47640 (partial GDN
  groups), #48850 (embedding modules). The failing case involved text-LoRA keys `model.layers.*`; Nimble's adapter uses
  `model.language_model.layers.*`, which may map correctly - **verify** by comparing label logprobs with/without the
  adapter against HF PEFT before trusting it.
- openjev notes: Qwen3.5 linear-attention layers make vLLM cache prompts in 528-token blocks, so short shared states
  don't share prefill.
- Alternative engine: surogate lists Qwen hybrid linear-attention modules (`linear_attn.in_proj_qkv/z/a/b`,
  `out_proj`) as supported runtime-LoRA targets, with per-request adapter selection and decisions on adapters.

---------------------------------------------------------------------------------------------------

## C. "Chat + decisions" on one 96 GB RTX PRO 6000 - options ranked

1. **surogate + Rune v3 (best accuracy, one process).** `surogate serve ./rune-v3 --decision-temperature 2 ...`
   gives `/v1/decisions` (Jev-shaped; alias to `/v1/systemone` with a proxy) and OpenAI/Anthropic chat on the same
   51.6 GB model, leaving ~40 GB for KV. If Rune's chat is not good enough, add a stock chat model in the same process
   (surogate multi-model on one GPU needs a prepared `.sinfer` cache for the extra model), e.g. an NVFP4 Gemma 4 26B-A4B
   or `nvidia/Qwen3.6-27B-NVFP4` (the example surogate itself uses). surogate's decisions endpoint also works on a
   stock chat model or a LoRA adapter. Risks: young engine, CUDA 13 only, need builds with #217/#240.
2. **vLLM (or surogate) base model + decision LoRA hot-swap.** Only Nimble v2 ships an unmerged adapter (9B; weak:
   39.57). The strong candidate is Jebadiah: base `Qwen/Qwen3.8-27B@1d4bf0f2` serves chat, Jeb's rank-16 delta
   re-extracted as a LoRA serves decisions (untested idea), or simply serve the merged Jebadiah-27B as both (small
   LoRA, chat likely mostly intact but unmeasured). You must implement the model's prompt renderer + label-logprob
   readout + temperatures yourself (vLLM has no `/v1/systemone`; see Decider's vLLM `allowed_token_ids` + processed
   logprobs pattern). Check vLLM issue #49354 first.
3. **Winnow-12B via winnow-inference (llama.cpp): turnkey.** One loaded model serves `/v1/systemone` + OpenAI chat +
   vision, 12.7-23.8 GB; 50.02 skill but poorly calibrated (ECE 0.168, no fitted temperature). Fine as a
   single-user/low-concurrency box; raise context/parallel on 96 GB.
4. **razorback16/openjev (diffusion): turnkey, fastest, least accurate.** One Docker container, NVFP4 ~18 GB, tested on
   RTX PRO 6000, `/v1/systemone` + `/v1/chat/completions`; 37.25 skill, ECE 0.23; chat is DiffusionGemma-grade.

Not chat-capable (decision-only servers): AutoJev-27B, Decider 35B-A3B, Kev. They can still share the GPU next to a
separate chat server (e.g. AutoJev ~49 GiB + a ~20-30 GB NVFP4/FP8 chat model), but that is two processes.
