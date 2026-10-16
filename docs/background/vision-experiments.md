# Vision experiments (DS-034)

How we iterate on image-decision prompts and logic without overfitting the public vision suite. Design:
[the spec](../superpowers/specs/2026-10-16-vision-experiments-design.md). The experiments themselves are DS-035
(prompt, layout), DS-036 (image budget, calibration) and DS-037 (latency).

## Short answer

- **Why a split.** The public vision suite (12,210 rows) is half the board score. Tuning on all of it would
  overfit the number we are judged on, so a config is judged on a fixed **dev** split and only finalists touch
  a **holdout**.
- **Collect once, re-score offline.** `vision_collect.py` records raw letter logprobs per config; calibration,
  the letter prior and option orders are then CPU-only arms over the same file.
- **Paired statistics, no winner.** `vision_compare.py` reports the index change with a confidence interval,
  McNemar p, ECE, NLL, tokens and latency. The owner picks.

## 1. The splits

`scripts/vision_splits.py write` cuts three committed manifests in `data/splits/`. Rows that share any image
file are one group, and a group lives in exactly one split. A split takes at most 10 rows from any group,
chosen by `sha256(seed:row_id)`, so one 70-row FUNSD document cannot fill KIE; the group's other rows are
reserve. Per benchmark, capped groups are added by seeded hash until the target is reached: dev = min(136, 40%
of the benchmark), holdout = min(218, 40%). The rest is reserve and is never read. A benchmark can overshoot
by one capped group (KIE dev is 141).

| Benchmark | Dev | Holdout | Latency |
|---|---|---|---|
| BLINK | 136 | 218 | 30 |
| CV-Bench | 136 | 218 | 30 |
| CharXiv | 136 | 212 | 30 |
| InfographicVQA | 97 | 97 | 21 |
| KIE (CORD+FUNSD) | 141 | 223 | 31 |
| MMMU-Pro vision | 136 | 218 | 30 |
| Mind2Web | 136 | 218 | 30 |
| Moderation (Hateful Memes) | 136 | 218 | 30 |
| R-Bench-M | 136 | 218 | 30 |
| RealWorldQA | 136 | 218 | 29 |
| Winoground | 136 | 218 | 29 |
| **Total** | **1,462** | **2,276** | **320** |

The latency set is 320 rows drawn from dev; the first 20 are warm-up. Each manifest records the suite's
SHA-256, the seed and the grouping rule in `meta`, and a tool refuses a manifest whose suite hash no longer
matches the suite on disk.

## 2. Holdout rules

- Reading `vision-holdout` needs `--holdout` (collect and `vision_run.py`). Each read appends the date, tool,
  label and commit to `docs/results/vision-experiments/holdout-log.md`; from the 6th entry on it warns.
- Finalists only, at most 5 logged looks, and confirm once. Reused test sets overfit mostly through winner
  selection (Dwork et al. 2015; Recht et al. 2019), so the holdout is for confirming, not choosing.
- Nothing is ever fitted on holdout rows. A fitted arm on a holdout collect fits on all of a matching dev
  collect (`--fit-on`) and scores the holdout.

## 3. Collect

`scripts/vision_collect.py --profile P --label L` reads each split row straight from vLLM with the gateway's
own code (`build_batch`, `read_rows`), at concurrency 8, and records every order's raw letter logprobs plus
`input_tokens`, `shared_len` and `padded`.

- **A config** is a profile, a label, a layout, the orders to record (default `identity+reversed`, optional
  `cyclic:N`) and `--env KEY=VALUE` overrides such as `MM_PROCESSOR_KWARGS`. The label folder records the whole
  config; a second collect under the same label with another config is refused. `VLLM_URL` and `*_API_KEY` are
  refused in `--env`.
- **Same padding as live.** Reads use `pad_rows` = the question count, as text collect does, so an identity
  read equals what the live gateway would do. An identity+reversed arm on a padded profile (qwen3.8) is not
  live-equivalent: live runs one order.
- **Checks before any read:** the labels table exists, the served model matches the profile, and a probe image
  through `/inference/v1/generate` expands to the length the gateway counts (this catches a vLLM started with
  other mm kwargs). On `--split holdout` these run before the log entry is written.
- **Stamp and resume:** each record carries the layout hash, label-table hash, model, mm kwargs and commit.
  Resume ignores the commit, refuses other settings, and drops a truncated tail.
- Output: `.cache/vision-collect/<profile>/<label>/<split>.jsonl.gz` and `<split>.config.json`.

## 4. Offline arms

`scripts/vision_offline.py --collect FILE --arm A --orders O --out DIR` (CPU only). An arm is a subset of the
collected orders plus one calibration method:

| Method | What it does |
|---|---|
| `text` | The profile's text T and b, which is what ships today |
| `fit-T` | One image temperature |
| `fit-T-bench` | One temperature per benchmark |
| `pride` | A per-letter prior subtracted before T (Zheng et al., PriDe) |

- **Cross-fit.** On a dev collect, folds are `sha256("fold:" + group) % 2`; each row is scored with parameters
  fitted on the other fold, so no row is scored with a fit that saw it.
- **Holdout.** Fitted arms on a holdout collect need `--fit-on <dev collect>`; the dev collect's profile,
  layout, orders and env must match. `--fit-on` is refused for `text` and for dev collects.
- **Fallbacks.** A fit on fewer than 30 questions uses the text T (listed in `arm.json` and the console).
  PriDe needs at least 30 reads per option count, else that option count is left undebiased.
- **PriDe and orders.** With identity orders only, PriDe mixes the gold-position skew with the letter bias.
  Cyclic orders put each option in every position and separate them.

## 5. Compare and how to read it

`scripts/vision_compare.py --baseline NAME=DIR NAME=DIR ... --out-label L` takes offline arms (`DIR` holds
`scored.jsonl.gz`) and live kit runs (`results.jsonl.gz`). Mixing them: put the offline arm first as
`--baseline`, because a live full-suite run is cut to the baseline's ids but not the reverse.

- **Index** is the kit's: per benchmark skill = (acc - mean chance) / (1 - mean chance), clipped to [0, 1],
  then a weighted mean with the kit's weights, R-Bench-M 0.5, MMMU-Pro vision 0.25 and 1.0 for the rest. With
  these weights compare reproduces the stored full-suite 73.70.
- **Δ index [95% CI]** is config minus baseline, with a paired group bootstrap (10,000 resamples, groups
  resampled within each benchmark, seed 0). If the interval holds 0, the data do not separate the two.
- **McNemar p** is the exact two-sided test on rows where exactly one config is right (b: baseline only,
  c: config only). **d** is the discordant share (b + c) / N. SE(Δacc) is about sqrt(d / N), so d tells you
  whether N is enough: dev (~1,500) detects about +2 points at d <= 8%.
- **Agreement** is the share of rows with the same top answer. A high-agreement, near-zero Δ config is a
  different config that does the same job.
- **Per-benchmark Δ skill** shows where a change lands. One benchmark moving alone is a hint, not a result.
- **ΔECE, ΔNLL** are calibration; **tokens** is the mean `input_tokens`; **latency** is p50 and p80 when
  attached with `--latency NAME=DIR` (a dir with a latency run's `summary.json`).
- **Refusals:** configs that do not cover the same ids; a latency summary without a power limit at start and
  end, or with a limit that changed mid-run; summaries at different limits. Errored live rows count as wrong.
- Output: `docs/results/vision-experiments/<UTC>-<label>/summary.md` and `summary.json`. It never picks a
  winner.

## 6. Latency

```bash
uv run python scripts/vision_run.py --profile P --gateway URL --ids vision-latency --workers 1
```

- One worker, 320 rows in manifest order; the 20 warm-up rows are dropped by id from the summary.
- It reads the GPU power limit at start and end and samples telemetry into `telemetry.csv`, so every
  `vision_run` needs `nvidia-smi`. Latency is relative at the owner's limit; final numbers come from a 600 W box.
- Drift biases back-to-back runs, so a config that needs a vLLM restart runs **A-B-A**: baseline, config,
  baseline again. Configs that only change the gateway can alternate without a restart.

## 7. Cost per run

| Step | Time |
|---|---|
| Collect, dev, `identity+reversed` | about 12 min per config per model on a 600 W box (spec estimate) |
| Offline arm, compare | seconds to a minute, CPU |
| Latency set | one worker, 320 rows; minutes, plus a restart for A-B-A |
| Holdout collect | about 1.5x a dev collect (2,276 vs 1,462 rows); a logged look |

GPU jobs over 10 minutes need the owner's ok.

## 8. Research behind the choices (2026-10-16)

| Finding | Source | Effect on the design |
|---|---|---|
| IRT anchor subsets (tinyBenchmarks, metabench) estimate model scores within ~2% but are fitted on model-to-model variation | Polo et al. 2024; Kipnis et al. 2024 | Not used: unproven for prompt-vs-prompt; stratified random instead |
| Paired comparison: SE(Δacc) ≈ √(d/N), d = share of rows where configs disagree | standard; McNemar | Dev ≈1,500 detects ≈+2 pt at d ≤ 8%; compare reports d so N can be revisited |
| Reused test sets overfit mostly through winner selection | Dwork et al. 2015; Recht et al. 2019 | Fixed dev/holdout; holdout for finalists only, ≤5 logged looks |
| VLM multiple choice is order- and letter-biased; PriDe removes a letter prior estimated on a small sample | Zong et al. 2023; Zheng et al. (PriDe) | Offline arms for orders and a letter prior |
| Temperature scaling calibrates VLMs with few samples | Tu et al. 2024 | Offline `fit-T` and `fit-T-bench` arms, cross-fitted |
| Latency tails need hundreds of samples; drift biases back-to-back runs | general practice | 300 timed rows, warm-up dropped, A–B–A runs, power limit recorded |

## Caveats

- **Dev is not untouched.** Many configs are compared on it; the holdout is what guards against that.
- **Never train, calibrate or tune on Jev API outputs.** Gold labels only.
- **Text still needs its own check.** Every shipped change still gets a JevBench run.
