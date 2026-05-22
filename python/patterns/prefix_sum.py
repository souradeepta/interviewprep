"""Prefix Sum / Range Query Pattern Problems"""
from typing import List


def subarray_sum_equals_k(nums: List[int], k: int) -> int:
    """LeetCode 560. Subarray Sum Equals K."""
    count = 0
    prefix_sum = 0
    freq: dict[int, int] = {0: 1}
    for num in nums:
        prefix_sum += num
        count += freq.get(prefix_sum - k, 0)
        freq[prefix_sum] = freq.get(prefix_sum, 0) + 1
    return count


def range_sum_query(nums: List[int]) -> "RangeSum":
    """LeetCode 303. Range Sum Query - Immutable."""
    class RangeSum:
        def __init__(self, nums: List[int]):
            self.prefix = [0] * (len(nums) + 1)
            for i, n in enumerate(nums):
                self.prefix[i + 1] = self.prefix[i] + n

        def sum_range(self, left: int, right: int) -> int:
            return self.prefix[right + 1] - self.prefix[left]

    return RangeSum(nums)


def product_of_array_except_self(nums: List[int]) -> List[int]:
    """LeetCode 238. Product of Array Except Self."""
    n = len(nums)
    result = [1] * n
    left_product = 1
    for i in range(n):
        result[i] = left_product
        left_product *= nums[i]
    right_product = 1
    for i in range(n - 1, -1, -1):
        result[i] *= right_product
        right_product *= nums[i]
    return result


def pivot_index(nums: List[int]) -> int:
    """LeetCode 724. Find Pivot Index."""
    total = sum(nums)
    left_sum = 0
    for i, n in enumerate(nums):
        if left_sum == total - left_sum - n:
            return i
        left_sum += n
    return -1


def contiguous_array(nums: List[int]) -> int:
    """LeetCode 525. Contiguous Array."""
    prefix_map: dict[int, int] = {0: -1}
    count = max_len = 0
    for i, n in enumerate(nums):
        count += 1 if n == 1 else -1
        if count in prefix_map:
            max_len = max(max_len, i - prefix_map[count])
        else:
            prefix_map[count] = i
    return max_len


def minimum_size_subarray_sum(target: int, nums: List[int]) -> int:
    """LeetCode 209. Minimum Size Subarray Sum."""
    left = 0
    current_sum = 0
    min_len = float("inf")
    for right in range(len(nums)):
        current_sum += nums[right]
        while current_sum >= target:
            min_len = min(min_len, right - left + 1)
            current_sum -= nums[left]
            left += 1
    return 0 if min_len == float("inf") else min_len
