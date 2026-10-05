import asyncio
import time

import pytest

from gateway.governor import Governor


def timed(log: list, duration: float, value="ok"):
    """A fn that records (enter, exit) times and sleeps `duration` between them."""

    async def fn():
        enter = time.monotonic()
        await asyncio.sleep(duration)
        log.append((enter, time.monotonic()))
        return value

    return fn


async def test_off_by_default_passes_calls_through():
    g = Governor()
    assert g.enabled is False
    g.chat_started()
    assert g.throttling() is False
    assert g.wave_size() is None
    log = []
    start = time.monotonic()
    assert await g.call(timed(log, 0.01, "v")) == "v"
    assert time.monotonic() - start < 0.1


def test_invalid_settings_raise():
    for kwargs, name in (({"duty": 0}, "GOVERNOR_DUTY"), ({"duty": 1.5}, "GOVERNOR_DUTY"), ({"wave": 0}, "GOVERNOR_WAVE")):
        with pytest.raises(ValueError, match=name):
            Governor(**kwargs)


def test_counts_streams_and_never_goes_negative():
    g = Governor(duty=0.5)
    g.chat_started()
    g.chat_started()
    for _ in range(3):
        g.chat_ended()
    assert g.decoding == 0
    assert g.throttling() is False


def test_wave_size_only_while_throttling():
    g = Governor(duty=0.5, wave=3)
    assert g.wave_size() is None
    g.chat_started()
    assert g.wave_size() == 3


async def test_one_call_in_flight_while_throttling():
    g = Governor(duty=0.5)
    g.chat_started()
    log = []
    await asyncio.gather(g.call(timed(log, 0.01)), g.call(timed(log, 0.01)))
    (_, first_exit), (second_enter, _) = sorted(log)
    assert second_enter >= first_exit


async def test_pause_follows_duty():
    g = Governor(duty=0.25)
    g.chat_started()
    log = []
    await asyncio.gather(g.call(timed(log, 0.02)), g.call(timed(log, 0.02)))
    (_, first_exit), (second_enter, _) = sorted(log)
    assert second_enter - first_exit >= 0.055


async def test_caller_returns_before_the_pause_and_next_call_waits():
    g = Governor(duty=0.1)  # 20 ms of work earns a ~180 ms pause
    g.chat_started()
    log = []
    start = time.monotonic()
    await g.call(timed(log, 0.02))
    assert time.monotonic() - start < 0.1
    await g.call(timed(log, 0.001))
    (_, first_exit), (second_enter, _) = sorted(log)
    assert second_enter - first_exit >= 0.1


async def test_pause_ends_when_last_chat_ends():
    g = Governor(duty=0.1)
    g.chat_started()
    log = []
    await g.call(timed(log, 0.03))  # earns a ~270 ms pause
    second = asyncio.create_task(g.call(timed(log, 0.001)))
    await asyncio.sleep(0.02)
    ended = time.monotonic()
    g.chat_ended()
    await second
    assert sorted(log)[1][0] - ended < 0.1


async def test_no_pause_when_no_chat():
    g = Governor(duty=0.25)
    log = []
    await asyncio.gather(g.call(timed(log, 0.02)), g.call(timed(log, 0.02)))
    (_, first_exit), (second_enter, _) = sorted(log)
    assert second_enter < first_exit


async def test_cancel_in_the_call_frees_the_slot():
    g = Governor(duty=0.1)
    g.chat_started()
    task = asyncio.create_task(g.call(timed([], 0.05)))
    await asyncio.sleep(0.005)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    await asyncio.wait_for(g.call(timed([], 0.001)), timeout=0.5)


async def test_cancel_in_the_gate_frees_the_slot():
    g = Governor(duty=0.1)
    g.chat_started()
    log = []
    await g.call(timed(log, 0.02))  # earns a ~180 ms pause
    ready_at = time.monotonic() + 0.18
    waiting = asyncio.create_task(g.call(timed(log, 0.001)))
    await asyncio.sleep(0.02)
    waiting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiting
    await asyncio.wait_for(g.call(timed(log, 0.001)), timeout=0.5)
    assert sorted(log)[1][0] <= ready_at + 0.1
