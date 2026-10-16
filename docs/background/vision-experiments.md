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
- **Paired statistics, no winner.** `vision_compare.py` reports the index change with a group-bootstrap
  confidence interval (the headline), a row-level McNemar p, ECE, NLL, tokens and latency. The owner picks.

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

- Every tool that touches the holdout needs `--holdout` and logs the use: `vision_collect.py --split holdout`,
  `vision_run.py --ids vision-holdout`, `vision_offline.py` on a holdout collect, and
  `vision_compare.py --ids vision-holdout` (one entry per compare). Each entry appends the date, tool, label
  and commit to `docs/results/vision-experiments/holdout-log.md`, after every check that can refuse the run.
- The log warns once it holds more than 5 distinct labels; rereads under one label count once. The tools
  label differently (`vision_offline.py` adds the arm and orders), so one confirmation can count as several.
- Finalists only, at most 5 logged looks, and confirm once. Reused test sets overfit mostly through winner
  selection (Dwork et al. 2015; Recht et al. 2019), so the holdout is for confirming, not choosing.
- Nothing is ever fitted on holdout rows. A fitted arm on a holdout collect fits on all of a matching dev
  collect (`--fit-on`) and scores the holdout.

## 3. Collect

`scripts/vision_collect.py --profile P --label L` reads each split row straight from vLLM with the gateway's
own code (`build_batch`, `read_rows`), at concurrency 8, and records every order's raw letter logprobs and
suffix length, plus `input_tokens`, `shared_len`, `padded`, `unpadded_len`, `image_tokens` and `images_shared`.
Offline uses these to count an arm's tokens as live would: the unpadded prefix once, the arm's reads only.

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
- **Holdout.** Scoring a holdout collect needs `--holdout` and is logged. Fitted arms on it need
  `--fit-on <dev collect>`; the dev collect's profile, layout, orders and env must match, and so must its
  records' stamps apart from the commit (layout and label-table hashes, model, mm kwargs). `--fit-on` is
  refused for `text` and for dev collects.
- **Text calibration** is the profile's file under the collect's `--env` (`PREFIX_BLOCK` picks
  `calibration-<block>.json`). `arm.json` stores absolute paths.
- **Fallbacks.** A fit on fewer than 30 questions uses the text T (listed in `arm.json` and the console).
  PriDe needs at least 30 reads per option count, else that option count is left undebiased.
- **PriDe and orders.** With identity orders only, PriDe mixes the gold-position skew with the letter bias.
  Cyclic orders put each option in every position and separate them.

## 5. Compare and how to read it

`scripts/vision_compare.py --baseline NAME=DIR [NAME=DIR ...] [--ids vision-dev] --out-label L` takes offline
arms (`DIR` holds `scored.jsonl.gz`) and live kit runs (`results.jsonl.gz`). `--baseline` takes one config, the
one every other is paired against; the other configs follow as positional `NAME=DIR` arguments.

- **Rows.** `--ids` names the manifest (default `vision-dev`; `vision-holdout` needs `--holdout`). Live runs
  are cut to its ids; an offline arm must come from that split and score only its ids. Offline arms skip
  unsupported, invalid and no-gold rows, so put an offline arm first as `--baseline` when mixing: everything
  is then cut to its ids. `summary.md` lists the skipped rows per offline arm and the errored rows per live
  run.
- **No full-suite compare.** Compare always cuts live runs to a manifest (default `vision-dev`), so the CLI
  has no full-suite compare; use the kit's `vision score` for full-suite numbers.

- **Index** is the kit's: per benchmark skill = (acc - mean chance) / (1 - mean chance), clipped to [0, 1],
  then a weighted mean with the kit's weights, R-Bench-M 0.5, MMMU-Pro vision 0.25 and 1.0 for the rest. With
  these weights compare reproduces the stored full-suite 73.70.
- **Δ index [95% CI]** is config minus baseline, with a paired group bootstrap (10,000 resamples, groups
  resampled within each benchmark, seed 0). If the interval holds 0, the data do not separate the two.
- **McNemar p (rows)** is the exact two-sided test on rows where exactly one config is right (b: baseline
  only, c: config only). It is row-level and unweighted: it ignores image groups and benchmark weights, so the
  group-bootstrap CI on Δ index is the headline and p is a cross-check. **d** is the discordant share
  (b + c) / N.
- **What dev can detect.** Pooled accuracy has SE(Δacc) ≈ sqrt(d / N): 0.74 points on dev's 1,462 rows at
  d = 8% (CI about ±1.5). Δ index is noisier: each benchmark's Δskill is Δacc / (1 − chance) on ~136 rows,
  then weighted, so SE(Δindex) ≈ 100 · sqrt(Σ w² · d / (n (1 − chance)²)) / Σ w over benchmarks. On dev's
  counts and chances that is 1.24 at d = 8%: a 95% CI of about ±2.4 points and a minimum detectable effect of
  about 3.5 points at 80% power (2.80 SE). It scales with sqrt(d) and ignores clipping and group clustering;
  the bootstrap CI is the measured value.
- **Agreement** is the share of rows with the same top answer. A high-agreement, near-zero Δ config is a
  different config that does the same job.
- **Per-benchmark Δ skill** shows where a change lands. One benchmark moving alone is a hint, not a result.
- **ΔECE, ΔNLL** are calibration. **Tokens** is the mean `input_tokens` of the arm's own reads: an identity
  arm pays for one order, not every collected one; "—" marks an arm scored from an older collect. **Latency**
  is p50 and p80 when attached with `--latency NAME=DIR` (a dir with a latency run's `summary.json`).
- **Refusals:** a manifest cut from another suite file (as in `load_split`); configs that do not cover the
  same ids; an offline arm from another split than `--ids`; a
  live row not in the suite or whose gold is not an option; a latency summary without a power limit at start
  and end, or with a limit that changed mid-run; summaries at different limits. Errored live rows count as
  wrong.
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
| Paired comparison: SE(Δacc) ≈ √(d/N), d = share of rows where configs disagree | standard; McNemar | At d = 8%, dev (1,462) gives pooled accuracy a ±1.5 pt CI, but Δ index (weighted skill, ~136 rows per benchmark) SE ≈ 1.24: CI ±2.4 pt, MDE ≈ 3.5 pt at 80% power; compare reports d so N can be revisited |
| Reused test sets overfit mostly through winner selection | Dwork et al. 2015; Recht et al. 2019 | Fixed dev/holdout; holdout for finalists only, ≤5 logged looks |
| VLM multiple choice is order- and letter-biased; PriDe removes a letter prior estimated on a small sample | Zong et al. 2023; Zheng et al. (PriDe) | Offline arms for orders and a letter prior |
| Temperature scaling calibrates VLMs with few samples | Tu et al. 2024 | Offline `fit-T` and `fit-T-bench` arms, cross-fitted |
| Latency tails need hundreds of samples; drift biases back-to-back runs | general practice | 300 timed rows, warm-up dropped, A–B–A runs, power limit recorded |

## 9. Round 1 results (gemma-4-31b)

Design: [the campaign spec](../superpowers/specs/2026-10-16-vision-campaign-1-design.md). This section reports; the
owner's decision closes it.

- **Rows and date.** Dev split, 1,462 rows, 2026-10-16.
- **Power limit.** 510 W, local, so latency is relative.
- **Scope.** gemma-4-31b only; qwen3.8-27b's round 1 was not run.

### Factorial (E2-E4)

12 cells: budget {280, 560, 1120} x placement {current, imgfirst} x wording {none, worded}. Reference is
`budget=560 placement=current wording=none` (index 77.21). Results:
[`2026-10-16T223858Z-r1-gemma-factorial`](../results/vision-experiments/2026-10-16T223858Z-r1-gemma-factorial/summary.md).

| factor | level | Δ index [95% CI] |
|---|---|---|
| budget | 280 | -3.50 [-5.25, -1.81] |
| budget | 1120 | +1.01 [-0.53, +2.53] |
| placement | imgfirst | -0.06 [-1.03, +0.92] |
| wording | worded | +0.03 [-0.61, +0.66] |

| factors | levels | interaction [95% CI] |
|---|---|---|
| budget x placement | 280 x imgfirst | +0.17 [-1.66, +1.99] |
| budget x placement | 1120 x imgfirst | -0.78 [-2.64, +1.15] |
| budget x wording | 280 x worded | -0.24 [-1.69, +1.21] |
| budget x wording | 1120 x worded | +0.84 [-0.59, +2.29] |
| placement x wording | imgfirst x worded | +0.43 [-0.66, +1.59] |

- **Per benchmark.** At budget 280, CharXiv, InfographicVQA, Mind2Web and RealWorldQA fall with a CI that
  excludes 0. At budget 1120 only RealWorldQA moves (+0.075 skill [+0.018, +0.136]). Placement and wording have
  no benchmark with a CI that excludes 0.
- **Detectability.** The minimum detectable Δ index on dev is about 3.5 points. The CIs are unadjusted for
  multiple comparisons (9 index effects, 44 per-benchmark).

Latency per budget level (510 W; placement and wording change tokens, not timed separately) and mean input tokens:

| budget | p50 ms | p80 ms | mean input tokens (range over the 4 placement/wording cells) |
|---|---|---|---|
| 280 | 237 | 281 | 431-444 |
| 560 | 323 | 377 | 719-733 |
| 1120 | 712 | 766 | 1,295-1,308 |

Wording adds 13-14 tokens at every budget; placement adds none. Cell index, ECE and NLL are in the summary.

### T_image (E1)

Results: [`2026-10-16T223905Z-r1-gemma-t-image`](../results/vision-experiments/2026-10-16T223905Z-r1-gemma-t-image/dev.json).
One image temperature fitted on 1,800 non-suite rows (AI2D 900, A-OKVQA 900; identity orders): T_image 4.106
against the text T 4.263.

| set | rows | ECE text T -> T_image | NLL text T -> T_image | accuracy |
|---|---|---|---|---|
| calibration (non-suite) | 1,800 | 0.0166 -> 0.0125 | 0.2190 -> 0.2186 | n/a |
| dev | 1,462 | 0.0768 -> 0.0825 | 0.6079 -> 0.6165 | 0.8030 -> 0.8030 |

The non-suite set is much easier (calibration ECE 0.017) than dev (0.077), so its temperature may not transfer.
That is an observation, not a decision.

### Orders and PriDe (E5)

Baseline `fitT_id`, dev, 1,462 rows. Results:
[`2026-10-16T223919Z-r1-gemma-orders`](../results/vision-experiments/2026-10-16T223919Z-r1-gemma-orders/summary.md).

| config | index | Δ index [95% CI] | ECE | NLL | mean input tokens |
|---|---|---|---|---|---|
| fitT_id | 77.02 | baseline | 0.0407 | 0.5742 | 719 |
| pride_id | 76.76 | -0.26 [-1.07, +0.54] | 0.0406 | 0.5740 | 719 |
| fitT_cyc | 77.00 | -0.02 [-1.23, +1.21] | 0.0340 | 0.5783 | 966 |
| pride_cyc | 76.93 | -0.09 [-1.30, +1.15] | 0.0362 | 0.5776 | 966 |

Cyclic orders read 966 tokens per row against 719 (+247, about +34%). No arm separates from the baseline.

### Latency probes (E6)

- **Image sharing.** Results:
  [`image-sharing`](../results/archive/gemma-4-31b/2026-10-16T203121Z-image-sharing/summary.md). Gemma shares
  images across rows without warm-up: computed/usage token ratio (medians over 3 reps) is 0.96 / 0.98 / 0.95
  for the `all` / `prefix` / `row` arms at 4 questions and 0.84 / 0.86 / 0.84 at 16.
- **Image resend.** Results:
  [`image-resend`](../results/archive/gemma-4-31b/2026-10-16T203402Z-image-resend/summary.md). uuid-only image
  references were accepted on 300/300 requests with the same answer, at 70 ms (full) vs 59 ms (uuid) per row.
  Building and serializing the rows' JSON costs 0.8 ms and 0.32 MB per request.

### What the owner weighed

- **Budget 560 vs 1120.** 1120 was +1.01 index points [-0.53, +2.53] (CI includes 0) at about 2.2x latency
  (p50 712 vs 323 ms). 280 lost 3.50 points for 237 ms.
- **T_image.** Ship the 4.106 fit from this set, or keep the text T: it improved calibration-set ECE but
  worsened dev ECE and NLL, with accuracy unchanged.
- **uuid-only image reuse.** Building it would have saved about 11 ms per row (70 vs 59 ms) in this probe, at
  the cost of a new gateway path.
- **qwen3.8-27b round 1.** Not run; it would cost GPU time.

### Decision (2026-10-16)

Round 1 gave no convincing reason to change anything, so the owner kept all defaults: image budget 560 (gemma) /
max_pixels 1638400 (qwen3.8), the `header` layout, the text temperature for image rows, and identity orders.
T_image and its calibration-set builder were removed from the code base (they are in git history). uuid-only
image reuse was not built, and qwen3.8-27b's round 1 was not run.

## Caveats

- **Dev is not untouched.** Many configs are compared on it; the holdout is what guards against that.
- **Never train, calibrate or tune on Jev API outputs.** Gold labels only.
- **Text still needs its own check.** Every shipped change still gets a JevBench run.
