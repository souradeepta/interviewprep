from python.patterns.binary_search import (
    search_in_rotated_sorted_array, find_minimum_in_rotated_sorted_array,
    find_first_and_last_position, search_a_2d_matrix,
    koko_eating_bananas, capacity_to_ship_packages,
    peak_element, sqrt_floor
)


def test_search_rotated():
    assert search_in_rotated_sorted_array([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_in_rotated_sorted_array([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search_in_rotated_sorted_array([1], 0) == -1


def test_find_minimum_rotated():
    assert find_minimum_in_rotated_sorted_array([3, 4, 5, 1, 2]) == 1
    assert find_minimum_in_rotated_sorted_array([4, 5, 6, 7, 0, 1, 2]) == 0


def test_find_first_and_last():
    assert find_first_and_last_position([5, 7, 7, 8, 8, 10], 8) == [3, 4]
    assert find_first_and_last_position([5, 7, 7, 8, 8, 10], 6) == [-1, -1]


def test_search_2d_matrix():
    m = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
    assert search_a_2d_matrix(m, 3) is True
    assert search_a_2d_matrix(m, 13) is False


def test_koko_eating():
    assert koko_eating_bananas([3, 6, 7, 11], 8) == 4
    assert koko_eating_bananas([30, 11, 23, 4, 20], 5) == 30


def test_capacity_to_ship():
    assert capacity_to_ship_packages([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15


def test_peak_element():
    idx = peak_element([1, 2, 3, 1])
    assert idx == 2


def test_sqrt_floor():
    assert sqrt_floor(4) == 2
    assert sqrt_floor(8) == 2
    assert sqrt_floor(0) == 0
    assert sqrt_floor(1) == 1
    assert sqrt_floor(9) == 3
