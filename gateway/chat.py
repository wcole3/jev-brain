"""Chat and every other /v1/* call forwarded to vLLM unchanged, with a route() hook for phase 3."""

import json

import httpx
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

ALIASES = ("jev-latest", "jev-preview")

# vLLM answers a non-streaming request only once done, which long thinking can push past 600 s.
# So no read timeout: a client that gives up gets its request cancelled instead (gateway/disconnect.py).
PROXY_TIMEOUT = httpx.Timeout(600, read=None)


def route(body: dict) -> dict:
    """Phase 1: pass through. Phase 3 sets thinking and reasoning_effort from systemone answers."""
    return body


async def proxy(
    client: httpx.AsyncClient, method: str, path: str, content: bytes, params: dict | None = None
) -> StreamingResponse:
    """Stream vLLM's response back byte for byte (JSON and SSE alike)."""
    headers = {"content-type": "application/json"}
    request = client.build_request(method, path, content=content, params=params, headers=headers, timeout=PROXY_TIMEOUT)
    upstream = await client.send(request, stream=True)
    return StreamingResponse(
        upstream.aiter_bytes(),
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type"),
        background=BackgroundTask(upstream.aclose),
    )


async def chat_completions(client: httpx.AsyncClient, body: dict, served_model: str) -> StreamingResponse:
    if body.get("model") in ALIASES:
        body = body | {"model": served_model}  # vLLM only knows the served model name
    return await proxy(client, "POST", "/v1/chat/completions", json.dumps(route(body)).encode())


async def list_models(client: httpx.AsyncClient, served_model: str) -> dict:
    """vLLM's model list plus the Jev aliases, which all mean the loaded model."""
    listing = (await client.get("/v1/models")).json()
    base = next(m for m in listing["data"] if m["id"] == served_model)
    listing["data"] += [{**base, "id": alias} for alias in ALIASES]
    return listing
