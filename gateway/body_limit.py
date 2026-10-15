"""Refuse a POST whose declared body is over the limit before reading it. Plain ASGI, so disconnects still reach
the app (BaseHTTPMiddleware hides them)."""

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class BodyLimit:
    def __init__(self, app: ASGIApp, path: str, limit: int):
        self.app = app
        self.path = path
        self.limit = limit

    def too_big(self, scope: Scope) -> bool:
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"] != self.path:
            return False
        length = dict(scope["headers"]).get(b"content-length")
        return length is not None and int(length) > self.limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.too_big(scope):
            refusal = JSONResponse({"error": {"message": f"request body over {self.limit // 1_000_000} MB"}}, 400)
            await refusal(scope, receive, send)
            return
        await self.app(scope, receive, send)
