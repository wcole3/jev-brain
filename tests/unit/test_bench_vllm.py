import asyncio

import httpx
import pytest

from scripts.bench_vllm import Vllm, parse_cache_labels, parse_metrics


def metrics_text(kv: float, running: int, waiting: int, prompt: int, cached: int, generated: int, preempted: int):
    return f"""# HELP vllm:kv_cache_usage_perc KV-cache usage.
# TYPE vllm:kv_cache_usage_perc gauge
vllm:kv_cache_usage_perc{{engine="0",model_name="m"}} {kv}
vllm:num_requests_running{{engine="0",model_name="m"}} {running}.0
vllm:num_requests_waiting{{engine="0",model_name="m"}} {waiting}.0
vllm:num_requests_waiting_by_reason{{engine="0",reason="capacity"}} 99.0
vllm:prompt_tokens_total{{engine="0",model_name="m"}} {prompt}.0
vllm:prompt_tokens_by_source_total{{engine="0",source="local_compute"}} 5.0
vllm:prompt_tokens_cached_total{{engine="0",model_name="m"}} {cached}.0
vllm:generation_tokens_total{{engine="0",model_name="m"}} {generated}.0
vllm:num_preemptions_total{{engine="0",model_name="m"}} {preempted}.0
vllm:cache_config_info{{block_size="16",engine="0",num_gpu_blocks="5000",cache_dtype="auto"}} 1.0
"""


def test_parse_metrics_matches_names_exactly_and_sums_label_sets():
    text = metrics_text(0.5, 2, 1, 100, 40, 7, 0) + 'vllm:num_requests_waiting{engine="1"} 3.0\n'
    parsed = parse_metrics(text)
    assert parsed["vllm:num_requests_waiting"] == 4.0
    assert parsed["vllm:num_requests_waiting_by_reason"] == 99.0
    assert parsed["vllm:prompt_tokens_total"] == 100.0
    assert parsed["vllm:kv_cache_usage_perc"] == 0.5


def test_parse_cache_labels_returns_every_label():
    labels = parse_cache_labels(metrics_text(0, 0, 0, 0, 0, 0, 0))
    assert (labels["num_gpu_blocks"], labels["block_size"]) == ("5000", "16")
    assert parse_cache_labels("vllm:kv_cache_usage_perc 0.1\n") is None


def scripted_vllm(texts: list[str], records: list) -> Vllm:
    """A Vllm whose scrapes return `texts` in order; a huge interval leaves one sample per phase."""
    replies = iter(texts)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text=next(replies)))
    vllm = Vllm("http://vllm", records, interval=1000)
    vllm.client = httpx.AsyncClient(base_url="http://vllm", transport=transport)
    return vllm


def test_watch_records_counter_deltas_gauge_peaks_and_samples():
    records: list = []
    vllm = scripted_vllm(
        [
            metrics_text(0.10, 0, 0, 1000, 200, 50, 1),  # entry
            metrics_text(0.60, 3, 2, 1500, 300, 60, 1),  # first sample
            metrics_text(0.20, 1, 5, 3000, 1200, 90, 3),  # exit
        ],
        records,
    )

    async def phase():
        async with vllm.watch("warm"):
            await asyncio.sleep(0.05)

    asyncio.run(phase())
    summary, *samples = records
    assert summary == {
        "test": "vllm",
        "phase": "warm",
        "prompt_tokens": 2000,
        "cached_prompt_tokens": 1000,
        "generation_tokens": 40,
        "preemptions": 2,
        "kv_peak": 0.6,
        "kv_mean": pytest.approx(0.4),
        "waiting_peak": 5,
        "running_peak": 3,
    }
    assert [(s["test"], s["phase"], s["kv"], s["running"], s["waiting"]) for s in samples] == [
        ("vllm_sample", "warm", 0.6, 3, 2),
        ("vllm_sample", "warm", 0.2, 1, 5),
    ]
    assert 0 <= samples[0]["t"] <= samples[1]["t"]


def test_unreachable_vllm_records_nothing_and_warns_once(capsys):
    def refuse(request):
        raise httpx.ConnectError("down")

    records: list = []
    vllm = Vllm("http://vllm", records)
    vllm.client = httpx.AsyncClient(base_url="http://vllm", transport=httpx.MockTransport(refuse))

    async def phases():
        for name in ("cold", "warm"):
            async with vllm.watch(name):
                pass

    asyncio.run(phases())
    assert records == []
    assert capsys.readouterr().err.count("warning") == 1
