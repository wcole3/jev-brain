import pytest

from gateway.calibration import Calibration
from gateway.config import Settings
from gateway.layouts import load_layouts
from gateway.questions import render_state
from scripts import m3
from scripts.collect import all_orders
from scripts.experiments import BY_TYPE, KEEP, SHIPPED, per_group, qualifying, summary, verdict
from scripts.m3 import orders_data
from scripts.m3_layouts import count_state_tokens, layouts_study, switches_on_both, winners
from scripts.m3_report import layouts_markdown, orders_markdown
from scripts.metrics import Scored

LAYOUTS = sorted(load_layouts())
TOKENS = (100, 600, 3000, 9000)
SHIPPED_CAL = Calibration({"choice": 2.0, "score": 1.0, "noul": 1.0}, b=0.3, source="p/decider_chat/calibration.json")


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
    return orders_data(*data, "decider_chat", "identity", SHIPPED_CAL)


@pytest.fixture(scope="module")
def layouts(data):
    calib_recs, calib_rows, recs, rows = data
    state_tokens = {row_id: TOKENS[i % 4] for i, row_id in enumerate(rows)}
    splits = {split: (recs, rows, state_tokens) for split in ("index-dev", "eval")}
    return layouts_study(calib_recs, calib_rows, splits, "decider_chat", "identity", dict.fromkeys(splits, SHIPPED_CAL))


def test_orders_data_scores_every_arm_against_the_default(orders, data):
    rows = data[3]
    assert set(orders["arms"]) == {"identity", "identity+reversed", "cyclic:2", "cyclic:3", "cyclic:4", "pride", SHIPPED}
    for scores in orders["arms"].values():
        assert scores["overall"]["all"]["n"] == len(rows)
    assert orders["default"] == "identity" and "identity" not in orders["vs_default"]
    assert orders["vs_default"]["pride"]["overall"]["all"]["n"] == len(rows)
    assert set(orders["vs_default"]["cyclic:2"]["options"]) == {"2"}
    assert orders["arms"][SHIPPED]["T"] == SHIPPED_CAL.T and orders["arms"][SHIPPED]["reads"] == 1


def test_orders_data_reports_read_costs_and_order_diagnostics(orders):
    assert orders["arms"]["identity+reversed"]["reads"] == 2 and orders["arms"]["pride"]["mean_reads"] == 1
    assert orders["arms"]["cyclic:4"]["mean_reads"] == 2  # two options: cyclic:4 is two orders
    assert 0 < orders["flips"]["overall"]["all"] <= 1 and orders["auroc"]["overall"]["all"] is not None
    assert set(orders["histograms"]) == {"identity", orders["best"]}


def test_pride_divides_out_a_prior_from_calib(orders):
    assert orders["pride_prior_options"] == [2]  # 40 calib questions of two options
    identity, pride = orders["arms"]["identity"]["overall"]["all"], orders["arms"]["pride"]["overall"]["all"]
    assert (identity["accuracy"], pride["accuracy"]) == pytest.approx((0.525, 0.525))  # fixture leans moved with the layout index
    assert pride["ece"] == pytest.approx(0.012751, abs=1e-6) and pride["nll"] < identity["nll"]


def test_layouts_study_compares_each_layout_on_shared_questions(layouts):
    data = layouts["splits"]["index-dev"]
    assert set(data["layouts"]) == {*LAYOUTS, SHIPPED} and set(data["vs_default"]) == {"blurb_header", "header", "question_first", SHIPPED}
    assert data["answered"] == {"any": 40, "all": 40, **dict.fromkeys(LAYOUTS, 40)}
    header = data["vs_default"]["header"]
    assert header["slice"]["long"]["n"] == 10 and set(header["length"]) == {"<512", "512-2k", "2k-8k", ">8k"}
    assert header["overall"]["all"]["n"] == 40
    assert data["winners"]["baseline"] == "decider_chat" and layouts["recommendation"] == KEEP
    assert set(data["winners"]["length"]) == {"<512", "512-2k", "2k-8k", ">8k"}


def test_count_state_tokens_counts_the_rendered_state():
    class PerCharacter:
        def __call__(self, texts, add_special_tokens):
            return {"input_ids": [list(text) for text in texts]}
    rows = {"a": {"state": "hello"}, "b": {"state": {"k": [1, 2]}}}
    assert count_state_tokens(PerCharacter(), rows) == {"a": len(render_state("hello")),
                                                        "b": len(render_state({"k": [1, 2]}))}


def answers(rights: list[bool], prefix: str) -> dict:
    return {(f"{prefix}{i}", "q"): Scored("index", "f", "choice", 0, [0.9, 0.1] if right else [0.1, 0.9])
            for i, right in enumerate(rights)}


def bucket_arms() -> tuple[dict, dict, dict]:
    # bucket a: header right where decider_chat is wrong; c: header ahead by one, CI spans zero; b: decider_chat
    rights = {"decider_chat": {"a": [False] * 10, "b": [True] * 30, "c": [True] * 10 + [False] * 10},
              "header": {"a": [True] * 10, "b": [False] * 30, "c": [False] * 9 + [True] * 11}}
    arms = {layout: {k: v for bucket, r in by_bucket.items() for k, v in answers(r, bucket).items()}
            for layout, by_bucket in rights.items()}
    groups = BY_TYPE | {"length": lambda key, item: key[0][0], "slice": lambda key, item: "rest"}
    return arms, {layout: per_group(items, groups, summary) for layout, items in arms.items()}, groups


def test_a_bucket_auto_switches_only_on_a_ci_clear_of_zero():
    got = winners(*bucket_arms(), "decider_chat")
    assert got["baseline"] == "decider_chat"
    assert got["length"]["a"]["winner"] == "header" and got["length"]["a"]["auto_switch"]
    assert got["length"]["c"]["winner"] == "header" and not got["length"]["c"]["auto_switch"]
    assert got["length"]["b"] == {"winner": "decider_chat", "accuracy": 1.0, "vs_baseline": None, "auto_switch": False}
    assert switches_on_both({"index-dev": {"winners": got}, "eval": {"winners": got}}) == ["length a: header"]
    unflagged = {"length": {}, "slice": {}}
    assert switches_on_both({"index-dev": {"winners": got}, "eval": {"winners": unflagged}}) == []


def test_auto_switch_is_measured_against_the_given_baseline():
    got = winners(*bucket_arms(), "header")
    assert got["baseline"] == "header" and got["length"]["b"]["winner"] == "decider_chat"
    assert got["length"]["b"]["auto_switch"] and got["length"]["b"]["vs_baseline"]["accuracy"][0] == 1.0
    assert got["length"]["a"] == {"winner": "header", "accuracy": 1.0, "vs_baseline": None, "auto_switch": False}


FLAT = {"n": 9, "accuracy": (0.01, -0.002, 0.02), "ece": (0.0, -0.01, 0.01)}


def win(gain: float) -> dict:
    return {"n": 9, "accuracy": (gain, gain / 2, 2 * gain), "ece": (0.0, -0.01, 0.01)}


def vs(**arms) -> dict:
    return {arm: {"overall": {"all": c}} for arm, c in arms.items()}


def test_qualifying_needs_a_ci_clear_of_zero_and_skips_non_candidates():
    comps = vs(**{"cyclic:2": FLAT, "identity+reversed": win(0.02), "pride": win(0.05), SHIPPED: win(0.05)})
    assert qualifying(comps, ["cyclic:2", "identity+reversed"]) == ["identity+reversed"]


def test_qualifying_takes_an_ece_gain_that_costs_no_accuracy():
    calmer = {"n": 9, "accuracy": (0.0, 0.0, 0.01), "ece": (-0.02, -0.03, -0.01)}
    costly = calmer | {"accuracy": (-0.01, -0.02, -0.001)}
    assert qualifying(vs(**{"cyclic:3": calmer}), ["cyclic:3"]) == ["cyclic:3"]
    assert qualifying(vs(**{"cyclic:3": costly}), ["cyclic:3"]) == []


def split(**arms) -> dict:
    return {"vs_default": vs(**arms), "qualifying": qualifying(vs(**arms), list(arms))}


def test_verdict_picks_the_cheapest_arm_both_splits_qualify_even_when_their_argmax_differs():
    splits = {"index-dev": split(**{"cyclic:3": win(0.03), "cyclic:4": win(0.02)}),
              "eval": split(**{"cyclic:3": win(0.02), "cyclic:4": win(0.03)})}
    assert verdict(splits, cost={"cyclic:3": 2.5, "cyclic:4": 3.0}.get) == "cyclic:3"
    assert verdict(splits, cost={"cyclic:3": 3.0, "cyclic:4": 2.5}.get) == "cyclic:4"


def test_verdict_breaks_a_cost_tie_on_the_mean_gain_and_keeps_the_default_without_overlap():
    splits = {"index-dev": split(**{"cyclic:2": win(0.01), "identity+reversed": win(0.04)}),
              "eval": split(**{"cyclic:2": win(0.05), "identity+reversed": win(0.03)})}
    assert verdict(splits, cost=lambda arm: 2) == "identity+reversed"  # mean gain 0.035 against 0.03
    apart = {"index-dev": split(**{"cyclic:2": win(0.01), "identity+reversed": FLAT}),
             "eval": split(**{"cyclic:2": FLAT, "identity+reversed": win(0.03)})}
    assert verdict(apart, cost=lambda arm: 2) == KEEP


def test_orders_report_reads_the_defaults_from_the_profile(monkeypatch, data):
    calib_recs, calib_rows, recs, rows = data
    monkeypatch.setattr(m3, "load", lambda profile, s: (calib_recs, calib_rows, "c") if s == "calib" else (recs, rows, s))
    monkeypatch.setattr(m3, "shipped_calibration", lambda s, layout, recs: SHIPPED_CAL)
    settings = Settings("p", "m", "r", "p", 4096, prompt_layout="header", option_orders="identity+reversed")
    monkeypatch.setattr(m3.Settings, "from_profile", lambda name: settings)
    got = m3.orders_report("p")
    assert got["meta"]["layout"] == "header" and got["splits"]["eval"]["default"] == "identity+reversed"
    assert "identity+reversed" not in got["splits"]["eval"]["vs_default"] and "identity" in got["splits"]["eval"]["vs_default"]
    assert got["meta"]["defaults"] == "PROMPT_LAYOUT header, OPTION_ORDERS identity+reversed (profiles/p.env)"


def test_layouts_report_runs_on_the_profile_defaults(monkeypatch, data):
    calib_recs, calib_rows, recs, rows = data
    monkeypatch.setattr(m3, "load", lambda profile, s: (calib_recs, calib_rows, "c") if s == "calib" else (recs, rows, s))
    monkeypatch.setattr(m3, "shipped_calibration", lambda s, layout, recs: SHIPPED_CAL)
    monkeypatch.setattr(m3, "load_tokenizer", lambda profile: None)
    monkeypatch.setattr(m3, "count_state_tokens", lambda tok, rows: dict.fromkeys(rows, 100))
    settings = Settings("p", "m", "r", "p", 4096, prompt_layout="header", option_orders="identity")
    monkeypatch.setattr(m3.Settings, "from_profile", lambda name: settings)
    got = m3.layouts_report("p")
    assert got["meta"]["orders"] == "identity" and got["splits"]["eval"]["default"] == "header"
    assert set(got["splits"]["eval"]["vs_default"]) == {"blurb_header", "decider_chat", "question_first", SHIPPED}
    assert got["meta"][SHIPPED] == "p/decider_chat/calibration.json: T choice 2.000, score 1.000, noul 1.000, b 0.300"
    assert "# p M3 layouts" in layouts_markdown(got)


def report(data: dict, **meta) -> dict:
    return {"meta": {"timestamp": "t", **meta}, "splits": {"index-dev": data, "eval": data}, "recommendation": KEEP,
            "auto_switch_on_both": []}


def test_markdown_renders_every_section(orders, layouts):
    text = orders_markdown(report(orders, profile="p", layout="decider_chat"))
    assert "## Provenance" in text and "| 2 | cyclic:2 |" in text and "flip rate" in text and "read cost" in text
    assert "| all | identity | 40 |" in text and "baseline |" in text and "PriDe prior from the calib split" in text
    assert "- pride (diagnostic, needs gateway support (no OPTION_ORDERS value)): index-dev Δ accuracy" in text
    assert f"- {SHIPPED}: index-dev Δ accuracy" in text and "- index-dev qualifies: " in text
    text = layouts_markdown(layouts | {"meta": {"timestamp": "t", "profile": "p", "orders": "identity"}})
    assert "| long | header |" in text and "auto-switch" in text and "Auto-switch on both splits: none" in text
    assert "the same reads per question for each layout (identity); latency measured live on the latency sample" in text
    assert "Baseline: decider_chat (the verdict's layout" in text and "compared on 40" in text
