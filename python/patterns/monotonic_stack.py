"""Monotonic Stack Pattern Problems"""
from typing import List


def next_greater_element(nums: List[int]) -> List[int]:
    """LeetCode 496 variant. For each element, find next greater to its right."""
    result = [-1] * len(nums)
    stack: List[int] = []
    for i, val in enumerate(nums):
        while stack and nums[stack[-1]] < val:
            idx = stack.pop()
            result[idx] = val
        stack.append(i)
    return result


def daily_temperatures(temperatures: List[int]) -> List[int]:
    """LeetCode 739. Daily Temperatures."""
    result = [0] * len(temperatures)
    stack: List[int] = []
    for i, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            idx = stack.pop()
            result[idx] = i - idx
        stack.append(i)
    return result


def largest_rectangle_in_histogram(heights: List[int]) -> int:
    """LeetCode 84. Largest Rectangle in Histogram."""
    stack: List[int] = []
    max_area = 0
    for i, h in enumerate(heights + [0]):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area


def trapping_rain_water_stack(height: List[int]) -> int:
    """LeetCode 42. Trapping Rain Water (monotonic stack approach)."""
    stack: List[int] = []
    water = 0
    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:
            bottom = stack.pop()
            if not stack:
                break
            left = stack[-1]
            width = i - left - 1
            bounded_height = min(height[left], h) - height[bottom]
            water += width * bounded_height
        stack.append(i)
    return water


def remove_k_digits(num: str, k: int) -> str:
    """LeetCode 402. Remove K Digits to form smallest number."""
    stack: List[str] = []
    for digit in num:
        while k and stack and stack[-1] > digit:
            stack.pop()
            k -= 1
        stack.append(digit)
    stack = stack[:-k] if k else stack
    return "".join(stack).lstrip("0") or "0"


def asteroid_collision(asteroids: List[int]) -> List[int]:
    """LeetCode 735. Asteroid Collision."""
    stack: List[int] = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            if stack[-1] < -a:
                stack.pop()
            elif stack[-1] == -a:
                stack.pop()
                alive = False
            else:
                alive = False
        if alive:
            stack.append(a)
    return stack
