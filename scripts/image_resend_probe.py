"""What re-sending the full image with every row costs, and whether vLLM takes a uuid-only image reference.

usage: uv run python scripts/image_resend_probe.py --profile P [--vllm URL] [--rows 300]   (env VLLM_API_KEY)
Writes docs/results/archive/<profile>/<UTC>-image-resend/ with results.json and summary.md.
"""

import argparse
import asyncio
import json
import os
import statistics
import time
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

GENERATE_PATH = "/inference/v1/generate"
SAMPLING = {"max_tokens": 1, "temperature": 0}
ERROR_CHARS = 300


def payload(model: str, ids: list[int], parts: list[dict]) -> dict:
    return {"model": model, "token_ids": ids, "content_parts": parts, "sampling_params": SAMPLING}


def uuid_only(parts: list[dict]) -> list[dict]:
    return [{"type": "image_url", "uuid": p["uuid"]} for p in parts]


def json_cost(model: str, batch) -> tuple[float, int]:
    """Milliseconds and bytes to build and serialize every row's generate payload, with no network."""
    start, size = time.perf_counter(), 0
    for row in batch.rows:
        parts = [image.part() for image in batch.images.images]
        size += len(json.dumps(payload(model, row.ids, parts)))
    return (time.perf_counter() - start) * 1000, size


async def timed_post(http: httpx.AsyncClient, body: dict) -> dict:
    """One generate call: wall ms, HTTP status and the error text. Never raises on a rejection."""
    start = time.perf_counter()
    try:
        r = await http.post(GENERATE_PATH, json=body)
    except httpx.HTTPError as e:
        return {"ms": (time.perf_counter() - start) * 1000, "status": None, "error": repr(e)[:ERROR_CHARS]}
    ms = (time.perf_counter() - start) * 1000
    return {"ms": ms, "status": r.status_code, "error": None if r.is_success else r.text[:ERROR_CHARS]}


async def measure(http: httpx.AsyncClient, model: str, batch) -> dict:
    json_ms, size = json_cost(model, batch)
    ids = batch.rows[0].ids
    parts = [image.part() for image in batch.images.images]
    full = await timed_post(http, payload(model, ids, parts))
    ref = await timed_post(http, payload(model, ids, uuid_only(parts)))
    return {"rows": len(batch.rows), "json_ms": json_ms, "payload_bytes": size, "full_ms": full["ms"],
            "full_status": full["status"], "uuid_ms": ref["ms"], "uuid_status": ref["status"],
            "uuid_error": ref["error"], "uuid_accepted": ref["status"] == 200}


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def summarize(records: list[dict]) -> dict:
    """Medians per request; the uuid timing only over requests where vLLM took the uuid-only part."""
    ok = [r for r in records if r["uuid_accepted"]]
    return {"requests": len(records), "uuid_accepted": len(ok),
            "json_ms": median([r["json_ms"] for r in records]),
            "payload_mb": median([r["payload_bytes"] / 1e6 for r in records]),
            "full_ms": median([r["full_ms"] for r in ok]), "uuid_ms": median([r["uuid_ms"] for r in ok])}


def fmt(value: float | None, digits: int = 1) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def summary_markdown(profile: str, s: dict) -> str:
    return "\n".join([
        f"# Image resend cost, {profile}", "",
        "json_ms and payload_mb: building and serializing all rows of a request (median per request).",
        "full_ms vs uuid_ms: row 1 with the image vs uuid only, medians over accepted requests.", "",
        "| requests | uuid accepted | json_ms | payload_mb | full_ms | uuid_ms |", "|---|---|---|---|---|---|",
        "| {} | {} | {} | {} | {} | {} |".format(
            s["requests"], s["uuid_accepted"], fmt(s["json_ms"]), fmt(s["payload_mb"], 2),
            fmt(s["full_ms"], 0), fmt(s["uuid_ms"], 0)),
    ]) + "\n"


def request_of(row: dict, layout: str, image_dir: Path) -> SystemOneRequest:
    images = [data_url(image_dir / p) for p in row["images"]]
    return SystemOneRequest.model_validate({"state": row["state"], "questions": row["questions"],
                                            "images": images, "layout": layout, "option_orders": "identity"})


async def run(s: Settings, vllm: str, n_rows: int) -> list[dict]:
    key = os.environ.get("VLLM_API_KEY")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    rows = vision_splits.load_split("vision-dev")[:n_rows]
    async with httpx.AsyncClient() as engine_client, httpx.AsyncClient(base_url=vllm, headers=headers,
                                                                       timeout=900) as http:
        engine = load_engine(s, engine_client, calibrated=False)
        if engine.vision is None:
            raise SystemExit(f"{s.profile} serves text only (SYSTEMONE_IMAGES is not 1)")
        records = []
        for row in rows:
            request = request_of(row, s.prompt_layout, vision_splits.SUITE.parent)
            batch = (await build_batch(engine, request))[2]
            r = {"id": row["id"], **await measure(http, s.served_model, batch)}
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
    settings = {"layout": s.prompt_layout, "rows": args.rows, "split": "vision-dev", "commit": git_revision()}
    (out / "results.json").write_text(json.dumps({"profile": args.profile, "settings": settings,
                                                  "records": records}, indent=1) + "\n")
    (out / "summary.md").write_text(summary_markdown(args.profile, summarize(records)))
    print(out)


if __name__ == "__main__":
    main()
