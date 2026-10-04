# M3 recommendations (2026-10-03)

From the M3 reports at commit 8076f88 (results commit 5a73644).

**How to read this:**
- **Rule:** a change qualifies on a split when its accuracy CI low is > 0, or its ECE CI high is < 0, without the other metric getting worse beyond its CI. A verdict needs both index-dev and eval. Each arm's T is an ungated calib fit with b = 0.
- **Splits:** index-dev is a stratified sample of Decision Index rows. eval is JevBench plus DecisionBench.
- **Costs:** read cost is reads per question; identity is 1. Live latency comes in Task 8.
- **Decision:** the owner makes the final call.

## Layout (identity order)

| Profile | header vs decider_chat, index-dev | header vs decider_chat, eval | Verdict |
|---|---|---|---|
| qwen3.6-27b | acc +0.020, qualifies | acc +0.017, qualifies | **header** |
| qwen3.8-27b | acc +0.010 [+0.006, +0.013], qualifies | acc +0.015 [+0.007, +0.023], but ECE +0.017 [+0.005, +0.029] worse | keep decider_chat. Auto-switch to header on both splits for states under 512 tokens and for the non-long slice |
| gemma-4-31b | acc +0.041 [+0.036, +0.045], ECE −0.030 | acc −0.004 [−0.012, +0.005], no gain | keep decider_chat |

question_first never qualified.

## Option order

| Profile | On decider_chat | On header |
|---|---|---|
| qwen3.6-27b | identity+reversed: acc +0.003 (index-dev), +0.011 (eval); 2 reads | cyclic:4: +0.003 / +0.007; 2.7–3.2 reads. identity+reversed fails on eval |
| qwen3.8-27b | keep identity: only cyclic:2 on eval | cyclic:2: +0.003 / +0.007; 2 reads |
| gemma-4-31b | identity+reversed: +0.007 / +0.008; 2 reads | identity+reversed: +0.005 / +0.015; 2 reads |

**PriDe:** it is reported but is never a candidate, because the gateway can't serve it. On qwen3.6 decider_chat eval it loses accuracy: −0.010 [−0.015, −0.006].

**qwen3.8's first-option bias (DS-020):** averaging orders recovers only about +0.3 points on index-dev. This is far short of the 4.3-point gap to simple-jev. The gap is not mainly order bias that averaging can fix.

## Cost of a second order

Two reads per question roughly doubles the decision rows per request. The state prefix is shared through the prefix cache, so prefill grows by about the size of the question block, not the whole prompt.

A full Index run takes about 8 h on a rented box with one order. With two orders, expect about 1.3–1.8× that, to be confirmed live.

## Proposed defaults (owner decides)

| Profile | Layout | Orders | Calibration refit |
|---|---|---|---|
| qwen3.6-27b | header | identity, or cyclic:4 for +0.3/+0.7 points at about 3× reads | none if identity; `--orders cyclic:4` otherwise |
| qwen3.8-27b | decider_chat | identity | none |
| gemma-4-31b | decider_chat | identity+reversed, for +0.7/+0.8 points at 2× reads | `--orders identity+reversed` |

## Decision (owner, 2026-10-03)

| Profile | Layout | Orders |
|---|---|---|
| qwen3.6-27b | **header** (was decider_chat) | identity |
| qwen3.8-27b | decider_chat | identity |
| gemma-4-31b | decider_chat | identity (2 orders not worth 2× reads) |

No calibration refit: every profile keeps identity, and header already has its own fitted file. The final full Index run per profile confirms the change.

## Index confirmation (2026-10-04)

Full Decision Index 0.2.1 runs, all at identity orders with each layout's own calibration:

| Profile | decider_chat Index | header Index | Summaries |
|---|---|---|---|
| qwen3.6-27b | 51.61 (borrowed T 1.943) | 55.92 | [decider_chat](../qwen3.6-27b/2026-10-01T152531Z-index/summary.md), [header](../qwen3.6-27b/2026-10-03T140831Z-vast-index/summary.md) |
| qwen3.8-27b | 51.47 | 56.01 | [decider_chat](../qwen3.8-27b/2026-10-03T133219Z-vast-index/summary.md), [header](../qwen3.8-27b/2026-10-04T022907Z-vast-index/summary.md) |
| gemma-4-31b | 57.16 | 60.61 | [decider_chat](../gemma-4-31b/2026-10-03T133229Z-vast-index/summary.md), [header](../gemma-4-31b/2026-10-04T013002Z-vast-index/summary.md) |

Board entries: Decider chat Qwen3.6 51.35, simple-jev Qwen3.8 55.7, Decider chat Gemma 57.33, Jev 57.9.

- **Lesson:** the offline rule (gain on both index-dev and eval) kept qwen3.8 and gemma on decider_chat. index-dev understated header's Index gain (+1.0 / +4.1 accuracy), and eval (JevBench + DecisionBench) showed none. The full Index decided it.
- **Costs:** about +10–17 ms median latency, 7–11 rows per profile refused for length (header prompts are longer), and ECE equal or better.
- **Ties:** ranking ties on ToolRet/BRIGHT stay at 55–62% at 4-decimal rounding.

**Header ships for all three profiles.**
