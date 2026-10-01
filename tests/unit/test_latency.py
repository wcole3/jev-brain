import httpx

from scripts.latency import summarize, time_rows


def test_time_rows_posts_one_request_at_a_time():
    seen = []

    def handler(request):
        seen.append(request.read())
        return httpx.Response(200, json={"answers": {}})

    client = httpx.Client(base_url="http://g", transport=httpx.MockTransport(handler))
    rows = [{"id": f"r{i}", "state": "s", "questions": {}, "meta": {"catalog_id": 1}} for i in range(3)]
    recs = time_rows(client, rows, {"layout": "header"})
    assert [r["status"] for r in recs] == [200] * 3 and all(r["ms"] >= 0 for r in recs)
    assert b'"layout": "header"' in seen[0] or b'"layout":"header"' in seen[0]


def test_summary_uses_answered_rows_and_per_catalog_medians():
    recs = [{"id": f"r{i}", "catalog_id": 1, "status": 200, "ms": float(i)} for i in range(10)]
    recs += [{"id": "x", "catalog_id": 2, "status": 422, "ms": 1.0}]
    s = summarize(recs)
    assert s["n"] == 11 and s["answered"] == 10 and s["median_ms"] == 5.0 and s["by_catalog"] == {1: 5.0}
