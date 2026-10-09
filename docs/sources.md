# Sources

Research done 26 September 2026 with Firecrawl plus the GitHub and Hugging Face APIs.
Detailed research notes with per-claim citations are in [appendix/](appendix/).

## Jev (official)

- Launch post: https://typesafe.ai/blog/introducing-system-one-models-and-jev
- API reference: https://docs.typesafe.ai/api
- Models, limits, pricing: https://docs.typesafe.ai/models
- Full docs in one file: https://docs.typesafe.ai/llms-full.txt
- Official workflow evals: https://evals.typesafe.ai/
- Customer agreement (distillation clause): https://typesafe.ai/legal/mca
- Official adapter (confidence formulas): https://github.com/typesafe-ai/system-one-adapter-python
- Hacker News launch thread (CEO comments): https://news.ycombinator.com/item?id=49717558

## Independent studies of Jev

- Architecture teardown (Archer Hume): https://archerhume.com/posts/jevs-architecture-unmasked/
- Out-of-distribution calibration: https://github.com/scienthoon/jev-ood-calibration
- Behaviour study: https://github.com/RINNECODER/jev-behavior-study
- Dice test: https://kantahayashiai.github.io/posts/jev-does-not-play-dice/
- OpenRouter vs Claude Opus 5 on Banking77: https://openrouter.ai/blog/insights/jev-vs-claude-opus-5-classification/

## Community tracker and benchmark

- Jev Decision Index (leaderboard + news): https://huggingface.co/spaces/multimodalart/jev-decision-index
- Leaderboard data used here: `data/index.json` in that Space (edition 0.3 since 2026-10-06; 0.2.1 values in `data/index-v0.2.1.json`)
- Harness: https://github.com/apolinario/decision-index
- Awesome lists: https://github.com/AnotiaWang/awesome-jev, https://github.com/hellogumbo/awesome-jev

## Inference-technique projects

| Project | Link |
|---|---|
| Decider (chat layout, vLLM server) | https://github.com/Mapika/decider |
| simple-jev | https://github.com/featherless-ai/simple-jev |
| reflex | https://github.com/kshetrajna12/reflex |
| jevfire | https://github.com/kikoncuo/jevfire |
| openjev-sglang | https://github.com/ekzhang/openjev-sglang |
| openvons | https://github.com/genai-craft/openvons |
| litjev | https://github.com/zhengxuyu/litjev |
| SemIf / openjev | https://github.com/TheoLeeCJ/openjev |
| snapjudge | https://github.com/Micha0827/snapjudge |
| jobe | https://github.com/MantisShrimpdev/jobe |
| jevmlx | https://github.com/bnsd55/jevmlx |
| mini-jev (study) | https://github.com/r-ms/mini-jev |
| jev-on-a-laptop (study) | https://github.com/rorshopping/jev-on-a-laptop |

## Diffusion route

- vLLM PR 57250 (merged 2026-09-22): https://github.com/vllm-project/vllm/pull/57250
- razorback16/openjev: https://github.com/razorback16/openjev
- djev: https://github.com/Davipar/djev-dev
- JoshuaSP/open-jev: https://github.com/JoshuaSP/open-jev
- GitHub Next localjev: https://github.com/githubnext/localjev

## Trained models

| Model | Weights | Code |
|---|---|---|
| Surogate Rune 26B-A4B v3 | https://huggingface.co/surogate/rune-26b-a4b-GGUF | https://github.com/invergent-ai/surogate |
| AutoJev-27B | https://huggingface.co/denis-pplx/autojev-27b | https://github.com/denis-pplx/autojev |
| Jebadiah 27B | https://huggingface.co/frontier-infra/jebadiah-27b | https://github.com/getainode/jebadiah |
| Winnow-12B | https://huggingface.co/EldanRing/Winnow-12B | https://github.com/EldanRing/winnow-inference |
| Decider 35B-A3B | https://huggingface.co/Mapika/decider-35b-a3b | https://github.com/Mapika/decider |
| Bespoke Nimble 9B v2 | https://huggingface.co/bespokelabs/Bespoke-Nimble-9B-v2 | https://github.com/bespokelabsai/nimble |
| Kev | https://huggingface.co/jaredpalmer/kev-9b | https://github.com/jaredpalmer/kev |
| Tev1 (Together AI) | https://huggingface.co/togethercomputer/Tev1-4B-experimental | https://github.com/togethercomputer/tev1 |

## Open engine issues that affect a combined server (checked 26 Sep 2026)

| Issue | Status | Effect |
|---|---|---|
| [SGLang #34719](https://github.com/sgl-project/sglang/issues/34719) (fix: [#34075](https://github.com/sgl-project/sglang/pull/34075)) | open | Scheduler crash when chat and token-logprob requests share a batch |
| [vLLM #51789](https://github.com/vllm-project/vllm/pull/51789) | open | Top-k logprob values of other requests can become `-inf` |
| [vLLM #42592](https://github.com/vllm-project/vllm/issues/42592) | open | Speculative decoding + label scoring can crash the server |
| [vLLM #49354](https://github.com/vllm-project/vllm/issues/49354) | open | LoRA can silently do nothing on Qwen3.5/3.6 hybrid models |
