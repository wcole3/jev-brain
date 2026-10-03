import pytest

from gateway.layouts import load_layouts
from scripts.collect import all_orders
from scripts.m3 import agree, layouts_data, orders_data, recommend
from scripts.m3_report import layouts_markdown, orders_markdown
from scripts.order_stats import in_prior_slice

LAYOUTS = sorted(load_layouts())
TOKENS = (100, 600, 3000, 9000)


def row(prefix: str, i: int) -> dict:
    """A two-option choice row in the test_offline ROW shape; every fourth one is in the long slice."""
    return {"id": f"{prefix}{i}", "source": "index", "family": "ContractNLI" if i % 4 == 0 else "f", "state": "s",
            "questions": {"c": {"type": "choice", "instructions": "pick", "criteria": {"a": None, "b": None}}},
            "gold": {"c": "ab"[i % 2]}}


def record(row_id: str, i: int, layout: str) -> dict:
    """Every collected order: the model likes one option, and shown position 0 by a lean that varies by row."""
    liked, lean = i % 3 % 2, (i % 5) * 0.4 + LAYOUTS.index(layout) * 0.2
    reads = [{"perm": perm, "logprobs": [(perm[0] == liked) + lean, float(perm[1] == liked)]} for perm in all_orders(2)]
    return {"id": row_id, "layout": layout, "status": "ok", "stamp": {}, "input_tokens": TOKENS[i % 4],
            "questions": {"c": reads}}


def dataset(prefix: str, n: int = 40) -> tuple[list[dict], dict]:
    rows = [row(prefix, i) for i in range(n)]
    return [record(r["id"], i, layout) for i, r in enumerate(rows) for layout in LAYOUTS], {r["id"]: r for r in rows}


@pytest.fixture(scope="module")
def data():
    calib_recs, calib_rows = dataset("c")
    recs, rows = dataset("r")
    return calib_recs, calib_rows, recs, rows


@pytest.fixture(scope="module")
def orders(data):
    return orders_data(*data, "decider_chat")


@pytest.fixture(scope="module")
def layouts(data):
    return layouts_data(*data)


def test_orders_data_scores_every_arm_on_every_question(orders, data):
    rows = data[3]
    assert set(orders["arms"]) == {"identity", "identity+reversed", "cyclic:2", "cyclic:3", "cyclic:4", "pride"}
    outside = sum(not in_prior_slice(r) for r in rows)
    assert 0 < outside < len(rows)
    for arm, summary in orders["arms"].items():
        assert summary["overall"]["all"]["n"] == (outside if arm == "pride" else len(rows))
    assert orders["vs_identity"]["identity"]["overall"]["all"]["accuracy"][0] == 0.0
    assert orders["vs_identity"]["pride"]["overall"]["all"]["n"] == outside
    assert set(orders["vs_identity"]["cyclic:2"]["options"]) == {"2"}


def test_orders_data_reports_read_costs_and_order_diagnostics(orders):
    assert orders["arms"]["identity+reversed"]["reads"] == 2 and orders["arms"]["pride"]["mean_reads"] == 1
    assert orders["arms"]["cyclic:4"]["mean_reads"] == 2  # two options: cyclic:4 is two orders
    assert 0 < orders["flips"]["overall"]["all"] <= 1 and orders["auroc"]["overall"]["all"] is not None
    assert set(orders["histograms"]) == {"identity", orders["best"]}


def test_layouts_data_compares_each_layout_on_shared_questions(layouts):
    assert set(layouts["layouts"]) == set(LAYOUTS)
    assert set(layouts["vs_decider_chat"]) == {"header", "question_first"}
    header = layouts["vs_decider_chat"]["header"]
    assert header["slice"]["long"]["n"] == 10 and set(header["length"]) == {"<512", "512-2k", "2k-8k", ">8k"}
    assert layouts["layouts"]["header"]["mean_input_tokens"] == sum(TOKENS) / 4
    assert set(layouts["winners"]["length"]) == {"<512", "512-2k", "2k-8k", ">8k"}
    assert all(not w["auto_switch"] or w["winner"] != layouts["winners"]["overall"]
               for w in layouts["winners"]["length"].values())


def test_recommend_needs_a_ci_clear_of_zero():
    flat = {"accuracy": (0.01, -0.002, 0.02), "ece": (0.0, -0.01, 0.01), "nll": (0.0, -0.01, 0.01)}
    win = {"accuracy": (0.02, 0.01, 0.03), "ece": (0.0, -0.01, 0.01), "nll": (-0.01, -0.02, 0.0)}
    assert recommend({"cyclic:2": flat}, "identity") == "keep the default"
    assert recommend({"cyclic:2": flat, "identity+reversed": win}, "identity") == "identity+reversed"


def test_recommend_takes_an_ece_gain_that_costs_no_accuracy():
    calmer = {"accuracy": (0.0, 0.0, 0.01), "ece": (-0.02, -0.03, -0.01), "nll": (0.0, -0.01, 0.01)}
    costly = calmer | {"accuracy": (-0.01, -0.02, -0.001)}
    assert recommend({"cyclic:3": calmer}, "identity") == "cyclic:3"
    assert recommend({"cyclic:3": costly}, "identity") == "keep the default"


def test_splits_must_agree():
    assert agree({"index-dev": "cyclic:2", "eval": "cyclic:2"}) == "cyclic:2"
    assert agree({"index-dev": "cyclic:2", "eval": "keep the default"}) == (
        "no change: splits disagree (cyclic:2 vs keep the default)")


def report(data: dict, **meta) -> dict:
    return {"meta": {"timestamp": "t", **meta}, "splits": {"index-dev": data, "eval": data},
            "recommendation": data["recommendation"]}


def test_markdown_renders_every_section(orders, layouts):
    text = orders_markdown(report(orders, profile="p", layout="decider_chat"))
    assert "## Provenance" in text and "| 2 | cyclic:2 |" in text and "flip rate" in text and "read cost" in text
    assert "+0.000 [+0.000, +0.000]" in text
    text = layouts_markdown(report(layouts, profile="p"))
    assert "| long | header |" in text and "auto-switch" in text and "read cost" in text
