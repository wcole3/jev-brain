# Option ordering & prompt layout for a Jev-style decision server — research notes

Date: 2026-09-28. Raw scraped material saved under
`/home/welb/devspace/jev-onto/.firecrawl/prompt-research/`.

---

## Q1. Option ordering / position bias

### Academic literature

**Zheng, Zhou, Meng, Zhou, Huang (2023), "Large Language Models Are Not Robust Multiple
Choice Selectors."** arXiv:2309.03882 (ICLR 2024).
https://arxiv.org/abs/2309.03882, full text https://arxiv.org/html/2309.03882v4
(saved: `zheng-fulltext.md`)

- 20 LLMs, 3 MCQ benchmarks (MMLU, ARC, ...), 2–5 options. Defines **selection bias**: the
  behavioral tendency to pick specific option IDs (e.g. "A") regardless of content, measured
  by **RStd** (standard deviation of per-letter recall) alongside accuracy.
- Two candidate causes tested via ablation: **token bias** (model's prior over ID tokens
  A/B/C/D independent of position) vs. **position bias** (preference for first/last position).
  Key finding, *contrary to Pezeshkpour & Hruschka and Wang et al.*: selection bias is driven
  **primarily by token bias, not position bias**. Evidence: removing option IDs and having the
  model select option content directly collapses RStd sharply (gpt-3.5-turbo, 0-shot: MMLU RStd
  5.5→1.0, ARC RStd 3.3→0.6), while merely shuffling the ID↔position mapping barely changes RStd
  (MMLU 5.5→5.1, ARC 3.3→3.7) even though it also perturbs prompt naturalness. Swapping the ID
  symbol set (a/b/c/d, 1/2/3/4, (A)/(B)/(C)/(D)) does not reduce RStd either.
- Simple prompting mitigations (explicit "avoid position bias" instruction, Chain-of-Thought)
  do **not** meaningfully reduce RStd (Table 2: Default RStd 5.5/3.3 → Debiasing-Instruct
  6.1/3.9, CoT 4.5/3.4 — no consistent improvement).
- Proposes **PriDe**: label-free, inference-time debiasing. Estimates the model's per-ID prior
  by permuting option content on a small sample (e.g. 5%) of items, then subtracts that prior
  from the full set's predictions. Cheap (near-zero extra compute vs. full permutation
  averaging) and transfers across domains/tasks. This is the state-of-the-art cheap alternative
  to full permutation averaging for a frozen model.
- **Relevance to us**: because bias is mostly a token/ID prior rather than positional, a
  fixed-position "always safest slot" heuristic doesn't fully fix it — permutation averaging
  (or PriDe-style prior subtraction) is needed regardless of *where* the correct answer sits.

**Pezeshkpour & Hruschka (2023), "Large Language Models Sensitivity to The Order of Options in
Multiple-Choice Questions."** arXiv:2308.11483.
https://arxiv.org/abs/2308.11483, full text https://arxiv.org/html/2308.11483v1
(saved: `pezeshkpour-fulltext.md`)

- Zero-shot: performance gap of **13%–75%** across benchmarks depending purely on option
  order (oracle best vs. worst ordering). Few-shot: gap persists, generally shrinks as few-shot
  accuracy rises but does not vanish, and does not reliably shrink from adding more
  demonstrations.
- Even a very strong model (GPT-4) at >90% accuracy still shows a sensitivity gap of **13.1%**.
- >60% of "sensitive" instances (samples where reordering options flips the answer) found in
  GPT-4 are also sensitive in InstructGPT (cross-model transfer of hard instances).
  Self-verification test: asking the model "could more than one choice be correct?" gets **>94%
  "yes"** on sensitive instances — order-sensitivity correlates with genuine model uncertainty.
- **Hits@1** (gold answer ranked first by the model's own ordering-sorted probabilities) tracks
  overall task accuracy closely; **Hits@2/Hits@3** capture **>95% / 100%** of correct
  predictions — i.e., when the model is right, the right answer is almost always in its own
  top-2/3, useful for justifying "top-two runoff" style mitigations (see jobe below).
  Proposes ordering-based mitigations that outperform naive majority-vote bootstrapping;
  amplifying/mitigating bias patterns range 20–72% / 0.9–38% sensitivity-gap coverage.

**Robinson & Rytting (Wingate), "Leveraging Large Language Models for Multiple Choice Question
Answering."** arXiv:2210.12353 (ICLR 2023).
https://arxiv.org/abs/2210.12353 (saved: `robinson-abs.md`)

- Introduces **multiple choice symbol binding (MCSB)**: a model's ability to correctly
  associate an answer letter/symbol with the option it labels when question + all options are
  presented jointly and the model outputs only the symbol (exactly our "Answer: (" readout
  design), vs. the older cloze approach (score each option's continuation likelihood
  independently, no joint comparison).
  Symbol-based reading lets the model explicitly compare options, is cheaper (no per-option
  forward pass), and is less sensitive to tokenization/length artifacts of the option text
  itself. MCSB ability varies a lot by model; models with high MCSB ability do much better with
  the natural (letter) approach than the cloze approach, closing most of the gap to
  cloze/fine-tuned SOTA — meaning our chosen "letter-logit" design is validated as strong
  *if* the chosen model has decent MCSB (worth spot-checking Qwen3.8/Qwen3.6/Gemma-4 on this).

**Zhao, Wallace, Feng, Klein, Singh (2021), "Calibrate Before Use: Improving Few-Shot
Performance of Language Models."** arXiv:2102.09690 (ICML 2021).
https://arxiv.org/abs/2102.09690 (saved: `zhao-abs.md`)

- GPT-3 few-shot accuracy is unstable and biased toward answers that are common in pretraining
  or that sit near the end of the prompt (recency effect over few-shot exemplars, not directly
  option order, but same family of bias).
- **Contextual calibration**: estimate the model's bias per answer by scoring a content-free
  input (e.g. "N/A") with the same prompt template, then fit calibration parameters so the
  content-free input's prediction is uniform across answers; apply that correction to real
  inputs.
- Improves average accuracy **up to 30.0 percentage points absolute** and reduces prompt-choice
  variance. This is the "prior calibration" family of mitigation, distinct from and
  combinable with permutation averaging / PriDe — it doesn't require multiple forward passes
  per real question, only one extra "content-free" calibration call (or an offline-fit
  correction), so it's cheap to add as a per-model, per-prompt-template profile.

### 2024–2026 follow-ups on debiasing / LLM-as-judge position bias

- **"A Systematic Study of Position Bias in LLM-as-a-Judge"** (aka "Judging the Judges"),
  arXiv:2406.07791 (also published IJCNLP 2025). https://arxiv.org/html/2406.07791v9
  (saved: `judge-position-bias.md`)
  - 15 LLM judges, MTBench + DevBench, 22 tasks, ~150,000 evaluation instances (pairwise +
    listwise). Defines **Repetition Stability** (is the judgment reproducible under repeated,
    identical queries — a prerequisite check before trusting bias measurements), **Position
    Consistency** (does the judge pick the same winner after swapping position), and
    **Preference Fairness** (primacy vs. recency direction/magnitude).
  - Position bias is **not random noise** — it's systematic per judge/task (confirmed via high
    repetition stability). It varies a lot by judge and by task family; direction
    (primacy/recency) even flips for the *same* model across datasets (e.g. GPT-4:
    recency-preferred on MTBench, primacy-preferred on DevBench). Bias is only weakly related
    to prompt/response length but **strongly related to the quality gap** between the two
    options being compared — bigger gap → higher position consistency (bias matters most on
    close calls).
  - Directly analogous to our option-order problem: expect order sensitivity to concentrate on
    "hard"/ambiguous questions where the model's true confidence is low — matches Jev's own
    finding (jev-behavior-study) that self-reported disagreement/uncertainty predicts flip risk.

- **"Mitigating Selection Bias in Large Language Models via Permutation-Aware GRPO"**,
  arXiv:2603.21016 (2026). https://arxiv.org/html/2603.21016v1 (saved:
  `permutation-debias-2026.md`)
  - A training-time (RL/GRPO) fix that samples multiple option permutations per question and
    rewards content-consistent, permutation-consistent answers. Confirms the field is still
    actively working the problem in 2026 but this is a **fine-tuning** approach, not applicable
    to our frozen stock-instruct-model constraint — cite as evidence the problem persists into
    2026 for frontier-scale models, but not as a deployable mitigation for us.

- Also surfaced: "General Permutation Debiasing for Large Language Models" (ACL Findings 2024)
  and "Embracing Positional Bias in Multiple-Choice Question Answering" (AAAI) — both continue
  the permutation-averaging / PriDe-style lineage; not fetched in full text given time budget,
  but titles/abstracts corroborate that permutation-based correction remains the dominant
  practical mitigation family through 2024–2026.

### Jev-ecosystem evidence (verified against source repos)

**jev-behavior-study** — https://github.com/RINNECODER/jev-behavior-study
(saved: `jev-behavior-study-readme.md`)
- Confirms the headline number precisely: 6 arithmetic problems × 24 option orders × 3
  repetitions = 432 calls, correct-position counterbalanced. **Accuracy by correct-answer
  position: First 88.0% (95/108), Second 62.0% (67/108), Third 59.3% (64/108), Fourth 57.4%
  (62/108).** Explicit takeaway: "choice order is an evaluation variable, not harmless
  formatting... putting the answer first is not a reliability guarantee" (small N: 6 problems,
  option IDs not independently counterbalanced from position).
- Separately, a "facts in the middle" long-context test on Jev itself: dispersed conflicting
  records, correct answer accuracy **6/6 at start, 6/6 at end, but 1/6 (512 records) / 0/6
  (1,024 records) in the middle** — Jev itself shows classic lost-in-the-middle degradation at
  scale (2,182 → 14,726 input tokens).

**archerhume.com, "Jev's architecture unmasked"** —
https://archerhume.com/posts/jevs-architecture-unmasked/ (saved:
`jevs-architecture-unmasked.md`)
- Reverse-engineering essay. Strong direct evidence of **listwise option processing** (not
  independent per-option scoring): reversing options shifted a technical-support classification
  probability from **~0.84–0.89 to ~0.93–0.96** even though per-option text was unchanged
  ("option_order" probe, https://archerhume.com/research/jev/evidence.json). A "reference card"
  probe (moving one option across positions, with a value-switch control) found the option
  **last** position gave 6/6 (48/48 pooled) correct with tight, near-certain probabilities,
  while **first or middle** position gave probabilities "scattered widely around 0.5" despite
  the model's final decision always technically having access to the needed information — i.e.
  probability calibration, not just the argmax, is order-sensitive. Changing only one *other*
  option's value changed which *earlier* option won, which the author argues rules out a
  design that scores each option independently and only normalizes at the end — it argues for
  a shared, listwise readout (echoing the "FIRST" listwise-ranking mechanism,
  arXiv:2406.15657, cited in the piece) where all options attend to each other before the
  decision token.
- Practical implication for us: because probabilities (not just argmax) shift with order, a
  downstream threshold-based policy (e.g. "act only if p≥0.9") can flip behavior purely from
  reordering — this is a calibration risk, independent of raw accuracy.

**reflex** — https://github.com/kshetrajna12/reflex, `docs/results/order-averaging.md`
(saved: `reflex-order-averaging.md`)
- "Option-order averaging: the cheapest calibration gain we found." Ask each question in **2
  distinct option orders** (also reversing yes/no), average the two probability distributions —
  same forward-pass cost class, no training.
- 4B model, frozen, default prompt, public **hard-tier** items: accuracy **0.658 → 0.685**
  (76/111), **ECE 0.086 → 0.081**, "probability fidelity" 0.708→0.740, calibration axis
  76.8→78.9. Hard-item p50 latency basically unchanged (0.18s→0.19s; cost is one extra branch
  in one shared-prefix forward pass, not a second document prefill).
- 27B model (Qwen3.8-27B): hard 0.703→0.766 (85/111), ECE 0.088→0.061, beats the Jev-official
  reference point (0.730) on this dev set (caveat: dev set was used throughout development, and
  Jev's own ECE, 0.031, is still about half theirs).
- On **external, never-trained-on sets**: accuracy roughly flat (0.808→0.810 mean over 4 sets)
  and calibration flat within noise — the calibration win is clearest on their own hard/public
  items, weaker/noisier generalization claim.
- What did **not** help: 4 orders instead of 2 (marginal accuracy gain, worse ECE on buggy
  code, not rerun); wording ensembles (worse on both public and external sets, esp. because
  Yes/No-token readouts carry a "say yes" prior that pulls averages the wrong way).
- Introduces a **disagreement signal** (mean total-variation distance between order/wording
  readings) that strongly predicts whether the *averaged* answer is right: TVD<0.05 → 90.8%
  accuracy; TVD 0.05–0.15 → 70.2%; TVD 0.15–0.30 → 69.1%; TVD>0.30 → 25.0% (n=8, noisy). Used
  to gate selective re-answering with a thinking pass only on high-disagreement items.

**jobe** — https://github.com/MantisShrimpdev/jobe (saved: `jobe-github.md`)
- Ships `jobe.orders`: scores under several option orders, averages, and **reports flip_rate**
  as a first-class diagnostic ("it pays only in proportion to the fragility it fixes").
- **E2 control (option-order robustness), flip rate by difficulty tier: easy 2.1%, standard
  8.3%, hard 23.4%.** E1 control (shuffled context) is far more destructive: hard-tier accuracy
  0.613 → 0.306 with shuffled context, vs. gemma4-8B "had not moved at all" (model-dependent
  fragility).
- **Averaging the hard tier did NOT pay**: accuracy 0.613 → 0.613 for double the forward
  passes; ECE moved only 0.005. Of 11 answers averaging changed, it fixed 3 and broke 3 — the
  authors' explicit conclusion: "the 22.5% order instability is symmetric noise, not a
  correctable bias — so flip rate does **not** predict whether averaging helps" (a direct,
  important caveat against assuming permutation averaging is free money; it depends on whether
  the flips are a systematic bias or genuine 50/50 model uncertainty).
- Also ships a **top-two runoff** idea (not yet run as a scoring mode) motivated by Pezeshkpour
  & Hruschka's Hits@2 finding: correct option is in the model's own top-2 87% of the time vs.
  61% at rank 1 — reframing order-sensitivity mitigation as "trust the top-2 set, break ties
  smartly" rather than full permutation averaging.
- Prefix caching numbers relevant to Q2 as well: `jobe.prefix` gets **11× speedup per question
  after the first** on a 2k-token document (0/8 flips vs. uncached, bf16-ulp-identical logits);
  batched suffixes add **1.9× over serial, ~15× over uncached** at batch 2 (batch 8 was slower
  than serial on a 10 GB card — a concrete ceiling on how much batching helps on constrained
  hardware).

**SemIf / openjev** — https://github.com/TheoLeeCJ/openjev, now published under
`TheoLeeCJ/SemIf-OpenJev` (saved: `openjev-github.md`, `semif-results.md`)
- `docs/RESULTS.md`, "Robustness and confidence" section, 36 owned base cases (0.723 mean-family
  balanced accuracy for direct logits): **Option reversal → direct-logit accuracy 0.813, with
  10/36 flips.** (Reranker baseline, for contrast: accuracy dropped to 0.498 with only 2/36
  flips — order-invariant by construction but that stability doesn't help when the underlying
  choice is wrong.) Two other meaning-preserving perturbations tested alongside: "criterion
  wrapper" (0.706 acc, 9 flips) and "irrelevant context" (0.821 acc, 4 flips direct / 13 flips
  reranker).
- Explicit conclusion: "the direct model's option-order flips matter even though variant
  accuracy remained strong; positional wording and probability movements are not solved."

**mini-jev** — https://github.com/r-ms/mini-jev (saved: `mini-jev-readme.md`)
- On Qwen3-4B-Instruct-2507, bf16, greedy, CLINC150 intent classification (13,600 questions):
  **position prior is flat** — "the most likely next token is an option letter in 13,600/13,600
  questions... position prior is flat." This is evidence that, for this model/task at least,
  simple first-token argmax over letters isn't dominated by a fixed positional favorite (a
  useful counterpoint/nuance to Jev's own strong position-1 advantage — bias severity is clearly
  model- and task-dependent).
- Shared-KV-cache correctness check: same accuracy with/without cache (0.8484 vs 0.8483);
  **59/13,500 answers flip** near ties when caching is used, consistent with a different
  floating-point arithmetic path rather than a real correctness bug — a useful sanity bound
  ("expect O(0.4%) noise-level flips from prefix caching alone, unrelated to option order").
- Ships a `B1perm` "option-order rotation" experimental arm (present in the harness; specific
  rotation results not detailed in the README beyond the flat-prior finding above).

**snellingio/system-one** — https://github.com/snellingio/system-one (saved:
`snellingio-github.md`)
- Ships an **evaluation tool that explicitly "checks whether rotating Choice options changes
  the result"** (`tools/evals.py`) as one of its accuracy-by-question-type reports — i.e. a
  reusable rotation-stability regression check, intended to run against labeled data before
  setting routing/review thresholds. No specific published numeric results were found in the
  README (it's positioned as a tool/harness rather than a results writeup), but it validates
  that a rotation-stability gate is considered a standard pre-production check in this
  ecosystem, consistent with jobe's `decisionGate.ts` E2 control.

### Practical recommendation for our Phase-2 option-order experiment

Design (cheap because state-first layout already shares the KV prefix across all option-order
variants of a question — only the tiny per-question suffix needs re-encoding per permutation):

1. **Conditions**: identity order, full reversal, and k=2–4 cyclic rotations (start with k=2,
   i.e. one extra order per question — reflex's evidence is that 2 orders captured most of the
   available gain and 4 orders didn't clearly help). For A/B/C/D with k options, a full
   cyclic-permutation sweep (Zheng et al.'s ablation style) is affordable to *measure* bias but
   too expensive to run live per question at k>2 for many-question requests; reserve full-sweep
   for offline calibration/prior estimation (PriDe-style), not per-request serving.
2. **Metrics** (mirroring what the ecosystem already tracks): accuracy, **flip rate** (identity
   vs. reversed/rotated, overall and by difficulty tier — jobe shows tier stratification
   matters, 2.1%/8.3%/23.4%), **ECE** and a probability/TVD-based **disagreement signal**
   (reflex: TVD<0.05 → ~91% acc, TVD>0.30 → ~25% acc — a strong, cheap "should I trust this
   answer or re-check/route to a human" gate), and a **position-prior histogram** (per-letter
   recall / RStd à la Zheng et al.) to distinguish genuine position bias from pure token-ID
   bias — this matters because the fix differs (token bias → PriDe-style prior subtraction;
   position bias → literally vary placement).
3. **Cost model with prefix caching**: for N questions over one shared state, k permutations
   per question costs roughly k× the *question-suffix* forward-pass work, not k× the *state*
   prefill — reflex measured a 3-question request going from ~180ms to ~280ms warm (roughly
   +50%, not +100%) purely from doubling branch count inside one shared-prefix pass. jobe's
   prefix caching gets 11× speedup per question after the first on a 2k-token doc, so extra
   permutation branches riding on the same cached prefix are cheap relative to a cold
   prefill. Budget: default to k=2 (identity + reversed) as the standard profile; escalate to
   full permutation averaging or PriDe-style offline prior calibration only for
   high-stakes/low-confidence question types identified via the disagreement signal.
4. **Before trusting averaging as a fix, check jobe's caveat**: on their hard tier, averaging
   did *not* improve accuracy (0.613→0.613) because the flips were "symmetric noise," not a
   correctable bias — so flip rate alone is not sufficient evidence that averaging will help;
   run the accuracy/ECE check per tier/question-type before turning averaging on as a default,
   and prefer per-tier temperature/config over one global setting (jobe: "a single global
   temperature does not transfer across tiers").
5. **Mitigations worth exposing as layout/profile options**:
   - `permutation_averaging: {orders: 2}` (identity + reversed) — reflex's validated default;
     cheapest, measurable ECE/accuracy win on hard items, near-zero latency cost under prefix
     caching.
   - `permutation_averaging: {orders: k_cyclic}` for k>2 — available but not default; use only
     where offline eval shows it helps (jobe's counter-evidence that more orders ≠ better).
   - `pride_calibration` (offline-fit per-ID token-bias correction from a small permuted
     calibration sample, à la Zheng et al.) — cheapest of all at serve time (no extra forward
     passes), good complement to or substitute for live permutation averaging when the bias is
     token-driven rather than positional.
   - `contextual_calibration` (Zhao et al., content-free-input probability correction) — an
     orthogonal per-template/per-model calibration knob, fit offline once per prompt layout.
   - `disagreement_gate` (reflex's TVD-based signal) to route low-confidence/high-disagreement
     questions to a more expensive readout (extra permutations, or a thinking pass) rather than
     paying the cost on every question.

---

## Q2. Long documents: where to put the questions

### Literature on query placement relative to long context

**Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni, Liang (2023), "Lost in the Middle: How
Language Models Use Long Contexts."** arXiv:2307.03172 (TACL 2024).
https://arxiv.org/abs/2307.03172, full text https://arxiv.org/html/2307.03172
(saved: `lost-in-middle-abs.md`, `lost-in-middle-full.md`)

- Core finding: performance is highest when the relevant information is at the **beginning or
  end** of the context and drops significantly when it's in the **middle**, even for models
  explicitly built for long context — a **U-shaped** accuracy-by-position curve.
- **Query-aware contextualization** (placing the query **before AND after** the
  documents/key-value pairs, so a decoder-only model can attend to the query while encoding
  each document, not just at generation time) — tested directly:
  - On the **synthetic key-value retrieval task**, this is transformative: near-perfect
    performance restored across 75/140/300 pairs (GPT-3.5-Turbo-16K hits ~100% on 300 pairs
    with query-aware contextualization vs. a worst case of 45.6% without it).
  - On **multi-document QA** (closer to our real task), it "minimally affects performance
    trends" — slightly better when the answer is at the very beginning, slightly worse
    otherwise. **Nuance for us**: query-first/query-repeated helps most for pure
    lookup/retrieval-shaped tasks, much less for reasoning/QA-shaped tasks — relevant to
    predicting how much our "header" layout (questions before state) will help on genuinely
    reasoning-heavy MCQ vs. straightforward extraction.
- Also: encoder-decoder (bidirectional) architectures were more robust to position than
  decoder-only, but that's an architecture choice, not applicable if we're stuck on stock
  decoder-only instruct models.

**Anthropic, "Prompt engineering for Claude's long context window"** (2023).
https://www.anthropic.com/news/prompting-long-context (saved: `anthropic-long-context.md`)

- Multiple-choice recall study on a 70–95K token document: recommends putting instructions **at
  the end of the prompt** for best recall, and notes performance for smaller models
  monotonically worsens the further the relevant passage is from the end of the prompt (i.e.
  recency matters a lot for weaker models); Claude 2 showed only "a small dip in the middle" at
  95K, i.e. a shallower U-curve for a stronger long-context model.

**Anthropic's current docs, "Prompting best practices"**
https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
(saved: `claude-best-practices.md`)

- Explicit, current guidance for 20k+ token prompts: **"Put longform data at the top: Place
  your long documents and inputs near the top of your prompt, above your query, instructions,
  and examples. This improves performance across all models."** And: **"Queries at the end can
  improve response quality by up to 30 percent in tests, especially with complex, multidocument
  inputs."** This is exactly the number referenced in the task brief, confirmed verbatim —
  i.e. **state-first / query-last is Anthropic's own default recommendation** for long-context
  accuracy, which aligns with (not conflicts with) our prefix-caching-driven state-first design
  as long as we're doing one question per shared state, not restructuring per-question.

**OpenAI, "GPT-4.1 Prompting Guide."**
https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide
(saved: `gpt41-prompting-guide.md`)

- Section 2, "Long context": **"Especially in long context usage, placement of instructions and
  context can impact performance. If you have long context in your prompt, ideally place your
  instructions at both the beginning and end of the provided context, as we found this to
  perform better than only above or below. If you'd prefer to only have your instructions once,
  then above the provided context works better than below."** — i.e. OpenAI's ranked preference
  is **sandwich (both ends) > instructions-before-document > instructions-after-document**,
  which is the opposite single-instruction ranking from Anthropic/Gemini's "query at the end"
  guidance below. This is a real disagreement in the public guidance and is worth treating as
  **model-family-dependent** rather than a universal law — supports our plan to make layout a
  configurable/testable profile rather than hard-coding one "best" layout.

**Google Gemini API docs, long-context FAQ.**
https://ai.google.dev/gemini-api/docs/long-context (saved: `gemini-longcontext-docs.md`)

- "**Where is the best place to put my query in the context window?** In most cases, especially
  if the total context is long, the model's performance will be better if you put your query /
  question at the end of the prompt (after all the other context)." — matches Anthropic's
  guidance, opposite framing from OpenAI's "sandwich" recommendation (though OpenAI's
  single-instruction fallback is also "above," i.e. before, which is a third position).

**RULER benchmark.** Hsieh et al. (2024), arXiv:2404.06654 (COLM 2024).
https://arxiv.org/abs/2404.06654 (saved: `ruler-abs.md`)

- Shows vanilla needle-in-a-haystack (simple retrieval) is a poor proxy for real long-context
  ability: 17 long-context LMs get near-perfect NIAH scores but show large performance drops as
  length/task-complexity increase on RULER's harder task categories (multi-hop tracing,
  aggregation). Only half of models claiming ≥32K context maintain "satisfactory" performance
  even at 32K. **Relevance**: our long-document MCQ task (especially cross-referencing across
  an invoice, per snapjudge below) is closer to RULER's harder multi-hop/aggregation tasks than
  to simple NIAH, so we should not assume a model's "good NIAH score" predicts good performance
  on our actual cross-referencing questions.

### snapjudge — verified layouts and numbers

https://github.com/Micha0827/snapjudge (saved: `snapjudge-readme.md`)

Three layouts, explicitly named in the README/API: `state_first`, `question_first`, `header`
("all questions listed, then the state, then each question"). Default is `auto`: question-first
normally, **flips to state-first automatically when the state is long (>2,000 characters) and
there are several questions**, "so that the state is prefilled once and shared by all
questions."

- **Snap Run game benchmark** (Qwen3.6-35B-A3B, 38 short-sentence obstacle descriptions,
  English/German):

  | layout | English | German |
  |---|---|---|
  | state first | 89%, median 397 ms | 89%, median 423 ms |
  | question first (default) | **100%, median 78 ms** | **97%, median 83 ms** |

  Quote: "Put the fixed question before the data... in our tests the model was also more
  accurate: 89% → 97–100% on the game sentences." Each obstacle here is short (one sentence),
  so question-first's lack of shared-prefix benefit across obstacles doesn't matter — each
  request is effectively single-question.

- **Invoice cross-referencing (long-document) comparison against Jev**, on TypeSafe's public
  20-case eval set, ~8,000-token invoices, questions asking whether a line item is confirmed by
  the buyer's own records elsewhere in the document (the hardest question type in the whole
  eval — 65/75 for Jev vs. 106/109 vs 107/109 parity on the easy yes/no invoice questions):

  | layout | Correct (of 75) | Wall time (five invoices) |
  |---|---|---|
  | state first | 41 | 4.7 min |
  | **header** (all questions + state, then each question) | **45** | **4.3 min** |
  | question first | **50** | much slower — "6–8× slower... up to 13 minutes for a 48-question invoice on the M2 Max" |
  | Jev (published) | **65** | – |

  Exact quote: "the 35B-A3B answered 41 of the 75 choices correctly state-first, 45 with the
  header and 50 question-first; the header run took 4.3 minutes, the state-first run 4.7."
  The `header` layout idea is credited to "a discussion on r/LocalLLaMA." The authors caveat:
  "Four items are a hint rather than proof, so `auto` does not use it yet" — i.e. even
  snapjudge's own maintainers do not consider the header-layout accuracy win statistically
  solid yet, despite it also being the shared-prefix-preserving option.
- Overall Jev-vs-local-model comparison (TypeSafe's 373-case public eval, question-first as
  used by default for short cases): Jev 87.7% (308/351) vs. Qwen3.8-27B 81.2% (303/373) vs.
  Qwen3.6-35B-A3B 77.5% (289/373); nearly all of the gap is concentrated in the invoice
  cross-referencing question type described above, not in short-text questions.
- Mechanism note directly relevant to our design: "Question first, cached... A long state (>
  2,000 characters) with several questions flips the order instead, so that the state is
  prefilled once and shared by all questions" — i.e. snapjudge's own `auto` heuristic is
  essentially the state-length/question-count threshold logic requested in the task brief,
  already implemented and battle-tested by another Jev-ecosystem project.

### Prefix-sharing status and latency cost per layout, for N questions over one long state

| Layout | Shared KV prefix across the N questions? | Notes |
|---|---|---|
| `state_first` (`Context: <state>` then each question) | **Yes** — state is prefilled once, all N question-suffixes reuse it | Standard vLLM automatic-prefix-caching win; cost ≈ one state prefill + N small suffix passes. snapjudge/jobe/mini-jev all confirm large speedups from this (jobe: 11× per question after the first on a 2k-token doc; reflex: shared prefix + doubled branches only ~+50% latency, not +100%). Best accuracy on short/no-cross-reference cases; weakest on invoice-style cross-referencing (snapjudge: 41/75). |
| `question_first` (question+options cached, state as suffix) | **No**, unless N=1 — each question has a *different* cached head, so the (potentially very long) state must be re-prefilled behind each one | snapjudge: fast and *more accurate* when the "document" is actually short/single-purpose (Snap Run: 78 ms vs 397 ms, 100% vs 89% accuracy) — but on a genuinely long, multi-question document this inverts: "6–8× slower... up to 13 minutes for a 48-question invoice," despite also being the *most accurate* single layout there (50/75). Right choice for N=1 requests or where per-question caching of a short fixed question set matters more than document reuse. |
| `header` (all N questions listed once, then state, then each question again) | **Yes** — header+state together form one shared prefix; only the trailing per-question repeat is a small suffix | snapjudge: comparable wall-clock to state-first (4.3 vs 4.7 min for 5 invoices) but higher accuracy on the hard cross-referencing case (45/75 vs 41/75) — plausibly because Lost-in-the-Middle's "query-aware contextualization" effect (query before the data) gets partial credit even though the state is technically still processed causally. Authors flag this as not yet statistically solid (4 items). Reasonable phase-2 experimental default for long documents with many questions, pending validation at larger N. |

### Recommended layout set and auto-switch policy

- **`decider_chat` (state-first)** — default. Best fit for our core design goal (one KV prefix
  shared across all questions on a shared state) and is also literature-endorsed by
  Anthropic/Gemini's "put the document first, query last" guidance for single-query long-context
  accuracy. Use for the common case: moderate-length state, multiple questions per request.
- **`question_first`** — auto-switch to this **only when a request has exactly one question**
  (or the state is short enough that re-prefilling per question is cheap, e.g. below the 2,000
  character/token threshold snapjudge already uses) — since prefix sharing then buys nothing and
  snapjudge's own game-benchmark data shows a real accuracy AND latency win from
  question-first when there's no shared-prefix reason not to (89%→100% accuracy, 397ms→78ms).
- **`header`** — offer as an experimental profile for **long state + many questions +
  cross-referencing/extraction-heavy question types** (the exact regime where state-first loses
  the most, per snapjudge's invoice result). Given the literature's mixed signal (Lost in the
  Middle: query-aware placement helps retrieval-shaped tasks much more than QA/reasoning-shaped
  tasks; OpenAI recommends sandwich/both-ends, Anthropic/Gemini recommend query-last only), and
  snapjudge's own "hint, not proof" caveat, this should be **A/B tested per question-type / per
  model** before defaulting to it, not shipped as the default for all long documents.
- **Auto-switch thresholds to start from** (borrowing snapjudge's own heuristic as a baseline,
  refined by question count): state length **>~2,000 characters (~500–700 tokens)** AND
  **question count ≥2** → state-first (or header, once validated) instead of question-first;
  single-question requests always get question-first regardless of state length, since there is
  no shared-prefix benefit to lose. Given our actual latency-sensitive production setting (many
  questions per shared state, vLLM automatic prefix caching already assumed), state-first should
  stay the hard default; header should only flip on for a state-length/question-count band we
  determine empirically (start by testing at snapjudge's own invoice scale, ~8,000 tokens /
  15 questions per document, where the header layout's advantage was measured).
