"""Binary Search Pattern Problems"""
from typing import List
import math


def search_in_rotated_sorted_array(nums: List[int], target: int) -> int:
    """LeetCode 33. Search in Rotated Sorted Array."""
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1


def find_minimum_in_rotated_sorted_array(nums: List[int]) -> int:
    """LeetCode 153. Find Minimum in Rotated Sorted Array."""
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    return nums[left]


def find_first_and_last_position(nums: List[int], target: int) -> List[int]:
    """LeetCode 34. Find First and Last Position of Element in Sorted Array."""
    def find_bound(is_first: bool) -> int:
        left, right = 0, len(nums) - 1
        bound = -1
        while left <= right:
            mid = (left + right) // 2
            if nums[mid] == target:
                bound = mid
                if is_first:
                    right = mid - 1
                else:
                    left = mid + 1
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return bound
    return [find_bound(True), find_bound(False)]


def search_a_2d_matrix(matrix: List[List[int]], target: int) -> bool:
    """LeetCode 74. Search a 2D Matrix."""
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    left, right = 0, m * n - 1
    while left <= right:
        mid = (left + right) // 2
        val = matrix[mid // n][mid % n]
        if val == target:
            return True
        elif val < target:
            left = mid + 1
        else:
            right = mid - 1
    return False


def koko_eating_bananas(piles: List[int], h: int) -> int:
    """LeetCode 875. Koko Eating Bananas."""
    left, right = 1, max(piles)
    while left < right:
        mid = (left + right) // 2
        hours = sum(math.ceil(p / mid) for p in piles)
        if hours <= h:
            right = mid
        else:
            left = mid + 1
    return left


def capacity_to_ship_packages(weights: List[int], days: int) -> int:
    """LeetCode 1011. Capacity To Ship Packages Within D Days."""
    def can_ship(capacity: int) -> bool:
        day_count, current = 1, 0
        for w in weights:
            if current + w > capacity:
                day_count += 1
                current = 0
            current += w
        return day_count <= days

    left, right = max(weights), sum(weights)
    while left < right:
        mid = (left + right) // 2
        if can_ship(mid):
            right = mid
        else:
            left = mid + 1
    return left


def peak_element(nums: List[int]) -> int:
    """LeetCode 162. Find Peak Element."""
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] < nums[mid + 1]:
            left = mid + 1
        else:
            right = mid
    return left


def sqrt_floor(x: int) -> int:
    """LeetCode 69. Sqrt(x) — return floor of square root."""
    if x < 2:
        return x
    left, right = 1, x // 2
    while left <= right:
        mid = (left + right) // 2
        if mid * mid == x:
            return mid
        elif mid * mid < x:
            left = mid + 1
        else:
            right = mid - 1
    return right
