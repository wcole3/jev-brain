# Top "inference technique" Jev reproductions: how each runs and whether it can share a GPU with a chat endpoint

Researched 2026-09-26. Target: one server on 1x RTX PRO 6000 Blackwell (96 GB) serving both
`/v1/chat/completions` and a Jev-style `/v1/systemone` from one loaded model.

Raw material is under `/home/welb/devspace/jev-onto/.firecrawl/infer/`. Files are named `<owner>_<repo>__<path with _>`.
Scores are from the Decision Index 0.2.1 data file (`infer/index-v0.2.1.json`, from
https://huggingface.co/spaces/multimodalart/jev-decision-index/resolve/main/data/index-v0.2.1.json) and
`notes/leaderboard-summary.txt`. That index runs on one RTX PRO 6000, the same card as the target.

| project | index skill | ECE | p50 | base | backend on the index run |
|---|---|---|---|---|---|
| Jev (closed) | 57.89 | 0.074 | 524 ms | - | - |
| Decider chat, Gemma-4-31B | 57.33 | 0.047 | 108.5 ms | google/gemma-4-31B-it | unreleased research server `decider2.serve_chat_adaptive` over `serve_chat_lowmem` (HF transformers) |
| simple-jev (featherless) | 55.74 | 0.113 | 373 ms | Qwen/Qwen3.8-27B bf16 | `hf-server/hf_server.py` (HF transformers, fla kernels) |
| reflex 27B | 52.16 | 0.024 | 108.3 ms | Qwen/Qwen3.8-27B-FP8 | reflex frontend over SGLang 0.5.20, triton attention, `--permutations 2` |
| Decider chat, Qwen3.6-27B | 51.35 | 0.021 | 83.6 ms | Qwen/Qwen3.6-27B bf16 | `decider.serve` v1.2.1 chat layout (HF transformers + CUDA graphs) |
| Jevfire | 49.37 | 0.052 | 89.6 ms | Qwen3.8-27B-FP8 | `DecisionEngine` client over a vLLM 0.29.0 OpenAI server |
| openjev-sglang | not on index | - | - | Qwen3.6-35B-A3B NVFP4 | SGLang 0.5.19 + a FastAPI sidecar |

The `latency_path` strings are quoted from `index-v0.2.1.json` -> `models[].latency_path`.

All of these projects use the same readout:
1. Render the state and the question with the model's chat template, with thinking turned off.
2. End each question row at an answer slot.
3. Read the next-token logits (or log-softmax values) of single-token option labels (A..Z, then two-letter tokens).
4. Softmax over the allowed labels, optionally divided by a temperature T.
5. Assemble the typed answer in code.

A log-softmax value differs from the logit by a constant per position, so any server that returns exact
log-probabilities for chosen token IDs gives the same distribution as raw logits. Both vLLM and SGLang provide
that. This is why the sidecar pattern works.

---

## 1. Mapika/decider: "Decider chat" readout on stock checkpoints

- Repo: https://github.com/Mapika/decider. 535 stars, Apache-2.0, last push 2026-09-25 (decider-ai 1.5.0,
  commit a5120cc). PyPI: `decider-ai` 1.5.0, import name `decider`.
- Blog: https://dev.to/mapika/decider-one-forward-pass-typed-decisions-calibrated-probabilities-32c9
  (`infer/blog_decider_devto.md`). It says stock Qwen3.6-27B and Gemma-4-26B-A4B-it "both read above our trained
  35B" under the decider readout, and that the next series will start from post-trained bases.

### What "chat layout" / "chat readout" means
- Decider's own weights (decider-2b/4b/35b) are trained on a **plain** layout:
  `Context: ... Question ... Options: (A) .. Answer: (`.
- The **chat layout** (added in 1.2.0, `docs/CHANGELOG.md`) wraps each row in the tokenizer's chat template: a
  single user turn, no system prompt, `enable_thinking=False`. The letter is read at the final ` (` of `Answer: (`.
  For Qwen3.5-family models:
  `<|im_start|>user\n Context:\n<state> \n\nQuestion: <q>\nOptions:\n(A) ..\n(B) .. <|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n Answer: (`
  (`infer/Mapika_decider__docs_CHANGELOG.md` around line 192).
- `DECIDER_LAYOUT=chat` (1.5.0) forces this layout on a **stock instruct checkpoint** that has no
  `decider_config.json`. "Decider chat · <model>" on the index means exactly this: a stock instruct model with no
  weight changes, the chat-layout prompt, and softmax(letter logits / T) with a fitted T.
- Published temperature: **Qwen/Qwen3.6-27B at T = 1.943** (README "What's new", `docs/SERVING.md` §8).
- No temperature is published for Gemma-4-31B.
- `decider.prompt.ChatTemplate` is generic. It passes `enable_thinking=False` when the template knows the switch
  and closes an open thinking block otherwise (`infer/Mapika_decider__decider_prompt.py`, lines 205-243). Gemma's
  template therefore works in principle.

### Servers (three routes)
1. **`decider.serve`**: HF transformers in-process, `EngineV2`.
   - Captures CUDA graphs keyed on (batch, length) at start-up: 89 graphs, and about 25 GB of graph memory on the 4B.
   - Forks a shared-prefix KV cache per question and bounds the fork with `DECIDER_SHARED_FORK_GB`.
   - Endpoints: `/v1/systemone` (TypeSafe wire format, so the official SDKs work with
     `TYPESAFE_BASE_URL=http://localhost:8000`), `/decide`, `/health`, `/stats`.
   - This server was used for the "Decider chat · Qwen3.6-27B" index row.
   - Launch: `scripts/serve.sh <model> 8000`, or
     `DECIDER_MODEL=Qwen/Qwen3.6-27B DECIDER_LAYOUT=chat DECIDER_TEMPERATURE=1.943 uvicorn decider.serve:app`.
   - It **owns the model**. There is no chat endpoint.
2. **`decider.serve_vllm`** (1.5.0, `infer/Mapika_decider__decider_serve_vllm.py`).
   - Runs **vLLM 0.29.0 in-process**: `vllm.v1.engine.async_llm.AsyncLLM.from_engine_args(...)` with
     `enable_prefix_caching=True, language_model_only=True, worker_extension_cls="decider.vllm_worker.WorkerExtension"`.
   - Each row is `engine.generate(TokensPrompt(ids), SamplingParams(max_tokens=1, temperature=0.0, logprob_token_ids=[letters]))`,
     followed by `softmax(logprob/T)`.
   - Endpoints: `/v1/systemone` (independent questions only), `/v1/models`, `/health`, `/stats`.
     **There is no `/v1/chat/completions`.** The FastAPI app owns the AsyncLLM. Adding chat would mean mounting
     vLLM's OpenAI serving classes on the same engine yourself.
   - `decider.vllm_worker` monkey-patches `vllm.sampling_params.MAX_LOGPROB_TOKEN_IDS` (and the V2 runner copy in
     `vllm/v1/worker/gpu/sample/logprob.py`) from 128 to 256 inside each worker, so a question with up to 255
     options is one request. It also turns off cuDNN SDPA, which returns wrong masked-attention output on Blackwell
     with torch 2.13/2.14.
   - Prefix reuse comes from vLLM's automatic prefix cache. For hybrid Qwen3.5/3.6 models the recurrent state is
     cached only at block boundaries: 784 tokens for Qwen3.6-27B with bf16 KV. The first row is therefore run alone
     when the shared prefix covers at least one block.
   - Install (it needs a separate venv because vLLM needs numpy 2 and decider-ai pins numpy < 2):
     ```bash
     python -m venv decider-vllm && . decider-vllm/bin/activate
     pip install vllm==0.29.0 fastapi "uvicorn[standard]" jinja2 huggingface_hub
     pip install --no-deps decider-ai
     DECIDER_MODEL=Qwen/Qwen3.6-27B DECIDER_LAYOUT=chat DECIDER_TEMPERATURE=1.943 DECIDER_VLLM_GPU_MEMORY_UTILIZATION=0.90 \
         uvicorn decider.serve_vllm:app --host 127.0.0.1 --port 8000
     ```
   - Measured on one B300 with bf16 Qwen3.6-27B: median 32.3 ms, p95 430 ms, 99.62% argmax agreement with the
     submitted index run.
   - The FP8 checkpoint was *slower* (block-scaled CUTLASS FP8 GEMM) and changes answers (99.02% agreement)
     (`docs/SERVING.md` §8.1).
3. **`decider2.serve_chat*`**: an unreleased research server.
   - The Gemma-4-31B index row says "decider2.serve_chat_adaptive over serve_chat_lowmem as board (graph server
     serve_chat OOMs on 96 GB)".
   - `docs/SERVING.md` §4.2 mentions that `decider2/serve_chat.py` subclasses `Engine.score_shared`.
   - This code is **not in the public repo**. The public equivalent for Gemma would be `decider.serve_vllm` with
     `DECIDER_MODEL=google/gemma-4-31B-it DECIDER_LAYOUT=chat` and your own temperature fitted with
     `python -m decider.calibrate`. That exact configuration has not been benchmarked publicly.

### Readout details
- Labels: A..J (narrow), then K..Z, then single-token two-letter strings, up to 255 options (`prompt.MAX_OPTIONS`).
- Options are in request order. No permutation averaging is done.
- Score questions have 2..10 levels, optionally with "isolated levels" (one yes/no row per level).
- Noul returns P(yes). Confidence follows TypeSafe's definition from 1.3.0 onward.
- Calibration is one temperature, or per-type temperatures (`temperature_by_type`).
  `python -m decider.calibrate records.jsonl` fits them by NLL.

### Fit on 96 GB
- Qwen3.6-27B bf16 has about 56 GB of weights (27.8B params per the index) and fits in vLLM at 0.90 utilization.
- In-process `decider.serve` with the full CUDA-graph grid is tight. The Gemma-31B graph server OOMed on 96 GB.
- Gemma-4-31B bf16 weights are about 65 GB (32.7B params per the index). They fit in vLLM with a smaller KV cache.

### Coexistence verdict
- Neither public server exposes chat. `serve_vllm` is the closest because the engine is vLLM.
- The prompt builder (`decider.serve.prepare`) and the temperature code are reusable as a library in front of any
  vLLM endpoint that supports `logprob_token_ids`.

---

## 2. featherless-ai/simple-jev

- Repo: https://github.com/featherless-ai/simple-jev. 551 stars, Apache-2.0, last push 2026-09-26 (image chat
  support added). Hosted demo: https://simple-jev-demo-api.featherless.ai/v1/ (2k context, 2 RPS).
- Backend: **HF transformers + PyTorch in-process** (`hf-server/hf_server.py`, a single file of about 62 KB).
  - Dependencies: torch>=2.6, transformers>=5.16.1, accelerate.
  - The README says: "No worker, stream, FP8, kernel, or other performance optimizations are included."
  - The index run used bf16 with fla kernels and fell back to a torch conv because causal-conv1d was absent.
- Execution model:
  - Finds the exact common token prefix across the question branches and prefills it once with `use_cache=True`.
  - Copies and repeats the cache per suffix batch (`reorder_cache`) and reads the logit at each row's last token.
  - **Requests are processed serially** behind a model lock. Parallelism exists only inside a request, and there is
    no cross-request cache.
  - The admission queue returns 429 when full (17 admitted requests).
- API: `POST /v1/classifier`, with `/v1/systemone` as an alias (hidden from OpenAPI). Also `/v1/models` and
  `/health`.
  - The API is "inspired by" TypeSafe but has project-specific behavior: Score returns a `legend`, Choice
    confidence is the max probability, and Noul is either P(yes) binary or a nine-bin 0.01-0.99 mapping depending
    on the policy.
  - Input is `state` or chat `messages`. Images are supported for Qwen-VL, Qwen3.5, Gemma3/4 and LLaVA.
- Launch:
  ```bash
  git clone https://github.com/featherless-ai/simple-jev.git && cd simple-jev
  python3.13 -m venv .venv && . .venv/bin/activate && python -m pip install -e './hf-server'
  simple-jev --model Qwen/Qwen3.8-27B --device auto --dtype bfloat16 \
    --max-request-branches 256 --max-model-len 32768 --max-choice-options 255 --enforce-model-id
  ```
  The index row used `--max-model-len 65536` and batch tokens 65536.
- Readout:
  - Prompt "policies" are auto-selected from the architecture fingerprint. Qwen3.8-27B gets `examples_binary`
    (legacy) or `shared_examples_binary` (sharing-safe).
  - Policies add worked examples, and some repeat the state twice. Choice branches get a fixed three-line
    `[thinking]` prefill.
  - Labels: A-Z then a-x (up to 50), then tokenizer-validated two-letter uppercase labels up to 255.
  - Softmax over the permitted labels. Multi-token labels are rejected, not truncated.
  - **No calibration**: the docs state the probabilities "are not calibrated probabilities of correctness." There
    is no temperature and no permutation averaging.
  - Specification: `common/PROMPT_STRUCTURE_V1.md`. `eval/prompt_search.py` picks the best policy per model.
- Fit on 96 GB: 27B bf16 is about 55 GB of weights plus per-batch KV copies.
  - On the index (a 96 GB RTX PRO 6000), 203 of 760 latency rows ran out of GPU memory at the server's default
    batch. They were re-answered in-process with a batch-size ladder.
  - Its p50 of 373 ms is the slowest of the top group.
- Coexistence verdict:
  - The server owns the model and has no chat endpoint.
  - `attach_routes(app, get_service)` is an explicit hook for **embedding the classifier routes in another FastAPI
    app**. In principle you could add a transformers `generate()` chat route in the same process on the same
    weights, but you would be writing a slow HF-generate chat server that serializes with a lock.
  - This project's value to you is its prompt policies and (vendored) scoring code. Its serving engine is not
    useful for a combined server. `common/` is plain Python designed to be reused by "other inference
    implementations".
- Also in the repo: RFDT (Really Fancy Decision Training) for task-specific fine-tuning, and vendored eval suites.

---

## 3. kshetrajna12/reflex

- Repo: https://github.com/kshetrajna12/reflex. 153 stars, MIT, last push 2026-09-27 (last main commit 231f896 on
  2026-09-22). WebGPU demo: https://kshetrajna12.github.io/reflex/ (Qwen3.5-0.8B).
- Two backends:
  - **transformers in-process** (default, `reflex.engine`). Uses a KV cache per state and isolates branches with a
    packed attention mask or batch-expanded cache copies.
  - **`--backend sglang --sglang-url http://127.0.0.1:30000`**: a pure sidecar where "the reflex process holds no
    weights, so it needs no GPU of its own" (`docs/SERVING.md`, `src/reflex/backends/sglang.py`).
- SGLang protocol (copied from openjev-sglang):
  1. Warm the radix cache with the shared prefix. This call uses `max_new_tokens=1` and requests one unused token
     id (see the crash below).
  2. Send all branches in one native `POST /generate`, where `input_ids` is a list of lists and each item carries
     `return_logprob=true`, `logprob_start_len=-1`, `token_ids_logprob=[label ids]` and its own `rid`.
  3. Read `meta_info.output_token_ids_logprobs`.
  Required SGLang flags: radix cache on, and `--mamba-radix-cache-strategy extra_buffer` for hybrid Qwen.
- API: `POST /v1/systemone` ("same request and response shapes as TypeSafe's hosted API"). Also `/v1/models`,
  `/health`, `/healthz`, an optional bearer key (`--api-key` / `REFLEX_API_KEY`) and an `x-reflex-latency-ms` header.
- Launch:
  ```bash
  git clone https://github.com/kshetrajna12/reflex && cd reflex && git checkout stable && uv sync
  uv run reflex-serve --stable --port 8008                     # in-process, Qwen3.5-4B, permutations 2
  # sidecar over SGLang:
  python3 -m sglang.launch_server --model-path Qwen/Qwen3.8-27B-FP8 --port 30000 --mem-fraction-static 0.85 \
     --context-length 65536 --max-running-requests 32 --max-mamba-cache-size 320 --mamba-ssm-dtype bfloat16 \
     --mamba-radix-cache-strategy extra_buffer --chunked-prefill-size 8192 --attention-backend triton
  uv run reflex-serve --backend sglang --sglang-url http://127.0.0.1:30000 --model Qwen/Qwen3.8-27B-FP8 --permutations 2 --port 8008
  ```
  The full-index flags come from `scripts/decision_index/serve_h100.py`. That run used `fa3`, which is
  Hopper-only; the RTX PRO 6000 index run used the triton attention backend.
- Readout:
  - Lettered options; A..Z only, so **at most 26 choice options**. Score has 2..10 levels.
  - Noul is read as a lettered yes/no pair by default (`noul_readout: letters`).
  - **Two option orders per question, averaged** (`--permutations 2`). Measured on the public items: hard tier
    0.658 -> 0.685, ECE 0.086 -> 0.081, and pooled external ECE 0.055 -> 0.032
    (`docs/results/order-averaging.md`).
  - Optional per-primitive temperature scaling (`reflex-eval-mmlu --fit-temperature`, `reflex-calibrate refit`).
    `stable` ships with no calibration file.
  - The index 0.2.1 run used an unpublished "wide_choice.py" overlay for more than 26 options, plus admission
    patches. The public main branch still refuses questions with more than 26 options (14,500 refusals in the
    0.1 full run, `docs/results/decision-index.md`).
- Memory (`docs/results/sglang-backend.md`, GB10):
  - Qwen3.8-27B bf16 on SGLang: 51.7 GB weights plus 14.6 GB KV plus 4.3 GB graphs, about 85 GB total.
  - `RadixArk/Qwen3.8-27B-NVFP4`: 22.8 GB weights, about 54 GB total, and faster (208 ms warm p50). Its
    calibration is worse, though: ECE 0.044 -> 0.067.
  - SGLang limits concurrency through the mamba state slots, and each reflex request fans out to
    questions x permutations branches. Use `--mamba-ssm-dtype bfloat16` to double the slots.
- **Coexistence verdict:** the architecture is right, because SGLang owns the GPU and SGLang's own
  `/v1/chat/completions` is on the same port as `/generate`. There is a serious blocker, however (see the
  analysis section): **SGLang issue #34719**.

---

## 4. kikoncuo/jevfire

- Repo: https://github.com/kikoncuo/jevfire. 69 stars, MIT, last push 2026-09-18. Site with visual guide and
  browser demos: https://kikoncuo.github.io/jevfire/.
- Backend: **a pure CPU HTTP sidecar over a standard `vllm serve` OpenAI server**. The README says: "vLLM owns
  CUDA execution and KV state. JEVfire is a lightweight HTTP sidecar; it does not load another copy of the model."
- vLLM features it relies on (`docs/deployment.md`, `jevfire/core.py`):
  - Native batched `/v1/completions`, with `prompt` as a list of token-id lists.
  - `max_tokens: 1, temperature: 0, logprobs: 0`.
  - **`logprob_token_ids`**: the exact logprobs of the selected label ids. This is a vLLM request field; stock vLLM
    caps it at 128.
  - `return_tokens_as_token_ids`, `add_special_tokens: false`.
  - Optional `cache_salt`.
  - **Automatic prefix caching**, with an optional "aligned prefill" that pads the common prefix to the verified
    hybrid cache block (1,568 tokens in their Qwen3.8-27B-FP8 setup).
  - For 129-255 choices the prompt is scored in two chunks and the raw logprobs are merged. An optional one-line
    patch raises vLLM 0.29's `MAX_LOGPROB_TOKEN_IDS` to 256.
- The exact tested backend was an RTX PRO 6000 Blackwell, the same card as the target:
  ```bash
  vllm serve Qwen/Qwen3.8-27B-FP8 --revision 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a --served-model-name qwen3.8-27b \
    --host 127.0.0.1 --port 8000 --tensor-parallel-size 1 --gpu-memory-utilization 0.45 --max-num-batched-tokens 2096 \
    --max-num-seqs 64 --max-model-len 16384 --kv-cache-dtype fp8 --reasoning-parser qwen3 --enable-prefix-caching --language-model-only
  pip install -e '.[dev]'
  DECISION_VLLM_URL=http://127.0.0.1:8000 DECISION_MODEL=qwen3.8-27b DECISION_TOKENIZER=Qwen/Qwen3.8-27B-FP8 \
    python -m uvicorn jevfire.app:app --host 127.0.0.1 --port 8010 --no-access-log
  ```
  The index run used `--max-model-len 262144` and GPU utilization 0.9.
- API: **`POST /v1/decisions`**, its own schema: flat `boolean` and `enum` fields, 1-64 fields, up to 255 choices,
  and a `score_temperature` parameter. It is **not the Jev `/v1/systemone` wire format** and has no Score type.
  The Decision Index kit used its own adapter (`DecisionEngine`) to map requests.
- Readout:
  - One system prompt ("return exactly its option label").
  - Each field is appended as `Selected field definition: {name, description, options:{label: value}}`.
  - Labels are verified single tokens: A-Z, AA.., then a-z.
  - softmax(logprob / score_temperature) over the field's labels. `scores_are_calibrated` is always false.
  - No permutation averaging. Optional abstention via `min_probability`.
  - Headline claim: 28 fields in 497 ms on the RTX PRO 6000, versus 5.1 s for constrained JSON generation.
- **Coexistence verdict: works as-is on vLLM.**
  - The same `vllm serve` process also serves `/v1/chat/completions` (thinking is available through
    `--reasoning-parser qwen3`).
  - It is the lowest-friction "one model, both endpoints" setup, but it is only a decision API, not Jev-wire. For
    `/v1/systemone` you need an adapter, or you use decider's prompt code against the same vLLM (see the
    recommendation).
  - Its index score (49.37) is the lowest of the five.

---

## 5. ekzhang/openjev-sglang

- Repo: https://github.com/ekzhang/openjev-sglang. 328 stars, **no license file** (GitHub `license: null`), last
  push 2026-09-25. It is not on the index.
- Backend: SGLang 0.5.19 (`lmsysorg/sglang:v0.5.19-cu130`) with the Rust frontend, radix cache and breakable
  prefill CUDA graphs, plus a **separate Python FastAPI process** that talks to SGLang over localhost HTTP.
  - The default model is `nvidia/Qwen3.6-35B-A3B-NVFP4`, public name `Qwen/Qwen3.6-35B-A3B`.
  - Deployment target: one B200 on Modal (`modal_app.py`).
- SGLang launch (`src/openjev/runtime.py`):
  ```
  --mem-fraction-static 0.8 --moe-runner-backend flashinfer_cutlass --mamba-radix-cache-strategy extra_buffer
  --cuda-graph-backend-prefill breakable --cuda-graph-max-bs-decode 64 --enable-metrics
  ```
  The profile adds `--language-only --attention-backend trtllm_mha --kv-cache-dtype fp8_e4m3`.
  `trtllm_mha` targets B200 (SM100). On an RTX PRO 6000 (SM120) you would need a different attention backend
  (triton or flashinfer), and NVFP4 MoE support on SM120 should be verified.
  The server refuses `--disable-radix-cache` and `--disable-cuda-graph`.
- Modes:
  - `uv run openjev serve --sglang-python /path/to/sglang/bin/python` launches SGLang itself.
  - **`uv run openjev serve --connect http://127.0.0.1:30000`** attaches to an existing SGLang, which must have a
    matching model and tokenizer revision, selected-token logprobs, radix cache and enough context.
- API: `POST /v1/systemone` (TypeSafe/Jev HTTP API), plus `/v1/models`, `/v1/limits`, `/health`, `/health/live`,
  and docs at `/` and `/docs`.
  - The `jev-latest` alias is accepted.
  - The README says: "SGLang's generation and administration routes remain on localhost and aren't forwarded
    publicly." Chat would come from exposing SGLang's own port.
- Readout:
  - Protocol: N+1 calls to `/generate` with `max_new_tokens=1`. The first warms the radix cache with the prefix;
    then each branch is `prefix + question + "Answer:\n"` with `token_ids_logprob=[labels]` and
    `logprob_start_len=-1`.
  - Labels are A-Z plus verified two-letter tokens, **at most 64 answers and 64 questions**.
  - Temperature: `OPENJEV_TEMPERATURE`, default 1.0.
  - Confidence is 1 - H/log n. The docs say the probabilities "are not calibrated estimates."
  - There is no permutation averaging.
  - Its evals put it roughly level with plain Qwen3.8-27B one-token MMLU-Pro (58.8% vs 60.0%) and well below Jev
    (82.9%) (`evals/results/qwen38-27b/report.md`).
- It originated the SGLang workaround for the mixed-logprob crash (warm-ups request one unused token id).
- **Coexistence verdict:** it is a sidecar by design (`--connect`), so SGLang can serve chat on :30000 at the same
  time. It has the same SGLang #34719 hazard, it has no license, and it tops out at 64 options.

---

## Chat coexistence analysis

### A. Which projects can share one loaded model with `/v1/chat/completions`?

| project | owns weights? | sidecar mode | chat on same engine out of the box? |
|---|---|---|---|
| decider `serve` | yes (HF) | no | no |
| decider `serve_vllm` | yes (in-process vLLM AsyncLLM) | no | no. You would need to mount vLLM's OpenAI chat serving on its engine or port its 20-line `_logprobs` onto HTTP |
| simple-jev | yes (HF, serial) | no. `attach_routes()` allows embedding in another FastAPI app | no |
| reflex | transformers by default; **none with `--backend sglang`** | yes (SGLang `/generate`) | yes, SGLang serves chat on the same port, **but see #34719** |
| jevfire | none | yes (vLLM `/v1/completions`) | **yes, it works today**. Not Jev-wire (`/v1/decisions`, no Score) |
| openjev-sglang | none (with `--connect`) | yes (SGLang `/generate`) | yes, **but see #34719** |

### B. Engine-level hazards when mixing chat and decision traffic
1. **SGLang: scheduler crash on mixed batches.** Issue https://github.com/sgl-project/sglang/issues/34719
   (`infer/sglang_issue34719.json`) is still open.
   - The scheduler dies with `AttributeError: 'list' object has no attribute 'tolist'` whenever a request that uses
     `token_ids_logprob` shares a batch with a request that does not. That covers a normal chat completion.
   - The bug affects both the prefill and decode paths. It was confirmed on v0.5.14-v0.5.17, and a comment on
     2026-09-23 says it **still reproduces on v0.5.20**, the latest release (2026-09-18).
   - `--disable-overlap-schedule` does not avoid it.
   - The fix PR https://github.com/sgl-project/sglang/pull/34075 is open and not merged.
   - The reflex and openjev workaround (warm-up calls also request an unused token id) only keeps *their own*
     traffic uniform. An ordinary chat client co-batched with a decision request can take the server down into a
     crash loop.
   - **Do not run chat and reflex or openjev on one stock SGLang** unless you patch SGLang with #34075 (and
     re-verify the prefill path), or force every chat request to also carry `token_ids_logprob`. The second option
     was not verified for SGLang's OpenAI chat route.
2. **vLLM: silent logprob corruption in the V1 sampler, open PR https://github.com/vllm-project/vllm/pull/51789.**
   - When a `logprob_token_ids` request shares a batch with a `logprobs=k` (top-k) request, the *other* requests'
     top-k logprobs become -inf. Text is unaffected and nothing crashes.
   - Chat clients that do not ask for logprobs are unaffected.
   - The PR says the V2 model runner already merges per request. decider's worker patch touches the V2 runner path
     (`vllm/v1/worker/gpu/sample/logprob.py`).
3. **vLLM: speculative decoding combined with `logprob_token_ids` can crash the RejectionSampler.** Issue
   https://github.com/vllm-project/vllm/issues/42592 is open; the fix PR #44727 is open.
   - Do **not** enable MTP or speculative decoding (commonly used for Qwen chat speed) on the shared server.
4. **Precision changes calibration.**
   - FP8 changed about 1% of decider's argmaxes and was slower on a B300 (`decider docs/SERVING.md` §8.1).
   - NVFP4 raised reflex ECE by about 50% (`reflex docs/SERVING.md`).
   - A temperature fitted for one checkpoint, precision, prompt or layout does not transfer. Refit after any change.
5. **Hybrid (Qwen3.5/3.6/3.8) prefix caching is block-granular.** It uses 784-1,568 token blocks and mamba "align"
   or `extra_buffer` modes. Chat traffic and decision traffic compete for the same prefix cache and mamba slots.

### C. vLLM features that make a combined server easy (checked in vLLM source)
- **`logprob_token_ids`** is a request field on both `/v1/completions` and `/v1/chat/completions` in v0.30.0
  (`vllm/entrypoints/openai/{completion,chat_completion}/protocol.py`, saved as
  `infer/vllm_v0.30.0_*_protocol.py`). The cap is `MAX_LOGPROB_TOKEN_IDS = 128` in `vllm/sampling_params.py`, and
  it is not supported with beam search.
- **`/generative_scoring`** is a built-in vLLM route (present in v0.29.0 and v0.30.0; docs at
  `docs/serving/online_serving/generative_scoring.md`, saved as `infer/vllm_v0.30.0_generative_scoring.md`).
  - Input: `query` + `items` + `label_token_ids`. Output: the softmaxed probability of the first label.
  - It is available automatically on any generative model, on the same server as chat. It only returns one scalar
    per item (the first label), so it is too narrow for Choice distributions. `/v1/completions` with
    `logprob_token_ids` is the better primitive.
- **`--middleware <import.path>`** (v0.30.0 `vllm/entrypoints/launchers/cli_args.py` line 323): adds arbitrary
  ASGI middleware to `vllm serve`.
  - `app.state.engine_client` is set in `launchers/api_server/app_state.py`.
  - A middleware can therefore intercept `POST /v1/systemone` and call
    `engine_client.generate(TokensPrompt, SamplingParams(max_tokens=1, logprob_token_ids=...))` in-process. That
    gives a single process and a single port, with chat and decisions co-scheduled by vLLM.
  - No project ships this yet. It is a design option, and decider's `serve_vllm._logprobs` is almost exactly the
    code needed.
- Open vLLM feature requests: #56767 and #56782 ("compact LM-head fast path for fixed-candidate scoring") would
  make label scoring cheaper.

### D. Projects that already serve chat and decisions from one loaded model (outside the top five)
- **EldanRing/winnow-inference**: a native llama.cpp server. "`/v1/systemone` ... `/v1/chat/completions` retains
  llama-server's chat, vision, and streaming interfaces", with "the same loaded model". It is built for the
  fine-tuned Winnow-12B (Gemma 4 12B) GGUF. See `trained/gh_EldanRing_winnow-inference_README.md`.
- **razorback16/openjev**: DiffusionGemma 26B-A4B on vLLM, with `POST /v1/systemone` and
  `POST /v1/chat/completions` (model `diffusiongemma-26b`) on one server. It is diffusion-specific and depends on
  vLLM PR #57250 (merged). See `trained/gh_razorback16_openjev_README.md`.
- **invergent-ai/surogate** (`surogate serve`, a native C++/CUDA engine): `/v1/chat/completions` plus
  `/v1/decisions`, which uses OpenRouter's decisions-API field names rather than Jev-wire, in one process. The
  decision readout is option-letter softmax with `--decision-temperature`, and the shared state is prefilled once.
  Its docs say "Chat, completions and every other endpoint are unaffected." See `trained/gh_surogate_decisions.md`.
- Thin clients over any OpenAI server with logprobs: genai-craft/openvons (`/v1/systemone` over `vllm serve`) and
  bnsd55/jevmlx (`--backend openai`). They are lower quality on the index.

---

## Recommendation: combined chat + `/v1/systemone` on one 96 GB RTX PRO 6000

**Use one `vllm serve` process as the only owner of the weights. Put a thin CPU-only `/v1/systemone` layer in
front that uses decider's chat-layout readout, and have that layer proxy `/v1/chat/completions` through, so there
is one port.**

1. Engine (vLLM 0.29 or 0.30).
   - Model: `vllm serve Qwen/Qwen3.6-27B` in bf16, about 56 GB. It is the only stock model with a published,
     validated temperature for this readout: T 1.943, index 51.35, ECE 0.021.
   - Alternatively `google/gemma-4-31B-it` in bf16, about 65 GB. It has the best index skill (57.33), but you must
     fit T yourself, and the index number came from unreleased code.
   - Flags: `--enable-prefix-caching --gpu-memory-utilization 0.90`, and a max-model-len sized for chat (32-64k).
   - Do **not** enable speculative decoding.
   - Optionally apply the 256 `MAX_LOGPROB_TOKEN_IDS` patch (jevfire `patches/`, or decider's worker extension).
     Without it, chunk questions with more than 128 options.
2. Decision layer.
   - Use `decider.serve.prepare` (chat layout, thinking off, answer slot " (") and `decider.temperature` from
     `pip install --no-deps decider-ai`.
   - Replace `serve_vllm._logprobs`' in-process `engine.generate` with jevfire's HTTP call to `/v1/completions`:
     `prompt=[token ids]`, `max_tokens=1`, `logprob_token_ids=[letters]`, `return_tokens_as_token_ids=true`.
   - Run the first row alone when the prefix covers at least one cache block (decider already does this).
   - Refit T with `python -m decider.calibrate` if you change the model or precision.
   - Optionally add reflex-style two-order averaging (about 1.1x the cost, better ECE).
3. The same FastAPI app serves `/v1/systemone` and reverse-proxies `/v1/chat/completions` and `/v1/models` to vLLM.
   - For a true single process, implement the same logic as a vLLM `--middleware` using `app.state.engine_client`.
4. Avoid SGLang-based sidecars (reflex, openjev) for mixed traffic until sglang #34075 is merged, because of #34719.
   Avoid simple-jev's and decider.serve's HF engines here: they own the weights, cannot serve chat efficiently,
   and are tight on 96 GB at 27-31B with graphs and cache forks.

Fastest zero-code proof of concept: `vllm serve` plus the jevfire sidecar gives chat and decisions from one model
today on this exact card (their benchmark hardware), but through `/v1/decisions` rather than `/v1/systemone`.
