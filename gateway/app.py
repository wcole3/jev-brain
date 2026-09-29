"""FastAPI gateway: /v1/systemone, chat proxy, /v1/models, /health, and /v1/* passthrough to vLLM."""

import logging
import uuid
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

log = logging.getLogger(__name__)


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


async def vllm_version(client: httpx.AsyncClient) -> str | None:
    try:
        return (await client.get("/version")).json()["version"]
    except (httpx.HTTPError, ValueError, KeyError):
        return None


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

    @app.exception_handler(Exception)
    async def failed(request: Request, exc: Exception):
        # log the id and error type only, never the request content
        request_id = uuid.uuid4().hex
        log.error("request %s failed: %s", request_id, type(exc).__name__)
        return JSONResponse({"error": {"message": "internal error", "request_id": request_id}}, status_code=500)

    @app.get("/health")
    async def health(request: Request):
        engine = request.app.state.engine
        try:
            ok = (await request.app.state.client.get("/health")).status_code == 200
        except httpx.TransportError:
            ok = False
        s = engine.settings
        body = {
            "status": "ok" if ok else "vllm unavailable",
            "profile": s.profile,
            "served_model": s.served_model,
            "hf_model": s.hf_model,
            "hf_revision": s.hf_revision,
            "prompt_layout": s.prompt_layout,
            "option_orders": s.option_orders,
            "vllm_version": await vllm_version(request.app.state.client) if ok else None,
            "layouts": sorted(engine.layouts),
        }
        return JSONResponse(body, status_code=200 if ok else 503)

    @app.post("/v1/systemone", dependencies=auth)
    async def systemone(body: SystemOneRequest, request: Request):
        return await decide(request.app.state.engine, body)

    @app.post("/v1/chat/completions", dependencies=auth)
    async def chat_completions(request: Request):
        return await chat.chat_completions(
            request.app.state.client, await request.json(), request.app.state.engine.settings.served_model
        )

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
