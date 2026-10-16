"""Raw letter logprobs for each vision split row, read straight from vLLM with the gateway's own code.

usage: uv run python scripts/vision_collect.py --profile P --label L [--split dev] [--layout header]
       [--orders identity+reversed] [--env KEY=VALUE ...] [--vllm URL] [--concurrency 8] [--holdout]
Needs vLLM up and idle with the profile's settings. Resumes where it stopped.
"""

import argparse
import asyncio
import base64
import dataclasses
import gzip
import hashlib
import io
import json
import mimetypes
import os
import uuid
from pathlib import Path

import httpx
import PIL.Image
from pydantic import ValidationError

from gateway.app import load_engine, vllm_client
from gateway.config import ROOT, Settings, read_env_file
from gateway.decide import build_batch, read_rows
from gateway.orders import option_orders
from gateway.questions import render_question
from gateway.readout import GENERATE_PATH
from gateway.schema import ImageError, Question, RequestError, SystemOneRequest
from scripts import vision_splits
from scripts.collect import ATTEMPTS, BACKOFF, repair, stamp

COLLECT = ROOT / ".cache" / "vision-collect"
PROBE_SIZE = (1280, 1092)
CHUNK = 500  # records written per flush, so a crash loses at most one chunk


def settings_for(profile: str, env: dict[str, str], vllm: str) -> Settings:
    """The profile with --env overrides, images on, and vLLM's key from the environment."""
    merged = read_env_file(ROOT / "profiles" / f"{profile}.env") | env | {"SYSTEMONE_IMAGES": "1"}
    key = os.environ.get("VLLM_API_KEY") or None
    return dataclasses.replace(Settings.from_env(merged), vllm_url=vllm, vllm_api_key=key)


def require_labels(s: Settings, layout: str) -> None:
    path = s.data_dir(layout) / "labels.json"
    if not path.exists():
        raise SystemExit(f"{path} missing: run scripts/build_labels.py for {s.profile} {layout}")


def run_stamp(engine, layout: str, commit: str) -> dict:
    """collect.py's stamp plus what shapes an image read: the label table, the model and the image kwargs."""
    s = engine.settings
    labels = hashlib.sha256((s.data_dir(layout) / "labels.json").read_bytes()).hexdigest()
    extra = {"hf_model": s.hf_model, "labels_sha256": labels, "mm_processor_kwargs": s.mm_processor_kwargs}
    return stamp(engine, layout) | extra | {"commit": commit}


def probe_png() -> str:
    """A PNG data URL no earlier request sent: a random colour and one random pixel give it a new cache key."""
    seed = uuid.uuid4().bytes
    im = PIL.Image.new("RGB", PROBE_SIZE, tuple(seed[:3]))
    im.putpixel((0, 0), tuple(seed[3:6]))
    out = io.BytesIO()
    im.save(out, format="PNG")
    return "data:image/png;base64," + base64.b64encode(out.getvalue()).decode()


async def self_check(engine, client: httpx.AsyncClient, layout: str) -> None:
    """Refuse a vLLM that expands images to another length than the gateway counts (other mm kwargs)."""
    question = {"q": {"type": "noul", "instructions": "The image is bright"}}
    request = SystemOneRequest(state="", questions=question, images=[probe_png()], layout=layout)
    batch = (await build_batch(engine, request))[2]
    ids, image = batch.rows[0].ids, batch.images.images[0]
    sampling = {"max_tokens": 1, "temperature": 0}
    body = {"model": engine.settings.served_model, "token_ids": ids, "content_parts": [image.part()],
            "sampling_params": sampling, "return_token_ids": True}
    r = await client.post(GENERATE_PATH, json=body)
    r.raise_for_status()
    got, want = len(r.json()["prompt_token_ids"]), len(ids) + engine.vision.added(image)
    if got != want:
        raise SystemExit(f"self-check: vLLM expanded the probe to {got} tokens, the gateway counts {want}; "
                         "start vLLM with this config's MM_PROCESSOR_KWARGS")


def data_url(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError as e:
        raise ImageError(f"{path}: {e.strerror}") from e
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def option_names(row: dict, layout) -> list:
    """The answer question's option names in caller order (choice keys, levels or False/True)."""
    return render_question(Question.model_validate(row["questions"]["answer"]), layout).names


def gold_index(names: list, expected) -> int | None:
    return names.index(expected) if expected in names else None


async def collect_one(engine, row: dict, group: str, layout: str, orders: str, rec_stamp: dict) -> dict:
    rec = {"id": row["id"], "benchmark": row["benchmark"], "group": group, "layout": layout, "names": [],
           "gold": None, "input_tokens": None, "shared_len": None, "padded": None, "reads": [], "stamp": rec_stamp}
    try:
        names = option_names(row, engine.layouts[layout])
        rec |= {"names": names, "gold": gold_index(names, row["expected"].get("answer"))}
        images = [data_url(vision_splits.SUITE.parent / p) for p in row["images"]]
        request = SystemOneRequest.model_validate(
            {"state": row["state"], "questions": row["questions"], "images": images, "layout": layout,
             "option_orders": orders}
        )
        r = await read_rows(engine, request, pad_rows=len(request.questions))  # pad as the live default would
    except ValidationError as e:
        return rec | {"status": "invalid", "error": str(e).splitlines()[0]}
    except RequestError as e:  # includes ImageError: a missing, unreadable or refused image
        return rec | {"status": "unsupported", "error": str(e)}
    reads = [{"perm": perm, "logprobs": lp} for lp, perm in r.reads["answer"]]
    read = {"input_tokens": r.input_tokens, "shared_len": r.shared_len, "padded": r.padded, "reads": reads}
    return rec | {"status": "ok"} | read


async def collect_retrying(engine, *args) -> dict:
    """vLLM hiccups (5xx, dropped connections) get retried with backoff; a lasting one stops the run."""
    for attempt in range(ATTEMPTS - 1):
        try:
            return await collect_one(engine, *args)
        except httpx.HTTPError:
            await asyncio.sleep(BACKOFF * 2**attempt)
    return await collect_one(engine, *args)


def resume(path: Path, layout: str, rec_stamp: dict) -> set[str]:
    """Ids already collected; drops a truncated tail. Refuses records read under other settings but commit."""
    if not path.exists():
        return set()
    return {i for i, _ in repair(path, {layout: rec_stamp}, ignore=("commit",))}


async def collect(engine, rows: list[dict], layout: str, orders: str, path: Path, rec_stamp: dict, done: set[str],
                  concurrency: int = 8) -> int:
    """Append a record per row not in done; returns how many were written."""
    group = vision_splits.groups(vision_splits.read_suite())
    todo = [row for row in rows if row["id"] not in done]
    gate = asyncio.Semaphore(concurrency)

    async def one(row):
        async with gate:
            return await collect_retrying(engine, row, group[row["id"]], layout, orders, rec_stamp)

    with gzip.open(path, "at", encoding="utf-8") as out:
        for start in range(0, len(todo), CHUNK):
            for rec in await asyncio.gather(*(one(row) for row in todo[start : start + CHUNK])):
                out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"{min(start + CHUNK, len(todo))}/{len(todo)}", flush=True)
    return len(todo)


PER_SPLIT = ("split", "commit")  # differ between a label's splits; each record's stamp carries the commit


def check_config(folder: Path, config: dict) -> None:
    """Refuse a label folder collected under another config."""
    path = folder / "config.json"
    if path.exists():
        old = json.loads(path.read_text())
        diff = sorted(k for k in (old.keys() | config.keys()) - set(PER_SPLIT) if old.get(k) != config.get(k))
        if diff:
            raise SystemExit(f"{folder} was collected with other {diff}: use another --label")


def write_configs(folder: Path, config: dict) -> None:
    """config.json and <split>.config.json, each written once."""
    folder.mkdir(parents=True, exist_ok=True)
    for path in (folder / "config.json", folder / f"{config['split']}.config.json"):
        if not path.exists():
            path.write_text(json.dumps(config, indent=1) + "\n")


async def require_model(client: httpx.AsyncClient, s: Settings) -> None:
    served = [m["id"] for m in (await client.get("/v1/models")).json()["data"]]
    if s.served_model not in served:
        raise SystemExit(f"vLLM serves {served}, not {s.served_model}: start the {s.profile} profile first")


async def run(args, transport: httpx.AsyncBaseTransport | None = None) -> int:
    s = settings_for(args.profile, args.env, args.vllm)
    require_labels(s, args.layout)
    try:
        option_orders(2, args.orders)
    except ValueError as e:
        raise SystemExit(str(e)) from e
    commit = vision_splits.commit()
    config = {"profile": s.profile, "label": args.label, "layout": args.layout, "orders": args.orders,
              "env": args.env, "split": args.split, "commit": commit}
    folder = COLLECT / s.profile / args.label
    path = folder / f"{args.split}.jsonl.gz"
    async with vllm_client(s, transport) as client:
        engine = load_engine(s, client, calibrated=False)  # raw reads: calibration is applied offline
        await require_model(client, s)
        await self_check(engine, client, args.layout)
        rec_stamp = run_stamp(engine, args.layout, commit)
        check_config(folder, config)
        done = resume(path, args.layout, rec_stamp)
        # load_split logs a holdout use, so it comes after every check that can refuse the run
        rows = vision_splits.load_split(f"vision-{args.split}", holdout=args.holdout, tool="vision_collect",
                                        label=args.label)
        write_configs(folder, config)
        n = await collect(engine, rows, args.layout, args.orders, path, rec_stamp, done, args.concurrency)
    print(f"wrote {n} records to {path}")
    return n


def env_pair(text: str) -> tuple[str, str]:
    key, sep, value = text.partition("=")
    if not sep or not key:
        raise argparse.ArgumentTypeError(f"--env takes KEY=VALUE, got {text!r}")
    if key.endswith("API_KEY"):  # config.json records --env; keys come from the environment only
        raise argparse.ArgumentTypeError(f"{key} comes from the environment, not --env")
    if key == "VLLM_URL":
        raise argparse.ArgumentTypeError("VLLM_URL is set with --vllm, not --env")
    return key, value


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--split", default="dev", choices=("dev", "holdout", "latency"))
    p.add_argument("--layout", default="header")
    p.add_argument("--orders", default="identity+reversed")
    p.add_argument("--env", type=env_pair, nargs="+", action="extend", default=[], metavar="KEY=VALUE")
    p.add_argument("--vllm", default=os.environ.get("VLLM_URL", "http://127.0.0.1:8000"))
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--holdout", action="store_true", help="read the holdout split (logged)")
    args = p.parse_args(argv)
    args.env = dict(args.env)
    return args


if __name__ == "__main__":
    asyncio.run(run(parse_args()))
