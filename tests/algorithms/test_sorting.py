import pytest
from python.algorithms.sorting.sorting import (
    bubble_sort, selection_sort, insertion_sort,
    merge_sort, quick_sort, heap_sort,
    counting_sort, radix_sort
)

CASES = [
    ([3, 1, 4, 1, 5, 9, 2, 6], [1, 1, 2, 3, 4, 5, 6, 9]),
    ([], []),
    ([1], [1]),
    ([2, 1], [1, 2]),
    ([5, 5, 5], [5, 5, 5]),
    (list(range(10, 0, -1)), list(range(1, 11))),
]


@pytest.mark.parametrize("arr,expected", CASES)
def test_bubble_sort(arr, expected):
    assert bubble_sort(arr[:]) == expected


@pytest.mark.parametrize("arr,expected", CASES)
def test_selection_sort(arr, expected):
    assert selection_sort(arr[:]) == expected


@pytest.mark.parametrize("arr,expected", CASES)
def test_insertion_sort(arr, expected):
    assert insertion_sort(arr[:]) == expected


@pytest.mark.parametrize("arr,expected", CASES)
def test_merge_sort(arr, expected):
    assert merge_sort(arr[:]) == expected


@pytest.mark.parametrize("arr,expected", CASES)
def test_quick_sort(arr, expected):
    assert quick_sort(arr[:]) == expected


@pytest.mark.parametrize("arr,expected", CASES)
def test_heap_sort(arr, expected):
    assert heap_sort(arr[:]) == expected


@pytest.mark.parametrize("arr,expected", [
    ([3, 1, 4, 1, 5, 9], [1, 1, 3, 4, 5, 9]),
    ([], []),
    ([0, 0, 0], [0, 0, 0]),
])
def test_counting_sort(arr, expected):
    assert counting_sort(arr[:]) == expected


@pytest.mark.parametrize("arr,expected", [
    ([170, 45, 75, 90, 802, 24, 2, 66], [2, 24, 45, 66, 75, 90, 170, 802]),
    ([], []),
    ([1], [1]),
])
def test_radix_sort(arr, expected):
    assert radix_sort(arr[:]) == expected
