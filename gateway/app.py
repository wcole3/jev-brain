"""FastAPI gateway: /v1/systemone, chat proxy, /v1/models, /health, and /v1/* passthrough to vLLM."""

import logging
import secrets
import uuid
from collections.abc import Mapping
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException
from transformers import AutoTokenizer

from gateway import chat
from gateway.calibration import load_temperatures
from gateway.config import Settings
from gateway.decide import Engine, decide
from gateway.disconnect import unless_disconnected
from gateway.labels import load_labels
from gateway.layouts import load_layouts
from gateway.padding import load_padding
from gateway.prompts import chat_frame
from gateway.readout import Readout
from gateway.schema import RequestError, SystemOneRequest

# uvicorn's logger is the one configured in the container, so INFO lines reach its log.
log = logging.getLogger("uvicorn.error")

CLIENT_CLOSED_REQUEST = 499  # nginx's status for a client that left; nobody reads it


def vllm_client(s: Settings, transport: httpx.AsyncBaseTransport | None) -> httpx.AsyncClient:
    """The gateway's one connection pool to vLLM; every call carries vLLM's key when it has one."""
    auth = {"Authorization": f"Bearer {s.vllm_api_key}"} if s.vllm_api_key else {}
    return httpx.AsyncClient(base_url=s.vllm_url, headers=auth, timeout=600, transport=transport)


def load_engine(s: Settings, client: httpx.AsyncClient) -> Engine:
    if s.systemone_max_len > s.max_model_len:
        raise ValueError(f"SYSTEMONE_MAX_LEN {s.systemone_max_len} exceeds MAX_MODEL_LEN {s.max_model_len}")
    tok = AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
    layouts = load_layouts()
    return Engine(
        settings=s,
        tokenizer=tok,
        layouts=layouts,
        frames={name: chat_frame(tok, layout) for name, layout in layouts.items()},
        labels={name: load_labels(s.data_dir(name) / "labels.json", tok, layout) for name, layout in layouts.items()},
        temperatures={name: load_temperatures(s.data_dir(name) / "calibration.json") for name in layouts},
        readout=Readout(client, s.served_model, s.warm_min_prefix_tokens, s.warm_up),
        padding=load_padding(s, tok),
    )


def require_key(request: Request) -> None:
    key = request.app.state.engine.settings.api_key
    given = request.headers.get("authorization", "").encode("latin-1")  # the header's raw bytes
    if key and not secrets.compare_digest(given, f"Bearer {key}".encode()):
        raise HTTPException(401, "invalid or missing API key", headers={"WWW-Authenticate": "Bearer"})


def error(status: int, message: str, headers: Mapping[str, str] | None = None) -> JSONResponse:
    return JSONResponse({"error": {"message": message}}, status_code=status, headers=headers)


def field_path(e: dict) -> str:
    """'questions.q.type' for ('body', 'questions', 'q', 'type'); 'body' for the body as a whole."""
    if e["type"] == "json_invalid":
        return "body"  # its loc ends in a character offset, not a field
    return ".".join(str(part) for part in e["loc"][1:] or e["loc"])


def validation_message(exc: RequestValidationError) -> str:
    """All errors on one line: '<field>: <msg>', joined by '; '."""
    return "; ".join(f"{field_path(e)}: {e['msg']}" for e in exc.errors())


def client_left(endpoint: str) -> Response:
    log.info("%s cancelled: client disconnected", endpoint)
    return Response(status_code=CLIENT_CLOSED_REQUEST)


async def json_object(request: Request) -> dict | None:
    """The body as a JSON object, or None when it is not one."""
    try:
        body = await request.json()
    except ValueError:  # invalid JSON or invalid UTF-8
        return None
    return body if isinstance(body, dict) else None


async def vllm_version(client: httpx.AsyncClient) -> str | None:
    try:
        return (await client.get("/version")).json()["version"]
    except (httpx.HTTPError, ValueError, KeyError):
        return None


def create_app(settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        s = settings or Settings.from_env()
        async with vllm_client(s, transport) as client:
            app.state.client = client
            app.state.engine = load_engine(s, client)
            yield

    app = FastAPI(title="jev-brain gateway", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    auth = [Depends(require_key)]

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return error(exc.status_code, exc.detail, exc.headers)  # keeps WWW-Authenticate and Allow

    @app.exception_handler(RequestValidationError)
    async def invalid_body(request: Request, exc: RequestValidationError):
        return error(422, validation_message(exc))

    @app.exception_handler(RequestError)
    async def refused(request: Request, exc: RequestError):
        return error(422, str(exc))

    @app.exception_handler(httpx.TransportError)
    async def vllm_down(request: Request, exc: httpx.TransportError):
        return error(503, "model server unavailable")

    @app.exception_handler(httpx.TimeoutException)
    async def vllm_slow(request: Request, exc: httpx.TimeoutException):
        return error(504, "model server timed out")

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
            "prefix_pad": s.prefix_pad,
            "prefix_block": s.prefix_block,
            "prefix_pad_always": s.prefix_pad_always,
            "systemone_max_len": s.systemone_max_len,
            "warm_min_prefix_tokens": s.warm_min_prefix_tokens,
            "warm_up": s.warm_up,
            "vllm_version": await vllm_version(request.app.state.client) if ok else None,
            "layouts": sorted(engine.layouts),
        }
        return JSONResponse(body, status_code=200 if ok else 503)

    @app.post("/v1/systemone", dependencies=auth)
    async def systemone(body: SystemOneRequest, request: Request):
        answer = await unless_disconnected(request, decide(request.app.state.engine, body))
        return client_left("systemone") if answer is None else answer

    @app.post("/v1/chat/completions", dependencies=auth)
    async def chat_completions(request: Request):
        body = await json_object(request)
        if body is None:
            return error(400, "request body must be a JSON object")
        served_model = request.app.state.engine.settings.served_model
        call = chat.chat_completions(request.app.state.client, body, served_model)
        upstream = await unless_disconnected(request, call)
        return client_left("chat") if upstream is None else upstream

    @app.get("/v1/models", dependencies=auth)
    async def models(request: Request):
        return await chat.list_models(request.app.state.client, request.app.state.engine.settings.served_model)

    @app.api_route("/v1/{path:path}", methods=["GET", "POST"], dependencies=auth)
    async def passthrough(path: str, request: Request):
        content = await request.body()
        headers, params = chat.forwarded(request.headers), request.query_params.multi_items()
        call = chat.proxy(request.app.state.client, request.method, f"/v1/{path}", content, headers, params)
        upstream = await unless_disconnected(request, call)
        return client_left("passthrough") if upstream is None else upstream

    return app


app = create_app()
