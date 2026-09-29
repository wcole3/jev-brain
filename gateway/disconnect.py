"""Stop working for a client that has gone away, so vLLM aborts the abandoned request too."""

import asyncio
from collections.abc import Awaitable

from starlette.requests import Request


async def until_disconnected(request: Request) -> None:
    """Returns once the client has gone. Call it only after the body is read."""
    while (await request.receive())["type"] != "http.disconnect":
        pass


async def unless_disconnected[T](request: Request, work: Awaitable[T]) -> T | None:
    """The work's result, or None when the client left first; the work is then cancelled."""
    task = asyncio.ensure_future(work)
    watcher = asyncio.create_task(until_disconnected(request))
    try:
        await asyncio.wait([task, watcher], return_when=asyncio.FIRST_COMPLETED)
        if not task.done():
            watcher.result()  # a failed watcher raises here instead of passing for a disconnect
            task.cancel()
            await asyncio.wait([task])  # unlike `await task`, this never swallows our own cancellation
        # work that finished in the race still returns, so its open upstream response gets closed
        return None if task.cancelled() else task.result()
    finally:
        task.cancel()
        watcher.cancel()
