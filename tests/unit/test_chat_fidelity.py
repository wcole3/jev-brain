from scripts.chat_fidelity import PROMPTS, compare, first_difference


def rec(*contents):
    return {
        "model": "m",
        "replies": [{"prompt": f"p{i}", "content": c, "reasoning": None} for i, c in enumerate(contents)],
    }


def test_first_difference_reports_index_and_prefix_share():
    assert first_difference("abcd", "abxd") == (2, 0.5)
    assert first_difference("abc", "abcdef") == (3, 0.5)


def test_compare_counts_exact_matches_and_lists_mismatches():
    text = compare(rec("same", "abcd"), rec("same", "abxd"))
    assert "exact match: 1/2 (50%)" in text
    assert "| p1 |" in text


def test_twenty_prompts():
    assert len(PROMPTS) == 20 and len(set(PROMPTS)) == 20
