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


def test_strict_fails_on_error_rows_and_on_an_incomplete_full_run():
    ok, error = {"status": "ok"}, {"status": "error"}
    assert evaluate.strict_failure([ok], COMPLETE, subset=False) is None
    assert evaluate.strict_failure([ok, error, error], COMPLETE, subset=False) == "2 error rows"
    incomplete = {"complete": False, "completed": 9}
    assert evaluate.strict_failure([ok], incomplete, subset=False) == "run incomplete: 9 rows"
    assert evaluate.strict_failure([ok], incomplete, subset=True) is None


@pytest.fixture
def index_run_here(tmp_path, monkeypatch):
    """cmd_index with the gateway, shards, merge and harness scoring stubbed; rows go in run/merged/results.jsonl."""
    real_client = httpx.AsyncClient
    health = {"profile": "p", "served_model": "m"}
    monkeypatch.setattr(evaluate.httpx, "AsyncClient", lambda **kw: real_client(
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json=health)), **kw))

    async def run_index(args, run, health):
        return {"codes": [0], "seconds": 60, "vllm": [], "idle": [], "busy": []}

    monkeypatch.setattr(evaluate, "ROOT", tmp_path)
    monkeypatch.setattr(evaluate, "run_index", run_index)
    monkeypatch.setattr(evaluate.index_run, "merge", lambda shards, out: None)
    monkeypatch.setattr(evaluate, "score", lambda merged: {"complete": True, "completed": 2})
    monkeypatch.setattr(evaluate, "index_summary", lambda *a: "body\n")
    monkeypatch.setattr(evaluate, "git_revision", lambda: "abc")
    monkeypatch.setattr(evaluate.host_info, "summary", lambda: "host")
    run = tmp_path / "run"
    (run / "merged").mkdir(parents=True)
    return run


@pytest.mark.parametrize("statuses, strict, fails", [
    (["ok", "ok"], True, False), (["ok", "error"], True, True), (["ok", "error"], False, False)])
async def test_index_strict_exits_nonzero_after_writing_the_summary(index_run_here, statuses, strict, fails):
    rows = "".join(f'{{"status": "{s}"}}\n' for s in statuses)
    (index_run_here / "merged" / "results.jsonl").write_text(rows)
    argv = ["index", "--profile", "p", "--run-dir", str(index_run_here), *(["--strict"] if strict else [])]
    if fails:
        with pytest.raises(SystemExit, match="1 error rows") as exit_:
            await evaluate.cmd_index(evaluate.parse_args(argv))
        assert exit_.value.code != 0
    else:
        await evaluate.cmd_index(evaluate.parse_args(argv))
    summary = index_run_here.parent / "docs" / "results" / "p" / "run-index" / "summary.md"
    assert summary.read_text().endswith("body\n")


def offline_args(*extra):
    return evaluate.parse_args(["offline", "--profile", "qwen3.6-27b", "--split", "eval", *extra])


def test_offline_temperature_overrides_every_type_without_an_offset():
    args = offline_args("--temperature", "1.943")
    cal = evaluate.offline_calibration(args, None, None)
    assert cal.T == {"choice": 1.943, "score": 1.943, "noul": 1.943} and cal.b == 0.0
    assert cal.source == "override T=1.943" and cal.orders is None
    assert evaluate.arm_suffix(args) == "-T1.943"
    assert evaluate.arm_suffix(offline_args("--uncalibrated")) == "-uncalibrated"
    with pytest.raises(SystemExit):
        offline_args("--temperature", "2", "--uncalibrated")
