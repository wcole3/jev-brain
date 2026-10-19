# Order averaging and answer labels (round 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Offline order-policy arms for text and image, and experiment label sets (lowercase, spaced, digits, symbols,
unused, content) collected through the gateway's own row builder, with screen reports for both models.

**Architecture:** Label sets are an experiment-layout feature: a `labels` key in `prompts/experiments/*.toml`
selects a set; `gateway/labels.py` builds the set and the per-question labels; `prompts.build_rows` uses them only when
the layout's set is not `letters`, so served layouts are untouched. Order policies are pure functions over collected
reads (`scripts/order_policies.py`) shared by a text report and an image report. GPU work is collects only, run
locally with cool-downs.

**Tech Stack:** Python 3.12, uv, pytest, transformers tokenizers (no torch), vLLM 0.30 (collects only), numpy.

**Spec:** `docs/superpowers/specs/2026-10-17-orders-and-labels-design.md`

## Global Constraints

- Never train, calibrate or tune on Jev API outputs; never touch vision holdout rows (`data/splits/vision-holdout.json`).
- Served layouts (`prompts/*.toml`) and their `labels.json` stay byte-identical; built ids for them stay identical.
- Experiment layouts live in `prompts/experiments/`; the gateway never loads them.
- GPU chunks over 10 minutes need the owner's ok. Runs are local at 510 W. Between label sets: ≥ 10 min idle and GPU
  ≤ 50 °C (`nvidia-smi --query-gpu=temperature.gpu`), whichever is later.
- No ship thresholds; reports only, the owner picks.
- Commits local only; never `git push`. Stage explicit paths; never `git add -A`. Caveman Conventional Commits,
  subject ≤ 50 chars, trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Comments ≤ 2 lines; small focused files; code reads like the surrounding code.
- Never `pkill -f`; kill by pgid.
- `uv run pytest -q` and `uv run ruff check .` pass after every task.

## Review Focus

1. A label set on a question with more than 10 options builds the same read ids as on a short one (no merge with
   neighbours) — test in Task 2.
2. Noul questions (`no`/`yes`) under a label set read the set's ids and map back to the right option — test in Task 2.
3. `content` with duplicate, empty, or same-first-token option texts falls back to letters rather than reading a
   shared id — test in Task 2.
4. A policy that needs an order the collect does not hold (n/2 rotation on the identity+reversed image collect)
   refuses with the missing perm named, rather than scoring fewer reads — test in Task 5.
5. Resuming a collect with a different layout file or label set under the same `--label` refuses — test in Task 3.

## Rulings (from the spec)

- **Text index:** no offline kit index exists for text. Text arms report accuracy, ECE, NLL (M3's paired bootstrap)
  and an approximate skill: per `source/family`, (acc − mean 1/n) / (1 − mean 1/n), clipped at 0, unweighted mean.
  Labelled "approx skill"; the kit index comes from a full Index run on finalists only.
- **Text cost:** text records hold no per-read token counts, so text cost is reads per question and share of
  questions paying a second read. Image adds suffix tokens (records have `suffix_len`).

## After this plan (not tasks here)

The owner's picks, then for each pick: live A-B-A latency, one logged vision holdout confirmation, JevBench and a
full Index run; label sets the owner picks get full calib/eval/index-dev collects (spec §2 Confirm).

## Tickets (controller, before Task 1)

Create two DoStuff tickets (`dostuff-tickets` skill) and note their ids in the ledger: "Round 3: option-order
policies (text + image)" and "Round 3: answer label sets (text + image)", type Research, links to the spec.

---

### Task 1: Label sets in layouts and label tables

**Files:**
- Modify: `gateway/layouts.py` (optional keys `labels`, `answer_label`)
- Modify: `gateway/labels.py` (per-set tables)
- Create: `prompts/experiments/labels-letters.toml`, `labels-lower.toml`, `labels-spaced.toml`, `labels-digits.toml`,
  `labels-symbols.toml`, `labels-unused.toml`, `labels-content.toml`
- Test: `tests/unit/test_labels.py`, `tests/unit/test_layouts.py`

**Interfaces:**
- Produces: `Layout.labels: str = "letters"`, `Layout.answer_label: str = "{label}"`;
  `LABEL_SETS = ("letters", "lower", "spaced", "digits", "symbols", "unused", "content")`;
  `Labels` gains `set: str = "letters"`, `fallback: "Labels | None" = None`, `read: list[str] | None = None`
  (the text read after the slot per label; None for `letters` and `unused`);
  `build_labels(tok, layout) -> dict` unchanged for `letters`, and for other sets adds keys `set`,
  `fallback_names`, `fallback_ids`; `labels_from_table(table: dict) -> Labels`;
  `SYMBOLS: list[str]` (32 ASCII punctuation, `'` first, rest shuffled by `random.Random("labels-symbols")`).

Layout files (all copy `prompts/header.toml`'s wording; only these keys differ):

| File | `labels` | `option` | `answer` | `answer_label` |
|---|---|---|---|---|
| labels-letters | letters | `\n({label}) {text}` | `Answer: (` | default |
| labels-lower | lower | `\n({label}) {text}` | `Answer: (` | default |
| labels-spaced | spaced | `\n{label}) {text}` | `Answer:` | `" {label}"` |
| labels-digits | digits | `\n({label}) {text}` | `Answer: (` | default |
| labels-symbols | symbols | `\n{label} {text}` | `Answer:` | `" {label}"` |
| labels-unused | unused | `\n{label} {text}` | `Answer:` | default |
| labels-content | content | `\n{label}{text}` | `Answer:` | `" {label}"` |

- [ ] **Step 1: Write the failing tests**

```python
def test_served_layouts_have_no_new_keys_and_same_hash():
    for name, layout in load_layouts().items():
        assert layout.labels == "letters" and layout.answer_label == "{label}"
        assert layout.sha256 == hashlib.sha256((PROMPTS_DIR / f"{name}.toml").read_bytes()).hexdigest()

def test_unknown_label_set_refused(tmp_path):  # labels = "emoji" -> ValueError naming LABEL_SETS

def test_served_label_tables_byte_identical(gemma_tok, qwen_tok):
    # scripts.build_labels.table_for(tok, layout, settings) for every prompts/ layout serialises (save_labels format)
    # to exactly data/<profile>/<layout>/labels.json

def test_set_sizes_and_fallback(gemma_tok):
    sizes = {"lower": 26, "spaced": 26, "digits": 9, "symbols": 32}
    for name, size in sizes.items():
        lab = labels_from_table(build_labels(gemma_tok, experiment(name)))
        assert len(lab.names) == size and len(lab.fallback.names) >= 249
    assert SYMBOLS[0] == "'" and len(set(SYMBOLS)) == 32

def test_every_label_one_token_in_context(gemma_tok, qwen_tok):
    # for every set except unused/content, every name and every fallback name: encode(answer + read) == slot + [id]

def test_unused_only_with_unused_tokens(gemma_tok, qwen_tok):
    # gemma: 255 ids of <unused0>..<unused254>; qwen: ValueError "no <unusedN> tokens"
```

Use the tokenizers from the local HF cache (`HF_HUB_OFFLINE=1`; fixtures as other tokenizer tests do; skip if absent).

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_labels.py tests/unit/test_layouts.py -q`
Expected: FAIL (no `labels` attribute / no `LABEL_SETS`).

- [ ] **Step 3: Implement**

- `layouts.py`: read optional `labels` (must be in `LABEL_SETS`) and `answer_label` (must contain `{label}`).
  `LABEL_SETS` lives in `layouts.py` (imported by `labels.py`) to avoid a cycle.
- `labels.py`: `build_labels` keeps today's code path for `letters`. For other sets: candidate names
  (lower a..z, spaced A..Z, digits 1..9, `SYMBOLS`, unused `<unused0>..<unused254>` from the vocab), read text
  `answer_label.format(label=name)`, id = the single token after `encode(answer)` in `encode(answer + read)`; a name
  that is not one token there raises `ValueError`. `unused` takes ids from the vocab directly (no text check).
  `content` has no own names: its table is the fallback only. Fallback = today's `label_table` names that pass the
  same in-context check with this layout's slot and `answer_label`, in order.
- Seven layout files per the table.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_labels.py tests/unit/test_layouts.py -q` then `uv run pytest -q`
Expected: PASS, full suite green.

- [ ] **Step 5: Commit**

```bash
git add gateway/layouts.py gateway/labels.py prompts/experiments/labels-*.toml tests/unit/test_labels.py tests/unit/test_layouts.py
git commit -m "feat(labels): experiment label sets"
```

### Task 2: Rows with experiment label sets

**Files:**
- Modify: `gateway/labels.py` (`question_labels`)
- Modify: `gateway/prompts.py` (`Row.label_tag`, set path in `build_rows`)
- Test: `tests/unit/test_prompts_label_sets.py`

**Interfaces:**
- Consumes: Task 1's `Labels` (with `set`, `fallback`, `read`), `Layout.labels`, `Layout.answer_label`.
- Produces: `question_labels(tok, layout, labels, texts: list[str]) -> tuple[list[str], list[int], str]` returning
  shown names, read ids and tag `"set"` or `"fallback"`; raises `RequestError` when even the fallback is too small.
  `Row.label_tag: str = "set"` (always `"set"` on `letters` layouts).

Rules:
- Fixed sets: `len(texts) <= len(labels.names)` → the set's names/ids, tag `set`; else the fallback, tag `fallback`.
- `content`: shown name `"- "` per option; read id = first token after the slot of `encode(answer + " " + text)`.
  Any repeated read id, or an empty text → fallback with shown names `"{letter}) "` and read ids of `" {letter}"`.
- Option ids for non-`letters` sets: each option line encoded on its own (`encode_each`) and concatenated; `unused`
  splices the id between `encode(option_open)` and `encode(option_close.format(text=...))`.
- `letters` layouts take today's path unchanged (`option_ids`, `labels.ids[: len(shown)]`).

- [ ] **Step 1: Write the failing tests**

```python
def test_served_header_rows_unchanged(gemma_tok):
    # build_rows for prompts/header.toml on a 3-question fixture (2, 4 and 12 options): ids and label_ids equal a
    # golden JSON written from the current main code path before this task (tests/fixtures/header_rows_golden.json)

def test_long_list_ids_match_short(gemma_tok):
    # lower set, 12 options vs first 4 of them: row.label_ids[:4] identical; every label id appears in row.ids once
    # right after the option-line opening

def test_noul_reads_set_ids(gemma_tok):
    # digits set, a noul question: label_ids == ids of "1", "2"; perm [1, 0] row reads the same ids in shown order

def test_fallback_past_size(gemma_tok):
    # digits set, 10 options -> tag "fallback", label_ids == fallback ids[:10]

def test_content_first_tokens_and_collisions(gemma_tok):
    # options ["approve", "reject"] -> tag "set", ids = first token of " approve"/" reject"
    # ["New York", "New Jersey"] -> tag "fallback"; ["", "x"] -> tag "fallback"

def test_unused_spliced(gemma_tok):
    # unused set: row.ids contain the <unused0> id once per first option line; label_ids are the vocab ids
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_prompts_label_sets.py -q`
Expected: FAIL. Generate `header_rows_golden.json` with the unmodified code first and commit it with the tests.

- [ ] **Step 3: Implement `question_labels` and the set path in `build_rows`.**

- [ ] **Step 4: Run tests**

Run: `uv run pytest -q`
Expected: PASS, including `test_served_header_rows_unchanged`.

- [ ] **Step 5: Commit**

```bash
git add gateway/labels.py gateway/prompts.py tests/unit/test_prompts_label_sets.py tests/fixtures/header_rows_golden.json
git commit -m "feat(prompts): rows for experiment label sets"
```

### Task 3: Text collect with experiment layouts, samples and orders

**Files:**
- Modify: `scripts/collect.py`
- Create: `scripts/index_dev_2k.py`, `data/splits/index-dev-2k.json`
- Modify: `scripts/splits.py` (`rows_for` accepts `index-dev-2k` and `calib-600`)
- Create: `data/splits/calib-600.json`
- Test: `tests/unit/test_collect.py`, `tests/unit/test_splits.py`

**Interfaces:**
- Consumes: Task 2's `Row.label_tag`; `scripts/vision_collect.add_layout_file(engine, path) -> str` (move it to
  `scripts/experiment_layouts.py` and import it from both collects; behaviour unchanged).
- Produces:
  - `collect.py` options `--layout-file PATH` (replaces `--layouts` for that run), `--orders identity|identity+reversed|all`
    (default `all` = today's `all_orders`), `--label NAME` (output `COLLECT/<profile>/<split>-<label>.jsonl.gz`;
    required with `--layout-file`); split choices gain `index-dev-2k`, `calib-600`.
  - Record key `label_tags: {qid: "set"|"fallback"}` only for non-`letters` sets, in both `collect.py` and
    `vision_collect.py` records; `collect.py`'s stamp gains `labels_sha256` and `layout_file` for experiment layouts.
  - `data/splits/index-dev-2k.json`: `host_compare.make_ids(index_meta(), index-dev ids, 2000)`, meta = `pins()` +
    `{"from": "index-dev", "rule": "every k-th whole linked group, ordered by benchmark and payload length",
    "rows": N, "edition": "0.3"}`.
  - `data/splits/calib-600.json`: 600 calib ids, per family proportional to calib's family counts (largest
    remainder), within a family the lowest `sha256("calib-600:" + id)`; meta = `pins()` + seed `"calib-600"`.

- [ ] **Step 1: Write the failing tests**

```python
def test_layout_file_collect_records_tags_and_stamp(fake_vllm, tmp_path):
    # --layout-file prompts/experiments/labels-digits.toml --orders identity+reversed --label digits on 2 fixture rows:
    # each question has exactly 2 reads (identity, reversed); label_tags present; stamp has labels_sha256, layout_file

def test_resume_refuses_other_layout_file(fake_vllm, tmp_path):
    # collect --label x with labels-digits, then again --label x with labels-lower -> SystemExit naming the stamp keys

def test_vision_collect_records_label_tags(fake_vllm, tmp_path):
    # vision_collect --layout-file labels-digits on a 10-option fixture row -> label_tags {qid: "fallback"}

def test_default_collect_unchanged(fake_vllm, tmp_path):
    # no new flags: same records as before (all_orders, no label_tags key, same stamp keys)

def test_index_dev_2k_subset_and_size():
    # every id in index-dev; whole groups only; 1,900 <= len <= 2,100

def test_calib_600_proportional():
    # 600 ids, all in calib; per-family counts within 1 of 600 * share
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_collect.py tests/unit/test_splits.py -q`
Expected: FAIL.

- [ ] **Step 3: Implement the flags, the move of `add_layout_file`, and the two manifests**

Write the manifests with `uv run python scripts/index_dev_2k.py` (it writes both; needs the Index export already on
disk, CPU only).

- [ ] **Step 4: Run tests**

Run: `uv run pytest -q && uv run ruff check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/collect.py scripts/vision_collect.py scripts/experiment_layouts.py scripts/index_dev_2k.py scripts/splits.py data/splits/index-dev-2k.json data/splits/calib-600.json tests/unit/test_collect.py tests/unit/test_splits.py
git commit -m "feat(collect): experiment layouts, samples, orders"
```

### Task 4: Unused-token embedding check

**Files:**
- Create: `scripts/unused_embeddings.py`
- Test: `tests/unit/test_unused_embeddings.py`

**Interfaces:**
- Produces: `bf16_rows(path: Path, tensor: str, rows: list[int]) -> np.ndarray` (float32, read from the safetensors
  header and byte offsets; bf16 → float32 by `uint16 << 16`); `report(profile) -> dict` with norms (min/median/max)
  of the 255 `<unused0..254>` rows vs 2,000 seeded ordinary rows, and mean pairwise cosine within each group;
  writes `docs/results/archive/<UTC>-r3-unused-embeddings/summary.md` + `summary.json`.

- [ ] **Step 1: Write the failing test**

```python
def test_bf16_rows_roundtrip(tmp_path):
    # write a tiny safetensors file by hand (header JSON + bf16 bytes of a known 4x3 matrix); rows [0, 2] equal the
    # matrix rows to bf16 precision
```

- [ ] **Step 2: Run to verify failure** — `uv run pytest tests/unit/test_unused_embeddings.py -q` → FAIL.
- [ ] **Step 3: Implement.** The embedding tensor name comes from `model.safetensors.index.json` in the gemma
  snapshot (the key ending in `embed_tokens.weight`); weights are read-only from the HF cache.
- [ ] **Step 4: Run** `uv run pytest -q`, then `uv run python scripts/unused_embeddings.py --profile gemma-4-31b`
  → summary written. The verdict line states the numbers only; the set is dropped if the owner agrees the rows are
  degenerate (near-zero norms or mean cosine > 0.9 within the unused group).
- [ ] **Step 5: Commit**

```bash
git add scripts/unused_embeddings.py tests/unit/test_unused_embeddings.py docs/results/archive/*-r3-unused-embeddings
git commit -m "feat(labels): unused-token embedding check"
```

### Task 5: Order policies and the text report

**Files:**
- Create: `scripts/order_policies.py`, `scripts/r3_orders.py`
- Test: `tests/unit/test_order_policies.py`, `tests/unit/test_r3_orders.py`

**Interfaces:**
- Consumes: `scripts.offline` (`gold_index`, `render_question`), `scripts.experiments` (`compare`, `paired`),
  `scripts.fit.golden_min`, `scripts.collect.records`, `scripts.splits.rows_for`, `gateway.calibration.softmax`,
  `gateway.orders.average_back`.
- Produces (in `order_policies.py`):
  - `Policy(name: str, second: str, gate: str, value: float | None, combine: str)`;
    `second` ∈ {"reversed", "half"} (half = rotation by n//2); `gate` ∈ {"never", "always", "top_p", "min_n",
    "aleria", "cyclic"}; `combine` ∈ {"mean-prob", "mean-logprob", "tn-prob"}.
  - `POLICIES: list[Policy]`: identity; always reversed; cyclic:2/3/4 (gate "cyclic", value k);
    top_p τ ∈ {0.5, 0.6, 0.7, 0.8, 0.9}; min_n k ∈ {3, 4, 5, 6, 8}; aleria — each family × the three combine rules
    (identity has one), each gated family with second "reversed" (text) — image adds "half".
  - `select(reads: dict[tuple[int, ...], list[float]], n: int, policy, first_T: float) -> list[tuple[list[float], list[int]]]`;
    raises `ValueError(f"missing perm {perm}")` when a needed perm was not collected.
  - `combine(chosen, rule: str, T: float, tn: tuple[float, float] | None) -> list[float]`
    (mean-logprob: per caller option, mean of logprobs over orders, then softmax at T; tn-prob: T = max(0.05, α + β ln n)).
  - `fit(questions: list[tuple[list, int, int]], rule: str) -> float | tuple[float, float]` (T by golden search on
    log T in [ln 0.05, ln 20]; tn by nested golden search over T(2), T(16) as round 2 R1 did).
  - `cost(chosen) -> int` (reads) and, given suffix lengths, extra suffix tokens.
- Produces (`r3_orders.py`): `uv run python scripts/r3_orders.py --profile P` → for each policy: fit on calib
  (header records of `.cache/collect/P/calib.jsonl.gz`), score index-dev and eval; writes
  `docs/results/archive/<UTC>-r3-orders-text-<profile>/summary.md` + `summary.json` with: accuracy, ECE, NLL and paired
  95% CIs vs identity (`experiments.compare`), approx skill (Rulings), mean reads, share paying a second read, per
  option bucket (`experiments.option_bucket`).

Gates read the first (identity) read at the profile's shipped choice/score/noul T (`data/P/header/calibration.json`).
Aleria: identity + half; if top answers differ and n ≥ 3, add n//4 and 3n//4 rotations (deduplicated).

- [ ] **Step 1: Write the failing tests**

```python
def test_gate_reads_second_only_when_unsure():
    # 3 questions with identity top-p 0.95, 0.6, 0.4; policy top_p 0.7 -> reads 1, 2, 2

def test_min_n():  # n=2 question 1 read, n=5 question 2 reads under min_n 4

def test_aleria_rule():
    # n=4, identity and half agree -> 2 reads; disagree -> 4 reads (0, 1, 2, 3 shifts); n=2 -> 2 reads, never more

def test_missing_perm_named():
    # reads hold identity+reversed only, n=5, policy second "half" -> ValueError containing "missing perm [2, 3, 4, 0, 1]"

def test_mean_logprob_renormalises():  # result sums to 1 and equals softmax(mean logprobs / T) on a hand case

def test_mean_prob_matches_blend():  # combine(..., "mean-prob", T) == gateway.decide.blend(chosen, T)

def test_fit_recovers_temperature():  # synthetic questions drawn at T=3 -> fit within 0.2 of 3

def test_report_on_fixture(tmp_path):
    # r3_orders on a 30-question fixture collect: identity arm's accuracy equals offline.evaluate's for identity
```

- [ ] **Step 2: Run to verify failure** — `uv run pytest tests/unit/test_order_policies.py tests/unit/test_r3_orders.py -q` → FAIL.
- [ ] **Step 3: Implement both files.**
- [ ] **Step 4: Run** `uv run pytest -q && uv run ruff check .` → PASS; then CPU runs for both profiles:
  `uv run python scripts/r3_orders.py --profile gemma-4-31b` and `--profile qwen3.8-27b` → two summaries.
- [ ] **Step 5: Commit**

```bash
git add scripts/order_policies.py scripts/r3_orders.py tests/unit/test_order_policies.py tests/unit/test_r3_orders.py docs/results/archive/*-r3-orders-text-*
git commit -m "feat(orders): order policies, text report"
```

### Task 6: Image order report

**Files:**
- Create: `scripts/vision_orders.py`
- Test: `tests/unit/test_vision_orders.py`

**Interfaces:**
- Consumes: Task 5's `POLICIES`, `select`, `combine`, `fit`, `cost`; `vision_offline.fold`; the arm-dir format
  `vision_offline.py` writes (`scored.jsonl.gz` + `arm.json`) so `vision_compare.py` reads it.
- Produces: `uv run python scripts/vision_orders.py --profile P --collect FILE [--collect FILE2] --out DIR` — merges
  per-row reads from the given collects (same row ids, same stamp except `orders`), scores every image policy with
  the text-fitted parameters from Task 5's `summary.json` (pass `--text-fit PATH`), writes one arm dir per policy
  under DIR plus a 2-fold group cross-fit reference arm per combine rule; then runs `vision_compare.py --baseline
  DIR/identity DIR/*` into `docs/results/vision-experiments/<UTC>-r3-orders-<profile>/`. Each arm's `arm.json`
  records mean reads, share paying, mean extra suffix tokens.

- [ ] **Step 1: Write the failing tests**

```python
def test_merge_collects_unions_reads(tmp_path):  # identity+reversed file + cyclic:4 file -> 5 perms for n=4 rows

def test_merge_refuses_other_stamp(tmp_path):  # different layout_sha256 -> SystemExit

def test_arm_dirs_readable_by_compare(tmp_path):  # vision_compare.load_offline reads every written arm dir

def test_extra_suffix_tokens(tmp_path):  # gated row with suffix_len 90 on the second read -> +90 counted
```

- [ ] **Step 2: Run to verify failure** — `uv run pytest tests/unit/test_vision_orders.py -q` → FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `uv run pytest -q && uv run ruff check .` → PASS. (The real run waits for Task 8's cyclic:4
  collects; run it then on the identity+reversed baseline alone first to check the reversed-only arms.)
- [ ] **Step 5: Commit**

```bash
git add scripts/vision_orders.py tests/unit/test_vision_orders.py
git commit -m "feat(orders): image order report"
```

### Task 7: Label screen report and pipeline check

**Files:**
- Create: `scripts/label_screen.py`
- Test: `tests/unit/test_label_screen.py`

**Interfaces:**
- Consumes: Task 3's collect outputs and `label_tags`; Task 5's `fit`/`combine`; `vision_compare.paired`, `index`,
  `ece`, `nll`; the letters control = existing collects (`.cache/collect/P/{calib,index-dev}.jsonl.gz` header records,
  `.cache/vision-collect/P/baseline/dev.jsonl.gz`).
- Produces:
  - `uv run python scripts/label_screen.py check --profile P` — compares the `letters` experiment collects
    (`calib-600-letters`, `index-dev-2k-letters`, image dev `labels-letters`) with the control on 200 rows of each:
    prints and records the identity top-answer agreement; exits non-zero below 0.98.
  - `uv run python scripts/label_screen.py screen --profile P --set S` — T fitted on the set's calib-600 collect
    (identity, `combine` mean-prob); on index-dev-2k (text) and image dev, paired against letters on the same
    questions: accuracy (text, M3 bootstrap), index (image, `vision_compare.paired`), ECE, NLL, predicted-position
    histogram vs gold, identity/reversed flip rate, fallback share; each on "pure" (tag `set`) and "all" questions.
    Writes `docs/results/archive/<UTC>-r3-labels-<set>-<profile>/summary.md` + `summary.json` (text) and the image
    arm dirs + compare output under `docs/results/vision-experiments/<UTC>-r3-labels-<set>-<profile>/`.

- [ ] **Step 1: Write the failing tests**

```python
def test_check_agreement(tmp_path):  # fixture control vs a copy with 1 of 50 tops changed -> 0.98, exit 0; 2 -> exit 1

def test_pure_subset_excludes_fallback(tmp_path):  # questions tagged fallback absent from "pure", present in "all"

def test_flip_rate_and_histogram(tmp_path):  # hand-made identity/reversed reads -> known flip rate and histogram

def test_pairs_only_shared_questions(tmp_path):  # a question unsupported in the set run is dropped from both arms
```

- [ ] **Step 2: Run to verify failure** — `uv run pytest tests/unit/test_label_screen.py -q` → FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `uv run pytest -q && uv run ruff check .` → PASS.
- [ ] **Step 5: Commit**

```bash
git add scripts/label_screen.py tests/unit/test_label_screen.py
git commit -m "feat(labels): label screen report"
```

### Task 8: GPU runs (controller; each chunk with the owner's ok)

Not a code task. The controller runs each chunk only after the owner's ok, local at 510 W. The runner script lives in
the scratchpad (not committed); between label sets it waits ≥ 10 min and until `nvidia-smi
--query-gpu=temperature.gpu --format=csv,noheader` ≤ 50. Stack up per profile with `make up PROFILE=P`, down after.

- [ ] **Step 1: Image cyclic:4 collects** (~1 h, both models):
  `uv run python scripts/vision_collect.py --profile P --label r3-cyclic4 --layout header --orders cyclic:4`.
  Then run Task 6's report with both collects; commit its results dir.
- [ ] **Step 2: Pipeline check** (~15 min): per profile, collect `labels-letters` on `calib-600`, `index-dev-2k`
  (`--orders identity+reversed --label letters`) and image dev
  (`vision_collect.py --layout-file prompts/experiments/labels-letters.toml --label labels-letters`), then
  `label_screen.py check`. Stop and report if any split is below 0.98.
- [ ] **Step 3: Label screens** (~40 min per set and model): sets lower, spaced, digits, symbols, content
  (+ unused on gemma if Task 4 did not drop it). Per set: the three collects as in Step 2 with that set's file, then
  `label_screen.py screen`; cool down; next set. Order: gemma all sets, then qwen.
- [ ] **Step 4: Commit results** — each results dir, explicit paths:

```bash
git add docs/results/vision-experiments/<dir> docs/results/archive/<dir>
git commit -m "docs(results): r3 <what>"
```

### Task 9: Docs and tickets

**Files:**
- Create: `docs/background/answer-labels.md`
- Modify: `docs/background/vision-experiments.md` (§10 Round 3 orders), `docs/background/prompt-layouts.md`
  (orders note under "Adding option-order averaging"), `docs/background/README.md` (index line),
  `docs/development.md` (one line each for `collect.py --layout-file` and `label_screen.py`)

- [ ] **Step 1:** Write `answer-labels.md`: short answer, the sets and their token checks (spec §2 table), mechanics
  (layout keys, fallback, content), the unused check result, screen results per model with links, caveats. Report
  only; the owner's decision paragraph is added after the pick.
- [ ] **Step 2:** Orders results in `vision-experiments.md` §10 (image) and the text summary in `prompt-layouts.md`,
  with links; the cost columns; no recommendation beyond the numbers.
- [ ] **Step 3:** Ticket progress notes and commit shas on both tickets; status → Verification and
  `request_ticket_complete` once the owner has the tables.
- [ ] **Step 4: Commit**

```bash
git add docs/background/answer-labels.md docs/background/vision-experiments.md docs/background/prompt-layouts.md docs/background/README.md docs/development.md
git commit -m "docs: round 3 orders and answer labels"
```

### Task 8b: Shuffled-letter label sets (owner addition, 2026-10-18)

Owner asked for shuffled letters after the main screen: keep the letter tokens, break the alphabetical sequence.

**Files:**
- Modify: `gateway/layouts.py` (`LABEL_SETS` gains `shuffled`, `shuffled-q`), `gateway/labels.py`
- Create: `prompts/experiments/labels-shuffled.toml`, `prompts/experiments/labels-shuffled-q.toml` (both copy
  `labels-letters.toml`: option `\n({label}) {text}`, answer `Answer: (`; only `labels` differs)
- Test: `tests/unit/test_labels.py`, `tests/unit/test_prompts_label_sets.py`

**Rules:**
- `shuffled`: names = A..Z in the fixed order `random.Random("labels-shuffled").shuffle(list(A..Z))`; ids = the
  in-context single tokens; size 26, then today's letters as fallback (tag `fallback`).
- `shuffled-q`: per question, A..Z shuffled by `random.Random("labels-shuffled-q:" + "\x1f".join(sorted(texts)))`;
  the first n go to shown positions 0..n-1. Seeding on the sorted option texts gives the same letter-to-position
  mapping for identity and reversed reads of one question. Size 26, then fallback.
- Neither changes served layouts or the `letters` path.

- [ ] Step 1: failing tests — `shuffled` names are a fixed permutation of A..Z, not alphabetical, stable across
  calls; `shuffled-q` gives the same names for two calls with the same texts in different order, different names for
  different texts (on a fixed fixture), every name one token in context; 27 options → fallback.
- [ ] Step 2: implement; Step 3: `uv run pytest -q`, `uv run ruff check .`; Step 4: commit
  `feat(labels): shuffled letter sets`.
- [ ] Step 5 (GPU, after the main Task 8 run): screens for `shuffled` and `shuffled-q` on both models (same three
  collects + `label_screen.py screen`, cool-down between sets).

### Task 9 change (owner, 2026-10-19): option-ordering background doc

After all round-3 results are in, Task 9 also creates `docs/background/option-ordering.md`: one home for option
order (how `gateway/orders.py` builds and averages orders, position and letter bias, PriDe, M3's text arms, round 1's
image E5 arms, round 3's text and image policies with their cost columns, rulings R6/R7). Order material now in other
background docs moves there and leaves a one-line link: candidates found by grep are `prompt-layouts.md` (§2 research
on option order, §3 "Adding option-order averaging"), `calibration.md` (§2-§3 and §6 order notes, step 4 of §7),
`decision-readout.md`, `noul-bias.md` (order vs yes/no lean), `vision-experiments.md` (§4 order arms, §9 E5) and
`images.md` (§5 order notes); hits about bf16 "flips" in `determinism.md` stay. Round-3 orders results then go in
the new doc instead of `vision-experiments.md` §10 / `prompt-layouts.md`; `docs/background/README.md` gains its line.
