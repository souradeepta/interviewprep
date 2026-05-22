"""
Two-Pointer Pattern Problems
============================
Classic interview problems solved with the two-pointer technique.
All solutions: Time O(n) or O(n log n), Space O(1) unless noted.
"""
from typing import List


def two_sum_sorted(numbers: List[int], target: int) -> List[int]:
    """LeetCode 167. Two Sum II — Input Array Is Sorted."""
    left, right = 0, len(numbers) - 1
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]
        elif s < target:
            left += 1
        else:
            right -= 1
    return []


def remove_duplicates(nums: List[int]) -> int:
    """LeetCode 26. Remove Duplicates from Sorted Array."""
    if not nums:
        return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1


def container_with_most_water(height: List[int]) -> int:
    """LeetCode 11. Container With Most Water."""
    left, right = 0, len(height) - 1
    max_area = 0
    while left < right:
        area = min(height[left], height[right]) * (right - left)
        max_area = max(max_area, area)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return max_area


def three_sum(nums: List[int]) -> List[List[int]]:
    """LeetCode 15. 3Sum — find all unique triplets summing to zero."""
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1
    return result


def is_palindrome(s: str) -> bool:
    """LeetCode 125. Valid Palindrome."""
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True


def sort_colors(nums: List[int]) -> None:
    """LeetCode 75. Sort Colors — Dutch National Flag."""
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1


def trap_rain_water(height: List[int]) -> int:
    """LeetCode 42. Trapping Rain Water."""
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    return water


def move_zeroes(nums: List[int]) -> None:
    """LeetCode 283. Move Zeroes."""
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1


def squares_of_sorted_array(nums: List[int]) -> List[int]:
    """LeetCode 977. Squares of a Sorted Array."""
    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1
    pos = n - 1
    while left <= right:
        if abs(nums[left]) > abs(nums[right]):
            result[pos] = nums[left] ** 2
            left += 1
        else:
            result[pos] = nums[right] ** 2
            right -= 1
        pos -= 1
    return result


def remove_element(nums: List[int], val: int) -> int:
    """LeetCode 27. Remove Element in-place."""
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != val:
            nums[slow] = nums[fast]
            slow += 1
    return slow
