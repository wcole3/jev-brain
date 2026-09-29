import pytest

from gateway.orders import average_back, option_orders


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
