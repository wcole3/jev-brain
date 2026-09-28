import pytest

from tests.helpers import tokenizer_for


@pytest.fixture(scope="session")
def qwen_tok():
    return tokenizer_for("qwen3.6-27b")
