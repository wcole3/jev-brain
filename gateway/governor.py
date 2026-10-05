"""Decision governor: while a chat stream decodes, decisions run one at a time with pauses (DS-007)."""

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class Governor:
    def __init__(self, duty: float = 1.0, wave: int = 4):
        if not 0 < duty <= 1:
            raise ValueError(f"duty must be in (0, 1], got {duty}")
        if wave < 1:
            raise ValueError(f"wave must be >= 1, got {wave}")
        self.duty = duty
        self.wave = wave
        self.decoding = 0
        self._lock = asyncio.Lock()
        self._idle = asyncio.Event()
        self._idle.set()

    @property
    def enabled(self) -> bool:
        return self.duty < 1.0

    def chat_started(self) -> None:
        self.decoding += 1
        self._idle.clear()

    def chat_ended(self) -> None:
        self.decoding = max(0, self.decoding - 1)
        if self.decoding == 0:
            self._idle.set()

    def throttling(self) -> bool:
        return self.enabled and self.decoding > 0

    def wave_size(self) -> int | None:
        return self.wave if self.throttling() else None

    async def call(self, fn: Callable[[], Awaitable[T]]) -> T:
        if not self.throttling():
            return await fn()
        async with self._lock:
            start = time.monotonic()
            result = await fn()
            if self.throttling():
                await self._pause(time.monotonic() - start)
            return result

    async def _pause(self, busy: float) -> None:
        """Idle for busy * (1 - duty) / duty, or until the last chat stream ends."""
        try:
            await asyncio.wait_for(self._idle.wait(), timeout=busy * (1 - self.duty) / self.duty)
        except TimeoutError:
            pass
