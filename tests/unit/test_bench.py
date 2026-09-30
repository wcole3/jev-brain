import datetime

import pytest

from scripts.bench import parse_args, run_suffix


def test_parse_args_chat_defaults_off():
    assert parse_args(["--profile", "p"]).chat is False


def test_parse_args_chat_flag_turns_it_on():
    assert parse_args(["--profile", "p", "--chat"]).chat is True


def test_parse_args_gateway_needs_a_profile():
    with pytest.raises(SystemExit):
        parse_args([])


def test_parse_args_jev_needs_no_profile():
    assert parse_args(["--target", "jev"]).target == "jev"


def test_parse_args_jev_rejects_chat():
    with pytest.raises(SystemExit):
        parse_args(["--target", "jev", "--chat"])


def test_run_suffix_is_utc_time_plus_flags():
    started = datetime.datetime(2026, 9, 29, 21, 9, 57, tzinfo=datetime.UTC)
    assert run_suffix(started, quick=False, jevbench_only=False) == "2026-09-29T210957Z"
    assert run_suffix(started, quick=True, jevbench_only=False) == "2026-09-29T210957Z-quick"
    assert run_suffix(started, quick=True, jevbench_only=True) == "2026-09-29T210957Z-quick-jevbench"
