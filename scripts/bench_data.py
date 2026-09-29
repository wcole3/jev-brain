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
