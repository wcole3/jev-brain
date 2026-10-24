"""What re-sending the full image with every row costs, and whether vLLM takes a uuid-only image reference.

usage: uv run python scripts/image_resend_probe.py --profile P [--vllm URL] [--rows 300]   (env VLLM_API_KEY)
Writes docs/results/archive/<profile>/<UTC>-image-resend/ with results.json and summary.md.
"""

import argparse
import asyncio
import inspect
import json
import os
import statistics
import time
from itertools import count
from pathlib import Path

import httpx

from gateway.app import load_engine
from gateway.config import Settings
from gateway.decide import build_batch
from gateway.schema import SystemOneRequest
from scripts import vision_splits
from scripts.bench import git_revision
from scripts.evaluate import now, results_dir
from scripts.vision_collect import data_url
from scripts.vision_run import stratified_sample

GENERATE_PATH = "/inference/v1/generate"
ERROR_CHARS = 300
SAME_ANSWER_DELTA = 0.5  # largest label logprob change that still counts as the same answer


def payload(model: str, ids: list[int], parts: list[dict], labels: list[int] | None = None) -> dict:
    """A generate body; with labels it asks for their logprobs plus a spare id, as Readout._generate does."""
    sampling = {"max_tokens": 1, "temperature": 0}
    if labels is not None:
        wanted = sorted(set(labels))
        spare = next(i for i in count() if i not in wanted)
        sampling |= {"logprobs": len(wanted) + 1, "logprob_token_ids": [*wanted, spare]}
    return {"model": model, "token_ids": ids, "content_parts": parts, "sampling_params": sampling}


def label_logprobs(response: httpx.Response, labels: list[int]) -> list[float] | None:
    try:
        top = response.json()["choices"][0]["logprobs"]["content"][0]["top_logprobs"]
        got = {e["token_id"]: e["logprob"] for e in top}
        return [got[i] for i in labels]
    except (ValueError, KeyError, IndexError, TypeError):
        return None


def uuid_only(parts: list[dict]) -> list[dict]:
    return [{"type": "image_url", "uuid": p["uuid"]} for p in parts]


def json_cost(model: str, batch) -> tuple[float, int]:
    """Milliseconds and bytes to build and serialize every row's generate payload, with no network."""
    start, size = time.perf_counter(), 0
    for row in batch.rows:
        parts = [image.part() for image in batch.images.images]
        size += len(json.dumps(payload(model, row.ids, parts)))
    return (time.perf_counter() - start) * 1000, size


async def timed_post(http: httpx.AsyncClient, body: dict, labels: list[int]) -> dict:
    """One generate call: wall ms, status, error text and label logprobs. Never raises on a rejection."""
    start = time.perf_counter()
    try:
        r = await http.post(GENERATE_PATH, json=body)
    except httpx.HTTPError as e:
        return {"ms": (time.perf_counter() - start) * 1000, "status": None, "error": repr(e)[:ERROR_CHARS],
                "logprobs": None}
    ms = (time.perf_counter() - start) * 1000
    return {"ms": ms, "status": r.status_code, "error": None if r.is_success else r.text[:ERROR_CHARS],
            "logprobs": label_logprobs(r, labels) if r.is_success else None}


def compare(full: list[float] | None, ref: list[float] | None) -> dict:
    """Largest label logprob change between the two calls, and whether the top label and answer held."""
    if full is None or ref is None:
        return {"max_abs_dlogprob": None, "top_match": False, "uuid_same_answer": False}
    delta = max(abs(a - b) for a, b in zip(full, ref, strict=True))
    top = full.index(max(full)) == ref.index(max(ref))
    return {"max_abs_dlogprob": delta, "top_match": top, "uuid_same_answer": top and delta <= SAME_ANSWER_DELTA}


async def measure(http: httpx.AsyncClient, model: str, batch, index: int = 0) -> dict:
    """Untimed warm-up, then the full and uuid calls timed in alternating order (even index: full first)."""
    json_ms, size = json_cost(model, batch)
    ids, labels = batch.rows[0].ids, batch.rows[0].label_ids
    parts = [image.part() for image in batch.images.images]
    bodies = {"full": payload(model, ids, parts, labels), "uuid": payload(model, ids, uuid_only(parts), labels)}
    await timed_post(http, bodies["full"], labels)
    order = ("full", "uuid") if index % 2 == 0 else ("uuid", "full")
    done = {name: await timed_post(http, bodies[name], labels) for name in order}
    full, ref = done["full"], done["uuid"]
    return compare(full["logprobs"], ref["logprobs"]) | {
            "order": "-".join(order), "rows": len(batch.rows), "json_ms": json_ms, "payload_bytes": size, "full_ms": full["ms"],
            "full_status": full["status"], "uuid_ms": ref["ms"], "uuid_status": ref["status"],
            "uuid_error": ref["error"], "uuid_accepted": ref["status"] == 200}


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def summarize(records: list[dict]) -> dict:
    """Medians per request; call timings only over requests whose uuid-only call gave the same answer."""
    ok = [r for r in records if r["uuid_accepted"]]
    same = [r for r in records if r["uuid_same_answer"]]
    return {"requests": len(records), "uuid_accepted": len(ok), "uuid_same_answer": len(same),
            "json_ms": median([r["json_ms"] for r in records]),
            "payload_mb": median([r["payload_bytes"] / 1e6 for r in records]),
            "full_ms": median([r["full_ms"] for r in same]), "uuid_ms": median([r["uuid_ms"] for r in same])}


def fmt(value: float | None, digits: int = 1) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def summary_markdown(profile: str, s: dict) -> str:
    return "\n".join([
        f"# Image resend cost, {profile}", "",
        "json_ms and payload_mb: building and serializing all rows of a request (median per request).",
        "full_ms vs uuid_ms: row 1 with the image vs uuid only, medians over same-answer requests.",
        "same answer: uuid-only top label equals the full call's and max |dlogprob| <= 0.5 (image really reused).", "",
        "| requests | uuid accepted | same answer | json_ms | payload_mb | full_ms | uuid_ms |", "|---|---|---|---|---|---|---|",
        "| {} | {} | {} | {} | {} | {} | {} |".format(
            s["requests"], s["uuid_accepted"], s["uuid_same_answer"], fmt(s["json_ms"]), fmt(s["payload_mb"], 2),
            fmt(s["full_ms"], 0), fmt(s["uuid_ms"], 0)),
    ]) + "\n"


def request_of(row: dict, layout: str, image_dir: Path) -> SystemOneRequest:
    images = [data_url(image_dir / p) for p in row["images"]]
    return SystemOneRequest.model_validate({"state": row["state"], "questions": row["questions"],
                                            "images": images, "layout": layout, "option_orders": "identity"})


async def run(s: Settings, vllm: str, n_rows: int) -> list[dict]:
    key = os.environ.get("VLLM_API_KEY")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    rows = stratified_sample(vision_splits.load_split("vision-dev"), n_rows)
    async with httpx.AsyncClient() as engine_client, httpx.AsyncClient(base_url=vllm, headers=headers,
                                                                       timeout=900) as http:
        engine = load_engine(s, engine_client, calibrated=False)
        if engine.vision is None:
            raise SystemExit(f"{s.profile} serves text only (SYSTEMONE_IMAGES is not 1)")
        records = []
        for index, row in enumerate(rows):
            request = request_of(row, s.prompt_layout, vision_splits.SUITE.parent)
            batch = (await build_batch(engine, request))[2]
            r = {"id": row["id"], **await measure(http, s.served_model, batch, index)}
            records.append(r)
            print(f"{r['id']} json {r['json_ms']:6.1f} full {r['full_ms']:6.0f} uuid {r['uuid_ms']:6.0f} "
                  f"status {r['uuid_status']}", flush=True)
    return records


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--vllm", default="http://127.0.0.1:8000")
    p.add_argument("--rows", type=int, default=300)
    args = p.parse_args()
    s = Settings.from_profile(args.profile)
    records = asyncio.run(run(s, args.vllm, args.rows))
    out = results_dir(args.profile, f"{now()}-image-resend", archive=True)
    settings = {"layout": s.prompt_layout, "rows": args.rows, "split": "vision-dev", "seed": inspect.signature(stratified_sample).parameters["seed"].default, "commit": git_revision()}
    (out / "results.json").write_text(json.dumps({"profile": args.profile, "settings": settings,
                                                  "records": records}, indent=1) + "\n")
    (out / "summary.md").write_text(summary_markdown(args.profile, summarize(records)))
    print(out)


if __name__ == "__main__":
    main()
