import json

import pytest

from gateway.layouts import load_layouts
from gateway.questions import render_question, render_state
from gateway.schema import Question, RequestError

LAYOUT = load_layouts()["decider_chat"]


def q(**kw):
    return render_question(Question(**kw), LAYOUT)


def test_choice_descriptions_null_and_objects():
    r = q(type="choice", instructions="Team?", criteria={"billing": "Payments", "sales": None, "x": {"k": 1}})
    assert r.options == ["billing: Payments", "sales", 'x: {"k": 1}']
    assert r.names == ["billing", "sales", "x"]


def test_choice_list_criteria():
    assert q(type="choice", instructions="?", criteria=["a", "b"]).options == ["a", "b"]


def test_choice_limits_use_harness_markers():
    with pytest.raises(RequestError, match="a choice needs at least two options"):
        q(type="choice", instructions="?", criteria={"a": None})
    with pytest.raises(RequestError, match="options per choice"):
        q(type="choice", instructions="?", criteria={str(i): None for i in range(256)})


def test_score_levels_and_legend_form():
    r = q(type="score", instructions="Angry?", criteria=["Calm", "Angry"])
    assert (r.options, r.names, r.legend) == (["0: Calm", "1: Angry"], [0, 1], ["Calm", "Angry"])
    assert q(type="score", instructions="?", criteria={"1": "b", "0": "a"}).options == ["0: a", "1: b"]
    with pytest.raises(RequestError, match="a score takes 2 to 10 levels"):
        q(type="score", instructions="?", criteria=[str(i) for i in range(11)])


def test_noul_rendering():
    assert q(type="noul", instructions="Urgent?").options == ["no", "yes"]
    r = q(type="noul", instructions="Urgent?", criteria={"true": "needs help now", "false": "can wait"})
    assert r.options == ["no: can wait", "yes: needs help now"]
    assert r.names == [False, True]


def test_noul_without_instructions_needs_a_description():
    r = q(type="noul", criteria={"true": "The customer is angry"})
    assert r.text == "Which answer fits the context?"
    with pytest.raises(RequestError, match="noul question without instructions"):
        q(type="noul")


def test_missing_instructions_rejected():
    with pytest.raises(RequestError, match="question without instructions"):
        q(type="choice", criteria=["a", "b"])


def test_render_state():
    assert render_state("plain text") == "plain text"
    assert render_state({"a": [1, 2]}) == '{"a": [1, 2]}'
    long_list = render_state({"r": [{"v": i} for i in range(8)]})
    assert json.loads(long_list)["r"][3] == {"_index": 3, "v": 3}
    assert json.loads(render_state(list(range(8))))[2] == {"_index": 2, "value": 2}
