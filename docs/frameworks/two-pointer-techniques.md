# Two Pointer Techniques: Converging and Diverging Strategies

Master two pointer patterns for efficient array and string manipulation.

---

## Two Pointer Patterns

### Pattern 1: Converging Pointers (Start from ends)

```python
# Two Sum in sorted array
def two_sum_sorted(arr, target):
    left, right = 0, len(arr) - 1
    
    while left < right:
        current_sum = arr[left] + arr[right]
        
        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1  # Need larger sum
        else:
            right -= 1  # Need smaller sum
    
    return [-1, -1]

# Time: O(n), Space: O(1)
```

### Pattern 2: Diverging Pointers (Start from middle)

```python
# Expand around center for palindromes
def longest_palindrome(s):
    def expand_around(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return s[left+1:right]
    
    longest = ""
    for i in range(len(s)):
        p1 = expand_around(i, i)  # Odd length
        p2 = expand_around(i, i + 1)  # Even length
        
        for p in [p1, p2]:
            if len(p) > len(longest):
                longest = p
    
    return longest

# Time: O(n²), Space: O(1)
```

### Pattern 3: Same Direction (Fast and Slow)

```python
# Remove duplicates from sorted array
def remove_duplicates(arr):
    if not arr:
        return 0
    
    slow = 0
    for fast in range(1, len(arr)):
        if arr[fast] != arr[slow]:
            slow += 1
            arr[slow] = arr[fast]
    
    return slow + 1

# Time: O(n), Space: O(1)
```

### Pattern 4: Partition (3-way partition)

```python
# Dutch National Flag (partition for 0, 1, 2)
def sort_colors(arr):
    left = 0
    mid = 0
    right = len(arr) - 1
    
    while mid <= right:
        if arr[mid] == 0:
            arr[left], arr[mid] = arr[mid], arr[left]
            left += 1
            mid += 1
        elif arr[mid] == 1:
            mid += 1
        else:  # arr[mid] == 2
            arr[mid], arr[right] = arr[right], arr[mid]
            right -= 1
    
    return arr

# Time: O(n), Space: O(1)
# Invariant: [0..left) = 0s, [left..mid) = 1s, [mid..right] = unsorted, (right..] = 2s
```

---

## Common Two Pointer Problems

| Problem | Pointers | Key Insight |
|---------|----------|-------------|
| Two Sum (sorted) | Start ends | Move towards middle |
| Container with water | Start ends | Move shorter side |
| Palindrome check | Start ends | Compare symmetric |
| Remove duplicates | Slow/fast same dir | Slow overwrites |
| Move zeroes | Slow/fast same dir | Slow tracks last non-zero |
| Remove element | Slow/fast same dir | Slow tracks valid elements |
| Longest palindrome | Expand from center | Diverging pointers |
| String permutation | Two pointers or hash | Compare all chars |
| Merge sorted arrays | Two pointers | Merge in place |

---

## Two Pointer Checklist

- ✓ Identified which two pointer pattern applies
- ✓ Initialized pointers correctly (start/end or slow/fast)
- ✓ Loop condition correct (left < right or fast < n)
- ✓ Movement logic correct (move towards solution)
- ✓ Tested on edge cases (empty, one element, all same)
- ✓ Time complexity O(n), Space O(1)

