# Inference-technique Jev reproductions: the "other" projects

Compiled 2026-09-26. Raw material is in `/home/welb/devspace/jev-onto/.firecrawl/infer2/`: READMEs, docs, source excerpts, GitHub API metadata and two scraped X posts.
Scope: projects that add **no new weights**. They take a stock LLM, prefill it with the shared state, read option-token logits and assemble the answer in code. Several also ship optional trained heads or LoRA; those are noted where they appear.
Not covered here (another agent has them): decider, simple-jev, reflex, jevfire, openjev-sglang.

---

## 1. Comparison table

| Project | Base model(s) | Backend | Owns model or sidecar? | `/v1/systemone`? | Readout | Max options | Stars / license / last push |
|---|---|---|---|---|---|---|---|
| [zhengxuyu/litjev](https://github.com/zhengxuyu/litjev) | Qwen3.x family; default **Qwen3.8-27B** on 1x H100 80GB; vision ckpts OK | HF transformers (PyTorch, CUDA 12.8), uv | Owns | **Yes**, exact schema (choice/score/noul) + `/v1/systemtwo` (exp.) | Shared prefill, then KV/recurrent state replicated. One batched branch per question ending in `Answer:`. Letter codes A–Z, AA–ZZ, AAA… each verified as one token. `lm_head` logit of the space-prefixed code at the last position, softmax over candidates. Optional temperature fit | 255 (choice), 2–10 (score), about 10 questions/request | 45 / Apache-2.0 / 2026-09-21 |
| [TheoLeeCJ/SemIf-OpenJev](https://github.com/TheoLeeCJ/SemIf) (formerly OpenJev; "SemIf" on leaderboard) | **Qwen3.5-4B** (pinned rev 851bf6e8); bridge to Qwen3.8-27B EXL3; browser: Qwen3-0.6B / MiniCPM5-2B / Qwen3.5-4B GGUF | PyTorch CUDA/MPS, MLX, llama.cpp (CPU), EXL3, **WebGPU via wllama** | Owns (CLI `semif-score`, no HTTP server) | No (own JSONL row format) | One forward pass. Softmax restricted to fixed uppercase letter tokens A–P. Modes: `direct`, `serial` (prefix reuse), `shared` (parallel suffix branches off one prefill, `reorder_cache`, right-padded) | **2–16** (browser 2–20) | **4,398** / MIT / 2026-09-23 |
| [Micha0827/snapjudge](https://github.com/Micha0827/snapjudge) | Qwen3.5 family MLX 4-bit: 4B, 9B, **Qwen3.6-35B-A3B** (recommended), Qwen3.8-27B | MLX (Apple Silicon only) | Owns | **Yes** + `debug`, `layout` extensions, bearer key | **Option keys (and a capitalized variant) tokenized into a prefix tree**. All branch points batched in one pass. Softmax over allowed tokens only, product along the path. **LM-head projection in fp32**. Question-first cached prompt head (LRU), flipped to state-first for long states | not stated (trie-based) | 14 / MIT / 2026-09-21 |
| [genai-craft/openvons](https://github.com/genai-craft/openvons) | Qwen3-4B-Instruct-2507 (zero-shot); Qwen3.8-27B; also frozen-backbone + trained heads | **Sidecar over vLLM OpenAI server** (`--logprobs-mode processed_logprobs`); separately own HF "Decision Model" | Both: `LLMBackend` is a pure sidecar | **Yes** (`openvons.lm.api.server`), plus `/v1/decision` | Sidecar: one chat request per question with `structured_outputs: {choice: labels}`, `max_tokens=1`, `temperature=0`, `logprobs`, `top_logprobs`. Filter to A..Z labels, renormalize. Own-model modes: naive / batched / kv_shared / **block_diag** (4-D block-diagonal mask, positions restart after state) | 26 via logprob (falls back to n-sample) | 14 / Apache-2.0 (+NOTICE) / 2026-09-21 |
| [sgoedecke/system-one](https://github.com/sgoedecke/system-one) | Qwen2.5-0.5B-Instruct (example); **Qwen3-8B** for Doom/Wikirace demos | HF transformers; Python library (typesafe-sdk types) | Owns (library, no server) | Uses `typesafe_sdk` types; **choice only** | Prefill `choice_index:` then read decimal-index tokens via `PrefixConstrainedLogitsProcessor`. With `cache_prefix=True` it **auto-detects the longest common token prefix across the question prompts**, prefills once, `batch_repeat_interleave`, left-pads the suffixes. Demo subclass uses 100 two-letter labels (`choice_label:`) | 255 requested, but capped by how many indexes are single tokens (≈10 on Qwen, which splits digits) | 34 / **no license** / 2026-09-18 |
| [snellingio/system-one](https://github.com/snellingio/system-one) ("System One Lite") | Qwen3-1.7B-4bit (default), Qwen3-4B-Instruct-2507-4bit | MLX; FastAPI; Python and TS SDKs | Owns | **Yes** (`/evaluate` alias) | Answer prefilled as `{"answer": "`. Masked read of answer-code tokens (A..Z, AA..) from a checked-in, tokenizer-hashed **code registry**. **Divides by the model-card temperature 0.7** before softmax. **No shared cache in serving**: each question is a full independent prompt, and cache reuse is gated by a parity experiment | **578** codes; 64 questions; score 2–10 | 45 / MIT / 2026-09-18 |
| [bnsd55/jevmlx](https://github.com/bnsd55/jevmlx) | Qwen2.5-7B-Instruct-4bit (default "quality"), 3B "fast"; any mlx-lm; also OpenAI-compatible backend | MLX; plus `--backend openai` (Ollama/vLLM logprobs, one request per field) | Owns (+ sidecar mode) | **Yes** + `/decide`, `/v1/models`, `/ready`; 429/413 backpressure | Two scorers: **`labels`** (default: prefix-free codebook search, trie over label remainders, P = Π branch softmaxes) and `slots` (single-token letter codes). Prefill once, KV broadcast, chunked batch with memory budget, **near-tie rescore at batch=1**, `prior_correction` (neutral-context prior), `legal_mass` leakage signal, nonce-fenced context, NONE_OF_ABOVE, constrained MAP across fields | 255 (preset) | 68 / MIT / 2026-09-25 |
| [MantisShrimpdev/jobe](https://github.com/MantisShrimpdev/jobe) | **Qwen3.5-4B** (pinned 851bf6e8), llama-3.2-3b also measured | HF transformers CUDA (Qwen3.5 build is CUDA-only because of the fla Triton kernel); stdlib HTTP server | Owns (in-process library + server) | **Yes** (wire-compatible with jev-browser, jev-ultrafast) | Single-token letters A–P. **Slot IDs resolved in context** (`encode(prompt+letter)[-1]`, needed for SentencePiece). Restricted softmax. `PrefixScorer` primes the evidence once. Batched suffixes are **right-padded**, expanded via `reorder_cache`. `orders.py` does permutation averaging (measured: no gain). `wide.py` narrows options through a tree | **16** (422 above; `--wide` tree) | 0 / MIT / 2026-09-24 |
| [r-ms/mini-jev](https://github.com/r-ms/mini-jev) | Qwen3-4B-Instruct-2507 (bf16, eager) | HF transformers 4.57.6 + xgrammar 0.2.7; teaching demo server | Owns (study + demo) | No (flat JSON schema in, demo) | **Preregistered** letter-read vs grammar-JSON. Candidate letter scores recomputed **in fp32** from the last hidden state. `B1cache` = shared prefix of system+text, per-field tails | 2–26 measured (k=2..16) | 57 / MIT / 2026-09-18 |
| [harshatheg/Qwen-2.5-1B-RLCD](https://huggingface.co/harshatheg/Qwen-2.5-1B-RLCD) + [Space](https://huggingface.co/spaces/drinkmoonshine/parallel-constrained-decoding) (viral original "PCD") | Qwen2.5-1.5B-Instruct (4-bit MLX); torch fallback on Space. **Repo contains code, not weights** | MLX (+ torch for Space), FastAPI, Gradio | Owns | No (`/api/run-parallel`) | "Catalog" prefill: system lists all fields, then context, then assistant `{\n`. **Suffix per field = `  "field": "<common-prefix>`**, read the **first token** of each choice remainder. Softmax/T. **Collisions fall back to up to 4 greedy tokens + string match + fallback `choices[0]` + synthesized confidence clamp(0.75, 0.9999)** | 255 claimed (broken by collisions) | 572 HF likes (Space 33) / Apache-2.0 / 2026-09-16 |
| [rorshopping/jev-on-a-laptop](https://github.com/rorshopping/jev-on-a-laptop) (+ lib [parallel-decisions](https://github.com/rorshopping/parallel-decisions)) | Qwen2.5-1.5B / **7B** / Qwen3-8B 4-bit MLX; 0.5B on CUDA | MLX (RLCD engine, cloned); Torch backend in parallel-decisions (prefix reuse, **CUDA Graphs**) | Owns | No | RLCD engine as-is; the study documents its flaws | 255 (RLCD) | 25 / MIT per README (GitHub: unrecognized; snapjudge says no license file) / 2026-09-17 |
| [daseinlabs/open-jev](https://github.com/daseinlabs/open-jev) | **Gemma 3 4B-it** | MLX (Apple) or PyTorch CPU/CUDA/MPS; FastAPI | Owns | **Yes** + `/score`, `/health` | **Multi-token option scoring**: log-prob of the full option continuation (names, level numbers, yes/no) after `Answer:\n`. Prefix shared **within a question** across its options. Normalization `sum` / `mean` / **`pmi`** (subtract the BOS-only unconditional log-prob). Optional trained cross-attention head on frozen features | 255 | 116 / MIT / 2026-09-24 |

Launch commands (verbatim from the READMEs):
- litjev: `uv run --locked litjev --model Qwen/Qwen3.8-27B [--device-map cuda:0] [--calibration calibration.json]` → `http://127.0.0.1:8000/v1/systemone`
- SemIf: `semif-score --mode direct|shared --model Qwen/Qwen3.5-4B --revision 851bf6e8... --input examples/decisions.jsonl --output results.jsonl` (`--backend mlx|llamacpp --gguf ...`)
- snapjudge: `snapjudge-serve --model mlx-community/Qwen3.6-35B-A3B-4bit` → `:8724/v1/systemone`
- openvons: `vllm serve Qwen/Qwen3-4B-Instruct-2507 --served-model-name qwen3-4b --port 8300 --logprobs-mode processed_logprobs`, then `DM_LLM_URL=http://127.0.0.1:8300/v1 python -m openvons.lm.api.server`
- sgoedecke: `SystemOne.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct").system_one(state=..., questions=..., cache_prefix=True)`
- snellingio: `cd server && uv sync && uv run uvicorn system_one_lite.api:app --port 8010` (`SYSTEM_ONE_MODEL=larger`)
- jevmlx: `jevmlx serve --model fast --port 8000`; sidecar: `jevmlx decide --backend openai --base-url http://localhost:11434/v1 --api-model llama3.2 ...`
- jobe: `python -m jobe.server --model <path> --port 8901 [--wide] [--ledger runs/ledger.jsonl]`
- mini-jev: `MINIJEV_DEVICE=cuda uv run python demo/server.py` → `:8765`
- RLCD: `bash run.sh` or `python3 -m uvicorn server.app:app --port 8000`
- jev-on-a-laptop: `./setup.sh && ./run_benchmark.sh`
- open-jev: `uv run openjev serve --backend torch --device cuda --batch-size 2`

---

## 2. Per-project notes and measured results

### litjev (zhengxuyu), the most faithful Jev contract on CUDA
- The pipeline has two forwards. Pass 1 prefills the state plus generic instructions. Pass 2 **replicates the KV and recurrent states** and batches each question's instructions, criteria and `Answer:`. Readout is `logits[i, len(suffix_i)-1, candidate_ids_i]` (`docs/how-it-works.md`).
- Original option keys map to internal letter codes (A–Z, then AA…ZZ, AAA…ZZZ), each verified as a single token at the boundary. Unsupported tokenizers are rejected, never truncated.
- Branches are isolated from one another. Question IDs are never sent to the model, so renaming one does not change its input.
- Confidence is the **normalized Gini** `(K·Σp² − 1)/(K − 1)`. It is explicitly *not* max-prob and not accuracy.
- Probabilities are uncalibrated by default. `litjev-mmlu --export-logits` feeds `litjev-calibrate` to fit a temperature, and the server loads it with `--calibration`.
- 27B BF16 is about 54 GB of weights alone. The tested hardware is 1x H100 80 GB.
- Also offers an experimental `/v1/systemtwo`: a small trained head routes individual questions to the backbone's own slow thinking.
- The blog thread ([x.com/yuzxfred](https://x.com/yuzxfred/status/2100896621173047367), Chinese) argues Jev's interface is mostly an inference contract. It lists limits: no "none of the above", no intermediate reasoning, questions can't see each other, long states cost prefill, and results depend on the template and option order. It notes Jev may use a packed tree (one forward), where litjev uses two forwards because of the hybrid Qwen architecture.

### SemIf / OpenJev (TheoLeeCJ), the best-evidenced baseline (4.4k stars)
- **Prompt:** system says "Apply the supplied criterion to the supplied evidence. Choose exactly one listed option. Respond with only its uppercase letter". The user turn is JSON `{"evidence", "criterion", "options":[{"letter","description"}]}`, with `enable_thinking=False`.
- **Guards:** each letter must be one round-trip token, and `encode(prompt+letter) == ids+[token]` (the boundary must not re-tokenize).
- **Shared mode:** the state prefix is cut at the evidence boundary, and **the last prefix token is dropped** because JSON punctuation can merge with it. `cache.reorder_cache(zeros(N))` expands the cache and suffixes are right-padded with explicit `position_ids`. `logits_to_keep` limits computation to the selected end positions. On MPS the branches run as a loop of deep-copied batch-1 caches instead.
- **Speed (RTX 3090, Qwen3.5-4B):** 21 binary criteria take **1.023 s** with direct logits versus 5.332 s for a compact generated JSON array (18/21 argmax agreement). On the 37×21 = 777-decision fixture (about 8k-char states): fresh 2.33 dec/s, serial prefix reuse 10.75, **parallel suffixes 20.03 dec/s**. BF16 fast paths changed 5–6 of 777 argmaxes.
- **Quality (Qwen3.5-4B BF16):**
  - Authored-144 balanced accuracy 0.813. The Qwen3.8-27B EXL3 bridge reaches 0.958.
  - WANLI 0.637.
  - **TypeSafe 102-row subset modal agreement 0.845 vs published Jev 0.883.** Total-variation distance 0.177 vs Jev 0.127.
  - Qwen3-Reranker-4B (yes/no per option) was worse for decisions (0.625) but equal on retrieval.
- **Perturbations (36 cases):** option reversal gave 10 flips, a criterion wrapper 9, irrelevant context 4. "Positional wording and probability movements are not solved." One confident (>0.8) non-`insufficient` answer appeared on the missing-evidence set.
- **Calibration (`docs/CALIBRATION.md`):** one scalar T per workload, fit by NLL, with out-of-fold ECE. Authored: T 1.23, ECE 0.068→0.038. **WANLI: T 2.50, ECE 0.208→0.069** (significant). Every: T 1.71, 0.050→0.047. **There is no single pooled temperature**, because T differs by workload. Per-class calibrators don't apply to runtime-defined options.
- **WebGPU:** wllama 3.6.1 reads log-probabilities of single-token labels, 2–20 options. Direct readout took 0.70 s (0.6B) and 3.27 s (4B Q4) in Chrome on a 3090.

### snapjudge (Micha0827), with the best Jev-agreement study on MLX
- **Question-first layout:** the system prompt plus question and options are prefilled once and kept as an LRU cache snapshot, so each request pays only for its state. This was **more accurate** on its game set (89% → 97–100%) and faster (397 ms → 78 ms median).
- For a long state (>2,000 chars) with several questions it flips to state-first so the state is shared.
- The `header` layout lists all questions, then the state, then each question. On 5 invoices it scored 45/75 (state-first 41, question-first 50) at state-first cost.
- Labels form a prefix tree: option keys plus capitalized variants are tokenized, and the tree branches where keys share leading tokens. Usually that is one forward. The option probability is the product along the tree path of softmaxes over allowed tokens.
- **The fp32 final projection** is needed because "bf16 logits around 20 are quantized in steps of 0.125".
- Qwen3.5 hybrid (linear/recurrent) layers can't be trimmed, so it snapshots and restores caches.
- **`coverage` debug field:** the probability mass on allowed labels. It is a leakage signal.
- Confidence is 1 − normalized entropy.
- **Against Jev on TypeSafe's 20 public cases (373 decisions):**
  - Jev 87.7% (308/351 answered).
  - **Qwen3.8-27B 4-bit 81.2%**, Qwen3.6-35B-A3B 77.5%.
  - Short texts are level with Jev (customer service 82/92 vs 81/92).
  - The gap is almost entirely **long-document cross-referencing**: invoice line-item checks on about 8k tokens scored 65/75 for Jev vs 38/75 for 35B-A3B. Question-first raised that to 50/75 but was 6–8× slower, up to 13 minutes on an M2 Max for 48 questions.
- **Authored-144 (SemIf set):** 4B 0.786, 9B 0.888, 35B-A3B 0.908, 27B 0.921. The German business set gets 93–96% with ECE 0.016–0.048.
- **Lessons:** use labels that do not appear in the question (label/question lexical overlap biases the answer). Keep numeric logic, such as the sign of an amount, in code.
- **LoRA (optional):** the adapter is a specialist and hurt the 4B off-domain (93.9 → 86.8). Fuse it in bf16, never re-quantize (0.775 → 0.606). Trained models were underconfident, and per-question-type temperature fixed that (ECE 0.158 → 0.032).

### openvons (genai-craft), the sidecar-over-vLLM pattern, measured on an RTX PRO 6000 Blackwell 96 GB
- `LLMBackend` sends one `/v1/chat/completions` per question with `structured_outputs: {"choice": labels}`, `max_tokens: 1`, `temperature: 0`, `logprobs: true`, `top_logprobs: min(max(n,5),100)` and `chat_template_kwargs: {enable_thinking: false}`. It then renormalizes the logprobs of labels A..Z. For more than 26 options it falls back to `sample` (n=20 samples at T=1 → empirical distribution). A `json` mode (one JSON-schema request for all questions) is the baseline.
- vLLM's server is launched with `--logprobs-mode processed_logprobs`, so the returned logprobs are post-processing. This is what makes the guided/masked distribution come back directly. (Assumption to verify on the vLLM version in use.)
- **Measured on the user's exact GPU class (`docs/lm_benchmark.md`, massive_scenario_en, 18-way):**
  - Qwen3-4B-Instruct vLLM guided choice + logprob, zero-shot: acc 0.823, **ECE 0.170 → 0.040 after temperature**, **p50 14.5 ms/question**.
  - Qwen3.8-27B vLLM, same readout: 0.875, ECE 0.068 → 0.017, 73.6 ms.
  - **Question-count scaling (short state, about 90 tokens), p50 ms at q = 1 / 2 / 4 / 8 / 16:**
    - vLLM 4B, parallel per-question guided-choice requests: **10.6 / 18.8 / 20.6 / 27.6 / 40.2**. Prefix caching shares the state.
    - vLLM 4B, one JSON-schema request: 64.6 / 114 / 254 / 508 / 895.
    - vLLM 27B, JSON schema: 359 / … / 6199.
    - Own HF decision model, 4B **block_diag**: 15.2 / 16.2 / 17.3 / **22.6** / 32.2. kv_shared: 29.3 / … / 48.4. naive: 14.9 / … / 239.
    - Long state (about 700 tokens): 4B block_diag 37.5 → 58.5 ms (q=1→16), versus JSON 65 → 882 ms.
  - "Removing the LM head doesn't speed anything up": vLLM with `max_tokens=1` is already 1 forward + LM head.
  - All four own-model multi-question modes agree within 1e-4 in fp32.
- **Trained-head variant (not "no weights"):**
  - A frozen Qwen3-4B with an embedding/bilinear head (option-line hidden state × decision-token query, mean pooling) scored 0.916. LoRA + head scored 0.933, beating 27B zero-shot at 0.875.
  - The head is **far better calibrated** (ECE 0.02 raw).
  - Falling back to the 27B LLM when unsure *lowers* accuracy.
  - Conf≥0.9 covers 79.8% at 98.2% accuracy, versus 27B at 95.4%.
- Explicit **"none of the above"** calibration and an execute / confirm / reject policy.
- Confidence in `/v1/systemone` is the **margin** (top1 − top2).
- The Japanese doc on the TypeSafe MCA flags that TypeSafe's terms prohibit publishing benchmarks and distilling from Jev outputs. It recommends against using Jev outputs as training or calibration data and against using the "Jev" name.
  - *Checked 2026-09-26 against https://typesafe.ai/legal/mca:* the distillation ban is confirmed (clause (b): no using Output "to perform model distillation, train a model to imitate the output of the Services, or develop ... a similar or competing product"). No benchmark-publishing ban was found in the MCA or the Acceptable Use Policy.

### sgoedecke/system-one, a minimal HF library
- Prompt: a JSON blob `{state, instructions, options:[{index,name,criteria}]}`, then assistant `choice_index:`. Candidate tokens are the decimal indexes that decode as single tokens after the prefix. `PrefixConstrainedLogitsProcessor` masks, then softmax.
- **Automatic common-prefix detection:** it takes the longest shared *token* prefix across all question prompts, which includes the state because the state comes first in the JSON. It prefills that once, calls `batch_repeat_interleave(N)` and left-pads the suffixes with computed `position_ids`. This is recommended for 3 or more questions.
- Choice only. Confidence is 1 − normalized entropy. Output tokens are reported as the number of questions.
- **Demos (Qwen3-8B):**
  - Doom: 172 ms median between actions, versus 600 ms for a tool-call agent (3.5×), and it issues multiple simultaneous inputs.
  - Wikirace: over 1k links, where **two-letter labels worked better than numeric indexes**.

### snellingio/system-one ("System One Lite"), a conservative MLX server
- The prompt has a `State:` header (+2/20 on eval), `Question k:` blocks and options `A: key — description`. The assistant answer is prefilled as `{"answer": "` and the code token is read at that slot.
- **Registry of 578 answer codes** per model, pinned to model revision and tokenizer hash, and checked at startup. A 422 is returned if a code does not land as one token.
- **Temperature 0.7 is applied (the model card's sampling T) before softmax.**
- **Deliberately no KV sharing in serving:** each question gets a full independent prompt with a copy of the state. A separate cache experiment must prove matching probabilities first.
- Confidence is `(max_p − 1/n)/(1 − 1/n)`.
- The eval tool includes a **rotation stability check** (rotate the options, compare winner and distribution distance).
- One request at a time (503 if busy); 64 questions max.

### jevmlx (bnsd55), the most engineered MLX engine (descended from the RLCD presets)
- Fields are compiled per tokenizer. A **bounded codebook search** picks prefix-free alias codes (a prefix-conflict graph plus backtracking). `labels` scoring uses a **trie over label remainders**, with P(choice) = Π of branch-point softmaxes.
- **`legal_mass`** is the full-vocabulary probability of the allowed continuations at the branch point, used as a leakage/abstention feature.
- **`prior_correction`** subtracts a neutral-context prior. That is contextual calibration, and the prior is LRU-cached.
- **Near-tie rescore:** candidates inside 0.05 nats are re-scored at the canonical batch=1 shape, because batching changes close BF16 decisions.
- Context is fenced with a sha256-derived nonce (a prompt-injection guard).
- NONE_OF_ABOVE; `abstain_below_margin`.
- **Constrained MAP** across fields (implies / excludes / requires_parent), and a selective second pass that conditions dependent fields on parents with `Given: {...}`.
- Chunks are sized by a measured memory budget, with halve-and-retry on allocation failure.
- The OpenAI-compatible backend sends one request per field. Options missing from top-k get a floor probability and `truncated: true`.
- **Leaderboard (45 TypeSafe public example cases, m5max):**

  | Model | naive generate | `labels` | `slots` (letters) |
  |---|---:|---:|---:|
  | Qwen2.5-7B | 67.7% | **82.1%** | 63.2% |
  | Qwen3-8B | 69.3% | **84.6%** | **34.7%** |

  On this benchmark, single-token letter slots were much worse than scoring the actual labels.

### jobe (MantisShrimpdev), the most honest "what didn't work" log (JevBench 9th of 71, top native-logit system)
- **JevBench public (231 items), frozen Qwen3.5-4B on an RTX 3080:** easy 1.000, standard 0.986, **hard 0.604** (Jev 0.741), all 0.805 with ECE 0.049. On 308 sealed decisions it scored below the chance line, like every frozen Qwen3.5-4B readout.
- **Latency:** llama-3.2-3b bf16 at 36.9 ms p50 end to end, with 1.0 ms pipeline overhead. **Eager attention beat SDPA for short un-batched prompts** (39.1 vs 50.4 ms). Timing on a GPU shared with Ollama was 12× worse.
- **Prefix cache on a 2k-token doc:** 1,302 → 117 ms per question after a 1.77 s prime (11×). Batch 2 → 59 ms/question (15×). Batch 8 was slower than serial on a 10 GB card.
- **Right-padding, not left:** left-padded rows drift 5–7 ulps because pads between prefix and suffix perturb hybrid recurrent/conv layers, even when masked.
- `reorder_cache` is used because `batch_repeat_interleave` is not implemented for Qwen3.5 linear-attention cache layers.
- **SentencePiece fix:** resolve slot IDs in context (`encode(prompt+letter)[-1]`), since `encode("A")` gives `▁A`, which is the wrong token.
- **Order averaging did not pay:** hard tier 0.613 → 0.613 for 2× passes, 3 answers fixed and 3 broken. Order instability (E2 flip rate 2.1% easy / 8.3% standard / 23.4% hard) is **symmetric noise, not correctable bias**.
- **A thinking pass on low confidence** pays only below about 0.45 confidence (4 fixed, 0 broken). At 0.57 it breaks things. In 71% of shared misses both modes give the *same* wrong answer, which points to a knowledge gap.
- **Tree narrowing beyond 16 options** costs about 2.8 points at 4–6 options (not significant). Balanced folding matters, and the shallowest tree is best.
- **Confidence as a gate:** a 0.80 threshold escalated 23% and caught 3/3 errors on an agent set. Hard-tier AUROC 0.79. It **cannot detect "none fit"** (p=0.998 for a nonsense-category request).
- **Control battery:** E1 shuffled context must destroy skill, E2 option order, plus a positional-bias check, all per tier. TinyLlama gives "confident reflex" output at the base rate.
- Server behavior: 422 for declared limits (not 500, since harnesses abort after three 500s), a warm-up decision before opening the port, a JSONL ledger of every decision including refusals, and `/health` reports which kernel bound.

### mini-jev (r-ms): preregistered study findings (Qwen3-4B-Instruct-2507, CLINC150)
1. **Reading letters matches grammar-constrained JSON on accuracy.** Intent: JSON 0.909 vs letters 0.907, Δ −0.22 pp with 95% CI [−1.44, +1.04] over 6,750 paired observations. Every k from 2 to 16 has a CI covering 0.
2. **The mechanism is real.** The argmax next token is a letter in 13,600/13,600 questions. Letters carry essentially all the mass (min 0.99999624). The **position prior is flat** (k=4: .275/.245/.240/.240). The unconstrained model writes the read letter in 199/200 controls.
3. **Speed:** 4× faster than JSON on short texts. On 2048-token texts it is 1.4× / 1.8× / 2.4× faster for 1 / 2 / 3 fields *with* a shared prefix. Without the prefix (re-reading the text per field) it loses (1.10–1.16× slower).
4. **The letter beats writing the option name:** +10.0 pp on intent [+8.4, +11.8], +13.2 pp on domain, and nil on boolean where the names are already single tokens.
   - **Sequence likelihood of whole names is worst:** 0.484 overall, 0.443 on intent. Two legitimate length normalizations disagree by 12 points, which shows strong length and tokenization sensitivity.
5. **Reading loses in two places.** Out of scope: "none" was picked 41/50 by letters vs 47/50 by JSON. Dependent fields: a boolean that follows from an earlier field gains 5 pp when written after it inside one JSON.
6. **Asking the model to write probabilities is terrible:** 0.346 vs 0.896, and 62% pick the first option.
7. **The shared KV cache doesn't change answers:** 0.8484 vs 0.8483, and 59/13,500 flips, all near ties. The same code on two RTX 4090s is bit-identical.
8. **Scores are recomputed in fp32** from the last hidden state, because the bf16 grid step at logit magnitude 16–32 is 0.125, "which would turn near ties into a position bias".
9. **Recommendations:**
   - Enums of 2–26 options: use letters.
   - More than 26: use two-level codes or hierarchical questions.
   - Copy-spans (phones, dates): turn them into choices by enumerating candidates found in the text.
   - Numbers: generate under a bounded grammar.
   - Many fields on one long text: letters on a shared prefix, with the question *after* the text.
   - Run records are on the Hub at `Mikhail/mini-jev-runs` (27,900 decisions with full candidate logits).
10. **Bug worth knowing:** in transformers 4.57, an explicit `position_ids` passed to `generate` gets sliced to its last column, so every decode step sits at the last prompt position. The first token is unaffected, so readouts are safe but generation is broken.

### harshatheg/Qwen-2.5-1B-RLCD (the viral "PCD"), and how it actually behaves
- **Name:** "RLCD" (Reinforcement Learning for Calibrated Decisions) is Jev's claimed training method. This HF repo has **no RL and no new weights**: it is an MLX/torch engine on stock Qwen2.5-1.5B-Instruct.
- **Pipeline:** a system "catalog" of all fields, then the context, then an assistant `{\n` prefill, with the KV cache broadcast to M rows. Each row's suffix is `  "field": "<commonprefix>`, and it reads the logits of the **first token of each choice's remainder**. Booleans use the first token of `true`/`false`.
- **Claims:** 5.6–7.0× vs its own greedy AR baseline on an M4 Max, e.g. 28 fields 1.9 s → 270 ms, and "calibrated" confidence (it is just softmax/T).
- **The collision path is the flaw.** When choices share a first token (e.g. the 255 tariff codes `0101.21`/`0101.29`, or `P1_HIGH`/`P1_CRITICAL`), it:
  1. greedily decodes up to 4 unconstrained tokens,
  2. fuzzy-matches the result to a choice,
  3. falls back to `choices[0]` if nothing matches,
  4. **fabricates confidence** as clamp(Π p, 0.75, 0.9999) with a uniform remainder.

  So the "255-choice" demo measures speed, not correct scoring.
- The cache slice for continuation also carries that row's pad positions.

### jev-on-a-laptop (rorshopping), honest benchmark using the RLCD engine
- **28-field fraud preset, M5 Air:** 1.5B 0.41 s vs 3.3 s naive; 7B 1.52 s; 8B 2.03 s (7–7.9×). None of the models could reliably emit valid 28-field JSON unconstrained; all were always valid through the constrained path. Support triage was only 4.4× because of the collision cost.
- **Labeled 72 decisions:** 1.5B 58% (= majority baseline), **7B 96%** primary, 8B 85% all-fields-exact. **Confidence doesn't flag errors: the 7B was >0.90 confident on 13 of its 20 wrong fields.**
- **Full public TypeSafe set (strict 343 common pairs):** Opus 89.8%, DeepSeek v4.1 Flash 89.5%, Sol 89.2%, **Jev 86.6%**, **local Qwen2.5-7B 73.8%**, Qwen3-8B 71.2% (3 workflows). An earlier 5-case "tie" was a small-sample artifact.
- **GPU (parallel-decisions Torch backend):**
  - Shared schema prefix: 88.5 → 61.9 ms.
  - **CUDA Graph replay of suffix shapes (StaticCache):** 60.1 → 51.8 ms (8 fields) and **240.9 → 83.8 ms (27 fields)**. Suffix p50 199.8 → 42.1 ms.
  - Running multiple processes on one GPU thrashes: the engine's own batching should be the concurrency.
- Its 7-item failure list for RLCD covers fake calibration, collisions, enums/booleans only, the hardcoded ChatML template and a weak greedy baseline.

### daseinlabs/open-jev: the multi-token scoring variant (Gemma 3 4B)
- Each question renders to plain text: state, instructions, options or levels, then `Answer:\n`. The **option names, level numbers or yes/no are scored as full continuations** in one prefix-shared batched pass per question.
- Normalization: `mean` (default, per-token average), `sum` (raw), or `pmi` (subtract the option's BOS-only unconditional log-prob, costing one extra pass).
- Confidence is 1 − normalized entropy. `usage.output_tokens` counts the scored label tokens.
- **Zero-shot result:** on the TypeSafe docs quickstart, Gemma is **over-confident** (p = 1.00) and disagrees with Jev on two judgment calls (noul 0.005 vs Jev 0.999).
- A trained cross-attention head on frozen Gemma features reached test top-1 0.970 with ECE 0.027. The shuffled-context control collapses to 0.258, which is the right sanity check.
- **Latency:** M5 Pro, 202-token context, 8 options with 242 option tokens: 0.17 s cached vs 0.68 s uncached.
- Tests compare cached padded scoring with full re-encoding, including Gemma's sliding-window attention.

### Critique: "OpenJev is NOT Jev open-sourced" ([x.com/mygtmhire](https://x.com/mygtmhire/status/2100666488625734103))
It restates SemIf's own caveats. OpenJev contains no TypeSafe model, architecture or RLCD training; it recreates the *interface pattern* on Qwen3.5-4B. The headline numbers are 1.023 s vs 5.332 s for 21 decisions and 20.03 dec/s shared. The key warning is that its probabilities should **not** be treated as calibrated like Jev's RLCD-trained output; calibrate on your own workload. The post has 3 likes and is more framing than technical critique.

---

## 3. The technique, step by step

**Core idea.** A causal LM's last-position logits already form a classifier over the vocabulary. If the prompt ends exactly where the answer token would go, the logits of the tokens that encode each allowed option are the model's judgment. Slice those k numbers, softmax them, and you have a distribution, with no decoding. The type system (choice / score / noul → JSON) lives in code, so malformed output is impossible by construction.

### Steps (single GPU, many questions about one state)
1. **Compile the question into a closed-form prompt.**
   - Put the state, the question's instructions and the options into the prompt, with each option given an **answer code**. That is usually a single-token letter (A, B, …, then AA…), sometimes the option key itself, sometimes a digit index.
   - End the prompt exactly at the answer slot: `Answer:`, `choice_index:`, `{"answer": "`, `"field": "`, or just after the assistant header with a "reply with only the letter" system instruction. Disable thinking (`enable_thinking=False`).
   - Verify tokenization: each code is one token *in context*, i.e. `encode(prompt + code) == encode(prompt) + [code_id]`. Codes must be unique, and none may be a prefix of another.
2. **Prefill the shared part once.** Layout matters:
   - **State first:** the state is the shared prefix, and questions are suffixes. This is the default for most projects.
   - **Question first:** the question plus options is cached across requests and the state is the suffix. snapjudge found this more accurate and cacheable for single questions.
   - **Header:** list all questions, then the state, then each question.
   - Cut the prefix on a token boundary and **drop the final prefix token** in case of BPE merges across the boundary (SemIf, jobe).
3. **Fork per question.** Pick one of these:
   - **KV broadcast / batch expansion** (RLCD, litjev, SemIf shared, jevmlx, jobe, sgoedecke): `cache.reorder_cache(zeros(N))` or `batch_repeat_interleave(N)`. Then one batched forward over the N suffixes, **right-padded** with explicit `position_ids = prefix_len + t` and `attention_mask = [1]*prefix + suffix_mask`.
   - **Tree / block-diagonal attention** (openvons `block_diag`): pack `[state | Q1 | Q2 | …]` into one sequence with a 4-D mask so each Qi sees only the state and itself, with positions restarting after the state. This is one forward, no cache copy, and the fastest measured (22.6 ms for 8 questions, 4B).
   - **Server prefix cache** (openvons sidecar, jevmlx openai backend): send N independent requests that share a byte-identical prefix. vLLM's automatic prefix caching reuses the state KV (40 ms for 16 questions, 4B, RTX PRO 6000).
   - **None** (snellingio): repeat the state per question. It is the safest for parity but costs O(N·state).
   - **Hybrid / recurrent models** (Qwen3.5 / 3.6 / 3.8 linear-attention layers): the state can't be trimmed, so snapshot and restore or deep-copy it. Use right-padding plus real lengths, because left-pads corrupt the recurrent state. Use `reorder_cache`, since `batch_repeat_interleave` is missing for those layers.
4. **Read the logits at each row's last real token.** Use `logits_to_keep` or gather before the LM head so the head runs on one vector per row. Project the candidate rows **in fp32**, since bf16 logits near 20 step by 0.125.
5. **Normalize over the allowed candidates only** ("restricted softmax"): `p_i = softmax(z_i / T)` over the k codes. For multi-token labels either:
   - use a **trie**: P(option) = Π of softmaxes over allowed next tokens at each branch point. That is one extra batched pass per trie depth, or none if all first tokens differ; or
   - use **full continuation log-likelihood** (open-jev) with sum, mean or PMI normalization.
6. **Map back to the typed answer.**
   - **choice:** argmax key plus `probabilities`.
   - **score:** levels are coded 0..n−1, and the answer is the probability-weighted mean index (the Jev semantics) plus `legend` and `probabilities`.
   - **noul:** P(yes) from a yes/no or A/B code pair.
   - **confidence:** Jev's formula is unpublished. Projects use normalized Gini (litjev), 1 − normalized entropy (snapjudge, sgoedecke, open-jev), chance-corrected max `(max−1/n)/(1−1/n)` (snellingio, jobe), or margin (openvons, jevmlx).
   - `usage.output_tokens = 0`.
7. **Optionally calibrate:** fit one scalar T per workload (or per question type) on labeled data by NLL. The argmax never moves; only confidence does.

### Main variants
| Axis | Options seen |
|---|---|
| Answer code | single-token letters (SemIf, litjev, jobe, snellingio, mini-jev, openvons); digit indexes (sgoedecke); two-letter labels (sgoedecke Wikirace, snellingio codes AA..); **the option keys themselves via trie** (snapjudge, jevmlx `labels`); first token of the JSON value (RLCD); full multi-token continuation (open-jev) |
| Answer slot | after the assistant header with "letter only" (SemIf, jobe); `Answer:` (litjev, open-jev); `choice_index:` (sgoedecke); `{"answer": "` (snellingio); JSON-value prefill `"field": "` (RLCD, jevmlx) |
| Fork | KV broadcast; block-diagonal / tree mask; server prefix cache; none |
| Normalize | restricted softmax at T=1; fixed T (0.7 snellingio); fitted T; PMI / neutral-prior subtraction (open-jev, jevmlx); trie product |
| Deployment | owns the model (most); **sidecar over an OpenAI-compatible server** (openvons, jevmlx `--backend openai`); in-browser (SemIf wllama) |
| Extras | trained head on frozen features (openvons, open-jev); LoRA (snapjudge, openvons); thinking fallback on low confidence (jobe, litjev `/systemtwo`); constrained MAP across fields (jevmlx) |

---

## 4. Failure modes and the fixes people used

| Failure | Evidence | Fixes tried and outcome |
|---|---|---|
| **Multi-token labels / first-token collisions** | RLCD collisions trigger a greedy decode + string match + `choices[0]` fallback + fake confidence clamp(0.75, 0.9999). The triage preset drops to 4.4× from 7.9× (jev-on-a-laptop) | Single-token letter codes verified at load; a **prefix-free codebook search** (jevmlx); a **trie with batched branch points** (snapjudge, jevmlx); full-sequence log-prob with normalization (open-jev). mini-jev: sequence likelihood of names gave 0.48 vs 0.91 for letters, and length normalizations disagree by 12 pts, so avoid it for semantic names |
| **Letters vs names, contradictory evidence** | mini-jev: letters beat names by +10 pp (Qwen3-4B-Instruct, CLINC150). jevmlx: `labels` beat `slots` (Qwen3-8B 84.6% vs 34.7%) on TypeSafe cases | Likely depends on model, template and how names are scored (trie branch softmax vs sequence likelihood vs written under a grammar). **Evaluate both on your own data and model.** Qwen3-8B's base (thinking) chat model may behave differently from Instruct-2507 |
| **Tokenizer boundary bugs** | SentencePiece `encode("A")` gives `▁A` ≠ the in-context `A` (jobe). JSON punctuation merges with the end of the evidence (SemIf, jobe). Qwen splits digits, so indexes ≥10 aren't single tokens (sgoedecke) | Resolve slot IDs in context, drop the last prefix token and assert the prefix is a token prefix of the full prompt, refuse with a 422 rather than truncate, pin tokenizer hashes (snellingio registry) |
| **Position / letter bias, order sensitivity** | SemIf: 10 flips out of 36 on option reversal. jobe E2 flip rate 2 / 8 / 23% easy / standard / hard. mini-jev: position prior flat on real texts | **Permutation averaging did NOT help** on jobe's hard tier (0.613 → 0.613, 3 fixed / 3 broken: symmetric noise). Measure rotation stability (snellingio) as a diagnostic. Use fp32 LM-head rows so bf16 ties don't become position bias (mini-jev, snapjudge) |
| **Miscalibration / overconfidence** | jev-on-a-laptop: 7B >0.90 on 13/20 errors. openvons: zero-shot 4B ECE 0.170. SemIf WANLI ECE 0.208 (T=2.5). open-jev Gemma p = 1.00 | **Per-workload temperature scaling** (SemIf 0.208 → 0.069; openvons 0.170 → 0.040). Per question type (snapjudge LoRA 0.158 → 0.032). No single pooled T works. Trained heads on frozen features are best calibrated (openvons ECE 0.02). Confidence is still useful as a *gate* (jobe AUROC 0.79; openvons conf≥0.9 → 98% acc at 80% coverage) |
| **No "none of the above"** | jobe: p = 0.998 for a request that fit no category. mini-jev: "none" picked 41/50 vs JSON 47/50 | Add an explicit NONE/other option (jevmlx `allow_none_of_above`, openvons none-calibration). Use a `legal_mass` / `coverage` leakage signal (jevmlx, snapjudge). Validate the evidence before the call |
| **Dependent questions** | mini-jev: a dependent boolean loses 5 pp when read alone | A second pass conditioned on parents (`Given:` header, jevmlx), constrained MAP across fields, or chaining in code |
| **Max-options limits** | Letters cap at 16 (SemIf, jobe) or 26 (openvons, mini-jev). vLLM top-k logprobs can drop the gold option (~0.9% per jobe) | Two-letter codes (snellingio 578; sgoedecke 100). Hierarchical narrowing (jobe `--wide`, about −2.8 pts at 4–6 options). Retrieve-then-decide. Two-level codes `A1…` (mini-jev). Sampling fallback (openvons) |
| **Long contexts** | snapjudge: the gap to Jev is almost all long-document cross-referencing (8k-token invoices 38/75 vs Jev 65/75); question-first helps (50/75) but is 6–8× slower. A 2048-token re-read per field loses to JSON unless the prefix is shared (mini-jev) | Share the state prefix. `header` layout (questions listed before the state). Larger or MoE models (27B → 81.2% overall). A thinking fallback only at very low confidence (jobe <0.45) |
| **Batch-shape numerical drift** | SemIf: 5–6/777 argmax changes. mini-jev: 59/13,500 flips on near ties. jobe: left-pad drift 5–7 ulps on hybrid models | Right-pad; rescore near-ties at batch=1 (jevmlx); keep candidate projections in fp32; treat serving configuration as part of the evaluated system |
| **Thinking models** | The first token is `<think>`/`Okay`, never the answer (jobe via EveryAppKit) | `enable_thinking=False` in the chat template, or prefill the answer slot |
| **Prompt injection from state** | snapjudge: a trap sentence ("JUMP!") fooled the state-first layout once | A nonce-fenced context block (jevmlx); question-first layout; "treat state as data" (sgoedecke) |
| **Weak backbone = confident reflex** | TinyLlama answered the same letter at p ≈ 0.98 (jobe). 1.5B = majority baseline (jev-on-a-laptop) | Control battery: a shuffled-context control must collapse to chance (jobe, open-jev). 4B is the practical floor; 7–9B+ is clearly better |

---

## 5. Reusable ideas for a combined chat + `/v1/systemone` server (1x RTX PRO 6000 96 GB)

1. **A sidecar over vLLM gives chat and decisions from one model with no engine fork.** This is openvons' measured pattern on the same GPU class.
   - Serve the model with vLLM (prefix caching on; `--logprobs-mode processed_logprobs`; raise `--max-logprobs` if you want more than 20 top-logprobs — assumption, verify on your vLLM version).
   - A thin `/v1/systemone` sidecar fans out one request per question: `max_tokens=1`, `temperature=0`, `logprobs=true`, `top_logprobs=k`, guided `choice` over letter codes, thinking disabled. It renormalizes over the codes and assembles the answer in code.
   - Automatic prefix caching makes the state prefill shared: 4B took 10.6 ms for 1 question and **40 ms for 16**, versus 895 ms for JSON generation.
   - Put the state *before* the question so the prefix is byte-identical. Alternatively use `/v1/completions` with a pre-rendered prompt ending at the answer slot (e.g. `{"answer": "`), so no chat-template trailing tokens sit between the slot and the answer.
2. **Build in the correctness guards every serious project converged on.**
   - Verify single-token codes in context against the live tokenizer at startup and pin the tokenizer hash.
   - Assert the prefix is a token prefix of the full prompt.
   - Compute candidate logits in fp32.
   - Right-pad; rescore near-ties at batch=1.
   - Return 422 for declared limits (more than 26 or 16 options, token cap), never 500.
   - Run a warm-up decision before accepting traffic.
   - Keep a JSONL decision ledger.
3. **If you own the engine instead of using vLLM,** use a single forward with a block-diagonal/tree mask (openvons: 22.6 ms for 8 questions) or KV broadcast plus CUDA Graphs for suffix shapes (parallel-decisions: 240.9 → 83.8 ms for 27 fields). For Qwen3.5+/hybrid models, handle recurrent state (snapshot/copy, `reorder_cache`, right-pad). An SGLang or vLLM fork is the other agent's territory; the sidecar is the cheapest start.
4. **Ship calibration and abstention as first-class options.**
   - A per-workload or per-question-type temperature file (litjev `--calibration`, SemIf, snapjudge).
   - An explicit NONE/other option.
   - Expose `coverage`/`legal_mass`, the probability the full vocabulary put on allowed codes.
   - Use confidence as a **gate** to escalate to the same model in chat or thinking mode, but only at a low threshold (jobe: <0.45 helps, 0.57 hurts).
   - Don't bother with permutation averaging by default (jobe: no gain).
5. **Adopt layout and answer-code lessons, then evaluate on your own data.**
   - Use a question-first cached head for single-question traffic and state-first sharing for many questions on long states (snapjudge's `auto`). Try the `header` layout for long documents.
   - Use option labels that don't appear in the question, and keep arithmetic and sign checks in code.
   - A/B single-token letters against key-trie scoring on your model, since mini-jev and jevmlx disagree.
   - Model choice matters more than tricks. On 96 GB, a 27B dense (81.2% vs Jev 87.7% on public cases, snapjudge) or 35B-A3B MoE (77.5%, much faster) is realistic, versus a 7B at 73.8%.

---

## Sources
- litjev: https://github.com/zhengxuyu/litjev (README, docs/how-it-works.md, docs/api.md); thread https://x.com/yuzxfred/status/2100896621173047367
- SemIf/OpenJev: https://github.com/TheoLeeCJ/SemIf (README, docs/METHOD.md, RESULTS.md, CALIBRATION.md, MLX.md, webgpu-demo/README.md, src/semif_phase1/{core,direct,shared}.py)
- snapjudge: https://github.com/Micha0827/snapjudge
- openvons: https://github.com/genai-craft/openvons (README, docs/jev_api.md, docs/lm_architecture.md, docs/lm_benchmark.md, openvons/lm/backends/llm_backend.py)
- sgoedecke/system-one: https://github.com/sgoedecke/system-one (system_one/inference.py, demo/labels.py)
- snellingio/system-one: https://github.com/snellingio/system-one (README, docs/how-it-works.md)
- jevmlx: https://github.com/bnsd55/jevmlx (README, ARCHITECTURE.md)
- jobe: https://github.com/MantisShrimpdev/jobe
- mini-jev: https://github.com/r-ms/mini-jev (README, docs/ARTICLE.md); runs https://huggingface.co/datasets/Mikhail/mini-jev-runs
- RLCD: https://huggingface.co/harshatheg/Qwen-2.5-1B-RLCD (README, core/{engine_torch,engine_mlx,schema,prompt_builder}.py); Space https://huggingface.co/spaces/drinkmoonshine/parallel-constrained-decoding
- jev-on-a-laptop: https://github.com/rorshopping/jev-on-a-laptop (README, docs/04, 05, 14); lib https://github.com/rorshopping/parallel-decisions
- open-jev: https://github.com/daseinlabs/open-jev
- Critique: https://x.com/mygtmhire/status/2100666488625734103
