import pytest
from pydantic import ValidationError

from gateway.schema import SystemOneRequest


def test_extra_fields_ignored_and_overrides_parsed():
    r = SystemOneRequest.model_validate({"state": "s", "model": "jev-latest", "foo": 1, "layout": "header",
                                         "questions": {"q": {"type": "noul", "extra": 2}}})
    assert r.layout == "header"
    assert r.option_orders is None
    assert r.questions["q"].type == "noul"


def test_unknown_question_type_rejected():
    with pytest.raises(ValidationError):
        SystemOneRequest.model_validate({"questions": {"q": {"type": "maybe"}}})
