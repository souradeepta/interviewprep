import pytest
from python.algorithms.dp.dp import (
    fibonacci, knapsack_01, lcs, lis, edit_distance,
    coin_change
)


class TestFibonacci:
    def test_base_cases(self):
        r = fibonacci(0)
        assert r["memoization"] == 0 and r["tabulation"] == 0
        r = fibonacci(1)
        assert r["memoization"] == 1 and r["tabulation"] == 1

    def test_fib_10(self):
        r = fibonacci(10)
        assert r["memoization"] == 55
        assert r["tabulation"] == 55

    def test_all_match(self):
        r = fibonacci(15)
        assert r["memoization"] == r["tabulation"]


class TestKnapsack:
    def test_basic(self):
        weights = [2, 3, 4, 5]
        values = [3, 4, 5, 6]
        result = knapsack_01(weights, values, 5)
        assert result[0] == 7  # max value

    def test_empty(self):
        result = knapsack_01([], [], 10)
        assert result[0] == 0

    def test_capacity_zero(self):
        result = knapsack_01([1, 2], [3, 4], 0)
        assert result[0] == 0


class TestLCS:
    def test_basic(self):
        dist, substr = lcs("abcde", "ace")
        assert dist == 3

    def test_no_common(self):
        dist, substr = lcs("abc", "xyz")
        assert dist == 0

    def test_identical(self):
        dist, substr = lcs("abc", "abc")
        assert dist == 3


class TestLIS:
    def test_basic(self):
        length, seq = lis([10, 9, 2, 5, 3, 7, 101, 18])
        assert length == 4

    def test_sorted(self):
        length, seq = lis([1, 2, 3, 4, 5])
        assert length == 5

    def test_reverse_sorted(self):
        length, seq = lis([5, 4, 3, 2, 1])
        assert length == 1


class TestEditDistance:
    def test_basic(self):
        dist, ops = edit_distance("horse", "ros")
        assert dist == 3

    def test_empty_strings(self):
        dist, ops = edit_distance("", "")
        assert dist == 0

    def test_one_empty(self):
        dist, ops = edit_distance("abc", "")
        assert dist == 3


class TestCoinChange:
    def test_basic(self):
        count, coins = coin_change([1, 5, 6, 9], 11)
        assert count == 2

    def test_impossible(self):
        count, coins = coin_change([2], 3)
        assert count == -1

    def test_zero_amount(self):
        count, coins = coin_change([1, 5], 0)
        assert count == 0
