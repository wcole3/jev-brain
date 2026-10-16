# Vision experiments harness design (DS-034)

Date: 2026-10-16. Status: approved in brainstorming, pending spec review.
Ticket: DS-034. Follow-ups that use it: DS-035 (prompt and layout), DS-036 (image budget and calibration),
DS-037 (latency). Background: [images.md](../../background/images.md),
[calibration.md](../../background/calibration.md), the text experiment tools (`scripts/collect.py`,
`scripts/offline.py`, `scripts/experiments.py`).

## Goal

Iterate on image-decision prompts and logic for accuracy and latency without overfitting the public vision
suite, which is half the board score. A config is collected once on a dev split and re-scored offline where
possible. Configs are compared with paired statistics, and the owner picks from the trade-off.

Done when:

- `data/splits/vision-dev.json`, `vision-holdout.json` and `vision-latency.json` are committed;
- gemma-4-31b and qwen3.8-27b each have a dev baseline (collect, four offline arms, latency) in one
  frontier table per model;
- a new config takes one collect command and one compare command;
- holdout rows are unreachable without `--holdout`, and every use is logged.

## Research behind the choices (2026-10-16)

| Finding | Source | Effect on the design |
|---|---|---|
| IRT anchor subsets (tinyBenchmarks, metabench) estimate model scores within ~2% but are fitted on model-to-model variation | Polo et al. 2024; Kipnis et al. 2024 | Not used: unproven for prompt-vs-prompt; stratified random instead |
| Paired comparison: SE(Δacc) ≈ √(d/N), d = share of rows where configs disagree | standard; McNemar | Dev ≈1,500 detects ≈+2 pt at d ≤ 8%; compare reports d so N can be revisited |
| Reused test sets overfit mostly through winner selection | Dwork et al. 2015; Recht et al. 2019 | Fixed dev/holdout; holdout for finalists only, ≤5 logged looks |
| VLM multiple choice is order- and letter-biased; PriDe removes a letter prior estimated on a small sample | Zong et al. 2023; Zheng et al. (PriDe) | Offline arms for orders and a letter prior |
| Temperature scaling calibrates VLMs with few samples | Tu et al. 2024 | Offline `fit-T` and `fit-T-bench` arms, cross-fitted |
| Latency tails need hundreds of samples; drift biases back-to-back runs | general practice | 300 timed rows, warm-up dropped, A–B–A runs, power limit recorded |

Raw research notes: `.firecrawl/ds-034/`, `.firecrawl/ds-034-vlm/` (git-ignored).

## Decisions

| Topic | Decision |
|---|---|
| Scope | The public vision suite only; text keeps its splits, and every shipped change still gets a JevBench check |
| What wins | No automatic rule: the harness reports skill, ECE and latency per config with confidence intervals; the owner picks |
| Splits | Dev ≈1,500, holdout ≈2,400, reserve ≈8,300 untouched until a submission run |
| Approach | Collect raw letter logprobs once per prompt-changing config, re-score offline for calibration, prior and orders; latency through the gateway |

## 1. Splits (`scripts/vision_splits.py`)

- Rows that share any image file are one group (union over shared paths); a group is in exactly one split.
- Stratified per benchmark with near-equal allocation, since the board weights benchmarks equally:
  dev = min(136, 40% of the benchmark), holdout = min(218, 40% of the benchmark). Assignment is by a hash of
  the group key and the seed, so it is deterministic.
- `vision-latency.json`: 320 rows drawn from dev, stratified and seeded; the first 20 are warm-up.
- Each manifest has `meta` (suite `vision-rows.jsonl` SHA-256, seed, grouping rule, per-benchmark counts)
  and `ids`. A tool refuses a manifest whose suite hash differs from the suite on disk.
- Holdout guard: tools that read `vision-holdout.json` need `--holdout`. Each use appends date, tool, label
  and commit to `docs/results/vision-experiments/holdout-log.md`, with a warning from the 6th entry on.

## 2. Collect (`scripts/vision_collect.py`)

- A config is a profile, a label, a layout (`prompts/*.toml`), the option orders to record (default
  `identity+reversed`, optional `cyclic:N`) and env overrides (`--env KEY=VALUE`, for example
  `MM_PROCESSOR_KWARGS`). The run folder records the whole config; there are no config files.
- For each split row it builds the batch with the gateway's code (`build_batch`, `image_context`) and reads it
  with `Readout.image_logprobs`, directly against vLLM, at concurrency 8.
- Per row it records run_id, benchmark, group, the expected answer, the option names, every order's perm with
  its raw letter logprobs, and `input_tokens`. Output: `.cache/vision-collect/<profile>/<label>/<split>.jsonl.gz`.
  It resumes and skips a truncated tail.
- Stamp: layout hash, label-table hash, model revision, mm kwargs and repo commit.
- Startup self-check: one probe image through `/inference/v1/generate` with `return_token_ids`. The run is
  refused unless the expanded length equals `vision.expanded` for the config's kwargs, which catches a vLLM
  started with other settings.
- A layout without a label table is refused (build it with `scripts/build_labels.py`).
- Cost: about 12 min per config per model on a 600 W box (1,500 rows × 2 orders).

## 3. Offline arms, compare and latency

**Offline** (`scripts/vision_offline.py`, CPU only): a collect file and an arm give scored rows (probabilities,
top answer, correct, NLL). An arm is a subset of the collected orders plus one calibration method:

| Method | What it does |
|---|---|
| `text` | The profile's text T and b, which is what ships today |
| `fit-T` | One image temperature |
| `fit-T-bench` | One temperature per benchmark |
| `pride` | A per-letter prior subtracted before T |

Every fitted method is 2-fold cross-fitted by group within dev: fit on one half, score the other, swap. Nothing
is ever fitted on holdout rows.

**Compare** (`scripts/vision_compare.py --baseline X C1 C2 …`): inputs are offline arms or live kit runs (which
carry probabilities). All configs must cover the same ids.

- Skill per benchmark is (acc − chance) / (1 − chance), with chance the mean of 1/options, matching the kit.
  The aggregate is the mean over benchmarks.
- Per config against the baseline: Δskill with a paired-bootstrap 95% CI (10,000 resamples, groups resampled
  within each benchmark), McNemar exact p, d, ΔECE, ΔNLL, mean input tokens, and latency when attached.
- A per-benchmark Δ table, and a frontier table (skill, ECE, latency per config).
- Output: `docs/results/vision-experiments/<UTC>-<label>/summary.md` and `summary.json`.

**Latency**: `scripts/vision_run.py --ids data/splits/vision-latency.json --workers 1` (the `--ids` option is
new). It drops 20 warm-up rows and times 300. Configs that need a vLLM restart run A–B–A, with the baseline
before and after. Each run records the power limit and GPU telemetry; compare refuses to mix power limits.

## 4. Where it runs

- Collect and dev live runs: locally at the owner's power limit (accuracy is unaffected; latency is relative).
- Final latency and holdout confirmations: rented 600 W boxes, through the existing remote queue.

## 5. Testing

- Splits: no group straddles splits; per-benchmark counts follow the rule; the same seed gives the same cut;
  holdout refused without the flag; stale suite hash refused.
- Collect: fake-vLLM tests of record shape, resume, stamp, self-check refusal and missing-labels refusal.
- Offline: cross-fit never scores a row with parameters fitted on it; the `text` arm reproduces the gateway's
  probabilities from the same logprobs.
- Compare: skill and chance equal the kit's on the stored full-suite results; bootstrap and McNemar checked on
  hand-made data; mismatched ids and mixed power limits refused.

## 6. Docs

- `docs/background/vision-experiments.md`: splits, holdout rules, statistics, how to read the compare table,
  cost per run.
- `docs/development.md`: a short "run a vision experiment" section.

## Out of scope

- The experiments themselves (DS-035, DS-036, DS-037).
- Encoder-side token pruning (needs model-code patches), crop or zoom second passes, and a generated
  "thinking" fallback for reasoning-heavy benchmarks.
- Text Index experiments.
