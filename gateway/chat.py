"""Chat and every other /v1/* call forwarded to vLLM unchanged, with a route() hook for phase 3."""

import json
from collections.abc import AsyncIterator, Mapping

import httpx
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

from gateway.governor import Governor

ALIASES = ("jev-latest", "jev-preview")

# vLLM answers a non-streaming request only once done, which long thinking can push past 600 s.
# So no read timeout: a client that gives up gets its request cancelled instead (gateway/disconnect.py).
PROXY_TIMEOUT = httpx.Timeout(600, read=None)

# The only client headers passed on. Never Authorization: it carries the gateway key, not vLLM's.
FORWARDED_HEADERS = ("content-type", "accept")


def route(body: dict) -> dict:
    """Phase 1: pass through. Phase 3 sets thinking and reasoning_effort from systemone answers."""
    return body


def forwarded(headers: Mapping[str, str]) -> dict[str, str]:
    """The client's headers that vLLM should see."""
    return {name: headers[name] for name in FORWARDED_HEADERS if name in headers}


async def counted(chunks: AsyncIterator[bytes], governor: Governor) -> AsyncIterator[bytes]:
    """Pass chunks through; the chat counts as decoding from its first chunk until the stream closes."""
    started = False
    try:
        async for chunk in chunks:
            if not started:
                governor.chat_started()
                started = True
            yield chunk
    finally:
        if started:
            governor.chat_ended()


class ClosingResponse(StreamingResponse):
    """Closes the body iterator when the response ends, so a client that left still runs its finally blocks."""

    async def __call__(self, scope, receive, send) -> None:
        try:
            await super().__call__(scope, receive, send)
        finally:
            await self.body_iterator.aclose()


async def proxy(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    content: bytes,
    headers: dict[str, str],
    params: list[tuple[str, str]] | None = None,
    governor: Governor | None = None,
) -> StreamingResponse:
    """Stream vLLM's response back byte for byte (JSON and SSE alike); a governor counts it as a chat stream."""
    request = client.build_request(method, path, content=content, params=params, headers=headers, timeout=PROXY_TIMEOUT)
    upstream = await client.send(request, stream=True)
    chunks = upstream.aiter_bytes()
    return ClosingResponse(
        counted(chunks, governor) if governor else chunks,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type"),
        background=BackgroundTask(upstream.aclose),
    )


async def chat_completions(
    client: httpx.AsyncClient, body: dict, served_model: str, governor: Governor | None = None
) -> StreamingResponse:
    if body.get("model") in ALIASES:
        body = body | {"model": served_model}  # vLLM only knows the served model name
    content = json.dumps(route(body)).encode()
    headers = {"content-type": "application/json"}
    counting = governor if body.get("stream") else None  # only a streaming chat decodes for long
    return await proxy(client, "POST", "/v1/chat/completions", content, headers, governor=counting)


async def list_models(client: httpx.AsyncClient, served_model: str) -> dict:
    """vLLM's model list plus the Jev aliases, which all mean the loaded model."""
    listing = (await client.get("/v1/models")).json()
    base = next(m for m in listing["data"] if m["id"] == served_model)
    listing["data"] += [{**base, "id": alias} for alias in ALIASES]
    return listing
