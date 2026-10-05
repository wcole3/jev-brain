"""Long-chat smoke test: what one huge chat request costs, and what it does to short chat and decisions."""

import argparse
import asyncio
import json
import statistics
import time
from uuid import uuid4

import httpx

from gateway.config import ROOT, Settings
from scripts import host_info
from scripts.bench import git_revision
from scripts.bench_report import percentile, provenance
from scripts.evaluate import gateway_headers, now, probe_chat, results_dir

INSTRUCTION = "\n\nSummarize the text above in 2 sentences."
MARGIN = 256  # stop this many tokens short of the target: chat template and joins add a few
DECISION = {
    "state": "Customer: my invoice shows a charge I don't recognise and support hasn't replied in a week.",
    "questions": {"escalate": {"type": "noul", "instructions": "Should a manager see this"}},
}
FRESH_POOL = 1000  # fresh states built up front: idle samples plus about one per second of a long run


def filler_text() -> str:
    docs = [ROOT / "README.md", *sorted((ROOT / "docs" / "background").glob("*.md"))]
    return "\n\n".join(p.read_text() for p in docs)


def count_tokens(tok, texts: list[str]) -> list[int]:
    return [len(ids) for ids in tok(texts, add_special_tokens=False)["input_ids"]]


def build_prompt(tok, filler: str, target: int, margin: int = MARGIN) -> tuple[str, int]:
    """Filler repeated up to target - margin tokens, then the instruction. Returns (prompt, tokens)."""
    filler_ids = tok([filler], add_special_tokens=False)["input_ids"][0]
    instruction_len = count_tokens(tok, [INSTRUCTION])[0]
    room = max(target - margin - instruction_len, 0)
    whole, rest = divmod(room, len(filler_ids))
    body = "\n\n".join([filler] * whole + [tok.decode(filler_ids[:rest])])
    prompt = body + INSTRUCTION
    return prompt, count_tokens(tok, [prompt])[0]


async def long_chat(client: httpx.AsyncClient, served: str, prompt: str, max_tokens: int) -> dict:
    body = {
        "model": served,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "stream_options": {"include_usage": True},
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    start, first, chunks, usage = time.perf_counter(), None, 0, {}
    async with client.stream("POST", "/v1/chat/completions", json=body) as r:
        r.raise_for_status()
        async for line in r.aiter_lines():
            if not line.startswith("data: ") or line == "data: [DONE]":
                continue
            event = json.loads(line[6:])
            usage = event.get("usage") or usage
            if event.get("choices"):
                chunks += 1
                first = first or time.perf_counter()
    end = time.perf_counter()
    first = first or end
    done = usage.get("completion_tokens", chunks)
    return {
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": done,
        "ttft_s": first - start,
        "decode_tok_s": done / max(end - first, 1e-9),
    }


def fresh_states(tok, filler: str, n: int, tokens: int) -> list[str]:
    """n states of about `tokens` tokens, each starting with a unique nonce so no prefix is shared."""
    nonces = [f"Ticket {uuid4().hex}\n" for _ in range(n)]
    filler_ids = tok([filler], add_special_tokens=False)["input_ids"][0]
    return [nonce + tok.decode(filler_ids[: max(tokens - used, 0)]) for nonce, used in zip(nonces, count_tokens(tok, nonces))]


async def probe_decision(client: httpx.AsyncClient, body: dict = DECISION) -> dict:
    start = time.perf_counter()
    try:
        (await client.post("/v1/systemone", json=body)).raise_for_status()
    except httpx.HTTPError as e:
        return {"error": type(e).__name__}
    return {"ms": (time.perf_counter() - start) * 1000}


def probe_fresh(client: httpx.AsyncClient, states: list[str]):
    """Probe that sends the next unused state each call."""
    unused = iter(states)

    async def probe() -> dict:
        state = next(unused, None)
        if state is None:
            return {"error": "out of fresh states"}
        return await probe_decision(client, DECISION | {"state": state})

    return probe


async def probe_loop(probe, stop: asyncio.Event, samples: list) -> None:
    while not stop.is_set():
        samples.append(await probe())
        await asyncio.sleep(1)


async def idle_samples(probe, n: int = 4) -> list[dict]:
    return [await probe() for _ in range(n)]


async def run(args, s: Settings, prompt: str, states: list[str]) -> dict:
    async with httpx.AsyncClient(base_url=args.gateway, headers=gateway_headers(), timeout=None) as client:
        health = (await client.get("/health")).json()
        if health["profile"] != args.profile:
            raise SystemExit(f"gateway serves {health['profile']!r}, not {args.profile!r}")
        chat = lambda: probe_chat(client, s.served_model)
        decide = lambda: probe_decision(client)
        fresh = probe_fresh(client, states)
        idle = {"chat": await idle_samples(chat), "decision": await idle_samples(decide), "fresh": await idle_samples(fresh)}
        stop, during = asyncio.Event(), {"chat": [], "decision": [], "fresh": []}
        probes = [
            asyncio.create_task(probe_loop(chat, stop, during["chat"])),
            asyncio.create_task(probe_loop(decide, stop, during["decision"])),
            asyncio.create_task(probe_loop(fresh, stop, during["fresh"])),
        ]
        try:
            long = await long_chat(client, s.served_model, prompt, args.max_tokens)
        finally:
            stop.set()
            await asyncio.gather(*probes)
    return {"health": health, "long": long, "idle": idle, "during": during}


def stats(samples: list[dict], key: str) -> str:
    values = [x[key] for x in samples if key in x]
    if not values:
        return f"no samples ({len(samples)} errors)"
    return f"{statistics.median(values):.0f} / {percentile(values, 0.95):.0f} / {len(values)}"


def render(raw: dict, meta: dict) -> str:
    long, idle, during = raw["long"], raw["idle"], raw["during"]
    rows = [
        "| Measure | Idle | During long request |",
        "| --- | --- | --- |",
        f"| Short chat TTFT ms (median / p95 / n) | {stats(idle['chat'], 'ttft_ms')} | {stats(during['chat'], 'ttft_ms')} |",
        f"| Decision ms (median / p95 / n) | {stats(idle['decision'], 'ms')} | {stats(during['decision'], 'ms')} |",
        f"| Fresh decision ms (median / p95 / n) | {stats(idle['fresh'], 'ms')} | {stats(during['fresh'], 'ms')} |",
    ]
    return "\n".join([
        f"# {meta['profile']} long-context chat\n",
        provenance(meta),
        "## Long request\n",
        "| Prompt tokens | Completion tokens | TTFT s | Decode tok/s |",
        "| --- | --- | --- | --- |",
        f"| {long['prompt_tokens']} | {long['completion_tokens']} | {long['ttft_s']:.1f} | {long['decode_tok_s']:.1f} |",
        "\n## Other traffic meanwhile\n",
        *rows,
        "",
    ])


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--profile", required=True)
    p.add_argument("--tokens", type=int, default=200_000)
    p.add_argument("--gateway", default="http://127.0.0.1:9000")
    p.add_argument("--fresh-tokens", type=int, default=1500, help="length of each never-cached decision state")
    p.add_argument("--max-tokens", type=int, default=256)
    p.add_argument("--dry-run", action="store_true", help="build the prompt and print its token count only")
    return p.parse_args(argv)


def main(argv=None) -> None:
    from transformers import AutoTokenizer

    args = parse_args(argv)
    s = Settings.from_profile(args.profile)
    tok = AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision, local_files_only=True)
    filler = filler_text()
    prompt, tokens = build_prompt(tok, filler, args.tokens)
    print(f"prompt tokens: {tokens} (target {args.tokens})")
    if args.dry_run:
        return
    raw = asyncio.run(run(args, s, prompt, fresh_states(tok, filler, FRESH_POOL, args.fresh_tokens))) | {"prompt_tokens_local": tokens}
    health = raw["health"]
    meta = {
        "timestamp": now(), "repo commit": git_revision(), "host": host_info.summary(), "profile": args.profile,
        "max_model_len": health.get("max_model_len", s.max_model_len),
        "systemone_max_len": health["systemone_max_len"], "target tokens": args.tokens,
    }
    out = results_dir(args.profile, f"{now()}-long-context", archive=True)
    (out / "raw.json").write_text(json.dumps(raw, indent=2))
    (out / "summary.md").write_text(render(raw, meta))
    print(out / "summary.md")


if __name__ == "__main__":
    main()
