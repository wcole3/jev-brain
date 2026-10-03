import pytest

from gateway.layouts import load_layouts
from scripts.collect import all_orders
from scripts.m3 import agree, layouts_data, orders_data, per_group, recommend, summary, switches_on_both, winners
from scripts.m3_report import layouts_markdown, orders_markdown
from scripts.metrics import Scored

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
    return {"id": row_id, "layout": layout, "status": "ok", "stamp": {}, "questions": {"c": reads}}


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
    state_tokens = {row_id: TOKENS[i % 4] for i, row_id in enumerate(data[3])}
    return layouts_data(*data, state_tokens)


def test_orders_data_scores_every_arm_on_every_question(orders, data):
    rows = data[3]
    assert set(orders["arms"]) == {"identity", "identity+reversed", "cyclic:2", "cyclic:3", "cyclic:4", "pride"}
    for scores in orders["arms"].values():
        assert scores["overall"]["all"]["n"] == len(rows)
    assert orders["vs_identity"]["identity"]["overall"]["all"]["accuracy"][0] == 0.0
    assert orders["vs_identity"]["pride"]["overall"]["all"]["n"] == len(rows)
    assert set(orders["vs_identity"]["cyclic:2"]["options"]) == {"2"}


def test_orders_data_reports_read_costs_and_order_diagnostics(orders):
    assert orders["arms"]["identity+reversed"]["reads"] == 2 and orders["arms"]["pride"]["mean_reads"] == 1
    assert orders["arms"]["cyclic:4"]["mean_reads"] == 2  # two options: cyclic:4 is two orders
    assert 0 < orders["flips"]["overall"]["all"] <= 1 and orders["auroc"]["overall"]["all"] is not None
    assert set(orders["histograms"]) == {"identity", orders["best"]}


def test_pride_divides_out_a_prior_from_calib(orders):
    assert orders["pride_prior_options"] == [2]  # 40 calib questions of two options
    assert orders["arms"]["pride"]["overall"] != orders["arms"]["identity"]["overall"]


def test_layouts_data_compares_each_layout_on_shared_questions(layouts):
    assert set(layouts["layouts"]) == set(LAYOUTS)
    assert set(layouts["vs_decider_chat"]) == {"header", "question_first"}
    header = layouts["vs_decider_chat"]["header"]
    assert header["slice"]["long"]["n"] == 10 and set(header["length"]) == {"<512", "512-2k", "2k-8k", ">8k"}
    assert set(layouts["winners"]["length"]) == {"<512", "512-2k", "2k-8k", ">8k"}


def answers(rights: list[bool], prefix: str) -> dict:
    return {(f"{prefix}{i}", "q"): Scored("index", "f", "choice", 0, [0.9, 0.1] if right else [0.1, 0.9])
            for i, right in enumerate(rights)}


def test_a_bucket_auto_switches_only_on_a_ci_clear_of_zero():
    # bucket a: header right where decider_chat is wrong; c: header ahead by one, CI spans zero; b: decider_chat
    rights = {"decider_chat": {"a": [False] * 10, "b": [True] * 30, "c": [True] * 10 + [False] * 10},
              "header": {"a": [True] * 10, "b": [False] * 30, "c": [False] * 9 + [True] * 11}}
    arms = {layout: {k: v for bucket, r in by_bucket.items() for k, v in answers(r, bucket).items()}
            for layout, by_bucket in rights.items()}
    groups = {"overall": lambda key, item: "all", "length": lambda key, item: key[0][0],
              "slice": lambda key, item: "rest"}
    got = winners(arms, {layout: per_group(items, groups, summary) for layout, items in arms.items()}, groups)
    assert got["overall"] == "decider_chat"
    assert got["length"]["a"]["winner"] == "header" and got["length"]["a"]["auto_switch"]
    assert got["length"]["c"]["winner"] == "header" and not got["length"]["c"]["auto_switch"]
    assert got["length"]["b"] == {"winner": "decider_chat", "accuracy": 1.0, "vs_overall": None, "auto_switch": False}
    assert switches_on_both({"index-dev": {"winners": got}, "eval": {"winners": got}}) == ["length a: header"]
    unflagged = {"length": {}, "slice": {}}
    assert switches_on_both({"index-dev": {"winners": got}, "eval": {"winners": unflagged}}) == []


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
            "recommendation": data["recommendation"], "auto_switch_on_both": []}


def test_markdown_renders_every_section(orders, layouts):
    text = orders_markdown(report(orders, profile="p", layout="decider_chat"))
    assert "## Provenance" in text and "| 2 | cyclic:2 |" in text and "flip rate" in text and "read cost" in text
    assert "+0.0000 [+0.0000, +0.0000]" in text and "PriDe prior from the calib split" in text
    text = layouts_markdown(report(layouts, profile="p"))
    assert "| long | header |" in text and "auto-switch" in text and "Auto-switch on both splits: none" in text
    assert "1 read per question for each layout (identity); latency measured live in Task 8" in text
