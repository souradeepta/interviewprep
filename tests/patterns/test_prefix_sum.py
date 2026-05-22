from python.patterns.prefix_sum import (
    subarray_sum_equals_k, range_sum_query,
    product_of_array_except_self, pivot_index,
    contiguous_array, minimum_size_subarray_sum
)


def test_subarray_sum_equals_k():
    assert subarray_sum_equals_k([1, 1, 1], 2) == 2
    assert subarray_sum_equals_k([1, 2, 3], 3) == 2
    assert subarray_sum_equals_k([1], 0) == 0


def test_range_sum_query():
    rs = range_sum_query([-2, 0, 3, -5, 2, -1])
    assert rs.sum_range(0, 2) == 1
    assert rs.sum_range(2, 5) == -1
    assert rs.sum_range(0, 5) == -3


def test_product_except_self():
    assert product_of_array_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert product_of_array_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]


def test_pivot_index():
    assert pivot_index([1, 7, 3, 6, 5, 6]) == 3
    assert pivot_index([1, 2, 3]) == -1
    assert pivot_index([2, 1, -1]) == 0


def test_contiguous_array():
    assert contiguous_array([0, 1]) == 2
    assert contiguous_array([0, 1, 0]) == 2
    assert contiguous_array([0, 0, 0, 1, 1, 1, 0]) == 6


def test_minimum_size_subarray_sum():
    assert minimum_size_subarray_sum(7, [2, 3, 1, 2, 4, 3]) == 2
    assert minimum_size_subarray_sum(4, [1, 4, 4]) == 1
    assert minimum_size_subarray_sum(11, [1, 1, 1, 1, 1, 1, 1, 1]) == 0
