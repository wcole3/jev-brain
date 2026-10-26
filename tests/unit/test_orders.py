import pytest

from gateway.orders import average_back, gate, live_rows, option_orders, rereads
from scripts.order_policies import Policy, perms, second_perm


def test_settings():
    assert option_orders(3, "identity") == [[0, 1, 2]]
    assert option_orders(3, "identity+reversed") == [[0, 1, 2], [2, 1, 0]]
    assert option_orders(4, "cyclic:2") == [[0, 1, 2, 3], [2, 3, 0, 1]]
    assert option_orders(2, "cyclic:5") == [[0, 1], [1, 0]]
    with pytest.raises(ValueError):
        option_orders(3, "shuffle")
    with pytest.raises(ValueError):
        option_orders(3, "cyclic:0")


def test_cyclic_k_is_clamped_to_n():
    assert option_orders(3, "cyclic:1000000000") == [[0, 1, 2], [1, 2, 0], [2, 0, 1]]


def test_average_back_maps_positions_to_caller_options():
    # identity favours shown position 0 (option 0); reversed favours shown position 0 (option 2)
    probs = [[0.7, 0.2, 0.1], [0.7, 0.2, 0.1]]
    assert average_back(probs, [[0, 1, 2], [2, 1, 0]]) == pytest.approx([0.4, 0.2, 0.4])


def test_min_n_adds_reversed_from_k_options():
    assert option_orders(3, "min_n:4+reversed") == [[0, 1, 2]]
    assert option_orders(4, "min_n:4+reversed") == [[0, 1, 2, 3], [3, 2, 1, 0]]


def test_top_p_reads_identity_first_and_names_its_threshold():
    assert option_orders(5, "top_p:0.9+reversed") == [[0, 1, 2, 3, 4]]
    assert gate("top_p:0.9+reversed") == 0.9
    assert gate("min_n:4+reversed") is None and gate("identity") is None


def test_reread_p_reads_identity_first_and_names_its_threshold():
    assert option_orders(5, "reread_p:0.9") == [[0, 1, 2, 3, 4]]
    assert gate("reread_p:0.9") == 0.9 and gate("reread_p:1") == 1.0
    assert rereads("reread_p:0.9") and not rereads("top_p:0.9+reversed")


@pytest.mark.parametrize(
    "bad",
    ["min_n:x+reversed", "min_n:1+reversed", "min_n:4+half", "top_p:0+reversed", "top_p:1.5+reversed", "top_p:0.9",
     "reread_p:0", "reread_p:1.5", "reread_p:x", "reread_p:", "reread_p:0.9+reversed", "reread_p:0.9+"],
)
def test_malformed_gated_settings_raise(bad):
    with pytest.raises(ValueError):
        option_orders(4, bad)
    with pytest.raises(ValueError):
        gate(bad)


def test_live_rows_counts_what_the_first_pass_reads():
    assert live_rows([2, 4, 5], "min_n:4+reversed") == 5
    assert live_rows([2, 4, 5], "top_p:0.9+reversed") == 3
    assert live_rows([2, 4, 5], "reread_p:0.9") == 3


@pytest.mark.parametrize("n", [2, 3, 4, 5, 8])
def test_min_n_matches_round_3_policy(n):
    reads = {tuple(p): [0.0] * n for p in option_orders(n, "identity+reversed")}
    policy = Policy("x", "reversed", "min_n", 4, "mean-prob")
    assert option_orders(n, "min_n:4+reversed") == perms(reads, n, policy, 1.0)
    assert option_orders(n, "identity+reversed")[1] == second_perm(n, "reversed")
