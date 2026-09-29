"""vLLM's own view of a bench phase: KV cache use and token counts, read from its /metrics."""

import asyncio
import contextlib
import re
import sys
import time

import httpx

GAUGES = {
    "kv": "vllm:kv_cache_usage_perc",
    "running": "vllm:num_requests_running",
    "waiting": "vllm:num_requests_waiting",
}
COUNTERS = {
    "prompt_tokens": "vllm:prompt_tokens_total",
    "cached_prompt_tokens": "vllm:prompt_tokens_cached_total",
    "generation_tokens": "vllm:generation_tokens_total",
    "preemptions": "vllm:num_preemptions_total",
}
LINE = re.compile(r"^([\w:]+)(?:\{.*\})?\s+(\S+)\s*$")


def parse_metrics(text: str) -> dict[str, float]:
    """Prometheus text to {exact metric name: value summed over its label sets}."""
    totals: dict[str, float] = {}
    for line in text.splitlines():
        match = LINE.match(line)
        if match:
            totals[match[1]] = totals.get(match[1], 0.0) + float(match[2])
    return totals


def parse_kv_capacity(text: str) -> tuple[int, int] | None:
    """(num_gpu_blocks, block_size) from the cache_config_info labels."""
    for line in text.splitlines():
        if line.startswith("vllm:cache_config_info{"):
            labels = dict(re.findall(r'(\w+)="([^"]*)"', line))
            return int(labels["num_gpu_blocks"]), int(labels["block_size"])
    return None


class Vllm:
    """Scrapes one vLLM server; appends per-phase records to `records`."""

    def __init__(self, url: str, records: list, interval: float = 0.25):
        self.client = httpx.AsyncClient(base_url=url, timeout=5)
        self.records, self.interval, self.warned = records, interval, False

    async def aclose(self) -> None:
        await self.client.aclose()

    async def scrape(self) -> str | None:
        """The /metrics text, or None (with one warning per run) when vLLM can't be read."""
        try:
            r = await self.client.get("/metrics")
            r.raise_for_status()
            return r.text
        except httpx.HTTPError:
            if not self.warned:
                print(f"warning: cannot read vLLM metrics at {self.client.base_url}; no KV data", file=sys.stderr)
                self.warned = True
            return None

    async def kv_capacity(self) -> tuple[int, int] | None:
        text = await self.scrape()
        return parse_kv_capacity(text) if text else None

    async def snapshot(self) -> dict[str, float] | None:
        text = await self.scrape()
        metrics = parse_metrics(text) if text else {}
        if GAUGES["kv"] not in metrics:
            return None
        return {key: metrics.get(name, 0.0) for key, name in (GAUGES | COUNTERS).items()}

    async def sample_forever(self, samples: list, began: float) -> None:
        while True:
            if snap := await self.snapshot():
                samples.append({"t": time.perf_counter() - began} | {key: snap[key] for key in GAUGES})
            await asyncio.sleep(self.interval)

    @contextlib.asynccontextmanager
    async def watch(self, phase: str):
        """Record counter deltas and gauge peaks for the block; never fails the run."""
        before = await self.snapshot()
        began, samples = time.perf_counter(), []
        sampler = asyncio.create_task(self.sample_forever(samples, began)) if before else None
        try:
            yield
        finally:
            if sampler:
                sampler.cancel()
                await asyncio.gather(sampler, return_exceptions=True)
                after = await self.snapshot()
                if after:
                    samples.append({"t": time.perf_counter() - began} | {key: after[key] for key in GAUGES})
                    self.record(phase, before, after, samples)

    def record(self, phase: str, before: dict, after: dict, samples: list) -> None:
        summary = {"test": "vllm", "phase": phase} | {key: round(after[key] - before[key]) for key in COUNTERS}
        kv = [s["kv"] for s in samples]
        summary |= {
            "kv_peak": max(kv),
            "kv_mean": sum(kv) / len(kv),
            "waiting_peak": max(s["waiting"] for s in samples),
            "running_peak": max(s["running"] for s in samples),
        }
        self.records.append(summary)
        self.records += [{"test": "vllm_sample", "phase": phase} | s for s in samples]
