from python.patterns.monotonic_stack import (
    next_greater_element, daily_temperatures,
    largest_rectangle_in_histogram, trapping_rain_water_stack,
    remove_k_digits, asteroid_collision
)


def test_next_greater_element():
    assert next_greater_element([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
    assert next_greater_element([1, 2, 3]) == [2, 3, -1]


def test_daily_temperatures():
    assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]


def test_largest_rectangle():
    assert largest_rectangle_in_histogram([2, 1, 5, 6, 2, 3]) == 10
    assert largest_rectangle_in_histogram([2, 4]) == 4


def test_trapping_rain_stack():
    assert trapping_rain_water_stack([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert trapping_rain_water_stack([4, 2, 0, 3, 2, 5]) == 9


def test_remove_k_digits():
    assert remove_k_digits("1432219", 3) == "1219"
    assert remove_k_digits("10200", 1) == "200"
    assert remove_k_digits("10", 2) == "0"


def test_asteroid_collision():
    assert asteroid_collision([5, 10, -5]) == [5, 10]
    assert asteroid_collision([8, -8]) == []
    assert asteroid_collision([10, 2, -5]) == [10]
