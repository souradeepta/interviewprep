import pytest
from python.patterns.sliding_window import (
    max_subarray_sum_k, length_of_longest_substring,
    min_window_substring, longest_substring_k_distinct,
    max_consecutive_ones_iii, permutation_in_string,
    find_all_anagrams, subarray_product_less_than_k,
    longest_repeating_char_replacement
)


def test_max_subarray_sum_k():
    assert max_subarray_sum_k([2, 1, 5, 1, 3, 2], 3) == 9
    assert max_subarray_sum_k([2, 3, 4, 1, 5], 2) == 7


def test_length_of_longest_substring():
    assert length_of_longest_substring("abcabcbb") == 3
    assert length_of_longest_substring("bbbbb") == 1
    assert length_of_longest_substring("pwwkew") == 3
    assert length_of_longest_substring("") == 0


def test_min_window_substring():
    assert min_window_substring("ADOBECODEBANC", "ABC") == "BANC"
    assert min_window_substring("a", "a") == "a"
    assert min_window_substring("a", "aa") == ""


def test_longest_substring_k_distinct():
    assert longest_substring_k_distinct("eceba", 2) == 3
    assert longest_substring_k_distinct("aa", 1) == 2


def test_max_consecutive_ones_iii():
    assert max_consecutive_ones_iii([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2) == 6
    assert max_consecutive_ones_iii([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3) == 10


def test_permutation_in_string():
    assert permutation_in_string("ab", "eidbaooo") is True
    assert permutation_in_string("ab", "eidboaoo") is False


def test_find_all_anagrams():
    assert find_all_anagrams("cbaebabacd", "abc") == [0, 6]
    assert find_all_anagrams("abab", "ab") == [0, 1, 2]


def test_subarray_product_less_than_k():
    assert subarray_product_less_than_k([10, 5, 2, 6], 100) == 8
    assert subarray_product_less_than_k([1, 2, 3], 0) == 0


def test_longest_repeating_char_replacement():
    assert longest_repeating_char_replacement("ABAB", 2) == 4
    assert longest_repeating_char_replacement("AABABBA", 1) == 4
