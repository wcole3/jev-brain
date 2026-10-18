# Order averaging and answer labels, round 3 (text and image)

Date: 2026-10-17. Status: draft for owner review. Models: gemma-4-31b and qwen3.8-27b.
Background: [vision-research.md](../../appendix/vision-research.md) (round 2 research and CPU tests),
[m3-recommendations.md](../../results/archive/m3-recommendations.md) (M3 order arms, 2026-10-03),
[vision-experiments.md](../../background/vision-experiments.md) (DS-034 harness), round 2 CPU results
(`docs/results/vision-experiments/2026-10-17T013235Z-r2-cpu-*`).

## Goal

Two experiment tracks, on text and image decisions, for both models:

1. **Orders.** Find an option-order rule worth its cost. M3 showed gemma gains 0.5-1.5 accuracy points from a second
   order on text, and the owner rejected it at 2× reads; this round tests cheaper rules (gated, selective, adaptive)
   and how reads are combined.
2. **Labels.** See what happens when the answer token is not a letter: lowercase, space-prefixed letters, digits,
   ASCII symbols (a single quote among them), Gemma's unused tokens, and each option's own first token.

The harness reports; the owner picks. Nothing ships without the owner's pick, a live A-B-A latency run, one logged
vision holdout confirmation, a JevBench check and a full Index run (as M3 did).

Done when:

- every order arm below has text (index-dev, eval) and image (dev) tables for both models;
- every label set below has a screen table for both models (Gemma only for `unused`);
- the owner has picked, or kept the defaults, for each track.

## Constraints

- Never train, calibrate or tune on Jev API outputs; never use vision holdout rows except the one logged confirmation.
- Served layouts (`prompts/*.toml`) and their label tables stay byte-identical; experiments use
  `prompts/experiments/`.
- GPU chunks over 10 minutes need the owner's ok. Runs are local at the owner's power limit (510 W). Between label
  sets the box cools: at least 10 minutes idle and the GPU at or below 50 °C (`nvidia-smi`), whichever is later.
- No thinking, no image-budget changes, no multi-token option scoring.
- Commits stay local; the owner pushes.

## 1. Orders track

### Data

- **Text:** the existing header collects from M3, `.cache/collect/{profile}/{calib,eval,index-dev}.jsonl.gz` (layout
  hash `567cc639`, current model revisions). Each question already holds identity, reversed and cyclic:2/3/4 reads, so
  the text arms need no GPU.
- **Image:** the existing DS-034 dev collects (identity + reversed), plus one new dev collect per model with
  `--orders cyclic:4` (shifts 0, n/4, n/2, 3n/4).

### Arms

"Second order" is the reversed order on text; on image both reversed and the n/2 rotation are tried.

| Family | Rule |
|---|---|
| Baselines | identity; identity+reversed; cyclic:2, cyclic:3, cyclic:4 (M3's arms, re-scored) |
| Gated second read | identity first; add the second order only when the first read's top probability < τ, τ ∈ {0.5, 0.6, 0.7, 0.8, 0.9} |
| Selective by option count | add the second order only when n ≥ k, k ∈ {3, 4, 5, 6, 8} |
| Aleria adaptive | identity + rotation by n/2; when their top answers differ and n ≥ 3, add n/4 and 3n/4 |

Each family is scored under three combination rules:

- **mean-prob:** softmax each order at T, average probabilities (today's `blend`);
- **mean-logprob:** average the orders' letter logprobs per option, then softmax at T (renormalized);
- **T(n)-prob:** as mean-prob, with T = α + β·ln n fitted per model on text calib (round 2 R1).

### Calibration

- Each arm's final T (or α, β) is fitted on text calib with that arm, as M3 did.
- Gates always use the shipped T on the first read, so a gate never depends on the arm's own fit.
- Image arms use the text-fitted parameters. A 2-fold group cross-fit on image dev is reported as a reference only.

### Metrics

- **Text:** accuracy and ECE with M3's paired bootstrap on index-dev and eval; Decision Index skill on index-dev.
- **Image:** dev index with `vision_compare` (paired group bootstrap, 10k, seed 0), ECE, NLL.
- **Cost, every arm:** mean reads per question, extra suffix tokens per question, share of questions that pay a
  second read.
- No ship thresholds; the owner picks from the tables.

## 2. Labels track

### Label sets

Each set is an experiment layout `prompts/experiments/labels-<set>.toml` with the header layout's wording except the
option line, the answer slot and the new `labels` key.

| Set | Option line | Answer slot | Token read | Size, then fallback |
|---|---|---|---|---|
| `letters` (control) | `(A) text` | `Answer: (` | `A` | 255, today's table |
| `lower` | `(a) text` | `Answer: (` | `a` | 26, then today's letters |
| `spaced` | `A) text` | `Answer:` | ` A` | 26, then today's letters |
| `digits` | `(1) text` | `Answer: (` | `1` | 9, then today's letters |
| `symbols` | `' text` | `Answer:` | ` '` | 32 ASCII symbols, fixed seeded order with `'` first, then today's letters |
| `unused` (gemma) | `<unused0> text` | `Answer:` | `<unused0>` | as many as needed, only if the embedding check passes |
| `content` | `- text` | `Answer:` | first token of ` text` | per question; today's letters when two options share a first token |

Checked on both tokenizers (2026-10-17): lowercase and digits are single tokens after `(`; space-prefixed capitals and
all 32 ASCII symbols are single tokens after `Answer:`; most symbols merge with `(` (only `]` and `}` stay single), so
`symbols` uses the spaced slot. Gemma has 6,233 `<unusedN>` tokens; qwen3.8's tokenizer has none.

A question whose option count exceeds the set's size, or a `content` question with a shared first token, is rendered
with today's letters and tagged `fallback`. Results are reported on the pure subset (no fallback) and on all
questions.

### Mechanics

- `Layout` gains an optional `labels` key (default `letters`; served layouts omit it, so their hashes do not change).
- `gateway/labels.py` builds a table per set. The in-context single-token check covers every label a question can
  use, not only the first 10.
- `content`: `prompts.build_rows` computes each question's read ids from its option texts in context; the label table
  is not used. Experiment layouts only.
- `scripts/collect.py --layout-file PATH`, as `vision_collect.py` has, plus a seeded row sample (`--sample N`).
- **`unused` embedding check (CPU):** norms and pairwise cosine of the `<unusedN>` embedding rows (read from the
  safetensors with numpy) against ordinary tokens. If the rows are near zero or near identical, the set is dropped and
  the finding reported.

### Screen collects

Per model and set, identity + reversed reads:

- text calib sample, 600 rows (seeded, stratified like `calib.json`), to fit T;
- text `index-dev-2k`: a new manifest `data/splits/index-dev-2k.json`, 2,000 rows of the current index-dev (edition
  0.3) by `compare-2k`'s rule (every k-th whole linked group, ordered by benchmark and payload length). The old
  `compare-2k` was cut from edition 0.2.1 and only 111 of its rows are in today's index-dev;
- image dev (1,462 rows).

A pipeline check runs first: the `letters` layout through the experiment path on 200 rows of each split must match
the existing collects (same top answer on ≥ 98% of questions).

### Screen metrics

Against `letters` on the same rows: accuracy and index (paired bootstrap), ECE and NLL (T refit on the calib
sample), predicted-label histogram vs gold (token bias), reversed-order flip rate (position bias), fallback share.

### Confirm

Sets the owner picks after the screen get full calib, eval and index-dev collects and the same tables as the orders
track.

## 3. Work

### Code (no GPU)

1. `labels` key, per-set label builder, full in-context check, `prompts/experiments/labels-*.toml`.
2. `content` readout path in `build_rows` (experiment layouts only).
3. `collect.py --layout-file` and `--sample`; the `index-dev-2k` manifest.
4. Offline order arms for text and image: gated, selective, Aleria, the three combination rules; reusing
   `offline.py`, `m3.py`, `vision_offline.py`, `vision_compare.py`.
5. The `unused` embedding check.

### GPU (local, 510 W, each chunk with the owner's ok)

| Item | Estimate |
|---|---|
| Image dev `cyclic:4` collect, 2 models | ~1 h |
| Pipeline check, `letters` via the experiment path, 2 models | ~15 min |
| Label screens: 6 sets on gemma, 5 on qwen, ~40 min each | ~7.5 h plus cool-downs |

### Outputs

- Results: `docs/results/vision-experiments/<UTC>-r3-*` (image) and `docs/results/archive/<UTC>-r3-*` (text).
- Docs: `docs/background/answer-labels.md` (sets, mechanics, results); orders results in `vision-experiments.md` §10
  and `prompt-layouts.md`.
- Tickets: one DoStuff ticket per track.

## 4. Testing

- Every label set: each label a question can use is one token in context; fallback starts past the set's size.
- `content`: right read ids on hand-made options; fallback on a shared first token.
- Served layouts: label tables and built ids byte-identical to today's files.
- `collect.py --layout-file`: fake-vLLM tests of record shape, stamp and resume.
- Offline arms: a gated arm reads a second order only on gated questions; Aleria's rule on hand-made reads;
  mean-logprob renormalizes; reads-per-question counts.

## Out of scope

- Thinking, image budget, tiling, multi-token option likelihood.
- Changing a served layout, label table or `OPTION_ORDERS` before the owner picks.
