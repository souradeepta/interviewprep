"""
Sliding Window Pattern Problems
================================
Fixed-size and variable-size window problems.
"""
from typing import List
from collections import defaultdict, Counter


def max_subarray_sum_k(nums: List[int], k: int) -> int:
    """Maximum sum of any subarray of exactly length k."""
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum


def length_of_longest_substring(s: str) -> int:
    """LeetCode 3. Longest Substring Without Repeating Characters."""
    char_index: dict[str, int] = {}
    max_len = 0
    left = 0
    for right, ch in enumerate(s):
        if ch in char_index and char_index[ch] >= left:
            left = char_index[ch] + 1
        char_index[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len


def min_window_substring(s: str, t: str) -> str:
    """LeetCode 76. Minimum Window Substring."""
    if not t:
        return ""
    need = Counter(t)
    have: dict[str, int] = defaultdict(int)
    formed = 0
    required = len(need)
    left = 0
    best = (float("inf"), 0, 0)
    for right, ch in enumerate(s):
        have[ch] += 1
        if ch in need and have[ch] == need[ch]:
            formed += 1
        while formed == required:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right)
            have[s[left]] -= 1
            if s[left] in need and have[s[left]] < need[s[left]]:
                formed -= 1
            left += 1
    return "" if best[0] == float("inf") else s[best[1]: best[2] + 1]


def longest_substring_k_distinct(s: str, k: int) -> int:
    """LeetCode 340. Longest Substring with At Most K Distinct Characters."""
    freq: dict[str, int] = defaultdict(int)
    left = max_len = 0
    for right, ch in enumerate(s):
        freq[ch] += 1
        while len(freq) > k:
            freq[s[left]] -= 1
            if freq[s[left]] == 0:
                del freq[s[left]]
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len


def max_consecutive_ones_iii(nums: List[int], k: int) -> int:
    """LeetCode 1004. Max Consecutive Ones III (flip at most k zeros)."""
    left = zeros = max_len = 0
    for right in range(len(nums)):
        if nums[right] == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len


def permutation_in_string(s1: str, s2: str) -> bool:
    """LeetCode 567. Permutation in String."""
    if len(s1) > len(s2):
        return False
    need = Counter(s1)
    window = Counter(s2[:len(s1)])
    if window == need:
        return True
    for i in range(len(s1), len(s2)):
        add_ch = s2[i]
        remove_ch = s2[i - len(s1)]
        window[add_ch] += 1
        window[remove_ch] -= 1
        if window[remove_ch] == 0:
            del window[remove_ch]
        if window == need:
            return True
    return False


def find_all_anagrams(s: str, p: str) -> List[int]:
    """LeetCode 438. Find All Anagrams in a String."""
    result = []
    need = Counter(p)
    window = Counter(s[:len(p)])
    if window == need:
        result.append(0)
    for i in range(len(p), len(s)):
        window[s[i]] += 1
        old_ch = s[i - len(p)]
        window[old_ch] -= 1
        if window[old_ch] == 0:
            del window[old_ch]
        if window == need:
            result.append(i - len(p) + 1)
    return result


def subarray_product_less_than_k(nums: List[int], k: int) -> int:
    """LeetCode 713. Subarray Product Less Than K."""
    if k <= 1:
        return 0
    product = 1
    left = count = 0
    for right in range(len(nums)):
        product *= nums[right]
        while product >= k:
            product //= nums[left]
            left += 1
        count += right - left + 1
    return count


def longest_repeating_char_replacement(s: str, k: int) -> int:
    """LeetCode 424. Longest Repeating Character Replacement."""
    freq: dict[str, int] = defaultdict(int)
    max_freq = left = max_len = 0
    for right, ch in enumerate(s):
        freq[ch] += 1
        max_freq = max(max_freq, freq[ch])
        window_size = right - left + 1
        if window_size - max_freq > k:
            freq[s[left]] -= 1
            left += 1
        max_len = max(max_len, right - left + 1)
    return max_len
