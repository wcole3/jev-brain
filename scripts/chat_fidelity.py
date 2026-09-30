"""Check that chat replies stay identical across gateway settings: record greedy replies, then compare.

uv run python scripts/chat_fidelity.py record --gateway http://127.0.0.1:9000 --out a.json
uv run python scripts/chat_fidelity.py compare a.json b.json
"""

import argparse
import json
import os
from pathlib import Path

import httpx

PROMPTS = [
    "What is the capital of Australia?",
    "Who wrote 'Pride and Prejudice'?",
    "Name three primary colours.",
    "What is the boiling point of water at sea level in Fahrenheit?",
    "Explain in one sentence what a black hole is.",
    "What is 17 * 23?",
    "Solve for x: 3x + 7 = 25.",
    "If a train travels 120 km in 1.5 hours, what is its average speed?",
    "What is the derivative of x^3 * sin(x)?",
    "Is 221 a prime number? Explain briefly.",
    "Write a Python function that reverses a string.",
    "Write a SQL query that returns the ten most recent orders from a table named orders.",
    "What does this do: `[x * x for x in range(5) if x % 2 == 0]`?",
    "Write a JavaScript function that checks whether a number is even.",
    "Explain the difference between a list and a tuple in Python.",
    (
        "Summarise in two sentences: The Industrial Revolution began in Britain in the late 18th century. "
        "It moved work from farms and small workshops to factories, driven by steam power and mechanised textiles. "
        "Cities grew quickly, and so did both wealth and hardship."
    ),
    (
        "Summarise in one sentence: Photosynthesis is the process by which plants turn light, water and carbon "
        "dioxide into sugar and oxygen. It takes place mostly in the leaves, inside chloroplasts."
    ),
    "Give me a three-item packing list for a day hike.",
    "Translate 'good morning, how are you?' into French.",
    "Write a haiku about the sea.",
]


def record(gateway: str, out: Path) -> None:
    key = os.environ.get("GATEWAY_API_KEY")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    replies = []
    with httpx.Client(base_url=gateway, headers=headers, timeout=600) as client:
        served = client.get("/health").json()["served_model"]
        for prompt in PROMPTS:
            body = {
                "model": served,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 256,
                "stream": False,
            }
            r = client.post("/v1/chat/completions", json=body)
            r.raise_for_status()
            data = r.json()
            message = data["choices"][0]["message"]
            replies.append({"prompt": prompt, "content": message.get("content"), "reasoning": message.get("reasoning")})
    out.write_text(json.dumps({"model": served, "replies": replies}, indent=2))


def first_difference(a: str, b: str) -> tuple[int, float]:
    """(index of the first differing character, common prefix as a share of the longer text)."""
    index = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    return index, index / max(len(a), len(b), 1)


def reply_text(reply: dict) -> str:
    return f"{reply.get('reasoning') or ''}\n---\n{reply.get('content') or ''}"


def compare(a: dict, b: dict) -> str:
    """Markdown report over prompts present in both recordings."""
    theirs = {r["prompt"]: r for r in b["replies"]}
    pairs = [(r, theirs[r["prompt"]]) for r in a["replies"] if r["prompt"] in theirs]
    same = [x for x, y in pairs if reply_text(x) == reply_text(y)]
    out = [
        "# Chat fidelity",
        "",
        f"- models: {a.get('model')} vs {b.get('model')}",
        f"- exact match: {len(same)}/{len(pairs)} ({100 * len(same) / max(len(pairs), 1):.0f}%)",
        "",
    ]
    diffs = [(x, *first_difference(reply_text(x), reply_text(y))) for x, y in pairs if reply_text(x) != reply_text(y)]
    if diffs:
        out += ["| prompt | first differing char | common prefix share |", "|---|---|---|"]
        out += [f"| {x['prompt'][:50]} | {i} | {share:.0%} |" for x, i, share in diffs]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("--gateway", required=True)
    rec.add_argument("--out", type=Path, required=True)
    cmp = sub.add_parser("compare")
    cmp.add_argument("a", type=Path)
    cmp.add_argument("b", type=Path)
    args = parser.parse_args(argv)
    if args.command == "record":
        record(args.gateway, args.out)
    else:
        print(compare(json.loads(args.a.read_text()), json.loads(args.b.read_text())))


if __name__ == "__main__":
    main()
