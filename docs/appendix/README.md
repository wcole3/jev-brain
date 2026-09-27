# Appendix: detailed research notes

The raw research behind the main docs, with a source for almost every claim.
Written by research sub-agents on 26 September 2026, then spot-checked (open/merged
status of the cited GitHub issues and PRs, the TypeSafe terms, the vLLM
`logprob_token_ids` field).

| File | Covers |
|---|---|
| [jev-notes.md](jev-notes.md) | Jev itself: API schema, limits, pricing, calibration studies, architecture, RLCD |
| [inference-top-projects.md](inference-top-projects.md) | decider, simple-jev, reflex, jevfire, openjev-sglang: how each runs, chat coexistence, engine bugs |
| [inference-other-projects.md](inference-other-projects.md) | litjev, SemIf, snapjudge, openvons, jobe, mini-jev and others; the technique and its failure modes |
| [trained-and-diffusion.md](trained-and-diffusion.md) | Diffusion route and the strongest trained open models |
| [schema-audit-inference.md](schema-audit-inference.md) | Source-code audit of answer fields and `confidence` in 12 inference-technique servers |
| [schema-audit-trained.md](schema-audit-trained.md) | Same audit for trained and diffusion servers |

Paths like `infer/...` or `trained/...` inside these notes point to raw scrapes in the
local `.firecrawl/` cache, which is git-ignored.
