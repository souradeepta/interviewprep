import pytest
from python.algorithms.searching.searching import (
    binary_search, binary_search_recursive, binary_search_first,
    binary_search_last, search_rotated_array
)


class TestBinarySearch:
    def test_found_middle(self):
        assert binary_search([1, 3, 5, 7, 9], 5) == 2

    def test_found_left(self):
        assert binary_search([1, 3, 5, 7, 9], 1) == 0

    def test_found_right(self):
        assert binary_search([1, 3, 5, 7, 9], 9) == 4

    def test_not_found(self):
        assert binary_search([1, 3, 5, 7, 9], 4) == -1

    def test_empty(self):
        assert binary_search([], 1) == -1

    def test_single_element_found(self):
        assert binary_search([5], 5) == 0

    def test_single_element_not_found(self):
        assert binary_search([5], 3) == -1


class TestBinarySearchRecursive:
    def test_found(self):
        assert binary_search_recursive([2, 4, 6, 8], 6) == 2

    def test_not_found(self):
        assert binary_search_recursive([2, 4, 6, 8], 5) == -1


class TestBinarySearchFirst:
    def test_first_occurrence(self):
        assert binary_search_first([1, 2, 2, 2, 3], 2) == 1

    def test_not_found(self):
        assert binary_search_first([1, 3, 5], 2) == -1


class TestBinarySearchLast:
    def test_last_occurrence(self):
        assert binary_search_last([1, 2, 2, 2, 3], 2) == 3

    def test_not_found(self):
        assert binary_search_last([1, 3, 5], 2) == -1


class TestSearchRotated:
    def test_found_left(self):
        assert search_rotated_array([4, 5, 6, 7, 0, 1, 2], 5) == 1

    def test_found_right(self):
        assert search_rotated_array([4, 5, 6, 7, 0, 1, 2], 1) == 5

    def test_not_found(self):
        assert search_rotated_array([4, 5, 6, 7, 0, 1, 2], 3) == -1
