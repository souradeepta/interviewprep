import pytest
from python.patterns.two_pointer import (
    two_sum_sorted, remove_duplicates, container_with_most_water,
    three_sum, is_palindrome, sort_colors, trap_rain_water,
    move_zeroes, squares_of_sorted_array, remove_element
)


def test_two_sum_sorted():
    assert two_sum_sorted([2, 7, 11, 15], 9) == [1, 2]
    assert two_sum_sorted([2, 3, 4], 6) == [1, 3]


def test_remove_duplicates():
    nums = [1, 1, 2, 3, 3]
    assert remove_duplicates(nums) == 3
    assert nums[:3] == [1, 2, 3]


def test_remove_duplicates_empty():
    assert remove_duplicates([]) == 0


def test_container_with_most_water():
    assert container_with_most_water([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert container_with_most_water([1, 1]) == 1


def test_three_sum():
    result = three_sum([-1, 0, 1, 2, -1, -4])
    assert sorted([sorted(t) for t in result]) == [[-1, -1, 2], [-1, 0, 1]]


def test_three_sum_no_result():
    assert three_sum([1, 2, 3]) == []


def test_is_palindrome():
    assert is_palindrome("A man, a plan, a canal: Panama") is True
    assert is_palindrome("race a car") is False
    assert is_palindrome(" ") is True


def test_sort_colors():
    nums = [2, 0, 2, 1, 1, 0]
    sort_colors(nums)
    assert nums == [0, 0, 1, 1, 2, 2]


def test_trap_rain_water():
    assert trap_rain_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert trap_rain_water([4, 2, 0, 3, 2, 5]) == 9
    assert trap_rain_water([]) == 0


def test_move_zeroes():
    nums = [0, 1, 0, 3, 12]
    move_zeroes(nums)
    assert nums == [1, 3, 12, 0, 0]


def test_squares_of_sorted_array():
    assert squares_of_sorted_array([-4, -1, 0, 3, 10]) == [0, 1, 9, 16, 100]
    assert squares_of_sorted_array([-7, -3, 2, 3, 11]) == [4, 9, 9, 49, 121]


def test_remove_element():
    nums = [3, 2, 2, 3]
    assert remove_element(nums, 3) == 2
    assert nums[:2] == [2, 2]
