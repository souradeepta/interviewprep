# Sliding Window Patterns: Efficient Subarray/Substring Solutions

Master the sliding window technique for solving array and string problems efficiently.

---

## Sliding Window Fundamentals

**Core Idea:** Maintain a window [left, right] that slides across array/string.

**When to Use:**
- Find longest/shortest subarray/substring with property X
- Find minimum window containing all elements
- Count subarrays/substrings satisfying condition

**Pattern:**
```
1. Initialize left = 0, right = 0
2. Expand right to include new element
3. If window is valid: record answer
4. If window is invalid: shrink from left
5. Repeat until right reaches end
```

---

## Fixed Window Size

```python
# Find maximum sum of k-sized window
def max_sum_window(arr, k):
    current_sum = sum(arr[:k])
    max_sum = current_sum
    
    for i in range(k, len(arr)):
        current_sum = current_sum - arr[i-k] + arr[i]
        max_sum = max(max_sum, current_sum)
    
    return max_sum

# Time: O(n), Space: O(1)
```

---

## Variable Window Size

### Pattern 1: Find Longest Subarray

```python
# Longest subarray with at most k distinct elements
def longest_substring_k_distinct(s, k):
    char_count = {}
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        # Expand: add right character
        char_count[s[right]] = char_count.get(s[right], 0) + 1
        
        # Shrink: remove characters until valid
        while len(char_count) > k:
            char_count[s[left]] -= 1
            if char_count[s[left]] == 0:
                del char_count[s[left]]
            left += 1
        
        # Record answer
        max_length = max(max_length, right - left + 1)
    
    return max_length

# Time: O(n), Space: O(k)
```

### Pattern 2: Find Shortest Subarray

```python
# Shortest substring containing all characters of target
def min_window_substring(s, target):
    if not target or not s:
        return ""
    
    target_count = {}
    for c in target:
        target_count[c] = target_count.get(c, 0) + 1
    
    window_count = {}
    left = 0
    formed = 0  # # of unique chars in window with desired freq
    min_length = float('inf')
    min_window = (0, 0)
    
    for right in range(len(s)):
        # Expand: add right character
        c = s[right]
        window_count[c] = window_count.get(c, 0) + 1
        
        if c in target_count and window_count[c] == target_count[c]:
            formed += 1
        
        # Shrink: contract from left
        while left <= right and formed == len(target_count):
            c = s[left]
            
            # Record answer
            if right - left + 1 < min_length:
                min_length = right - left + 1
                min_window = (left, right)
            
            # Remove left character
            window_count[c] -= 1
            if c in target_count and window_count[c] < target_count[c]:
                formed -= 1
            
            left += 1
    
    return s[min_window[0]:min_window[1]+1] if min_length != float('inf') else ""

# Time: O(n), Space: O(1) (constant alphabet size)
```

### Pattern 3: Count Subarrays

```python
# Count subarrays with at most k distinct elements
def count_subarrays_k_distinct(arr, k):
    def at_most_k_distinct(limit):
        char_count = {}
        left = 0
        count = 0
        
        for right in range(len(arr)):
            char_count[arr[right]] = char_count.get(arr[right], 0) + 1
            
            while len(char_count) > limit:
                char_count[arr[left]] -= 1
                if char_count[arr[left]] == 0:
                    del char_count[arr[left]]
                left += 1
            
            # All subarrays ending at right with at most k distinct
            count += right - left + 1
        
        return count
    
    # Exactly k = at_most_k - at_most_(k-1)
    return at_most_k_distinct(k) - at_most_k_distinct(k - 1)

# Time: O(n), Space: O(1)
```

---

## Common Sliding Window Problems

| Problem | Approach | Time | Space |
|---------|----------|------|-------|
| Max/min sum of k-sized window | Fixed window | O(n) | O(1) |
| Longest substring with k distinct | Variable window + hash map | O(n) | O(k) |
| Shortest substring with all chars | Variable window + hash map | O(n) | O(1) |
| Max consecutive ones after k flips | Variable window + count | O(n) | O(1) |
| Permutation in string | Variable window + hash map | O(n) | O(1) |
| Substring anagram | Variable window + hash map | O(n) | O(1) |
| Best time to buy/sell stock | Variable window | O(n) | O(1) |
| Minimum window substring | Variable window + hash map | O(n) | O(1) |

---

## Sliding Window Template

```python
def sliding_window_template(arr, target_property):
    left = 0
    result = 0
    state = {}  # Track state (hash map, counter, etc.)
    
    for right in range(len(arr)):
        # 1. Add element at right
        state = add_element(state, arr[right])
        
        # 2. Shrink window from left while invalid
        while not is_valid(state, target_property):
            state = remove_element(state, arr[left])
            left += 1
        
        # 3. Update result with current valid window
        result = update_result(result, right - left + 1)
    
    return result

# Key functions depend on problem:
# - is_valid: Check if window satisfies property
# - add_element: Update state when adding element
# - remove_element: Update state when removing element
# - update_result: How to accumulate answer
```

---

## Edge Cases & Optimization Tips

**Edge Cases:**
- Empty input
- Window size = 1
- Window size = array length
- All elements same
- No valid window exists

**Optimization Tips:**
- Use hash map for character frequency
- Use counter for faster ops (Python)
- Use set for presence tracking
- Use deque if order matters

**Complexity:**
- Each element visited at most twice (once by right, once by left)
- Time: O(n) not O(n²)
- Space: O(min(n, alphabet_size))

---

## Sliding Window Checklist

- ✓ Identified sliding window pattern (longest/shortest/count)
- ✓ Used two pointers (left, right)
- ✓ Expanded right to add elements
- ✓ Shrank left to maintain validity
- ✓ Updated result inside loop
- ✓ Verified on small examples (n=1,2,3)
- ✓ Time complexity is O(n), not O(n²)
- ✓ Handled edge cases (empty, k > n)

