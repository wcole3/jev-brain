import httpx
import pytest

from scripts import evaluate

COMPLETE = {"complete": True, "completed": 100}


def test_a_full_clean_run_is_judged():
    assert evaluate.unjudged_reason({"ok": 100}, COMPLETE) is None


def test_error_rows_block_the_parity_verdict():
    reason = evaluate.unjudged_reason({"ok": 97, "error": 3}, COMPLETE)
    assert reason == "3 error rows: resume with --run-dir"


def test_every_reason_is_named():
    reason = evaluate.unjudged_reason({"error": 1}, {"complete": False, "completed": 9}, "subset run")
    assert reason == "subset run; 1 error rows: resume with --run-dir; run incomplete: 9 rows"


def client_for(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url="http://gw", transport=httpx.MockTransport(handler))


async def test_probe_records_failures_instead_of_raising():
    def down(request):
        raise httpx.ConnectError("refused")

    async with client_for(down) as c:
        assert await evaluate.probe_chat(c, "m") == {"error": "ConnectError"}
    async with client_for(lambda r: httpx.Response(500, text="boom")) as c:
        assert await evaluate.probe_chat(c, "m") == {"error": "no chunks streamed"}


async def test_probe_measures_a_streamed_reply():
    sse = b'data: {"choices": []}\n\ndata: {"choices": []}\n\ndata: [DONE]\n\n'
    async with client_for(lambda r: httpx.Response(200, content=sse)) as c:
        sample = await evaluate.probe_chat(c, "m")
    assert set(sample) == {"ttft_ms", "chunks_per_s"}


def test_run_notes_count_failed_probes():
    outcome = {"codes": [0], "seconds": 60, "vllm": [], "idle": [{"error": "ConnectError"}],
               "busy": [{"ttft_ms": 10.0, "chunks_per_s": 50.0}, {"error": "ReadTimeout"}]}
    notes = evaluate.run_notes(outcome)
    assert "- chat idle: 1 of 1 probes failed" in notes
    assert "- chat during run: median TTFT 10 ms, 50.0 chunks/s (1 samples, 1 failed)" in notes


def test_offline_coverage_counts_collected_records_for_the_layout():
    recs = [{"id": "a", "layout": "header"}, {"id": "a", "layout": "decider_chat"}, {"id": "z", "layout": "header"}]
    assert evaluate.coverage(recs, {"a", "b"}, "header") == (1, 2)


def test_offline_refuses_short_coverage_unless_allowed():
    with pytest.raises(SystemExit, match="1 of 2 .* --allow-partial"):
        evaluate.check_coverage(1, 2, "header", allow_partial=False)
    evaluate.check_coverage(1, 2, "header", allow_partial=True)
    evaluate.check_coverage(2, 2, "header", allow_partial=False)
    assert evaluate.parse_args(["offline", "--profile", "p", "--split", "eval", "--allow-partial"]).allow_partial
