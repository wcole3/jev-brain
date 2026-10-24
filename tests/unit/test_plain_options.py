import pytest

from gateway.layouts import PROMPTS_DIR, load_layout
from tests.helpers import HLE, LAYOUTS, ORDERS, QUICKSTART, batch_for

D1 = "reread-d1"
ONE = {"hle": HLE["hle"]}


@pytest.fixture
def d1(monkeypatch):
    monkeypatch.setitem(LAYOUTS, D1, load_layout(PROMPTS_DIR / "experiments" / f"{D1}.toml"))


def test_served_layouts_have_no_plain_options():
    assert all("plain_options" not in layout.order for layout in LAYOUTS.values())


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_orders_share_everything_up_to_the_labelled_options(tok_name, request, d1):
    tok = request.getfixturevalue(tok_name)
    rows = batch_for(tok, D1, ONE, ORDERS).rows
    texts = [tok.decode(r.ids) for r in rows]
    plain = "Options:\n- Increase temperature\n- Decrease temperature\n- Increase Enzyme Concentration"
    assert all(plain in t and "(A) Increase temperature" in texts[0] for t in texts)
    cut = [t.rindex("\n\nQuestion:") for t in texts]
    assert len({t[: c] for t, c in zip(texts, cut)}) == 1  # identical up to the second question copy
    assert "\n\n\n" not in texts[0]


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_rows_end_like_the_served_layout(tok_name, request, d1):
    tok = request.getfixturevalue(tok_name)
    for d, s in zip(batch_for(tok, D1, QUICKSTART).rows, batch_for(tok, "blurb_header_reread", QUICKSTART).rows):
        served = tok.decode(s.ids)
        assert tok.decode(d.ids).endswith(served[served.rindex("\n\nQuestion:"):]) and d.label_ids == s.label_ids


def test_plain_options_must_follow_a_question(tmp_path):
    text = (PROMPTS_DIR / "experiments" / f"{D1}.toml").read_text()
    bad = text.replace('"question", "plain_options"', '"plain_options", "question"')
    (tmp_path / "bad.toml").write_text(bad)
    with pytest.raises(ValueError, match="plain_options"):
        load_layout(tmp_path / "bad.toml")
