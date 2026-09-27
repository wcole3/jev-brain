# 2. The open reproductions

Within ten days of Jev's launch, dozens of open projects appeared. The community tracker
[jev-decision-index](https://huggingface.co/spaces/multimodalart/jev-decision-index)
lists 64 of them and benchmarks 67 open entries.

**None of them is Jev.** They all copy Jev's *interface* (state + typed questions in,
probabilities out, often the exact `/v1/systemone` wire format). None has Jev's
weights, architecture or RLCD training.

## Five kinds of project

| Kind | What it is | New weights? | Count on tracker |
|---|---|---|---|
| **Inference technique** ("decoding") | A trick on a stock LLM: read the state once, then read the probabilities of the answer letters for every question in one batched pass | No | 18 |
| **Diffusion** | Run a text-diffusion model (DiffusionGemma) that fills all answer slots at once | No | 4 |
| **Trained** | Fine-tune a model (full fine-tune, LoRA, or a small scoring head) on decision data | Yes | 31 |
| **Prior art** | "This already existed": zero-shot classifiers such as GLiNER | Already existed | 2 |
| **Explainers** | Teardowns, benchmarks, awesome-lists | — | 9 |

### 1. Inference technique: "no training needed"

The biggest wave, and the one that matters most for a combined chat + decisions server.

A normal LLM already "knows" the answer to a multiple-choice question at the moment it
is about to write the answer letter. If you stop there and read the probabilities of
the tokens `A`, `B`, `C`…, you have a probability distribution without generating
anything. Do this for every question at once, reusing the state you already
processed, and you get Jev's behaviour on a stock model.

- **Best result:** Decider chat on stock Gemma 4 31B scores **57.3** vs Jev's **57.9**.
- **Keeps chat:** the model is unchanged, so the same model can still chat.
- **Weak spot:** raw probabilities are often badly calibrated until you fit a
  temperature on labelled data.

Details in [4-inference-technique.md](4-inference-technique.md).

### 2. Diffusion: "Jev mode" for DiffusionGemma

Text-diffusion models don't write left to right. They start from a "canvas" of noisy
token slots and clean all of them up in parallel. To use one like Jev, you write the
answer template into the canvas, leave one noisy slot per question, and run one step.
The model's guess for each slot is the answer distribution.

- Support is merged into vLLM ([PR 57250](https://github.com/vllm-project/vllm/pull/57250),
  on `main` since 22 September; not yet in a release).
- **Fastest** entry on the board ([razorback16/openjev](https://github.com/razorback16/openjev):
  38 ms median), but **less accurate** (32–49) and poorly calibrated (ECE ~0.21).
- [razorback16/openjev](https://github.com/razorback16/openjev) serves `/v1/systemone`
  and chat from one Docker container on your GPU class.

### 3. Trained models

Real training runs that teach a model the decision task. Main flavours:

| Flavour | How | Can it still chat? |
|---|---|---|
| Full fine-tune | Retrain a whole LLM on decision data | Sometimes (if the language head is kept) |
| LoRA | Train a small adapter on top of a frozen LLM | Yes, if you apply the adapter only to decision requests |
| LoRA + head / head only | Add a new small output layer that scores options | No |
| Small encoder | BERT-style classifier (GLiNER, ModernBERT) | No |

Strongest trained models (index score, Jev = 57.9):

| Model | Score | Base | Licence | Chat? | Serve with |
|---|---|---|---|---|---|
| [Surogate Rune 26B-A4B v3](https://huggingface.co/surogate/rune-26b-a4b-GGUF) | 57.4 | Gemma 4 26B MoE | Apache-2.0 | Yes (same model) | [surogate](https://github.com/invergent-ai/surogate) |
| [AutoJev-27B](https://huggingface.co/denis-pplx/autojev-27b) | 56.4 | Qwen3.8-27B | Apache-2.0 | No (LM head removed) | `autojev-serve` |
| [Jebadiah 27B](https://huggingface.co/frontier-infra/jebadiah-27b) | 54.7 | Qwen3.8-27B | Apache-2.0 | Probably (merged LoRA, untested) | `jebadiah-serve`, vLLM |
| [Winnow-12B](https://huggingface.co/EldanRing/Winnow-12B) | 50.0 | Gemma 4 12B | Apache-2.0 | Yes, by design | [winnow-inference](https://github.com/EldanRing/winnow-inference) (llama.cpp) |
| [Decider 35B-A3B](https://huggingface.co/Mapika/decider-35b-a3b) | 47.1 | Qwen3.5-35B MoE | Apache-2.0 | No | `decider.serve` |
| [Bespoke Nimble 9B v2](https://huggingface.co/bespokelabs/Bespoke-Nimble-9B-v2) | 39.6 | Qwen3.5-9B | Apache-2.0 | Yes (unmerged LoRA) | transformers, MLX, SGLang |

Fully open **recipes** (data + training code) exist for Nimble, Decider, Kev, Jebadiah
and Together AI's Tev1 ("[train your own Jev for $17](https://www.together.ai/blog/how-to-train-your-own-jev)").

### 4. Prior art

Teams behind zero-shot classifiers (e.g. [GLiNER 2.5](https://huggingface.co/collections/fastino/gliner25-models))
pointed out that "classify over caller-supplied labels in one pass" existed before Jev.
True for narrow classification, but on the broad benchmark these small encoders score
near chance (2–11 out of 100).

### 5. Explainers and studies worth reading

- [Jev's Architecture Unmasked](https://archerhume.com/posts/jevs-architecture-unmasked/): best black-box teardown.
- [jev-on-a-laptop](https://github.com/rorshopping/jev-on-a-laptop): honest benchmark of the decoding trick. Main
  finding: the confidence of a stock model does not reliably flag its errors.
- [mini-jev](https://github.com/r-ms/mini-jev): preregistered study showing letter-reading is as accurate as
  generating constrained JSON, and ~4× faster.
- [jev-ood-calibration](https://github.com/scienthoon/jev-ood-calibration): Jev's own calibration drops on unseen tasks.
- Curated lists: [AnotiaWang/awesome-jev](https://github.com/AnotiaWang/awesome-jev),
  [hellogumbo/awesome-jev](https://github.com/hellogumbo/awesome-jev).

## What is still not open

- **Jev's weights.** Every "openjev" or "-RLCD" repo is either a stock model plus
  decoding code, or an independently trained model.
- **The RLCD algorithm.** Only described at blog level. The viral
  "Qwen-2.5-1B-RLCD" repo contains no RL and no new weights.
- **A matching general model.** The best open models tie Jev on the community
  benchmark but still trail it on knowledge/reasoning and on long documents
  (e.g. cross-checking 8k-token invoices: Jev 65/75, best open 38–50/75,
  per [snapjudge](https://github.com/Micha0827/snapjudge)).
