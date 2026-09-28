# Phase 1: Shared vLLM Server with Chat + `/v1/systemone` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One vLLM process on one RTX PRO 6000 serves normal OpenAI chat (thinking on) and, through a thin FastAPI gateway, a Jev-compatible `/v1/systemone` decision endpoint from the same loaded model.

**Architecture:** vLLM (official `v0.30.0` image, bf16, no MTP) owns the model. The gateway (FastAPI, CPU only) proxies every chat request, and answers `/v1/systemone` itself:
1. It builds one prompt per question from an editable layout file.
2. It sends all prompts to vLLM `/v1/completions` with `max_tokens=1` and `logprob_token_ids` set to the option-label tokens.
3. It softmaxes each question's label logprobs, divided by a fitted temperature.
4. It returns Jev-shaped answers with TypeSafe's confidence formulas.

The default prompt layout reproduces decider's chat layout token for token, so decider's published temperature and its index scores are valid references.

**Tech Stack:**
- Python 3.12, uv, FastAPI, httpx, pydantic v2, pytest (+ pytest-asyncio), ruff
- transformers, used only for tokenizers and chat templates, on CPU
- Docker Compose, `vllm/vllm-openai:v0.30.0`

**Spec:** `docs/superpowers/specs/2026-09-28-systemone-server-design.md` (read it first). Background: `docs/README.md`, `docs/6-answer-compatibility.md`.

## Global Constraints

- vLLM image `vllm/vllm-openai:v0.30.0`. bf16 weights and bf16 KV cache. **No `--speculative-config` (no MTP).**
- Model profiles and pinned revisions:
  - `qwen3.8-27b` → `Qwen/Qwen3.8-27B@1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`
  - `qwen3.6-27b` → `Qwen/Qwen3.6-27B@6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`
  - `gemma-4-31b` → `google/gemma-4-31B-it@842da3794eaa0b77d5f08bae87a17459d91ff475`
- One model is loaded at a time: `docker compose --env-file profiles/<profile>.env up -d`.
- Host `~/.cache/huggingface` is mounted into both containers (the gateway's copy read-only). Never bake weights into an image.
- Ports: vLLM on `127.0.0.1:8000`, gateway on `127.0.0.1:9000`. Loopback only.
- No prompt text in Python. All wording lives in `prompts/<layout>.toml`.
- Label tables and temperatures live in `data/<profile>/<layout>/`. They are valid only for that tokenizer + layout, and the gateway refuses to start on a hash mismatch.
- The response matches Jev exactly:
  - `noul` is a float P(true) with no `confidence`;
  - `score` is the probability-weighted level, with a `legend`;
  - `confidence` uses TypeSafe's adapter formulas;
  - values are rounded to 4 decimals and `usage.output_tokens` is 0.
- Capacity refusals are HTTP 422 whose message contains one of these marker strings: `options per choice`, `a choice needs at least two options`, `a score takes 2 to 10 levels`, `maximum context length`.
- Code style: tutorial-clear, small focused files. Comments are at most 2 lines.
- Commit messages: caveman Conventional Commits, subject ≤ 50 chars, ending with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Never use Jev API outputs for training or calibration.

## File map

| Path | Responsibility |
|---|---|
| `pyproject.toml` | deps, pytest/ruff config, `gateway` package |
| `gateway/config.py` | `Settings` from env or a profile file |
| `gateway/schema.py` | Jev request model, `RequestError`, limits |
| `gateway/layouts.py` | load and validate `prompts/*.toml` |
| `gateway/questions.py` | Jev question → option texts; state → text |
| `gateway/labels.py` | single-token label table, hashes, save/load |
| `gateway/prompts.py` | chat frame + token ids per row (piecewise) |
| `gateway/orders.py` | option permutations and averaging back |
| `gateway/calibration.py` | temperatures, softmax |
| `gateway/answers.py` | probabilities → Jev answers + confidence |
| `gateway/readout.py` | vLLM `/v1/completions` label logprobs |
| `gateway/decide.py` | the whole systemone flow as one async function |
| `gateway/chat.py` | proxy, `route()` hook, model list |
| `gateway/app.py` | FastAPI wiring, auth, errors, startup |
| `prompts/*.toml` | layouts: `decider_chat`, `header`, `question_first` |
| `profiles/*.env` | one per model |
| `scripts/build_labels.py` | writes label tables |
| `scripts/decider_fixtures.py` | records decider's token ids (runs in its own venv) |
| `scripts/bench_data.py`, `scripts/bench.py` | benchmark requests and runner |
| `docker/gateway.Dockerfile`, `docker/vllm-entrypoint.sh`, `compose.yaml` | runtime |
| `tests/unit`, `tests/parity`, `tests/live` | tests |

## Task order and suggested implementer

The main agent orchestrates and reviews every task.

| # | Task | Implementer |
|---|---|---|
| 1 | Scaffold | Sonnet |
| 2 | Config + profiles | Sonnet |
| 3 | Schema + layouts + prompt files | Sonnet |
| 4 | Question rendering | Sonnet |
| 5 | Label tables + build script | Sonnet |
| 6 | Chat frame + row builder | **Opus** |
| 7 | Decider parity | **Opus** |
| 8 | Orders, calibration, answers | Sonnet |
| 9 | vLLM readout | Sonnet |
| 10 | `decide()` | **Opus** |
| 11 | Chat proxy + FastAPI app | **Opus** |
| 12 | Docker + compose + first bring-up | Sonnet + main agent (GPU) |
| 13 | Live tests | Sonnet |
| 14 | Benchmark | Sonnet |
| 15 | Bring-up of all profiles, reports, CLAUDE.md | main agent + **Opus** |

---

### Task 1: Scaffold

**Files:**
- Create: `pyproject.toml`, `gateway/__init__.py`, `scripts/__init__.py`, `tests/unit/test_smoke.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: importable package `gateway`; importable `scripts`; test commands `uv run pytest`, `uv run ruff check .`

- [ ] **Step 1: Write `pyproject.toml`**

```toml
[project]
name = "jev-brain"
version = "0.1.0"
description = "One vLLM model serving OpenAI chat and a Jev-compatible /v1/systemone endpoint"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "httpx>=0.27",
    "pydantic>=2.9",
    "transformers>=5.0",
    "jinja2>=3.1",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "ruff>=0.7",
    "typesafe-sdk==0.7.2",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["gateway"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
asyncio_mode = "auto"
markers = ["live: needs the running stack (docker compose up)"]
addopts = "-m 'not live'"

[tool.ruff]
line-length = 120
target-version = "py312"
```

- [ ] **Step 2: Create empty packages and a smoke test**

`gateway/__init__.py`:
```python
"""Gateway serving a Jev-compatible /v1/systemone endpoint next to vLLM's chat."""
```

`scripts/__init__.py`: empty file.

`tests/unit/test_smoke.py`:
```python
import gateway


def test_package_imports():
    assert gateway.__name__ == "gateway"
```

- [ ] **Step 3: Extend `.gitignore`**

Append:
```
.venv/
.cache/
__pycache__/
.pytest_cache/
.ruff_cache/
```

- [ ] **Step 4: Install and run**

Run: `uv sync && uv run pytest -q && uv run ruff check .`
Expected: `1 passed`, and ruff prints `All checks passed!`. This creates `uv.lock`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock gateway/__init__.py scripts/__init__.py tests/unit/test_smoke.py .gitignore
git commit -m "build: scaffold uv project and test setup" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Config and model profiles

**Files:**
- Create: `gateway/config.py`, `profiles/qwen3.8-27b.env`, `profiles/qwen3.6-27b.env`, `profiles/gemma-4-31b.env`, `tests/helpers.py`, `tests/conftest.py`, `tests/unit/test_config.py`

**Interfaces:**
- Produces:
  - `ROOT: Path`
  - `read_env_file(path: Path) -> dict[str, str]`
  - `Settings`, a frozen dataclass with fields `profile, hf_model, hf_revision, served_model, max_model_len, prompt_layout, option_orders, vllm_url, api_key, warm_min_prefix_tokens, data_root`, plus `Settings.from_env(env: dict | None = None)`, `Settings.from_profile(name: str)` and `settings.data_dir(layout: str) -> Path`
  - In `tests/helpers.py`: `PROFILES` and `tokenizer_for(profile)`. In `tests/conftest.py`: the fixture `qwen_tok`. Tests import shared values from `tests.helpers`, never from conftest or other test modules

- [ ] **Step 1: Write the failing test** `tests/unit/test_config.py`

```python
from gateway.config import ROOT, Settings, read_env_file
from tests.helpers import PROFILES


def test_read_env_file_skips_comments_and_strips_quotes(tmp_path):
    f = tmp_path / "x.env"
    f.write_text("# comment\nA=1\n\nB='two words'\nC={\"enable_thinking\": true}\n")
    assert read_env_file(f) == {"A": "1", "B": "two words", "C": '{"enable_thinking": true}'}


def test_every_profile_loads_with_a_pinned_revision():
    for name in PROFILES:
        s = Settings.from_profile(name)
        assert s.profile == name
        assert len(s.hf_revision) == 40
        assert s.data_dir("decider_chat") == ROOT / "data" / name / "decider_chat"


def test_blank_optional_keys_fall_back_to_defaults():
    s = Settings.from_env(
        {
            "PROFILE": "p",
            "HF_MODEL": "m",
            "HF_REVISION": "r",
            "SERVED_MODEL": "s",
            "MAX_MODEL_LEN": "1024",
            "PROMPT_LAYOUT": "",
            "GATEWAY_API_KEY": "",
        }
    )
    assert s.prompt_layout == "decider_chat"
    assert s.option_orders == "identity"
    assert s.api_key is None
    assert s.warm_min_prefix_tokens == 512
```

- [ ] **Step 2: Run it to see it fail**

Run: `uv run pytest tests/unit/test_config.py -q`
Expected: FAIL, `ModuleNotFoundError: No module named 'gateway.config'`

- [ ] **Step 3: Implement `gateway/config.py`**

```python
"""Settings from the environment (compose) or from a profile file (scripts, tests)."""

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_env_file(path: Path) -> dict[str, str]:
    """KEY=VALUE per line; blank lines and '#' comments skipped; single quotes stripped."""
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip("'")
    return env


@dataclass(frozen=True)
class Settings:
    profile: str
    hf_model: str
    hf_revision: str
    served_model: str
    max_model_len: int
    prompt_layout: str = "decider_chat"
    option_orders: str = "identity"
    vllm_url: str = "http://127.0.0.1:8000"
    api_key: str | None = None
    warm_min_prefix_tokens: int = 512
    data_root: Path = ROOT / "data"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        e = dict(os.environ) if env is None else env
        return cls(
            profile=e["PROFILE"],
            hf_model=e["HF_MODEL"],
            hf_revision=e["HF_REVISION"],
            served_model=e["SERVED_MODEL"],
            max_model_len=int(e["MAX_MODEL_LEN"]),
            prompt_layout=e.get("PROMPT_LAYOUT") or "decider_chat",
            option_orders=e.get("OPTION_ORDERS") or "identity",
            vllm_url=e.get("VLLM_URL") or "http://127.0.0.1:8000",
            api_key=e.get("GATEWAY_API_KEY") or None,
            warm_min_prefix_tokens=int(e.get("WARM_MIN_PREFIX_TOKENS") or 512),
            data_root=Path(e.get("DATA_ROOT") or ROOT / "data"),
        )

    @classmethod
    def from_profile(cls, name: str) -> "Settings":
        return cls.from_env(read_env_file(ROOT / "profiles" / f"{name}.env"))

    def data_dir(self, layout: str) -> Path:
        return self.data_root / self.profile / layout
```

- [ ] **Step 4: Write the three profiles**

`profiles/qwen3.6-27b.env`:
```
# Qwen3.6-27B, bf16. Start: docker compose --env-file profiles/qwen3.6-27b.env up -d
PROFILE=qwen3.6-27b
HF_MODEL=Qwen/Qwen3.6-27B
HF_REVISION=6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
SERVED_MODEL=qwen3.6-27b
MAX_MODEL_LEN=32768
REASONING_PARSER=qwen3
TOOL_PARSER=qwen3_coder
LANGUAGE_MODEL_ONLY=1
CHAT_TEMPLATE=
CHAT_TEMPLATE_KWARGS=
PROMPT_LAYOUT=decider_chat
OPTION_ORDERS=identity
```

`profiles/qwen3.8-27b.env`:
```
# Qwen3.8-27B, bf16. Start: docker compose --env-file profiles/qwen3.8-27b.env up -d
PROFILE=qwen3.8-27b
HF_MODEL=Qwen/Qwen3.8-27B
HF_REVISION=1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0
SERVED_MODEL=qwen3.8-27b
MAX_MODEL_LEN=32768
REASONING_PARSER=qwen3
TOOL_PARSER=qwen3_xml
LANGUAGE_MODEL_ONLY=1
CHAT_TEMPLATE=
CHAT_TEMPLATE_KWARGS=
PROMPT_LAYOUT=decider_chat
OPTION_ORDERS=identity
```

`profiles/gemma-4-31b.env`:
```
# Gemma 4 31B instruct, bf16; thinking on by default for chat.
PROFILE=gemma-4-31b
HF_MODEL=google/gemma-4-31B-it
HF_REVISION=842da3794eaa0b77d5f08bae87a17459d91ff475
SERVED_MODEL=gemma-4-31b
MAX_MODEL_LEN=32768
REASONING_PARSER=gemma4
TOOL_PARSER=gemma4
LANGUAGE_MODEL_ONLY=0
CHAT_TEMPLATE=/vllm-workspace/examples/tool_chat_template_gemma4.jinja
CHAT_TEMPLATE_KWARGS={"enable_thinking": true}
PROMPT_LAYOUT=decider_chat
OPTION_ORDERS=identity
```

- [ ] **Step 5: Shared test helpers** `tests/helpers.py` and `tests/conftest.py`

`tests/helpers.py`:
```python
"""Values shared by tests. Import from here, not from conftest or other test modules."""

import functools

from transformers import AutoTokenizer

from gateway.config import Settings

PROFILES = ["qwen3.8-27b", "qwen3.6-27b", "gemma-4-31b"]


@functools.cache
def tokenizer_for(profile: str):
    """The pinned tokenizer of a profile (downloads a few MB into the HF cache once)."""
    s = Settings.from_profile(profile)
    return AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
```

`tests/conftest.py`:
```python
import pytest

from tests.helpers import tokenizer_for


@pytest.fixture(scope="session")
def qwen_tok():
    return tokenizer_for("qwen3.6-27b")
```

- [ ] **Step 6: Run the tests**

Run: `uv run pytest tests/unit -q`
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add gateway/config.py profiles tests/helpers.py tests/conftest.py tests/unit/test_config.py
git commit -m "feat(config): add settings and model profiles" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Request schema, layouts and prompt files

**Files:**
- Create: `gateway/schema.py`, `gateway/layouts.py`, `prompts/decider_chat.toml`, `prompts/header.toml`, `prompts/question_first.toml`, `tests/unit/test_schema.py`, `tests/unit/test_layouts.py`

**Interfaces:**
- Consumes: `ROOT` (Task 2)
- Produces:
  - `schema.py`: `MAX_OPTIONS = 255`, `MAX_LEVELS = 10`, `class RequestError(ValueError)`, `Question(type, instructions, criteria)`, and `SystemOneRequest(state, model, questions: dict[str, Question], layout: str | None, option_orders: str | None)`
  - `layouts.py`: `Layout`, a frozen dataclass with fields `name, sha256, order, context, question, option, answer, described, noul, noul_question, questions, question_item` and properties `option_open` and `option_close`; `PROMPTS_DIR`; `load_layout(path) -> Layout`; `load_layouts(directory=PROMPTS_DIR) -> dict[str, Layout]`

- [ ] **Step 1: Write the failing tests**

`tests/unit/test_schema.py`:
```python
import pytest
from pydantic import ValidationError

from gateway.schema import SystemOneRequest


def test_extra_fields_ignored_and_overrides_parsed():
    r = SystemOneRequest.model_validate(
        {
            "state": "s",
            "model": "jev-latest",
            "foo": 1,
            "layout": "header",
            "questions": {"q": {"type": "noul", "extra": 2}},
        }
    )
    assert r.layout == "header"
    assert r.option_orders is None
    assert r.questions["q"].type == "noul"


def test_unknown_question_type_rejected():
    with pytest.raises(ValidationError):
        SystemOneRequest.model_validate({"questions": {"q": {"type": "maybe"}}})
```

`tests/unit/test_layouts.py`:
```python
import pytest

from gateway.layouts import PROMPTS_DIR, load_layout, load_layouts


def test_shipped_layouts_load():
    layouts = load_layouts()
    assert set(layouts) == {"decider_chat", "header", "question_first"}
    assert layouts["decider_chat"].order == ("context", "question", "options")
    assert layouts["header"].order == ("questions", "context", "question", "options")
    assert layouts["question_first"].order == ("question", "options", "context")


def test_decider_chat_text_matches_decider():
    d = load_layouts()["decider_chat"]
    assert d.context.format(state="S") == "Context:\nS"
    assert d.question.format(question="Q") == "\n\nQuestion: Q\nOptions:"
    assert (d.option_open, d.option_close) == ("\n(", ") {text}")
    assert d.answer == "Answer: ("
    assert d.described.format(name="billing", description="Payments") == "billing: Payments"
    assert d.noul == ("no", "yes")
    assert d.noul_question == "Which answer fits the context?"


def test_missing_placeholder_is_rejected(tmp_path):
    bad = (PROMPTS_DIR / "decider_chat.toml").read_text().replace("{state}", "")
    (tmp_path / "bad.toml").write_text(bad)
    with pytest.raises(ValueError, match="state"):
        load_layout(tmp_path / "bad.toml")


def test_hash_follows_the_text(tmp_path):
    text = (PROMPTS_DIR / "decider_chat.toml").read_text()
    (tmp_path / "a.toml").write_text(text)
    (tmp_path / "b.toml").write_text(text.replace("Question:", "Q:"))
    assert load_layout(tmp_path / "a.toml").sha256 != load_layout(tmp_path / "b.toml").sha256
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest tests/unit/test_schema.py tests/unit/test_layouts.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `gateway/schema.py`**

```python
"""The Jev /v1/systemone request (TypeSafe wire format) and the refusal error."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

MAX_OPTIONS = 255
MAX_LEVELS = 10


class RequestError(ValueError):
    """Refused with HTTP 422. Capacity messages keep the decision-index harness marker text."""


class Question(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["choice", "score", "noul"]
    instructions: Any = None
    criteria: Any = None


class SystemOneRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    state: Any = ""
    model: str = "jev-latest"
    questions: dict[str, Question]
    layout: str | None = None  # experiment override, not part of Jev's API
    option_orders: str | None = None  # experiment override, not part of Jev's API
```

- [ ] **Step 4: Implement `gateway/layouts.py`**

```python
"""Prompt layouts. All prompt wording lives in prompts/<name>.toml; this module only loads and checks it."""

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

from gateway.config import ROOT

PROMPTS_DIR = ROOT / "prompts"
PARTS = ("questions", "context", "question", "options")
REQUIRED = ("order", "context", "question", "option", "answer", "described", "noul", "noul_question")


@dataclass(frozen=True)
class Layout:
    name: str
    sha256: str
    order: tuple[str, ...]
    context: str
    question: str
    option: str
    answer: str
    described: str
    noul: tuple[str, str]
    noul_question: str
    questions: str = ""
    question_item: str = ""

    @property
    def option_open(self) -> str:
        return self.option.split("{label}")[0]

    @property
    def option_close(self) -> str:
        return self.option.split("{label}")[1]


def _check(name: str, data: dict) -> None:
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise ValueError(f"{name}: missing keys {missing}")
    order = data["order"]
    if (
        len(order) != len(set(order))
        or not set(order) <= set(PARTS)
        or not {"context", "question", "options"} <= set(order)
    ):
        raise ValueError(f"{name}: order must list context, question, options (and optionally questions) once each")
    needs = [
        ("context", "{state}"),
        ("question", "{question}"),
        ("option", "{label}"),
        ("described", "{name}"),
        ("described", "{description}"),
    ]
    if "questions" in order:
        needs += [("questions", "{questions}"), ("question_item", "{question}")]
    for key, placeholder in needs:
        if placeholder not in data.get(key, ""):
            raise ValueError(f"{name}: {key} needs {placeholder}")
    if "{text}" not in data["option"].split("{label}")[-1]:
        raise ValueError(f"{name}: option needs {{text}} after {{label}}")
    if len(data["noul"]) != 2:
        raise ValueError(f"{name}: noul must be [false word, true word]")


def load_layout(path: Path) -> Layout:
    raw = path.read_bytes()
    data = tomllib.loads(raw.decode())
    _check(path.name, data)
    return Layout(
        name=path.stem,
        sha256=hashlib.sha256(raw).hexdigest(),
        order=tuple(data["order"]),
        context=data["context"],
        question=data["question"],
        option=data["option"],
        answer=data["answer"],
        described=data["described"],
        noul=tuple(data["noul"]),
        noul_question=data["noul_question"],
        questions=data.get("questions", ""),
        question_item=data.get("question_item", ""),
    )


def load_layouts(directory: Path = PROMPTS_DIR) -> dict[str, Layout]:
    return {p.stem: load_layout(p) for p in sorted(directory.glob("*.toml"))}
```

- [ ] **Step 5: Write the three prompt files**

`prompts/decider_chat.toml`:
```toml
# Default layout: state first. Matches decider's chat layout token for token (tests/parity).
# Each part in `order` is tokenized on its own, like decider. Literal braces must be written {{ }}.
order = ["context", "question", "options"]
context = "Context:\n{state}"
question = "\n\nQuestion: {question}\nOptions:"
option = "\n({label}) {text}"
answer = "Answer: ("
described = "{name}: {description}"
noul = ["no", "yes"]
noul_question = "Which answer fits the context?"
```

`prompts/header.toml`:
```toml
# Experimental: list every question, then the state, then ask one. The list + state prefix is shared.
order = ["questions", "context", "question", "options"]
questions = "Questions that will be asked about the context:\n{questions}\n\n"
question_item = "- {question}"
context = "Context:\n{state}"
question = "\n\nQuestion: {question}\nOptions:"
option = "\n({label}) {text}"
answer = "Answer: ("
described = "{name}: {description}"
noul = ["no", "yes"]
noul_question = "Which answer fits the context?"
```

`prompts/question_first.toml`:
```toml
# Experimental: question and options first, state last. Questions do not share a prefix within a request.
order = ["question", "options", "context"]
question = "Question: {question}\nOptions:"
option = "\n({label}) {text}"
context = "\n\nContext:\n{state}"
answer = "Answer: ("
described = "{name}: {description}"
noul = ["no", "yes"]
noul_question = "Which answer fits the context?"
```

- [ ] **Step 6: Run the tests**

Run: `uv run pytest tests/unit -q`
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add gateway/schema.py gateway/layouts.py prompts tests/unit/test_schema.py tests/unit/test_layouts.py
git commit -m "feat(prompts): add request schema and layout files" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Question rendering

Mirrors decider's `systemone.render_question` / `render_state` (see `.firecrawl/infer/Mapika_decider__decider_systemone.py` if available, or `decider/systemone.py` in decider-ai 1.5.0).

**Files:**
- Create: `gateway/questions.py`, `tests/unit/test_questions.py`

**Interfaces:**
- Consumes: `Layout`, `load_layouts` (Task 3); `Question`, `RequestError`, `MAX_OPTIONS`, `MAX_LEVELS` (Task 3)
- Produces:
  - `render_state(state) -> str`
  - `Rendered`, a frozen dataclass with fields `type: str`, `text: str`, `options: list[str]`, `names: list`, `legend: list[str] | None`
  - `render_question(q: Question, layout: Layout) -> Rendered`

- [ ] **Step 1: Write the failing tests** `tests/unit/test_questions.py`

```python
import json

import pytest

from gateway.layouts import load_layouts
from gateway.questions import render_question, render_state
from gateway.schema import Question, RequestError

LAYOUT = load_layouts()["decider_chat"]


def q(**kw):
    return render_question(Question(**kw), LAYOUT)


def test_choice_descriptions_null_and_objects():
    r = q(type="choice", instructions="Team?", criteria={"billing": "Payments", "sales": None, "x": {"k": 1}})
    assert r.options == ["billing: Payments", "sales", 'x: {"k": 1}']
    assert r.names == ["billing", "sales", "x"]


def test_choice_list_criteria():
    assert q(type="choice", instructions="?", criteria=["a", "b"]).options == ["a", "b"]


def test_choice_limits_use_harness_markers():
    with pytest.raises(RequestError, match="a choice needs at least two options"):
        q(type="choice", instructions="?", criteria={"a": None})
    with pytest.raises(RequestError, match="options per choice"):
        q(type="choice", instructions="?", criteria={str(i): None for i in range(256)})


def test_score_levels_and_legend_form():
    r = q(type="score", instructions="Angry?", criteria=["Calm", "Angry"])
    assert (r.options, r.names, r.legend) == (["0: Calm", "1: Angry"], [0, 1], ["Calm", "Angry"])
    assert q(type="score", instructions="?", criteria={"1": "b", "0": "a"}).options == ["0: a", "1: b"]
    with pytest.raises(RequestError, match="a score takes 2 to 10 levels"):
        q(type="score", instructions="?", criteria=[str(i) for i in range(11)])


def test_noul_rendering():
    assert q(type="noul", instructions="Urgent?").options == ["no", "yes"]
    r = q(type="noul", instructions="Urgent?", criteria={"true": "needs help now", "false": "can wait"})
    assert r.options == ["no: can wait", "yes: needs help now"]
    assert r.names == [False, True]


def test_noul_without_instructions_needs_a_description():
    r = q(type="noul", criteria={"true": "The customer is angry"})
    assert r.text == "Which answer fits the context?"
    with pytest.raises(RequestError, match="noul question without instructions"):
        q(type="noul")


def test_missing_instructions_rejected():
    with pytest.raises(RequestError, match="question without instructions"):
        q(type="choice", criteria=["a", "b"])


def test_render_state():
    assert render_state("plain text") == "plain text"
    assert render_state({"a": [1, 2]}) == '{"a": [1, 2]}'
    long_list = render_state({"r": [{"v": i} for i in range(8)]})
    assert json.loads(long_list)["r"][3] == {"_index": 3, "v": 3}
    assert json.loads(render_state(list(range(8))))[2] == {"_index": 2, "value": 2}
```

- [ ] **Step 2: Run to see it fail**

Run: `uv run pytest tests/unit/test_questions.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'gateway.questions'`

- [ ] **Step 3: Implement `gateway/questions.py`**

```python
"""Jev questions → option texts, mirroring decider's systemone.render_question and render_state."""

import json
from dataclasses import dataclass
from typing import Any

from gateway.layouts import Layout
from gateway.schema import MAX_LEVELS, MAX_OPTIONS, Question, RequestError

ANNOTATE_MIN = 8  # decider numbers long arrays so paths like records[47] become lookups


def as_text(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def annotate_indices(x: Any) -> Any:
    if isinstance(x, list):
        if len(x) < ANNOTATE_MIN:
            return [annotate_indices(v) for v in x]
        return [
            {"_index": i, **annotate_indices(v)} if isinstance(v, dict) else {"_index": i, "value": annotate_indices(v)}
            for i, v in enumerate(x)
        ]
    if isinstance(x, dict):
        return {k: annotate_indices(v) for k, v in x.items()}
    return x


def render_state(state: Any) -> str:
    return state if isinstance(state, str) else json.dumps(annotate_indices(state), ensure_ascii=False)


@dataclass(frozen=True)
class Rendered:
    type: str  # choice | score | noul
    text: str  # the question as shown to the model
    options: list[str]  # option texts in the caller's order
    names: list[Any]  # what each option reports back (choice keys, level numbers, False/True)
    legend: list[str] | None = None  # score level descriptions


def described(layout: Layout, name: Any, description: Any) -> str:
    return (
        str(name) if description in (None, "") else layout.described.format(name=name, description=as_text(description))
    )


def question_text(q: Question, layout: Layout) -> str:
    if q.type == "noul" and q.instructions in (None, ""):
        criteria = q.criteria if isinstance(q.criteria, dict) else {}
        if all(criteria.get(k) in (None, "") for k in ("true", "false")):
            raise RequestError("noul question without instructions: criteria must describe true or false")
        return layout.noul_question
    text = "" if q.instructions is None else as_text(q.instructions)
    if not text:
        raise RequestError("question without instructions")
    return text


def render_choice(q: Question, text: str, layout: Layout) -> Rendered:
    criteria = {str(c): None for c in q.criteria} if isinstance(q.criteria, list) else q.criteria
    if not isinstance(criteria, dict):
        raise RequestError("choice criteria must map option names to descriptions")
    if len(criteria) < 2:
        raise RequestError("a choice needs at least two options")
    if len(criteria) > MAX_OPTIONS:
        raise RequestError(f"at most {MAX_OPTIONS} options per choice (got {len(criteria)})")
    names = list(criteria)
    return Rendered("choice", text, [described(layout, n, criteria[n]) for n in names], names)


def render_score(q: Question, text: str, layout: Layout) -> Rendered:
    levels = q.criteria
    if isinstance(levels, dict):  # legend form {"0": ..., "1": ...}
        try:
            levels = [levels[k] for k in sorted(levels, key=float)]
        except ValueError as e:
            raise RequestError("score legend keys must be level numbers") from e
    if not isinstance(levels, list) or not 2 <= len(levels) <= MAX_LEVELS:
        raise RequestError(f"a score takes 2 to {MAX_LEVELS} levels")
    options = [layout.described.format(name=i, description=as_text(d)) for i, d in enumerate(levels)]
    return Rendered("score", text, options, list(range(len(levels))), [as_text(d) for d in levels])


def render_noul(q: Question, text: str, layout: Layout) -> Rendered:
    if q.criteria is not None and not isinstance(q.criteria, dict):
        raise RequestError("noul criteria must be a map of optional true/false descriptions")
    criteria = q.criteria or {}
    no, yes = layout.noul
    options = [described(layout, no, criteria.get("false")), described(layout, yes, criteria.get("true"))]
    return Rendered("noul", text, options, [False, True])


def render_question(q: Question, layout: Layout) -> Rendered:
    text = question_text(q, layout)
    render = {"choice": render_choice, "score": render_score, "noul": render_noul}[q.type]
    return render(q, text, layout)
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/unit -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add gateway/questions.py tests/unit/test_questions.py
git commit -m "feat(prompts): render jev questions to option texts" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Label tables and the build script

**Files:**
- Create: `gateway/labels.py`, `scripts/build_labels.py`, `tests/unit/test_labels.py`

**Interfaces:**
- Consumes: `Layout`, `load_layouts` (Task 3); `Settings` (Task 2); the fixture `qwen_tok` (Task 2)
- Produces:
  - `MAX_LABELS = 255`, `NARROW = 10`
  - `Labels`, a frozen dataclass with fields `names: list[str]` and `ids: list[int]`
  - `label_table(tok) -> Labels`
  - `tokenizer_sha256(tok) -> str`
  - `build_labels(tok, layout) -> dict`
  - `save_labels(path, table)`
  - `load_labels(path, tok, layout) -> Labels`
  - CLI `uv run python scripts/build_labels.py --profile <name>`

- [ ] **Step 1: Write the failing tests** `tests/unit/test_labels.py`

```python
import string

import pytest

from gateway.labels import MAX_LABELS, build_labels, label_table, load_labels, save_labels
from gateway.layouts import load_layouts


def test_label_table_follows_deciders_rule(qwen_tok):
    labels = label_table(qwen_tok)
    assert labels.names[:26] == list(string.ascii_uppercase)
    assert len(labels.names) == len(set(labels.ids)) == MAX_LABELS
    for name, token in zip(labels.names, labels.ids):
        assert qwen_tok.encode(name, add_special_tokens=False) == [token]


def test_round_trip_and_stale_detection(qwen_tok, tmp_path):
    layouts = load_layouts()
    table = build_labels(qwen_tok, layouts["decider_chat"])
    path = tmp_path / "labels.json"
    save_labels(path, table)
    assert load_labels(path, qwen_tok, layouts["decider_chat"]).ids == table["ids"]
    with pytest.raises(RuntimeError, match="layout header changed"):
        load_labels(path, qwen_tok, layouts["header"])


def test_missing_file_explains_how_to_fix(qwen_tok, tmp_path):
    with pytest.raises(RuntimeError, match="build_labels.py"):
        load_labels(tmp_path / "labels.json", qwen_tok, load_layouts()["decider_chat"])
```

- [ ] **Step 2: Run to see it fail**

Run: `uv run pytest tests/unit/test_labels.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'gateway.labels'`

- [ ] **Step 3: Implement `gateway/labels.py`**

```python
"""Option labels (A..Z, then AA..), each exactly one token. Built once per tokenizer and layout."""

import hashlib
import json
import string
from dataclasses import dataclass
from pathlib import Path

from gateway.layouts import Layout

MAX_LABELS = 255
NARROW = 10  # up to 10 options are rendered as plain text "(A) ..", as decider does


@dataclass(frozen=True)
class Labels:
    names: list[str]
    ids: list[int]


def label_table(tok) -> Labels:
    """decider's rule: the first 255 of A..Z, AA..ZZ that encode to a single token on their own."""
    letters = string.ascii_uppercase
    names, ids = [], []
    for name in list(letters) + [a + b for a in letters for b in letters]:
        encoded = tok.encode(name, add_special_tokens=False)
        if len(encoded) == 1:
            names.append(name)
            ids.append(encoded[0])
        if len(names) == MAX_LABELS:
            break
    if len(names) < MAX_LABELS or len(set(ids)) < MAX_LABELS:
        raise ValueError("tokenizer has fewer than 255 distinct single-token labels")
    return Labels(names, ids)


def tokenizer_sha256(tok) -> str:
    text = json.dumps(tok.get_vocab(), sort_keys=True) + str(tok.chat_template)
    return hashlib.sha256(text.encode()).hexdigest()


def build_labels(tok, layout: Layout) -> dict:
    """The label table plus the hashes it depends on. A..J are also checked right after the answer slot."""
    labels = label_table(tok)
    slot = tok.encode(layout.answer, add_special_tokens=False)
    for name, token in zip(labels.names[:NARROW], labels.ids[:NARROW]):
        if tok.encode(layout.answer + name, add_special_tokens=False) != slot + [token]:
            raise ValueError(f"layout {layout.name}: label {name!r} is not one token after {layout.answer!r}")
    return {
        "layout": layout.name,
        "layout_sha256": layout.sha256,
        "tokenizer_sha256": tokenizer_sha256(tok),
        "names": labels.names,
        "ids": labels.ids,
    }


def save_labels(path: Path, table: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(table, indent=1) + "\n")


def load_labels(path: Path, tok, layout: Layout) -> Labels:
    """Refuse stale tables: the tokenizer or the layout text changed since build_labels ran."""
    if not path.exists():
        raise RuntimeError(f"{path} missing: run scripts/build_labels.py")
    table = json.loads(path.read_text())
    if table["tokenizer_sha256"] != tokenizer_sha256(tok):
        raise RuntimeError(f"{path}: tokenizer changed, rerun scripts/build_labels.py")
    if table["layout_sha256"] != layout.sha256:
        raise RuntimeError(f"{path}: layout {layout.name} changed, rerun scripts/build_labels.py")
    return Labels(table["names"], table["ids"])
```

- [ ] **Step 4: Implement `scripts/build_labels.py`**

```python
"""Write data/<profile>/<layout>/labels.json for every prompt layout.

usage: uv run python scripts/build_labels.py --profile qwen3.6-27b
"""

import argparse

from transformers import AutoTokenizer

from gateway.config import Settings
from gateway.labels import build_labels, save_labels
from gateway.layouts import load_layouts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    s = Settings.from_profile(parser.parse_args().profile)
    tok = AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
    for name, layout in load_layouts().items():
        table = build_labels(tok, layout) | {"model": s.hf_model, "revision": s.hf_revision}
        path = s.data_dir(name) / "labels.json"
        save_labels(path, table)
        print(f"wrote {path} ({len(table['ids'])} labels)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run the tests and the script once**

Run: `uv run pytest tests/unit -q && uv run python scripts/build_labels.py --profile qwen3.6-27b`
Expected: tests pass, and the script prints three `wrote data/qwen3.6-27b/<layout>/labels.json (255 labels)` lines.

- [ ] **Step 6: Commit** (the generated tables are committed in Task 15, after bring-up)

```bash
git add gateway/labels.py scripts/build_labels.py tests/unit/test_labels.py
git commit -m "feat(labels): build single-token label tables" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Chat frame and row builder

This task decides parity and prefix sharing. decider tokenizes each piece **separately**, in this order: chat head, context, question, options, chat tail, answer. More than 10 options are built as `encode(option_open) + [label id] + encode(option_close)`.

**Files:**
- Create: `gateway/prompts.py`, `tests/unit/test_prompts.py`, `tests/unit/golden/` (generated)
- Modify: `tests/helpers.py` (add `QUICKSTART`, `STATE`)

**Interfaces:**
- Consumes: `Layout`, `load_layouts` (Task 3); `Rendered`, `render_question` (Task 4); `Labels`, `label_table`, `NARROW` (Task 5); `PROFILES` and `tokenizer_for` (Task 2)
- Produces:
  - `ChatFrame(head: list[int], tail: list[int])` and `chat_frame(tok, layout) -> ChatFrame`
  - `Row(question_id: str, perm: list[int], ids: list[int], label_ids: list[int])`
  - `Batch(rows: list[Row], shared_len: int)` with the property `input_tokens: int`
  - `build_rows(tok, frame, layout, labels, state: str, questions: dict[str, Rendered], perms: dict[str, list[list[int]]]) -> Batch`

- [ ] **Step 1: Add the sample request to `tests/helpers.py`**

Append:
```python
QUICKSTART = {
    "department": {
        "type": "choice",
        "instructions": "Which team should handle this",
        "criteria": {
            "billing": "Payment or subscription issues",
            "technical": "Bugs or integration problems",
            "sales": "Pricing or account questions",
        },
    },
    "frustration": {
        "type": "score",
        "instructions": "How frustrated the customer appears",
        "criteria": ["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"],
    },
    "is_urgent": {"type": "noul", "instructions": "The message conveys urgency or time-sensitivity"},
}
STATE = "Hi, my Stripe integration keeps failing and I'm losing sales. Please help ASAP."
```

Then write the failing tests in `tests/unit/test_prompts.py`:
```python
from pathlib import Path

import pytest

from gateway.labels import label_table
from gateway.layouts import load_layouts
from gateway.prompts import build_rows, chat_frame
from gateway.questions import render_question
from gateway.schema import Question
from tests.helpers import PROFILES, QUICKSTART, STATE, tokenizer_for

GOLDEN = Path(__file__).parent / "golden"
LAYOUTS = load_layouts()


def batch_for(tok, layout_name, questions=QUICKSTART, orders=None):
    layout = LAYOUTS[layout_name]
    rendered = {k: render_question(Question(**v), layout) for k, v in questions.items()}
    perms = {k: orders or [list(range(len(r.options)))] for k, r in rendered.items()}
    return build_rows(tok, chat_frame(tok, layout), layout, label_table(tok), STATE, rendered, perms)


def assert_golden(name: str, text: str) -> None:
    path = GOLDEN / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        pytest.fail(f"wrote new golden {path}; review it, then rerun")
    assert text == path.read_text()


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("layout_name", sorted(LAYOUTS))
def test_prompts_match_golden(profile, layout_name):
    tok = tokenizer_for(profile)
    batch = batch_for(tok, layout_name)
    assert_golden(f"{profile}/{layout_name}.txt", "\n=====\n".join(tok.decode(r.ids) for r in batch.rows))


@pytest.mark.parametrize("layout_name", sorted(LAYOUTS))
def test_rows_share_the_reported_prefix(qwen_tok, layout_name):
    batch = batch_for(qwen_tok, layout_name)
    first = batch.rows[0].ids[: batch.shared_len]
    assert all(r.ids[: batch.shared_len] == first for r in batch.rows)
    assert batch.input_tokens == batch.shared_len + sum(len(r.ids) - batch.shared_len for r in batch.rows)


def test_prefix_sharing_by_layout(qwen_tok):
    head = len(chat_frame(qwen_tok, LAYOUTS["question_first"]).head)
    assert batch_for(qwen_tok, "question_first").shared_len == head
    assert batch_for(qwen_tok, "header").shared_len > batch_for(qwen_tok, "decider_chat").shared_len > head


def test_rows_end_at_the_answer_slot_with_one_label_per_option(qwen_tok):
    batch = batch_for(qwen_tok, "decider_chat")
    for row in batch.rows:
        assert qwen_tok.decode(row.ids[-4:]).endswith("Answer: (")
    assert [len(r.label_ids) for r in batch.rows] == [3, 3, 2]


def test_wide_choice_splices_label_tokens(qwen_tok):
    labels = label_table(qwen_tok)
    wide = {"q": {"type": "choice", "instructions": "Pick", "criteria": {f"opt{i}": None for i in range(12)}}}
    row = batch_for(qwen_tok, "decider_chat", wide).rows[0]
    for token in labels.ids[:12]:
        assert token in row.ids
    assert row.label_ids == labels.ids[:12]


def test_reversed_order_shows_options_reversed(qwen_tok):
    two = {"q": {"type": "choice", "instructions": "Pick", "criteria": {"first": None, "second": None}}}
    row = batch_for(qwen_tok, "decider_chat", two, orders=[[1, 0]]).rows[0]
    assert "(A) second\n(B) first" in qwen_tok.decode(row.ids)
    assert row.perm == [1, 0]
```

- [ ] **Step 2: Run to see it fail**

Run: `uv run pytest tests/unit/test_prompts.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'gateway.prompts'`

- [ ] **Step 3: Implement `gateway/prompts.py`**

```python
"""Token ids for one question per row, built part by part like decider so shared prefixes match exactly."""

from dataclasses import dataclass

from gateway.labels import NARROW, Labels
from gateway.layouts import Layout
from gateway.questions import Rendered

SENTINEL = "@@USER_CONTENT@@"
CLOSE_THINKING = {"<think>\n": "</think>\n\n", "<think>": "</think>\n\n", "<|channel>thought\n": "<channel|>"}


def encode(tok, text: str) -> list[int]:
    return tok.encode(text, add_special_tokens=False)


@dataclass(frozen=True)
class ChatFrame:
    head: list[int]  # chat template before the user content
    tail: list[int]  # after it: end of user turn, assistant turn opened with thinking closed


def chat_frame(tok, layout: Layout) -> ChatFrame:
    """decider's ChatTemplate: one user turn, no system prompt, thinking off."""
    kwargs = {"enable_thinking": False} if "enable_thinking" in str(tok.chat_template) else {}
    text = tok.apply_chat_template(
        [{"role": "user", "content": SENTINEL}], tokenize=False, add_generation_prompt=True, **kwargs
    )
    head, tail = text.split(SENTINEL)
    for opened, closed in CLOSE_THINKING.items():
        if tail.endswith(opened):
            tail += closed
            break
    frame = ChatFrame(encode(tok, head), encode(tok, tail))
    if encode(tok, tail + layout.answer) != frame.tail + encode(tok, layout.answer):
        raise ValueError(f"layout {layout.name}: the chat template tail merges with the answer slot")
    return frame


@dataclass(frozen=True)
class Row:
    question_id: str
    perm: list[int]  # perm[j] = index of the caller's option shown at position j
    ids: list[int]  # the full prompt, ending at the answer slot
    label_ids: list[int]  # tokens to read at the last position, one per shown option


@dataclass(frozen=True)
class Batch:
    rows: list[Row]
    shared_len: int  # leading tokens that every row has in common

    @property
    def input_tokens(self) -> int:
        """Shared prefix counted once, like Jev counts the state once."""
        return self.shared_len + sum(len(r.ids) - self.shared_len for r in self.rows)


def option_ids(tok, layout: Layout, labels: Labels, texts: list[str]) -> list[int]:
    """Up to 10 options: one text encode. More: label token ids spliced in so every label is one token."""
    if len(texts) <= NARROW:
        return encode(tok, "".join(layout.option.format(label=labels.names[j], text=t) for j, t in enumerate(texts)))
    ids = []
    for j, text in enumerate(texts):
        ids += encode(tok, layout.option_open) + [labels.ids[j]] + encode(tok, layout.option_close.format(text=text))
    return ids


def shared_len(frame: ChatFrame, layout: Layout, parts: dict[str, list[int]]) -> int:
    """Head plus every part placed before the first per-question part."""
    n = len(frame.head)
    for part in layout.order:
        if part in ("question", "options"):
            return n
        n += len(parts[part])
    return n


def build_rows(
    tok,
    frame: ChatFrame,
    layout: Layout,
    labels: Labels,
    state: str,
    questions: dict[str, Rendered],
    perms: dict[str, list[list[int]]],
) -> Batch:
    """One row per (question, option order). Parts shared by all rows are encoded once."""
    parts = {"context": encode(tok, layout.context.format(state=state))}
    if "questions" in layout.order:
        listed = "\n".join(layout.question_item.format(question=q.text) for q in questions.values())
        parts["questions"] = encode(tok, layout.questions.format(questions=listed))
    answer = encode(tok, layout.answer)
    rows = []
    for qid, q in questions.items():
        parts["question"] = encode(tok, layout.question.format(question=q.text))
        for perm in perms[qid]:
            shown = [q.options[i] for i in perm]
            parts["options"] = option_ids(tok, layout, labels, shown)
            ids = list(frame.head)
            for part in layout.order:
                ids += parts[part]
            rows.append(Row(qid, perm, ids + frame.tail + answer, labels.ids[: len(shown)]))
    return Batch(rows, shared_len(frame, layout, parts))
```

- [ ] **Step 4: Generate the goldens, review them, rerun**

Run: `uv run pytest tests/unit/test_prompts.py -q` (the first run fails with "wrote new golden", nine times)
Then open each file in `tests/unit/golden/<profile>/<layout>.txt` and check, for every profile:
- `decider_chat`: user turn = `Context:\n<state>\n\nQuestion: ...\nOptions:\n(A) ...`; the assistant turn has thinking closed and ends in `Answer: (`.
- `header`: the question list comes before `Context:`.
- `question_first`: `Question:` comes before `Context:`.
- Gemma: the turn markers belong to Gemma's template, and no thinking block is left open.

Run again: `uv run pytest tests/unit -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add gateway/prompts.py tests/helpers.py tests/unit/test_prompts.py tests/unit/golden
git commit -m "feat(prompts): build piecewise token rows per layout" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Decider parity

This test proves the `decider_chat` layout reproduces `decider.serve.prepare(independent=True, isolated=False, chat=...)` exactly. decider runs in its own venv because of its `numpy<2` pin. Its package `__init__` is empty, so torch is not needed for these modules.

**Files:**
- Create: `tests/parity/cases.json`, `scripts/decider_fixtures.py`, `tests/parity/test_decider_parity.py`, `tests/parity/fixtures/*.json` (generated)

**Interfaces:**
- Consumes: `build_rows`, `chat_frame` (Task 6); `render_question`, `render_state` (Task 4); `label_table`, `Labels` (Task 5); `load_layouts` (Task 3); `PROFILES`, `tokenizer_for` (Task 2)
- Produces: fixtures `tests/parity/fixtures/<profile>.json` = `{"decider": "1.5.0", "label_ids": [...], "rows": [[ids...] per row] per case}`

- [ ] **Step 1: Write `tests/parity/cases.json`**

```json
[
  {"state": "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.",
   "questions": {
     "department": {"type": "choice", "instructions": "Which team should handle this",
                    "criteria": {"billing": "Payment or subscription issues", "technical": "Bugs or integration problems", "sales": "Pricing or account questions"}},
     "frustration": {"type": "score", "instructions": "How frustrated the customer appears",
                     "criteria": ["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"]},
     "is_urgent": {"type": "noul", "instructions": "The message conveys urgency or time-sensitivity"}}},
  {"state": {"ticket": {"id": 7, "records": [{"t": 1}, {"t": 2}, {"t": 3}, {"t": 4}, {"t": 5}, {"t": 6}, {"t": 7}, {"t": 8}, {"t": 9}]}},
   "questions": {
     "kind": {"type": "choice", "instructions": {"question": "Which kind?", "hint": "records"}, "criteria": ["alpha", "beta", "gamma"]},
     "escalate": {"type": "noul", "instructions": "Escalate?", "criteria": {"true": "a human must look", "false": "automation is fine"}}}},
  {"state": "Invoice 42: 3 items, total 120.00 EUR, due 2026-10-01.",
   "questions": {
     "category": {"type": "choice", "instructions": "Which ledger category?",
                  "criteria": {"c0": "Travel", "c1": null, "c2": "Software", "c3": null, "c4": "Hardware", "c5": null,
                               "c6": "Meals", "c7": null, "c8": "Rent", "c9": null, "c10": "Utilities", "c11": {"note": "other"}}},
     "overdue": {"type": "noul", "criteria": {"true": "The invoice is overdue"}},
     "risk": {"type": "score", "instructions": "Payment risk", "criteria": {"1": "medium", "0": "low", "2": "high"}}}},
  {"state": "Café naïve — 東京 🚀 {braces} stay literal",
   "questions": {"lang": {"type": "choice", "instructions": "Main language?", "criteria": {"fr": "French", "ja": "Japanese"}}}}
]
```

- [ ] **Step 2: Write `scripts/decider_fixtures.py`**

```python
"""Record decider's token ids for tests/parity/cases.json. Runs in its own venv (decider pins numpy<2):

uv venv .cache/decider-venv
uv pip install --python .cache/decider-venv --no-deps decider-ai==1.5.0
uv pip install --python .cache/decider-venv transformers jinja2 "numpy<2" huggingface_hub
.cache/decider-venv/bin/python scripts/decider_fixtures.py --profile qwen3.6-27b
"""

import argparse
import json
from pathlib import Path

from decider import systemone as S1
from decider.prompt import chat_template, label_table
from decider.prompt_fast import build_rows
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent


def read_profile(name: str) -> dict[str, str]:
    """Plain parse: this venv does not have the gateway package."""
    lines = (ROOT / "profiles" / f"{name}.env").read_text().splitlines()
    return dict(line.split("=", 1) for line in lines if line.strip() and not line.startswith("#"))


def decider_rows(tok, case: dict) -> list[list[int]]:
    """decider.serve.prepare(independent=True, isolated=False), without loading the model."""
    rqs = {k: S1.render_question(v) for k, v in case["questions"].items()}
    flat, _ = S1.plan_rows(rqs, isolated=False)
    rows = [[(r["question"], list(r["options"]))] for r in flat]
    items, _ = build_rows(tok, S1.render_state(case["state"]), rows, max_ctx_tokens=32768, chat=chat_template(tok))
    return [item["ids"] for item in items]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    name = parser.parse_args().profile
    env = read_profile(name)
    tok = AutoTokenizer.from_pretrained(env["HF_MODEL"], revision=env["HF_REVISION"])
    cases = json.loads((ROOT / "tests" / "parity" / "cases.json").read_text())
    out = {"decider": "1.5.0", "label_ids": label_table(tok)[1], "rows": [decider_rows(tok, c) for c in cases]}
    path = ROOT / "tests" / "parity" / "fixtures" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write the parity test** `tests/parity/test_decider_parity.py`

```python
import json
from pathlib import Path

import pytest

from gateway.labels import label_table
from gateway.layouts import load_layouts
from gateway.prompts import build_rows, chat_frame
from gateway.questions import render_question, render_state
from gateway.schema import Question
from tests.helpers import PROFILES, tokenizer_for

HERE = Path(__file__).parent
CASES = json.loads((HERE / "cases.json").read_text())


@pytest.mark.parametrize("profile", PROFILES)
def test_decider_chat_matches_decider_token_for_token(profile):
    fixture = HERE / "fixtures" / f"{profile}.json"
    if not fixture.exists():
        pytest.fail(f"{fixture} missing: generate it with scripts/decider_fixtures.py")
    expected = json.loads(fixture.read_text())
    tok = tokenizer_for(profile)
    layout = load_layouts()["decider_chat"]
    labels = label_table(tok)
    assert labels.ids == expected["label_ids"]
    for case, rows in zip(CASES, expected["rows"], strict=True):
        questions = {k: render_question(Question(**v), layout) for k, v in case["questions"].items()}
        perms = {k: [list(range(len(q.options)))] for k, q in questions.items()}
        batch = build_rows(tok, chat_frame(tok, layout), layout, labels, render_state(case["state"]), questions, perms)
        assert [r.ids for r in batch.rows] == rows
```

- [ ] **Step 4: Create the decider venv and generate the fixtures**

```bash
uv venv .cache/decider-venv
uv pip install --python .cache/decider-venv --no-deps decider-ai==1.5.0
uv pip install --python .cache/decider-venv transformers jinja2 "numpy<2" huggingface_hub
for p in qwen3.8-27b qwen3.6-27b gemma-4-31b; do .cache/decider-venv/bin/python scripts/decider_fixtures.py --profile $p; done
```
Expected: three `wrote tests/parity/fixtures/<profile>.json` lines.

- [ ] **Step 5: Run parity**

Run: `uv run pytest tests/parity -q`
Expected: 3 passed. On a mismatch, decode both id lists with the tokenizer and diff them. Fix `prompts/decider_chat.toml` or `gateway/prompts.py`; never the fixture.

- [ ] **Step 6: Commit**

```bash
git add tests/parity scripts/decider_fixtures.py
git commit -m "test(parity): match decider chat layout tokens" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Option orders, calibration, answers

**Files:**
- Create: `gateway/orders.py`, `gateway/calibration.py`, `gateway/answers.py`, `data/qwen3.6-27b/decider_chat/calibration.json`, `tests/unit/test_orders.py`, `tests/unit/test_calibration.py`, `tests/unit/test_answers.py`

**Interfaces:**
- Consumes: `Rendered` (Task 4)
- Produces:
  - `orders.py`: `option_orders(n: int, setting: str) -> list[list[int]]` (raises `ValueError` on a bad setting) and `average_back(probs: list[list[float]], perms: list[list[int]]) -> list[float]`
  - `calibration.py`: `TYPES` and `load_temperatures(path) -> dict[str, float]`, plus `softmax(logprobs: list[float], temperature: float) -> list[float]`
  - `answers.py`: `choice_confidence(p)` and `score_confidence(p)`, plus `answer(q: Rendered, p: list[float]) -> dict`

- [ ] **Step 1: Write the failing tests**

`tests/unit/test_orders.py`:
```python
import pytest

from gateway.orders import average_back, option_orders


def test_settings():
    assert option_orders(3, "identity") == [[0, 1, 2]]
    assert option_orders(3, "identity+reversed") == [[0, 1, 2], [2, 1, 0]]
    assert option_orders(4, "cyclic:2") == [[0, 1, 2, 3], [2, 3, 0, 1]]
    assert option_orders(2, "cyclic:5") == [[0, 1], [1, 0]]
    with pytest.raises(ValueError):
        option_orders(3, "shuffle")
    with pytest.raises(ValueError):
        option_orders(3, "cyclic:0")


def test_average_back_maps_positions_to_caller_options():
    # identity favours shown position 0 (option 0); reversed favours shown position 0 (option 2)
    probs = [[0.7, 0.2, 0.1], [0.7, 0.2, 0.1]]
    assert average_back(probs, [[0, 1, 2], [2, 1, 0]]) == pytest.approx([0.4, 0.2, 0.4])
```

`tests/unit/test_calibration.py`:
```python
import json
import math

import pytest

from gateway.calibration import load_temperatures, softmax


def test_softmax_with_temperature():
    assert softmax([0.0, math.log(3)], 1.0) == pytest.approx([0.25, 0.75])
    assert softmax([0.0, 2.0], 2.0) == pytest.approx(softmax([0.0, 1.0], 1.0))


def test_missing_file_means_uncalibrated(tmp_path):
    assert load_temperatures(tmp_path / "calibration.json") == {"choice": 1.0, "score": 1.0, "noul": 1.0}


def test_partial_file_fills_defaults(tmp_path):
    f = tmp_path / "calibration.json"
    f.write_text(json.dumps({"choice": 1.5, "source": "test"}))
    assert load_temperatures(f) == {"choice": 1.5, "score": 1.0, "noul": 1.0}
```

`tests/unit/test_answers.py`:
```python
import pytest

from gateway.answers import answer, choice_confidence, score_confidence
from gateway.questions import Rendered


def test_confidence_matches_typesafe_examples():
    assert choice_confidence([0.88, 0.12, 0.0]) == pytest.approx(0.82)
    assert choice_confidence([0.85, 0.0, 0.15]) == pytest.approx(0.775)
    assert score_confidence([0.65, 0.30, 0.05]) == pytest.approx(0.40)
    assert score_confidence([0.0, 0.0, 0.1, 0.3, 0.6]) == pytest.approx(0.5833, abs=1e-4)


def test_answer_shapes():
    choice = Rendered("choice", "t", ["a: x", "b"], ["a", "b"])
    assert answer(choice, [0.25, 0.75]) == {
        "type": "choice",
        "choice": "b",
        "confidence": 0.5,
        "probabilities": {"a": 0.25, "b": 0.75},
    }
    score = Rendered("score", "t", ["0: lo", "1: hi"], [0, 1], ["lo", "hi"])
    assert answer(score, [0.25, 0.75]) == {
        "type": "score",
        "score": 0.75,
        "confidence": 0.5,
        "legend": {"0": "lo", "1": "hi"},
        "probabilities": {"0": 0.25, "1": 0.75},
    }
    noul = Rendered("noul", "t", ["no", "yes"], [False, True])
    assert answer(noul, [0.123456, 0.876544]) == {"type": "noul", "noul": 0.8765}
```

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest tests/unit/test_orders.py tests/unit/test_calibration.py tests/unit/test_answers.py -q`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `gateway/orders.py`**

```python
"""Show options in several orders and average the answers back to the caller's option positions."""


def option_orders(n: int, setting: str) -> list[list[int]]:
    """Permutations of range(n); perm[j] is the caller's option shown at position j."""
    identity = list(range(n))
    if setting == "identity":
        return [identity]
    if setting == "identity+reversed":
        return [identity, identity[::-1]]
    if setting.startswith("cyclic:"):
        k = int(setting.removeprefix("cyclic:"))
        if k < 1:
            raise ValueError("cyclic:<k> needs k >= 1")
        shifts = sorted({round(i * n / k) % n for i in range(k)})
        return [identity[s:] + identity[:s] for s in shifts]
    raise ValueError(f"unknown option_orders {setting!r}: use identity, identity+reversed or cyclic:<k>")


def average_back(probs: list[list[float]], perms: list[list[int]]) -> list[float]:
    total = [0.0] * len(perms[0])
    for p, perm in zip(probs, perms, strict=True):
        for shown, caller in enumerate(perm):
            total[caller] += p[shown]
    return [x / len(perms) for x in total]
```

- [ ] **Step 4: Implement `gateway/calibration.py`**

```python
"""Softmax temperatures per question type (fitted in phase 2; 1.0 means uncalibrated)."""

import json
import logging
import math
from pathlib import Path

log = logging.getLogger(__name__)
TYPES = ("choice", "score", "noul")


def load_temperatures(path: Path) -> dict[str, float]:
    if not path.exists():
        log.warning("%s missing: temperature 1.0 (uncalibrated)", path)
        return {t: 1.0 for t in TYPES}
    data = json.loads(path.read_text())
    return {t: float(data.get(t, 1.0)) for t in TYPES}


def softmax(logprobs: list[float], temperature: float) -> list[float]:
    top = max(logprobs)
    weights = [math.exp((x - top) / temperature) for x in logprobs]
    total = sum(weights)
    return [w / total for w in weights]
```

- [ ] **Step 5: Implement `gateway/answers.py`**

```python
"""Probabilities → Jev answers, with TypeSafe's confidence formulas (system-one-adapter confidence_metrics)."""

from gateway.questions import Rendered

DECIMALS = 4


def choice_confidence(p: list[float]) -> float:
    """(p_max − 1/K) / (1 − 1/K): 0 for a uniform guess, 1 when certain."""
    k = len(p)
    return 1.0 if k == 1 else max(0.0, (max(p) - 1 / k) / (1 - 1 / k))


def score_confidence(p: list[float]) -> float:
    """1 − expected distance from the most likely level, relative to a uniform guess."""
    n = len(p)
    if n == 1:
        return 1.0
    mode = max(range(n), key=p.__getitem__)
    spread = sum(x * abs(i - mode) for i, x in enumerate(p))
    uniform = sum(abs(i - (n - 1) / 2) for i in range(n)) / n
    return max(0.0, 1.0 - spread / uniform)


def answer(q: Rendered, p: list[float]) -> dict:
    """p is in the caller's option order and sums to 1."""
    if q.type == "noul":
        return {"type": "noul", "noul": round(p[1], DECIMALS)}
    if q.type == "choice":
        best = max(range(len(p)), key=p.__getitem__)
        return {
            "type": "choice",
            "choice": q.names[best],
            "confidence": round(choice_confidence(p), DECIMALS),
            "probabilities": {name: round(x, DECIMALS) for name, x in zip(q.names, p)},
        }
    return {
        "type": "score",
        "score": round(sum(i * x for i, x in enumerate(p)), DECIMALS),
        "confidence": round(score_confidence(p), DECIMALS),
        "legend": {str(i): d for i, d in enumerate(q.legend)},
        "probabilities": {str(i): round(x, DECIMALS) for i, x in enumerate(p)},
    }
```

- [ ] **Step 6: Seed decider's published temperature for Qwen3.6-27B**

`data/qwen3.6-27b/decider_chat/calibration.json`:
```json
{"choice": 1.943, "score": 1.943, "noul": 1.943,
 "source": "decider-ai 1.5.0 docs/SERVING.md section 8: Qwen3.6-27B bf16, chat layout. Replaced by our own fit in phase 2."}
```

- [ ] **Step 7: Run the tests**

Run: `uv run pytest tests/unit -q`
Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add gateway/orders.py gateway/calibration.py gateway/answers.py data/qwen3.6-27b/decider_chat/calibration.json tests/unit/test_orders.py tests/unit/test_calibration.py tests/unit/test_answers.py
git commit -m "feat(answers): add orders, temperatures and jev answers" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: vLLM readout

**Files:**
- Create: `gateway/readout.py`, `tests/unit/test_readout.py`

**Interfaces:**
- Consumes: `RequestError` (Task 3)
- Produces:
  - `MAX_LABEL_IDS = 128`
  - `Readout(client: httpx.AsyncClient, model: str, warm_min_prefix_tokens: int = 512)`
  - `await readout.letter_logprobs(prompts: list[list[int]], label_ids: list[list[int]], shared_len: int) -> list[list[float]]`, which returns one list per prompt in its `label_ids` order
  - Transport failures raise `httpx.TransportError`; the app maps them to 503.

- [ ] **Step 1: Write the failing tests** `tests/unit/test_readout.py`

```python
import json

import httpx
import pytest

from gateway.readout import Readout
from gateway.schema import RequestError


def fake_vllm(seen: list):
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        seen.append(body)
        logprobs = {f"token_id:{t}": -float(t) for t in body["logprob_token_ids"]}
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"index": i, "logprobs": {"top_logprobs": [logprobs]}} for i in reversed(range(len(body["prompt"])))
                ]
            },
        )

    return handler


def readout(handler) -> Readout:
    client = httpx.AsyncClient(base_url="http://vllm", transport=httpx.MockTransport(handler))
    return Readout(client, "m", warm_min_prefix_tokens=512)


async def test_reads_label_logprobs_in_label_order():
    seen = []
    out = await readout(fake_vllm(seen)).letter_logprobs([[1, 2], [1, 3]], [[30, 10], [20]], shared_len=1)
    assert out == [[-30.0, -10.0], [-20.0]]
    assert seen[0]["max_tokens"] == 1
    assert seen[0]["logprob_token_ids"] == [10, 20, 30]
    assert seen[0]["prompt"] == [[1, 2], [1, 3]]


async def test_more_than_128_labels_are_split_across_calls():
    seen = []
    ids = list(range(200))
    out = await readout(fake_vllm(seen)).letter_logprobs([[1]], [ids], shared_len=0)
    assert [len(b["logprob_token_ids"]) for b in seen] == [128, 72]
    assert out == [[-float(i) for i in ids]]


async def test_long_shared_prefix_warms_the_first_row_alone():
    seen = []
    await readout(fake_vllm(seen)).letter_logprobs([[1], [2], [3]], [[5], [5], [5]], shared_len=600)
    assert [len(b["prompt"]) for b in seen] == [1, 2]


async def test_context_too_long_becomes_a_refusal():
    def handler(request):
        return httpx.Response(400, text="This model's maximum context length is 32768 tokens.")

    with pytest.raises(RequestError, match="maximum context length"):
        await readout(handler).letter_logprobs([[1]], [[5]], shared_len=0)


async def test_unreachable_vllm_raises_transport_error():
    def handler(request):
        raise httpx.ConnectError("down")

    with pytest.raises(httpx.TransportError):
        await readout(handler).letter_logprobs([[1]], [[5]], shared_len=0)
```

- [ ] **Step 2: Run to see it fail**

Run: `uv run pytest tests/unit/test_readout.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'gateway.readout'`

- [ ] **Step 3: Implement `gateway/readout.py`**

```python
"""Read the log-probabilities of each row's option labels at its last position, via vLLM /v1/completions."""

import httpx

from gateway.schema import RequestError

MAX_LABEL_IDS = 128  # vLLM's cap on logprob_token_ids per request (MAX_LOGPROB_TOKEN_IDS)


class Readout:
    def __init__(self, client: httpx.AsyncClient, model: str, warm_min_prefix_tokens: int = 512):
        self.client = client
        self.model = model
        self.warm_min_prefix_tokens = warm_min_prefix_tokens

    async def letter_logprobs(
        self, prompts: list[list[int]], label_ids: list[list[int]], shared_len: int
    ) -> list[list[float]]:
        """One list per prompt, in the order of that prompt's label_ids."""
        if len(prompts) > 1 and shared_len >= self.warm_min_prefix_tokens:
            # compute the long shared prefix once so the other rows hit vLLM's prefix cache
            first = await self._read(prompts[:1], label_ids[:1])
            return first + await self._read(prompts[1:], label_ids[1:])
        return await self._read(prompts, label_ids)

    async def _read(self, prompts: list[list[int]], label_ids: list[list[int]]) -> list[list[float]]:
        wanted = sorted({i for ids in label_ids for i in ids})
        found: list[dict[int, float]] = [{} for _ in prompts]
        for start in range(0, len(wanted), MAX_LABEL_IDS):
            for row, got in zip(found, await self._call(prompts, wanted[start : start + MAX_LABEL_IDS])):
                row.update(got)
        return [[row[i] for i in ids] for row, ids in zip(found, label_ids)]

    async def _call(self, prompts: list[list[int]], ids: list[int]) -> list[dict[int, float]]:
        payload = {
            "model": self.model,
            "prompt": prompts,
            "max_tokens": 1,
            "temperature": 0,
            "logprobs": 0,
            "logprob_token_ids": ids,
            "return_tokens_as_token_ids": True,
            "add_special_tokens": False,
        }
        r = await self.client.post("/v1/completions", json=payload)
        if r.status_code == 400 and "maximum context length" in r.text:
            raise RequestError("prompt is longer than the maximum context length")
        r.raise_for_status()
        choices = sorted(r.json()["choices"], key=lambda c: c["index"])
        return [
            {int(k.removeprefix("token_id:")): v for k, v in c["logprobs"]["top_logprobs"][0].items()} for c in choices
        ]
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/unit -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add gateway/readout.py tests/unit/test_readout.py
git commit -m "feat(readout): read label logprobs from vllm" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: `decide()`: the whole systemone flow

This is one async function, so the phase-3 router can call it in-process.

**Files:**
- Create: `gateway/decide.py`, `tests/unit/test_decide.py`

**Interfaces:**
- Consumes: everything from Tasks 2–9
- Produces:
  - `Engine`, a frozen dataclass with fields `settings`, `tokenizer`, `layouts: dict[str, Layout]`, `frames: dict[str, ChatFrame]`, `labels: dict[str, Labels]`, `temperatures: dict[str, dict[str, float]]` and `readout` (any object with `letter_logprobs`)
  - `async decide(engine: Engine, request: SystemOneRequest) -> dict`, which returns a Jev response dict

- [ ] **Step 1: Write the failing tests** `tests/unit/test_decide.py`

```python
import dataclasses

import pytest

from gateway.calibration import softmax
from gateway.config import Settings
from gateway.decide import Engine, decide
from gateway.labels import label_table
from gateway.layouts import load_layouts
from gateway.prompts import chat_frame
from gateway.schema import RequestError, SystemOneRequest
from tests.helpers import QUICKSTART, STATE


class FavourFirstLabel:
    """Fake readout: label A always most likely (logprobs 0, -1, -2, ...)."""

    def __init__(self):
        self.calls = []

    async def letter_logprobs(self, prompts, label_ids, shared_len):
        self.calls.append((prompts, label_ids, shared_len))
        return [[-float(j) for j in range(len(ids))] for ids in label_ids]


@pytest.fixture
def engine(qwen_tok):
    layouts = load_layouts()
    return Engine(
        settings=Settings.from_profile("qwen3.6-27b"),
        tokenizer=qwen_tok,
        layouts=layouts,
        frames={n: chat_frame(qwen_tok, l) for n, l in layouts.items()},
        labels={n: label_table(qwen_tok) for n in layouts},
        temperatures={n: {"choice": 1.0, "score": 1.0, "noul": 1.0} for n in layouts},
        readout=FavourFirstLabel(),
    )


def request(**kw):
    return SystemOneRequest.model_validate({"state": STATE, "questions": QUICKSTART} | kw)


async def test_quickstart_answers_have_jev_shapes(engine):
    out = await decide(engine, request())
    p3 = softmax([0.0, -1.0, -2.0], 1.0)
    dept = out["answers"]["department"]
    assert dept["choice"] == "billing"
    assert list(dept["probabilities"].values()) == pytest.approx(p3, abs=1e-4)
    assert set(out["answers"]["frustration"]) == {"type", "score", "confidence", "legend", "probabilities"}
    assert out["answers"]["is_urgent"] == {"type": "noul", "noul": round(softmax([0.0, -1.0], 1.0)[1], 4)}
    assert out["model"] == "qwen3.6-27b"
    assert out["usage"]["output_tokens"] == 0 and out["usage"]["input_tokens"] > 0


async def test_reversed_orders_average_back(engine):
    out = await decide(engine, request(option_orders="identity+reversed"))
    p3 = softmax([0.0, -1.0, -2.0], 1.0)
    probs = list(out["answers"]["department"]["probabilities"].values())
    assert probs == pytest.approx([(p3[0] + p3[2]) / 2, p3[1], (p3[0] + p3[2]) / 2], abs=1e-4)
    assert len(engine.readout.calls[0][0]) == 6  # 3 questions x 2 orders


async def test_bad_overrides_are_refusals(engine):
    with pytest.raises(RequestError, match="unknown layout"):
        await decide(engine, request(layout="nope"))
    with pytest.raises(RequestError, match="unknown option_orders"):
        await decide(engine, request(option_orders="shuffle"))
    with pytest.raises(RequestError, match="must not be empty"):
        await decide(engine, SystemOneRequest.model_validate({"state": STATE, "questions": {}}))


async def test_too_long_prompt_is_refused_before_vllm(engine):
    small = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, max_model_len=50))
    with pytest.raises(RequestError, match="maximum context length"):
        await decide(small, request())
    assert engine.readout.calls == []
```

- [ ] **Step 2: Run to see it fail**

Run: `uv run pytest tests/unit/test_decide.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'gateway.decide'`

- [ ] **Step 3: Implement `gateway/decide.py`**

```python
"""The /v1/systemone flow as one async function, so the phase-3 router can call it in-process."""

import asyncio
from dataclasses import dataclass
from typing import Any

from gateway.answers import answer
from gateway.calibration import softmax
from gateway.config import Settings
from gateway.labels import Labels
from gateway.layouts import Layout
from gateway.orders import average_back, option_orders
from gateway.prompts import ChatFrame, build_rows
from gateway.questions import render_question, render_state
from gateway.schema import RequestError, SystemOneRequest


@dataclass(frozen=True)
class Engine:
    """Everything a decision needs, loaded once at startup."""

    settings: Settings
    tokenizer: Any
    layouts: dict[str, Layout]
    frames: dict[str, ChatFrame]
    labels: dict[str, Labels]
    temperatures: dict[str, dict[str, float]]
    readout: Any


async def decide(engine: Engine, request: SystemOneRequest) -> dict:
    s = engine.settings
    if not request.questions:
        raise RequestError("questions must not be empty")
    name = request.layout or s.prompt_layout
    if name not in engine.layouts:
        raise RequestError(f"unknown layout {name!r}; available: {sorted(engine.layouts)}")
    layout = engine.layouts[name]
    questions = {qid: render_question(q, layout) for qid, q in request.questions.items()}
    try:
        setting = request.option_orders or s.option_orders
        perms = {qid: option_orders(len(q.options), setting) for qid, q in questions.items()}
    except ValueError as e:
        raise RequestError(str(e)) from e

    batch = await asyncio.to_thread(
        build_rows,
        engine.tokenizer,
        engine.frames[name],
        layout,
        engine.labels[name],
        render_state(request.state),
        questions,
        perms,
    )
    longest = max(len(row.ids) for row in batch.rows)
    if longest >= s.max_model_len:
        raise RequestError(f"prompt is longer than the maximum context length ({longest} >= {s.max_model_len} tokens)")

    logprobs = await engine.readout.letter_logprobs(
        [r.ids for r in batch.rows], [r.label_ids for r in batch.rows], batch.shared_len
    )
    temperatures = engine.temperatures[name]
    reads: dict[str, list] = {qid: [] for qid in questions}
    for row, lp in zip(batch.rows, logprobs, strict=True):
        reads[row.question_id].append((softmax(lp, temperatures[questions[row.question_id].type]), row.perm))

    answers = {}
    for qid, q in questions.items():
        probs, perms_used = zip(*reads[qid])
        answers[qid] = answer(q, average_back(list(probs), list(perms_used)))
    return {
        "model": s.served_model,
        "answers": answers,
        "usage": {"input_tokens": batch.input_tokens, "output_tokens": 0},
    }
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest tests/unit -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add gateway/decide.py tests/unit/test_decide.py
git commit -m "feat(decide): wire systemone flow end to end" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: Chat proxy and FastAPI app

**Files:**
- Create: `gateway/chat.py`, `gateway/app.py`, `tests/unit/test_app.py`
- Modify: `tests/conftest.py` (add the `qwen_settings` fixture)

**Interfaces:**
- Consumes: `decide`, `Engine` (Task 10); `Readout` (Task 9); `load_labels`, `build_labels`, `save_labels` (Task 5); `load_temperatures` (Task 8); `chat_frame` (Task 6); `load_layouts` (Task 3); `Settings` (Task 2)
- Produces:
  - `create_app(settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI`, plus the module-level `app` used by uvicorn
  - Routes: `GET /health` (returns `{status, profile, served_model, layouts}`), `POST /v1/systemone`, `POST /v1/chat/completions`, `GET /v1/models`, and `GET|POST /v1/{path}` passthrough
  - `chat.route(body: dict) -> dict`, an identity hook for phase 3

- [ ] **Step 1: Replace `tests/conftest.py` with the version that adds `qwen_settings`**

```python
import dataclasses

import pytest

from gateway.config import Settings
from gateway.labels import build_labels, save_labels
from gateway.layouts import load_layouts
from tests.helpers import tokenizer_for


@pytest.fixture(scope="session")
def qwen_tok():
    return tokenizer_for("qwen3.6-27b")


@pytest.fixture
def qwen_settings(tmp_path, qwen_tok):
    """qwen3.6-27b settings whose data dir is a temp folder holding fresh label tables."""
    s = dataclasses.replace(Settings.from_profile("qwen3.6-27b"), data_root=tmp_path)
    for name, layout in load_layouts().items():
        save_labels(s.data_dir(name) / "labels.json", build_labels(qwen_tok, layout))
    return s
```

- [ ] **Step 2: Write the failing tests** `tests/unit/test_app.py`

```python
import dataclasses
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from gateway.app import create_app
from tests.helpers import QUICKSTART, STATE

SSE = b'data: {"choices": []}\n\ndata: [DONE]\n\n'


def fake_vllm(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/v1/completions":
        body = json.loads(request.content)
        top = {f"token_id:{t}": -0.001 * t for t in body["logprob_token_ids"]}
        return httpx.Response(
            200,
            json={"choices": [{"index": i, "logprobs": {"top_logprobs": [top]}} for i in range(len(body["prompt"]))]},
        )
    if path == "/v1/chat/completions":
        body = json.loads(request.content)
        if body.get("stream"):
            return httpx.Response(200, content=SSE, headers={"content-type": "text/event-stream"})
        return httpx.Response(200, json={"echo": body})
    if path == "/v1/models":
        return httpx.Response(200, json={"object": "list", "data": [{"id": "qwen3.6-27b", "object": "model"}]})
    if path == "/health":
        return httpx.Response(200)
    return httpx.Response(404, json={"path": path})


@pytest.fixture
def client(qwen_settings):
    with TestClient(create_app(qwen_settings, httpx.MockTransport(fake_vllm))) as c:
        yield c


def test_systemone_quickstart(client):
    r = client.post("/v1/systemone", json={"model": "jev-latest", "state": STATE, "questions": QUICKSTART})
    assert r.status_code == 200
    out = r.json()
    dept = out["answers"]["department"]
    assert set(dept["probabilities"]) == {"billing", "technical", "sales"}
    assert sum(dept["probabilities"].values()) == pytest.approx(1, abs=1e-3)
    assert set(out["answers"]["frustration"]["legend"]) == {"0", "1", "2"}
    assert set(out["answers"]["is_urgent"]) == {"type", "noul"}
    assert out["usage"]["output_tokens"] == 0


def test_capacity_refusal_carries_harness_marker(client):
    q = {"type": "choice", "instructions": "?", "criteria": {str(i): None for i in range(256)}}
    r = client.post("/v1/systemone", json={"state": "s", "questions": {"q": q}})
    assert r.status_code == 422
    assert "options per choice" in r.text


def test_chat_passthrough_plain_and_streaming(client):
    body = {"model": "qwen3.6-27b", "messages": [{"role": "user", "content": "hi"}]}
    assert client.post("/v1/chat/completions", json=body).json() == {"echo": body}
    r = client.post("/v1/chat/completions", json=body | {"stream": True})
    assert r.content == SSE
    assert r.headers["content-type"].startswith("text/event-stream")


def test_models_include_jev_aliases(client):
    ids = [m["id"] for m in client.get("/v1/models").json()["data"]]
    assert ids == ["qwen3.6-27b", "jev-latest", "jev-preview"]


def test_other_v1_paths_pass_through(client):
    r = client.get("/v1/unknown")
    assert r.status_code == 404
    assert r.json() == {"path": "/v1/unknown"}


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_api_key_is_enforced_when_set(qwen_settings):
    locked = dataclasses.replace(qwen_settings, api_key="secret")
    with TestClient(create_app(locked, httpx.MockTransport(fake_vllm))) as c:
        body = {"state": "s", "questions": {"q": {"type": "noul", "instructions": "ok?"}}}
        assert c.post("/v1/systemone", json=body).status_code == 401
        assert c.post("/v1/systemone", json=body, headers={"Authorization": "Bearer secret"}).status_code == 200


def test_vllm_down_is_503(qwen_settings):
    def down(request):
        raise httpx.ConnectError("down")

    with TestClient(create_app(qwen_settings, httpx.MockTransport(down))) as c:
        body = {"state": "s", "questions": {"q": {"type": "noul", "instructions": "ok?"}}}
        assert c.post("/v1/systemone", json=body).status_code == 503
```

- [ ] **Step 3: Run to see it fail**

Run: `uv run pytest tests/unit/test_app.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'gateway.app'`

- [ ] **Step 4: Implement `gateway/chat.py`**

```python
"""Chat and every other /v1/* call forwarded to vLLM unchanged, with a route() hook for phase 3."""

import json

import httpx
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

ALIASES = ("jev-latest", "jev-preview")


def route(body: dict) -> dict:
    """Phase 1: pass through. Phase 3 sets thinking and reasoning_effort from systemone answers."""
    return body


async def proxy(
    client: httpx.AsyncClient, method: str, path: str, content: bytes, params: dict | None = None
) -> StreamingResponse:
    """Stream vLLM's response back byte for byte (JSON and SSE alike)."""
    request = client.build_request(
        method, path, content=content, params=params, headers={"content-type": "application/json"}
    )
    upstream = await client.send(request, stream=True)
    return StreamingResponse(
        upstream.aiter_raw(),
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type"),
        background=BackgroundTask(upstream.aclose),
    )


async def chat_completions(client: httpx.AsyncClient, body: dict) -> StreamingResponse:
    return await proxy(client, "POST", "/v1/chat/completions", json.dumps(route(body)).encode())


async def list_models(client: httpx.AsyncClient, served_model: str) -> dict:
    """vLLM's model list plus the Jev aliases, which all mean the loaded model."""
    listing = (await client.get("/v1/models")).json()
    base = next(m for m in listing["data"] if m["id"] == served_model)
    listing["data"] += [{**base, "id": alias} for alias in ALIASES]
    return listing
```

- [ ] **Step 5: Implement `gateway/app.py`**

```python
"""FastAPI gateway: /v1/systemone, chat proxy, /v1/models, /health, and /v1/* passthrough to vLLM."""

from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from transformers import AutoTokenizer

from gateway import chat
from gateway.calibration import load_temperatures
from gateway.config import Settings
from gateway.decide import Engine, decide
from gateway.labels import load_labels
from gateway.layouts import load_layouts
from gateway.prompts import chat_frame
from gateway.readout import Readout
from gateway.schema import RequestError, SystemOneRequest


def load_engine(s: Settings, client: httpx.AsyncClient) -> Engine:
    tok = AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
    layouts = load_layouts()
    return Engine(
        settings=s,
        tokenizer=tok,
        layouts=layouts,
        frames={name: chat_frame(tok, layout) for name, layout in layouts.items()},
        labels={name: load_labels(s.data_dir(name) / "labels.json", tok, layout) for name, layout in layouts.items()},
        temperatures={name: load_temperatures(s.data_dir(name) / "calibration.json") for name in layouts},
        readout=Readout(client, s.served_model, s.warm_min_prefix_tokens),
    )


def require_key(request: Request) -> None:
    key = request.app.state.engine.settings.api_key
    if key and request.headers.get("authorization") != f"Bearer {key}":
        raise HTTPException(status_code=401, detail="invalid or missing API key")


def create_app(settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        s = settings or Settings.from_env()
        async with httpx.AsyncClient(base_url=s.vllm_url, timeout=600, transport=transport) as client:
            app.state.client = client
            app.state.engine = load_engine(s, client)
            yield

    app = FastAPI(title="jev-brain gateway", lifespan=lifespan)
    auth = [Depends(require_key)]

    @app.exception_handler(RequestError)
    async def refused(request: Request, exc: RequestError):
        return JSONResponse({"error": {"message": str(exc)}}, status_code=422)

    @app.exception_handler(httpx.TransportError)
    async def vllm_down(request: Request, exc: httpx.TransportError):
        return JSONResponse({"error": {"message": "model server unavailable"}}, status_code=503)

    @app.get("/health")
    async def health(request: Request):
        engine = request.app.state.engine
        try:
            ok = (await request.app.state.client.get("/health")).status_code == 200
        except httpx.TransportError:
            ok = False
        body = {
            "status": "ok" if ok else "vllm unavailable",
            "profile": engine.settings.profile,
            "served_model": engine.settings.served_model,
            "layouts": sorted(engine.layouts),
        }
        return JSONResponse(body, status_code=200 if ok else 503)

    @app.post("/v1/systemone", dependencies=auth)
    async def systemone(body: SystemOneRequest, request: Request):
        return await decide(request.app.state.engine, body)

    @app.post("/v1/chat/completions", dependencies=auth)
    async def chat_completions(request: Request):
        return await chat.chat_completions(request.app.state.client, await request.json())

    @app.get("/v1/models", dependencies=auth)
    async def models(request: Request):
        return await chat.list_models(request.app.state.client, request.app.state.engine.settings.served_model)

    @app.api_route("/v1/{path:path}", methods=["GET", "POST"], dependencies=auth)
    async def passthrough(path: str, request: Request):
        return await chat.proxy(
            request.app.state.client, request.method, f"/v1/{path}", await request.body(), dict(request.query_params)
        )

    return app


app = create_app()
```

- [ ] **Step 6: Run the tests**

Run: `uv run pytest tests/unit -q && uv run ruff check .`
Expected: all pass, and ruff is clean.

- [ ] **Step 7: Commit**

```bash
git add gateway/chat.py gateway/app.py tests/conftest.py tests/unit/test_app.py
git commit -m "feat(app): serve systemone and proxy chat" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 12: Docker, compose, first bring-up (qwen3.6-27b)

**Files:**
- Create: `docker/vllm-entrypoint.sh`, `docker/gateway.Dockerfile`, `.dockerignore`, `compose.yaml`

**Interfaces:**
- Consumes: the profiles (Task 2); `gateway.app:app` (Task 11); the labels in `data/<profile>/` (Task 5 script)
- Produces:
  - `docker compose --env-file profiles/<p>.env up -d` starts `vllm` (127.0.0.1:8000) and `gateway` (127.0.0.1:9000)
  - The gateway starts only after vLLM is healthy.

- [ ] **Step 1: `docker/vllm-entrypoint.sh`**

```bash
#!/usr/bin/env bash
# Build `vllm serve` flags from the profile env; optional flags only when set.
set -euo pipefail
args=(
  "$HF_MODEL" --revision "$HF_REVISION" --tokenizer-revision "$HF_REVISION"
  --served-model-name "$SERVED_MODEL" --host 0.0.0.0 --port 8000
  --enable-prefix-caching --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION:-0.90}"
  --max-model-len "$MAX_MODEL_LEN"
  --reasoning-parser "$REASONING_PARSER" --enable-auto-tool-choice --tool-call-parser "$TOOL_PARSER"
)
if [[ "${LANGUAGE_MODEL_ONLY:-0}" == "1" ]]; then args+=(--language-model-only); fi
if [[ -n "${CHAT_TEMPLATE:-}" ]]; then args+=(--chat-template "$CHAT_TEMPLATE"); fi
if [[ -n "${CHAT_TEMPLATE_KWARGS:-}" ]]; then args+=(--default-chat-template-kwargs "$CHAT_TEMPLATE_KWARGS"); fi
exec vllm serve "${args[@]}"
```

- [ ] **Step 2: `docker/gateway.Dockerfile` and `.dockerignore`**

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY gateway ./gateway
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "gateway.app:app", "--host", "0.0.0.0", "--port", "9000"]
```

`.dockerignore`:
```
.git
.venv
.cache
.firecrawl
docs
tests
data
prompts
```

- [ ] **Step 3: `compose.yaml`**

```yaml
# One model per run: docker compose --env-file profiles/<profile>.env up -d
services:
  vllm:
    image: vllm/vllm-openai:v0.30.0
    entrypoint: ["/bin/bash", "/opt/jev/vllm-entrypoint.sh"]
    ipc: host
    deploy:
      resources:
        reservations:
          devices: [{driver: nvidia, count: all, capabilities: [gpu]}]
    environment:
      HF_MODEL: ${HF_MODEL}
      HF_REVISION: ${HF_REVISION}
      SERVED_MODEL: ${SERVED_MODEL}
      MAX_MODEL_LEN: ${MAX_MODEL_LEN}
      REASONING_PARSER: ${REASONING_PARSER}
      TOOL_PARSER: ${TOOL_PARSER}
      LANGUAGE_MODEL_ONLY: ${LANGUAGE_MODEL_ONLY:-0}
      CHAT_TEMPLATE: ${CHAT_TEMPLATE:-}
      CHAT_TEMPLATE_KWARGS: ${CHAT_TEMPLATE_KWARGS:-}
      HF_TOKEN: ${HF_TOKEN:-}
    volumes:
      - ${HOME}/.cache/huggingface:/root/.cache/huggingface
      - ./docker/vllm-entrypoint.sh:/opt/jev/vllm-entrypoint.sh:ro
    ports: ["127.0.0.1:8000:8000"]
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 1800s

  gateway:
    build: {context: ., dockerfile: docker/gateway.Dockerfile}
    environment:
      PROFILE: ${PROFILE}
      HF_MODEL: ${HF_MODEL}
      HF_REVISION: ${HF_REVISION}
      SERVED_MODEL: ${SERVED_MODEL}
      MAX_MODEL_LEN: ${MAX_MODEL_LEN}
      PROMPT_LAYOUT: ${PROMPT_LAYOUT:-decider_chat}
      OPTION_ORDERS: ${OPTION_ORDERS:-identity}
      GATEWAY_API_KEY: ${GATEWAY_API_KEY:-}
      VLLM_URL: http://vllm:8000
      HF_HUB_OFFLINE: "1"
    volumes:
      - ${HOME}/.cache/huggingface:/root/.cache/huggingface:ro
      - ./prompts:/app/prompts:ro
      - ./data:/app/data:ro
    ports: ["127.0.0.1:9000:9000"]
    depends_on:
      vllm: {condition: service_healthy}
```

- [ ] **Step 4: Check the config renders**

Run: `docker compose --env-file profiles/gemma-4-31b.env config | grep -A3 CHAT_TEMPLATE_KWARGS`
Expected: `CHAT_TEMPLATE_KWARGS: '{"enable_thinking": true}'`

- [ ] **Step 5: First bring-up on qwen3.6-27b** (the first start downloads about 56 GB into the HF cache)

```bash
uv run python scripts/build_labels.py --profile qwen3.6-27b
docker compose --env-file profiles/qwen3.6-27b.env up -d --build
docker compose logs -f vllm   # wait for "Application startup complete"
curl -s localhost:9000/health
curl -s localhost:9000/v1/systemone -H 'content-type: application/json' -d '{"model":"jev-latest","state":"My card was charged twice for one order, please refund.","questions":{"dept":{"type":"choice","instructions":"Which team?","criteria":{"billing":null,"technical":null,"sales":null}},"urgent":{"type":"noul","instructions":"Needs a reply today"}}}'
curl -sN localhost:9000/v1/chat/completions -H 'content-type: application/json' -d '{"model":"qwen3.6-27b","messages":[{"role":"user","content":"Say hi"}],"stream":true,"max_tokens":64}' | head -5
```
Expected:
- `/health` returns `{"status":"ok","profile":"qwen3.6-27b",...}`.
- The decision returns `dept.choice == "billing"` and `urgent.noul` as a float.
- The chat streams `data:` lines.

If the gateway fails because it can't write to the read-only HF cache, change its mount to read-write, rerun, and record why in the commit body.

- [ ] **Step 6: Commit**

```bash
git add docker compose.yaml .dockerignore
git commit -m "build(docker): run vllm and gateway via compose" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 13: Live tests

**Files:**
- Create: `tests/live/conftest.py`, `tests/live/api.py`, `tests/live/test_sdk.py`, `tests/live/test_edge_cases.py`, `tests/live/test_chat.py`, `tests/live/test_stability.py`, `tests/live/test_prefix_cache.py`

**Interfaces:**
- Consumes: a running stack (Task 12)
- Produces: `uv run pytest -m live tests/live -v`

- [ ] **Step 1: `tests/live/conftest.py`**

```python
import os

import httpx
import pytest


@pytest.fixture(scope="session")
def gateway_url() -> str:
    url = os.environ.get("GATEWAY_URL", "http://127.0.0.1:9000")
    try:
        httpx.get(f"{url}/health", timeout=5).raise_for_status()
    except httpx.HTTPError:
        pytest.skip("stack not running: docker compose --env-file profiles/<profile>.env up -d")
    return url


@pytest.fixture(scope="session")
def vllm_url() -> str:
    return os.environ.get("VLLM_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def served_model(gateway_url) -> str:
    return httpx.get(f"{gateway_url}/health", timeout=5).json()["served_model"]
```

`tests/live/api.py`:
```python
import httpx


def post(url: str, body: dict) -> httpx.Response:
    return httpx.post(f"{url}/v1/systemone", json=body, timeout=600)
```

- [ ] **Step 2: `tests/live/test_sdk.py`**

```python
import pytest
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

pytestmark = pytest.mark.live


def test_official_sdk_quickstart(gateway_url):
    with TypeSafeClient(api_key="local", base_url=gateway_url) as client:
        response = client.system_one(
            state="Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. "
            "I'm losing sales. Please help ASAP.",
            questions={
                "department": Choice(
                    instructions="Which team should handle this",
                    criteria={
                        "billing": "Payment or subscription issues",
                        "technical": "Bugs or integration problems",
                        "sales": "Pricing or account questions",
                    },
                ),
                "frustration": Score(
                    instructions="How frustrated the customer appears",
                    criteria=["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"],
                ),
                "is_urgent": Noul(instructions="The message conveys urgency or time-sensitivity"),
            },
        )
    answers = response.answers
    assert answers["department"].choice == "technical"
    assert 0 <= answers["frustration"].score <= 2
    assert answers["is_urgent"].noul > 0.5
```

- [ ] **Step 3: `tests/live/test_edge_cases.py`**

```python
import pytest

from tests.live.api import post

pytestmark = pytest.mark.live


def choice(n: int) -> dict:
    return {"type": "choice", "instructions": "Which code applies?", "criteria": {f"code_{i}": None for i in range(n)}}


def test_null_descriptions_and_bare_noul(gateway_url):
    body = {
        "state": "Order 7 arrived broken.",
        "questions": {
            "kind": {"type": "choice", "instructions": "Issue?", "criteria": {"damage": None, "late": None}},
            "refund": {"type": "noul", "instructions": "A refund is appropriate"},
        },
    }
    r = post(gateway_url, body)
    assert r.status_code == 200
    assert set(r.json()["answers"]["refund"]) == {"type", "noul"}


def test_noul_described_without_instructions(gateway_url):
    body = {
        "state": "I am furious!!!",
        "questions": {"q": {"type": "noul", "criteria": {"true": "The writer is angry"}}},
    }
    assert post(gateway_url, body).json()["answers"]["q"]["noul"] > 0.5


@pytest.mark.parametrize("n", [130, 255])
def test_wide_choices(gateway_url, n):
    r = post(gateway_url, {"state": "code_7 applies.", "questions": {"q": choice(n)}})
    assert r.status_code == 200
    probs = r.json()["answers"]["q"]["probabilities"]
    assert len(probs) == n
    assert sum(probs.values()) == pytest.approx(1, abs=1e-2)


def test_too_many_options_refused_with_marker(gateway_url):
    r = post(gateway_url, {"state": "s", "questions": {"q": choice(256)}})
    assert r.status_code == 422
    assert "options per choice" in r.text


def test_oversized_state_refused_with_marker(gateway_url):
    r = post(gateway_url, {"state": "word " * 40000, "questions": {"q": choice(2)}})
    assert r.status_code == 422
    assert "maximum context length" in r.text
```

- [ ] **Step 4: `tests/live/test_chat.py`**

```python
import httpx
import pytest

pytestmark = pytest.mark.live


def test_chat_streams_with_thinking_on(gateway_url, served_model):
    body = {
        "model": served_model,
        "messages": [{"role": "user", "content": "What is 17 * 23?"}],
        "stream": True,
        "max_tokens": 512,
    }
    with httpx.stream("POST", f"{gateway_url}/v1/chat/completions", json=body, timeout=600) as r:
        assert r.status_code == 200
        lines = [line for line in r.iter_lines() if line.startswith("data: ")]
    assert lines[-1] == "data: [DONE]"
    assert len(lines) > 3
```

- [ ] **Step 5: `tests/live/test_stability.py`**

```python
import threading
import time

import httpx
import pytest

from tests.live.api import post

pytestmark = pytest.mark.live
BODY = {
    "state": "Customer: my invoice shows a charge I don't recognise and support hasn't replied in a week.",
    "questions": {
        "topic": {
            "type": "choice",
            "instructions": "Topic?",
            "criteria": {"billing": None, "shipping": None, "account": None, "other": None},
        },
        "anger": {"type": "score", "instructions": "Anger", "criteria": ["none", "some", "a lot"]},
        "escalate": {"type": "noul", "instructions": "Should a manager see this"},
    },
}


def distribution(answer: dict) -> list[float]:
    if answer["type"] == "noul":
        return [1 - answer["noul"], answer["noul"]]
    return list(answer["probabilities"].values())


def test_answers_stable_under_chat_load(gateway_url, served_model):
    idle = post(gateway_url, BODY).json()["answers"]
    stop = threading.Event()

    def chat_load():
        while not stop.is_set():
            httpx.post(
                f"{gateway_url}/v1/chat/completions",
                timeout=600,
                json={
                    "model": served_model,
                    "max_tokens": 512,
                    "messages": [{"role": "user", "content": "Write a long story about a lighthouse keeper."}],
                },
            )

    threads = [threading.Thread(target=chat_load) for _ in range(4)]
    for t in threads:
        t.start()
    time.sleep(3)
    try:
        loaded = [post(gateway_url, BODY).json()["answers"] for _ in range(5)]
    finally:
        stop.set()
        for t in threads:
            t.join()
    for run in loaded:
        for qid, answer in idle.items():
            p0, p1 = distribution(answer), distribution(run[qid])
            assert max(abs(a - b) for a, b in zip(p0, p1)) <= 0.02
            first, second = sorted(p0, reverse=True)[:2]
            if first - second > 0.05:
                assert p0.index(max(p0)) == p1.index(max(p1))
```

- [ ] **Step 6: `tests/live/test_prefix_cache.py`**

```python
import uuid

import httpx
import pytest

from tests.live.api import post

pytestmark = pytest.mark.live


def prefix_cache_hits(vllm_url: str) -> float:
    lines = httpx.get(f"{vllm_url}/metrics", timeout=10).text.splitlines()
    return sum(
        float(line.rsplit(" ", 1)[1]) for line in lines if line.startswith("vllm:") and "prefix_cache_hits" in line
    )


def test_questions_share_the_state_prefix(gateway_url, vllm_url):
    before = prefix_cache_hits(vllm_url)
    state = f"[{uuid.uuid4()}] " + "The quarterly report lists revenue, costs and staffing changes. " * 200
    questions = {f"q{i}": {"type": "noul", "instructions": f"Statement {i} is supported"} for i in range(8)}
    assert post(gateway_url, {"state": state, "questions": questions}).status_code == 200
    assert prefix_cache_hits(vllm_url) > before
```

- [ ] **Step 7: Run against the qwen3.6-27b stack from Task 12**

Run: `uv run pytest -m live tests/live -v`
Expected: every test passes. If `test_official_sdk_quickstart` fails because the model disagrees on `department`, print the answer and decide with the owner. Don't loosen the assertion without asking.

- [ ] **Step 8: Commit**

```bash
git add tests/live
git commit -m "test(live): cover sdk, limits, chat, load, cache" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 14: Benchmark

**Files:**
- Create: `data/bench/corpus.txt` (downloaded), `scripts/bench_data.py`, `scripts/bench.py`, `tests/unit/test_bench_data.py`

**Interfaces:**
- Consumes: `Settings` (Task 2); a running stack (Task 12)
- Produces:
  - `bench_data.synthetic_request(tok, rng, state_tokens, n_questions, n_options, nonce=True) -> dict`
  - `bench_data.jevbench_rows() -> list[dict]` and `bench_data.jevbench_request(row) -> tuple[dict, str]`, plus `bench_data.prediction(answer) -> str`
  - CLI `uv run python scripts/bench.py --profile <p> [--quick]`, which writes `docs/results/<p>/<date>/{raw.jsonl,summary.md}`

- [ ] **Step 1: Fetch the public-domain corpus**

Run: `mkdir -p data/bench && curl -sL https://www.gutenberg.org/cache/epub/1342/pg1342.txt -o data/bench/corpus.txt && wc -c data/bench/corpus.txt`
Expected: about 750 KB (*Pride and Prejudice*, public domain, Project Gutenberg header kept).

- [ ] **Step 2: Write the failing tests** `tests/unit/test_bench_data.py`

```python
import random

from scripts.bench_data import jevbench_request, prediction, synthetic_request


def test_synthetic_request_sizes(qwen_tok):
    req = synthetic_request(qwen_tok, random.Random(0), state_tokens=2048, n_questions=4, n_options=26, nonce=False)
    assert abs(len(qwen_tok.encode(req["state"], add_special_tokens=False)) - 2048) <= 16
    assert [q["type"] for q in req["questions"].values()] == ["choice", "score", "noul", "choice"]
    assert len(req["questions"]["q0"]["criteria"]) == 26


def test_nonce_makes_states_unique(qwen_tok):
    rng = random.Random(0)
    a = synthetic_request(qwen_tok, rng, 256, 1, 2)
    b = synthetic_request(qwen_tok, rng, 256, 1, 2)
    assert a["state"] != b["state"]


def test_jevbench_row_mapping():
    row = {
        "type": "score",
        "state": "s",
        "label": "2",
        "question": {"instructions": "How bad?", "levels": ["a", "b", "c"]},
    }
    req, gold = jevbench_request(row)
    assert req["questions"]["q"] == {"type": "score", "instructions": "How bad?", "criteria": ["a", "b", "c"]}
    assert gold == "2"


def test_prediction_per_type():
    assert prediction({"type": "choice", "choice": "x"}) == "x"
    assert prediction({"type": "noul", "noul": 0.7}) == "yes"
    assert prediction({"type": "score", "probabilities": {"0": 0.1, "1": 0.6, "2": 0.3}}) == "1"
```

- [ ] **Step 3: Run to see it fail**

Run: `uv run pytest tests/unit/test_bench_data.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.bench_data'`

- [ ] **Step 4: Implement `scripts/bench_data.py`**

```python
"""Benchmark requests: seeded synthetic sweeps, and the JevBench gold rows (Apache-2.0)."""

import functools
import json
import random
import uuid

import httpx

from gateway.config import ROOT

CORPUS = ROOT / "data" / "bench" / "corpus.txt"
JEVBENCH_CACHE = ROOT / ".cache" / "jevbench"
JEVBENCH_TREE = "https://api.github.com/repos/model-collapse/jev-bench/git/trees/main?recursive=1"
JEVBENCH_RAW = "https://raw.githubusercontent.com/model-collapse/jev-bench/main/"
LEVELS = ["Very casual", "Casual", "Neutral", "Formal", "Very formal"]


@functools.cache
def corpus_ids(tok) -> list[int]:
    return tok.encode(CORPUS.read_text(), add_special_tokens=False)


def state_text(tok, rng: random.Random, n_tokens: int, nonce: bool) -> str:
    """A slice of real prose about n_tokens long; the nonce defeats cross-request prefix caching."""
    ids = corpus_ids(tok)
    start = rng.randrange(0, len(ids) - n_tokens)
    text = tok.decode(ids[start : start + n_tokens])
    return f"[run {uuid.uuid4().hex[:8]}] {text}" if nonce else text


def synthetic_questions(n_questions: int, n_options: int) -> dict:
    """Cycle choice / 5-level score / noul so every type is timed."""
    kinds = [
        lambda i: {
            "type": "choice",
            "instructions": f"Which theme best fits part {i} of the passage?",
            "criteria": {f"theme_{j}": f"The passage is mainly about theme {j}" for j in range(n_options)},
        },
        lambda i: {"type": "score", "instructions": "How formal is the language?", "criteria": LEVELS},
        lambda i: {"type": "noul", "instructions": f"The passage names at least {i + 1} people"},
    ]
    return {f"q{i}": kinds[i % 3](i) for i in range(n_questions)}


def synthetic_request(
    tok, rng: random.Random, state_tokens: int, n_questions: int, n_options: int, nonce: bool = True
) -> dict:
    return {
        "model": "jev-latest",
        "state": state_text(tok, rng, state_tokens, nonce),
        "questions": synthetic_questions(n_questions, n_options),
    }


def jevbench_rows() -> list[dict]:
    """JevBench gold rows, downloaded once into .cache/jevbench/."""
    JEVBENCH_CACHE.mkdir(parents=True, exist_ok=True)
    listing = JEVBENCH_CACHE / "files.json"
    if not listing.exists():
        tree = httpx.get(JEVBENCH_TREE, timeout=30).json()["tree"]
        paths = [t["path"] for t in tree if t["path"].startswith("data/") and t["path"].endswith(".jsonl")]
        listing.write_text(json.dumps(sorted(paths)))
    rows = []
    for path in json.loads(listing.read_text()):
        local = JEVBENCH_CACHE / path.replace("/", "__")
        if not local.exists():
            local.write_text(httpx.get(JEVBENCH_RAW + path, timeout=60).text)
        rows += [json.loads(line) for line in local.read_text().splitlines() if line.strip()]
    return [r for r in rows if r.get("reliability") == "gold"]


def jevbench_request(row: dict) -> tuple[dict, str]:
    question = {"type": row["type"], "instructions": row["question"]["instructions"]}
    if row["type"] == "choice":
        question["criteria"] = row["question"]["options"]
    elif row["type"] == "score":
        question["criteria"] = row["question"]["levels"]
    return {"model": "jev-latest", "state": row["state"], "questions": {"q": question}}, str(row["label"])


def prediction(answer: dict) -> str:
    """The answer in JevBench's label format: option key, 'yes'/'no', or level index."""
    if answer["type"] == "choice":
        return answer["choice"]
    if answer["type"] == "noul":
        return "yes" if answer["noul"] >= 0.5 else "no"
    return max(answer["probabilities"], key=answer["probabilities"].get)
```

- [ ] **Step 5: Implement `scripts/bench.py`**

```python
"""Latency benchmark through the gateway, so it measures what clients see.

usage: uv run python scripts/bench.py --profile qwen3.6-27b [--gateway http://127.0.0.1:9000] [--quick]
"""

import argparse
import asyncio
import datetime
import json
import random
import time

import httpx
from transformers import AutoTokenizer

from gateway.config import ROOT, Settings
from scripts.bench_data import jevbench_request, jevbench_rows, prediction, synthetic_request

FULL = {
    "state_tokens": (256, 2048, 8192),
    "questions": (1, 4, 16, 64),
    "options": (2, 26, 255),
    "repeats": 5,
    "seconds": 30,
    "jevbench": None,
}
QUICK = {
    "state_tokens": (256, 2048),
    "questions": (1, 16),
    "options": (2, 26),
    "repeats": 2,
    "seconds": 10,
    "jevbench": 50,
}
CHAT_PROMPTS = {
    "short": "Name three prime numbers.",
    "long": "Explain step by step how a hash map resolves collisions, with an example.",
}


async def timed_post(client: httpx.AsyncClient, body: dict) -> tuple[float, dict]:
    start = time.perf_counter()
    r = await client.post("/v1/systemone", json=body)
    r.raise_for_status()
    return (time.perf_counter() - start) * 1000, r.json()


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


async def sweep(client, tok, rng, grid: dict, warm: bool, records: list) -> None:
    """Sequential latency per (state length, questions, options); warm repeats one state."""
    for n_tok in grid["state_tokens"]:
        for n_q in grid["questions"]:
            for n_opt in grid["options"]:
                fixed = synthetic_request(tok, rng, n_tok, n_q, n_opt, nonce=False)
                await timed_post(client, fixed)
                for _ in range(grid["repeats"]):
                    body = fixed if warm else synthetic_request(tok, rng, n_tok, n_q, n_opt)
                    ms, _ = await timed_post(client, body)
                    records.append(
                        {
                            "test": "warm" if warm else "cold",
                            "state_tokens": n_tok,
                            "questions": n_q,
                            "options": n_opt,
                            "ms": ms,
                        }
                    )


async def throughput(client, tok, rng, workers: int, seconds: int, records: list) -> None:
    done = 0
    stop = time.perf_counter() + seconds

    async def worker():
        nonlocal done
        while time.perf_counter() < stop:
            await timed_post(client, synthetic_request(tok, rng, 2048, 16, 26))
            done += 1

    start = time.perf_counter()
    await asyncio.gather(*(worker() for _ in range(workers)))
    records.append({"test": "throughput", "workers": workers, "requests_per_s": done / (time.perf_counter() - start)})


async def jevbench(client, limit: int | None, records: list) -> None:
    for row in jevbench_rows()[:limit]:
        body, gold = jevbench_request(row)
        ms, out = await timed_post(client, body)
        records.append(
            {"test": "jevbench", "type": row["type"], "ms": ms, "correct": prediction(out["answers"]["q"]) == gold}
        )


async def chat_once(client, served: str, prompt: str) -> tuple[float, float]:
    """(time to first token in ms, streamed chunks per second after it)."""
    body = {"model": served, "messages": [{"role": "user", "content": prompt}], "stream": True, "max_tokens": 512}
    start, first, chunks = time.perf_counter(), None, 0
    async with client.stream("POST", "/v1/chat/completions", json=body) as r:
        async for line in r.aiter_lines():
            if line.startswith("data: ") and line != "data: [DONE]":
                chunks += 1
                first = first or time.perf_counter()
    end = time.perf_counter()
    return (first - start) * 1000, chunks / max(end - first, 1e-9)


async def chat_under_load(client, tok, rng, served: str, records: list) -> None:
    for label, prompt in CHAT_PROMPTS.items():
        ttft, tps = await chat_once(client, served, prompt)
        records.append({"test": "chat", "load": "none", "prompt": label, "ttft_ms": ttft, "chunks_per_s": tps})
    stop = asyncio.Event()

    async def decisions():
        while not stop.is_set():
            await timed_post(client, synthetic_request(tok, rng, 2048, 16, 26))

    load = [asyncio.create_task(decisions()) for _ in range(4)]
    for label, prompt in CHAT_PROMPTS.items():
        ttft, tps = await chat_once(client, served, prompt)
        records.append({"test": "chat", "load": "4 systemone", "prompt": label, "ttft_ms": ttft, "chunks_per_s": tps})
    stop.set()
    await asyncio.gather(*load)


def summary(records: list) -> str:
    lines = ["| test | state tokens | questions | options | p50 ms | p95 ms |", "|---|---|---|---|---|---|"]
    groups: dict[tuple, list] = {}
    for r in records:
        if r["test"] in ("cold", "warm"):
            groups.setdefault((r["test"], r["state_tokens"], r["questions"], r["options"]), []).append(r["ms"])
    for key, ms in groups.items():
        lines.append(f"| {' | '.join(map(str, key))} | {percentile(ms, 0.5):.0f} | {percentile(ms, 0.95):.0f} |")
    lines += ["", "| workers | requests/s |", "|---|---|"]
    lines += [f"| {r['workers']} | {r['requests_per_s']:.1f} |" for r in records if r["test"] == "throughput"]
    bench = [r for r in records if r["test"] == "jevbench"]
    if bench:
        ms = [r["ms"] for r in bench]
        accuracy = sum(r["correct"] for r in bench) / len(bench)
        lines += [
            "",
            f"JevBench gold: {len(bench)} rows, accuracy {accuracy:.3f} (uncalibrated sanity check), "
            f"p50 {percentile(ms, 0.5):.0f} ms, p95 {percentile(ms, 0.95):.0f} ms",
        ]
    lines += ["", "| chat prompt | load | TTFT ms | chunks/s |", "|---|---|---|---|"]
    lines += [
        f"| {r['prompt']} | {r['load']} | {r['ttft_ms']:.0f} | {r['chunks_per_s']:.1f} |"
        for r in records
        if r["test"] == "chat"
    ]
    return "\n".join(lines) + "\n"


async def main(args) -> None:
    s = Settings.from_profile(args.profile)
    tok = AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
    grid, rng, records = (QUICK if args.quick else FULL), random.Random(0), []
    async with httpx.AsyncClient(base_url=args.gateway, timeout=600) as client:
        await sweep(client, tok, rng, grid, warm=False, records=records)
        await sweep(
            client,
            tok,
            rng,
            grid | {"state_tokens": (2048,), "questions": (16,), "options": (26,)},
            warm=True,
            records=records,
        )
        for workers in (1, 4, 16):
            await throughput(client, tok, rng, workers, grid["seconds"], records)
        await jevbench(client, grid["jevbench"], records)
        await chat_under_load(client, tok, rng, s.served_model, records)
    out = ROOT / "docs" / "results" / s.profile / datetime.date.today().isoformat()
    out.mkdir(parents=True, exist_ok=True)
    (out / "raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    (out / "summary.md").write_text(
        f"# {s.profile} benchmark ({'quick' if args.quick else 'full'})\n\n" + summary(records)
    )
    print((out / "summary.md").read_text())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--gateway", default="http://127.0.0.1:9000")
    parser.add_argument("--quick", action="store_true")
    asyncio.run(main(parser.parse_args()))
```

- [ ] **Step 6: Run the unit tests, then a quick bench against the running stack**

Run: `uv run pytest tests/unit -q && uv run python scripts/bench.py --profile qwen3.6-27b --quick`
Expected: tests pass. The bench prints a summary with the sweep table, throughput, JevBench (50 rows) and the chat table, and writes `docs/results/qwen3.6-27b/<date>/`.

- [ ] **Step 7: Commit** (the quick report stays uncommitted; full reports are committed in Task 15)

```bash
git add data/bench/corpus.txt scripts/bench_data.py scripts/bench.py tests/unit/test_bench_data.py
git commit -m "feat(bench): add latency benchmark through gateway" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 15: Bring up all three profiles, commit reports, update CLAUDE.md

This is the definition of done from the spec. Run it for each profile in turn: `qwen3.6-27b`, `qwen3.8-27b`, `gemma-4-31b`.

**Files:**
- Create: `data/<profile>/<layout>/labels.json` (all profiles), `docs/results/<profile>/<date>/{raw.jsonl,summary.md}`
- Modify: `CLAUDE.md`

- [ ] **Step 1: For each profile, run the full cycle**

```bash
P=qwen3.6-27b   # then qwen3.8-27b, then gemma-4-31b
uv run python scripts/build_labels.py --profile $P
docker compose down
docker compose --env-file profiles/$P.env up -d --build
until curl -sf localhost:9000/health >/dev/null; do sleep 15; done
uv run pytest tests/unit tests/parity -q
uv run pytest -m live tests/live -v
uv run python scripts/bench.py --profile $P
```
Expected: all tests pass and a full report is written. Record any failure and its fix in the commit body. Don't paper over it.

- [ ] **Step 2: Commit labels and reports per profile**

```bash
git add data/$P docs/results/$P
git commit -m "feat($P): add labels and phase-1 bench report" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 3: Update `CLAUDE.md`** with a `## Commands` section and a short `## Architecture` section

```markdown
## Commands

- Install: `uv sync`
- Unit tests (CPU): `uv run pytest -q`; a single test: `uv run pytest tests/unit/test_prompts.py::test_rows_share_the_reported_prefix -q`
- Parity with decider: `uv run pytest tests/parity -q` (fixtures from `scripts/decider_fixtures.py`, run in `.cache/decider-venv`)
- Live tests (stack running): `uv run pytest -m live tests/live -v`
- Lint: `uv run ruff check .`
- Label tables (after any tokenizer or `prompts/*.toml` change): `uv run python scripts/build_labels.py --profile <p>`
- Run a model: `docker compose --env-file profiles/<p>.env up -d --build` (gateway :9000, vLLM :8000)
- Benchmark: `uv run python scripts/bench.py --profile <p> [--quick]`

## Architecture

- `gateway/decide.py` is the whole `/v1/systemone` flow, in order:
  1. `questions.render_question` turns each question into option texts;
  2. `orders.option_orders` chooses the option orders;
  3. `prompts.build_rows` builds the token ids piecewise (chat frame + layout parts);
  4. `readout.Readout` asks vLLM `/v1/completions` with `max_tokens=1` and `logprob_token_ids`;
  5. `calibration.softmax` applies the temperature;
  6. `orders.average_back` maps probabilities back to the caller's options;
  7. `answers.answer` builds the Jev answer.
- Prompt wording lives only in `prompts/<layout>.toml`. Editing it requires rebuilding the labels (the gateway refuses stale hashes) and refitting temperatures.
- `chat.route()` is the phase-3 hook where systemone answers will steer chat requests.
```

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add commands and architecture to CLAUDE.md" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

## Self-review notes (spec coverage)

| Spec item | Task |
|---|---|
| vLLM v0.30.0, bf16, no MTP, loopback, HF cache mount | 12 |
| Three profiles, pinned revisions, one at a time | 2, 12, 15 |
| Thinking on for chat (Gemma via kwargs), off in systemone prompts | 2, 6, 12 |
| Editable layouts, per-request override, three shipped layouts | 3, 6, 10 |
| Option orders setting + per-request override | 8, 10 |
| Label tables built ahead of time, hash-checked | 5, 11, 15 |
| Jev validation and 422 markers | 3, 4, 10, 11, 13 |
| Readout: one batched call, warm-first, >128 split | 9 |
| Temperatures per profile/layout/type, default 1.0 | 8, 11 |
| Jev answer shapes + TypeSafe confidence, 4 decimals, usage | 8, 10 |
| Errors: 503 when vLLM is down, 422 when the prompt is too long | 9, 10, 11 |
| Chat proxy (streaming), `route()` hook, other `/v1/*`, model aliases, API key | 11 |
| Unit, parity, live tests | 1–11, 7, 13 |
| Benchmark: synthetic sweep, nonce/warm, JevBench, chat under load, reports | 14, 15 |
| Definition of done for all three profiles | 15 |
