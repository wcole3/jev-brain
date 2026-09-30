# The benchmarks, explained

Two public benchmarks and one bench of our own show up in this repo's docs. Their numbers
look inconsistent until you know what each one measures. This doc explains all three.

## Short answer

- **Decision Index 0.2.1** is the community leaderboard: ~120k requests over 38 benchmarks,
  scored as chance-corrected "skill" (0 = random, 100 = perfect). Jev scores 57.9 there.
- **JevBench** is a small typed-decision test (choice, noul, score) scored as plain
  accuracy. Jev scores ~91 there. Same model, different ruler, so the numbers are not comparable.
- **Our bench** (`scripts/bench.py`) runs speed and load tests through the gateway, plus
  JevBench pinned to one commit. It can also point at the real Jev API.
- **Numbers differ for five reasons:** skill vs accuracy, chance correction, which rows
  were sampled, network latency, and run-to-run noise (about ±0.2 points).

## 1. The Decision Index 0.2.1

A community leaderboard, not run by TypeSafe. The board is the HF Space
[multimodalart/jev-decision-index](https://huggingface.co/spaces/multimodalart/jev-decision-index);
the harness is [apolinario/decision-index](https://github.com/apolinario/decision-index).
Our summary of the board is [../3-leaderboard.md](../3-leaderboard.md).

**What it runs:** 120,340 requests from 38 counted benchmarks (MMLU-Pro, GPQA, BFCL,
BANKING77 and so on) in five areas. Each request gives a `state` and typed questions,
and the model returns a probability per option.

| Area | Weight |
|---|---|
| Knowledge & Reasoning | 25.8% |
| Language Understanding | 25.8% |
| Retrieval & Classification | 20.0% |
| Tools & Automation | 18.3% |
| Arts & Human Taste | 10% (fixed) |

The other four areas share 90% in proportion to the square root of their benchmark count.
Inside an area, 13 "gold" benchmarks weigh 1.2 and the rest 1.0.

**Skill score.** Each benchmark is first scored with its own metric (accuracy, macro-F1,
nDCG@10...). Then chance is removed:

```
skill = clip( (score - chance) / (1 - chance), 0, 1 )      0 = random guessing, 100 = perfect
```

A yes/no benchmark has chance 0.5. An accuracy of 0.75 there is a skill of 50, not 75.
The index is 100 x the weighted mean of the five area scores.

**Fairness rules** (from the harness README):

- No truncation. A request that does not fit is recorded `unsupported`.
- No option filtering. Every option must get a probability.
- No prompt tuning. Each model uses its own published prompt and readout.
- **Unanswered = wrong.** Errors, unsupported and abstained requests score zero before
  chance correction.

**ECE** (expected calibration error) is reported next to the index. Group answers by stated
confidence, then compare each group's average confidence with its actual accuracy. ECE is
the size-weighted average gap; 0 is perfect, lower is better. See [calibration.md](calibration.md).

**Latency protocol.** The maintainers measure it themselves: one process on one RTX PRO 6000,
one request at a time, on a private held-out sample. Models over 1,000 ms median are not added
to the board. Jev's 524 ms is a hosted HTTPS round trip, so the site itself calls it "not a
controlled comparison" with local runs.

## 2. JevBench

An independent, open benchmark of the three Jev question types. It is not affiliated with
TypeSafe. We pin it to upstream commit `fcec62f`
([model-collapse/jev-bench](https://github.com/model-collapse/jev-bench)); locally a clone sits in the git-ignored `.cache/jev-bench-upstream/`.

**Types** (see [../1-what-is-jev.md](../1-what-is-jev.md)): `choice` picks one option key, `noul` answers yes/no,
`score` picks a level index on an ordered scale.

**Sources.** The 1,682 gold rows come from three places:

| Source | What it is | Gold rows |
|---|---|---|
| panoramic | synthetic or computed questions (commerce, logic, moderation...) | 400 choice, 400 noul, 100 score |
| banking77 | intent classification, human labels (CC-BY-SA) | 300 choice |
| typed_decisions | operational topics (support, security, invoices, agent traces) | 50 choice, 225 noul, 207 score |

Counts are from our cached data and the results table in [../results/jevbench-vs-jev.md](../results/jevbench-vs-jev.md).

**Gold vs silver.** Every row has a `reliability` tier. Gold is human, objective or
computed labels. Silver is labelled by a panel of models. The board reports gold only, so a
model is not flattered by labels made by its cousins. Upstream ships 2,934 rows in total: 1,682 gold and 1,252 silver.

**`eval_metric`.** `exact` rows (all `noul`, all `choice`, computed maths) count a prediction as right only when it
equals the label. `ordinal` rows (subjective `score`) have ordered levels, so off by one is a small miss.
Here 207 rows are ordinal; panoramic's 100 score rows are `exact`.

**QWK and MAE, worked example.** Six rows, levels 0-4, gold = `[0, 1, 2, 3, 4, 2]`.
(Values computed with our `qwk` in [`scripts/bench_report.py`](../../scripts/bench_report.py).)

| Predictions | Exact % | MAE | QWK |
|---|---|---|---|
| `[0,1,2,3,4,2]` perfect | 100 | 0.0 | 1.0 |
| `[1,1,2,3,3,2]` two off by one | 67 | 0.33 | 0.86 |
| `[2,2,2,2,2,2]` always the middle | 33 | 1.0 | 0.0 |
| `[4,3,2,1,0,2]` reversed | 33 | 2.0 | -1.0 |

- **MAE** (mean absolute error): the average number of levels you are off. Lower is better.
- **QWK** (quadratic-weighted kappa): agreement beyond chance, where a miss of *d* levels
  costs *d* squared. 1 = perfect, 0 = no better than guessing, below 0 = worse than chance
  (ranking backwards). Two near misses barely hurt; far misses hurt a lot.

Upstream pools all ordinal rows into one confusion matrix ([`bench_eval.py`](https://github.com/model-collapse/jev-bench/blob/fcec62f13ce961115af0d16317f0ff15986a9a25/bench_eval.py)).
We do the same.

**Errors count as wrong.** A failed or unparseable request scores as a wrong answer. Our
Jev run had one HTTP error out of 1,682 and it lowers the score.

**232 vs 1,682 rows.** The upstream leaderboard used a 232-row gold sample, whose row ids
are not published; upstream calls the board's uncertainty "+-~4%".
Jev scores 88.8 there, and 91.1-91.3 on all 1,682 rows: inside that margin. We cannot
rerun the 232 rows exactly.

## 3. Our bench

[`scripts/bench.py`](../../scripts/bench.py) talks to the gateway (so it sees what a client
sees) and reads vLLM's `/metrics` ([`bench_vllm.py`](../../scripts/bench_vllm.py)).

| Phase | What it sends | What it tells you |
|---|---|---|
| cold | seeded synthetic requests; a random nonce in each state defeats prefix caching | worst-case latency per (state length, questions, options) |
| warm | one fixed request repeated, after one warm-up call | latency when the cache helps |
| throughput x1/4/16 | 2,048-token state, 16 questions, 26 options, for 30 s (10 s with `--quick`) | requests per second |
| jevbench | one gold row per request | accuracy, plus latency on tiny requests |
| chat (`--chat`) | chat alone, then under 4 systemone streams | contention; off by default until DS-007 |

The request builders are in [`bench_data.py`](../../scripts/bench_data.py) (synthetic text
comes from `data/bench/corpus.txt`, seed 0). `--quick` shrinks the grid and uses 50 JevBench
rows; `--jevbench-only` skips everything else.

**KV/token table.** Each phase also records vLLM's counters, so the summary has one row per
phase. Two token counts matter:

- **usage:** Jev-style `usage.input_tokens`, the least work possible (state once, each question once).
- **computed:** prompt tokens minus prefix-cache hits, what the GPU actually prefilled.

**Computed / usage** = 1.0 means perfect reuse. On the `--quick` run the throughput phases
sit at 2.67, so the GPU does 2.7 times the necessary work. The jevbench phase is exactly
1.00 because one-question requests share nothing. The full explanation is in
[prompt-sharing.md](prompt-sharing.md); the numbers are in
[../results/qwen3.6-27b/2026-09-29T210957Z-quick/summary.md](../results/qwen3.6-27b/2026-09-29T210957Z-quick/summary.md).

**Provenance.** Every `summary.md` starts with a list: timestamp, repo commit (`-dirty` if
code changed), target, JevBench SHA `fcec62f13ce9...`, rows available and run, profile, HF
model and revision, prompt layout, option orders, vLLM version, KV capacity. Any number can
be traced to the code and data that made it.

**`--target jev`** runs JevBench against `https://api.typesafe.ai` with the same request
builder and scoring (key from `TYPESAFE_API_KEY` or `secrets/.jev-key`). Jev's per-row
answers stay in `.cache/jev-results/`; only the summary is committed, because TypeSafe's
terms forbid training or calibrating on Jev outputs ([CLAUDE.md](../../CLAUDE.md) rules; see [../6-answer-compatibility.md](../6-answer-compatibility.md)).

**Results folders** are `docs/results/<profile>/<UTC timestamp>[-quick][-jevbench]/`, e.g.
`2026-09-29T130343Z-jevbench`, with `summary.md` and `raw.jsonl`. Phase-1 full runs are under
`2026-09-28T000000Z`.

**Calibration table.** JevBench summaries have a second table with ECE (15 bins), Brier
score and the noul yes/no bias (share said "yes", false-no and false-yes counts). It reads
each answer's probabilities, which runs recorded before 2026-09-30 lack. See [calibration.md](calibration.md).

## 4. Why the numbers differ

Running example: [../results/jevbench-vs-jev.md](../results/jevbench-vs-jev.md).

| Reason | Effect |
|---|---|
| **Skill vs accuracy** | The Index reports skill, JevBench reports accuracy. |
| **Chance correction** | Skill subtracts the guessing floor, so it is always lower than the raw score. |
| **Row set** | Different questions, different difficulty. |
| **Sample size** | 232 gold rows: about +-4 points. 1,682 rows: smaller error. |
| **Latency** | Jev pays for the network; local models do not. |
| **Noise** | Repeat runs differ slightly. |

- **Skill vs accuracy.** Jev is ~91 on JevBench and 57.9 on the Index. That is not a contradiction. The Index
  includes hard benchmarks (GPQA, HLE, ChessBench), and every score is chance-corrected. Illustration only (not a
  measurement): 87.5% on a yes/no test with chance 50% is a skill of 75.
- **Chance correction changes the ranking of tasks.** A 2-way yes/no gives free points that a 26-way choice does
  not. This is why the Index moved from accuracy to skill in 0.2.
- **Sample and row set.** Jev's board number is 88.8 on 232 rows and 91.1-91.3 on 1,682 rows, with the same
  per-type pattern.
- **Network latency.** Jev's p50 is 194 ms in our JevBench run and 524 ms on the Index. Ours are 62-89 ms on the local GPU
  for the same single-question rows. Jev's figure includes the HTTPS round trip; ours does not.
  The two Jev numbers also come from different request sets and clients, so they are not the same measurement.
- **Nondeterminism.** Two Jev passes over identical requests differ on 18 of 1,682 rows: 17 near-ties
  and one HTTP error. That is about +-0.2 points. Our bf16 models drift a few rows as well (84.2 -> 84.4 for
  qwen3.6 between two days). See [determinism.md](determinism.md).

**Rule of thumb:** compare numbers only within the same benchmark, row set and metric. Row-by-row runs on our own
bench are the most reliable comparison, because we control the data, the harness and the model.

## Caveats

- The Index and the Space update often; numbers here are the 2026-09-26/27 snapshot ([../3-leaderboard.md](../3-leaderboard.md)).
  The Space publishes point estimates with no uncertainty intervals.
- Upstream JevBench lists the gold tier as human, objective or computed labels; its data README also
  says the operational typed_decisions topics are labelled by a model panel plus deterministic recomputation. We have
  not audited which typed_decisions rows are tagged gold.
- The ~4-point margin for the 232-row board is upstream's own statement, not our calculation.
- Jev's row on the Index is reported by the community, not by TypeSafe.
- The worked QWK example is small and only for intuition; real QWK depends on the label distribution.

## Sources

- Decision Index kit README (scoring, weights, rules, latency): https://github.com/apolinario/decision-index
- Decision Index board and method note: https://huggingface.co/spaces/multimodalart/jev-decision-index
- JevBench (README, LEADERBOARD.md, `bench_eval.py`, `data/README.md`) at `fcec62f`: https://github.com/model-collapse/jev-bench
- Ours: [../3-leaderboard.md](../3-leaderboard.md), [../results/jevbench-vs-jev.md](../results/jevbench-vs-jev.md),
  [../appendix/](../appendix/), [`scripts/bench.py`](../../scripts/bench.py)
- Raw scrapes: `.firecrawl/background/benchmarks/` (git-ignored)
