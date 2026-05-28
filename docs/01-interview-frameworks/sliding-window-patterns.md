# Sliding Window Patterns: Efficient Subarray/Substring Solutions

**Level:** L3-L4
**Time to read:** ~20 min

Master the sliding window technique for solving array and string problems efficiently.

---

## Sliding Window Fundamentals

**Core Idea:** Maintain a window [left, right] that slides across array/string. Avoid recomputing from scratch.

**When to Use:**
- Find longest/shortest subarray/substring with property X
- Find minimum window containing all elements
- Count subarrays/substrings satisfying condition
- Any problem mentioning "contiguous" subarray/substring

**Why Sliding Window Works:**
```
Naive: Check all subarrays [O(n²) or worse]
Sliding Window: Each element added/removed once [O(n)]

Key insight: If [left, right] is invalid, no subarray 
ending at right with smaller left can be valid either.
```

**Pattern:**
```
1. Initialize left = 0, right = 0, state = {}
2. Expand right: add arr[right] to state
3. Shrink left: while state invalid, remove arr[left]
4. Update answer: process current valid window
5. Repeat until right reaches end
```

**Real Example Flow:**
```
Array: [2, 1, 3], Find max sum of window size 2
right=0: [2] → sum=2
right=1: [2,1] → sum=3, record
right=2: [1,3] → (remove 2) → [1,3] → sum=4, record
Answer: 4
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

## Real Interview Examples

### Example 1: Longest Substring Without Repeating Characters

```python
def lengthOfLongestSubstring(s):
    char_index = {}
    max_len = 0
    left = 0
    
    for right in range(len(s)):
        if s[right] in char_index and char_index[s[right]] >= left:
            # Found duplicate at earlier position, shrink
            left = char_index[s[right]] + 1
        
        char_index[s[right]] = right
        max_len = max(max_len, right - left + 1)
    
    return max_len

# Example: "abcabcbb"
# right=0: char_index={'a':0}, left=0, max_len=1
# right=1: char_index={'a':0,'b':1}, left=0, max_len=2
# right=2: char_index={'a':0,'b':1,'c':2}, left=0, max_len=3
# right=3: 'a' at index 0, so left=1, max_len=3
# right=4: 'b' at index 1, so left=2, max_len=3
# ...
# Answer: 3 ("abc")
# Time: O(n), Space: O(min(n, alphabet_size))
```

### Example 2: Max Consecutive Ones After Flipping at Most k Zeros

```python
def maxConsecutiveOnes(nums, k):
    left = 0
    zero_count = 0
    max_len = 0
    
    for right in range(len(nums)):
        if nums[right] == 0:
            zero_count += 1
        
        # Shrink window if too many zeros
        while zero_count > k:
            if nums[left] == 0:
                zero_count -= 1
            left += 1
        
        max_len = max(max_len, right - left + 1)
    
    return max_len

# Example: [1, 0, 1, 1, 0], k=1
# Can flip 1 zero to get longest 1-sequence
# Answer: 4 (flip middle 0: [1,1,1,1,0])
```

### Example 3: Permutation in String (Anagram Check)

```python
def checkInclusion(s1, s2):
    if len(s1) > len(s2):
        return False
    
    s1_count = {}
    window_count = {}
    
    # Count characters in s1
    for c in s1:
        s1_count[c] = s1_count.get(c, 0) + 1
    
    left = 0
    for right in range(len(s2)):
        # Add right character
        c = s2[right]
        window_count[c] = window_count.get(c, 0) + 1
        
        # Shrink if window too large
        if right - left + 1 > len(s1):
            c = s2[left]
            window_count[c] -= 1
            if window_count[c] == 0:
                del window_count[c]
            left += 1
        
        # Check if current window is permutation
        if window_count == s1_count:
            return True
    
    return False

# Example: s1="ab", s2="eidbaooo"
# Window "ba" at position 3-4 matches "ab"
# Answer: True
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

## Interview Tips & Common Mistakes

**How to Recognize Sliding Window Problems in Interview:**

| Keywords | Pattern |
|----------|---------|
| "longest/shortest subarray/substring" | Sliding window |
| "contiguous" | Sliding window |
| "maximum/minimum of k-sized window" | Fixed sliding window |
| "all elements of X in subarray" | Sliding window with hash map |
| "at most/exactly k distinct" | Sliding window with counter |

**Common Mistakes:**

| Mistake | Fix |
|---------|-----|
| Forgetting to shrink window | Add while loop to contract from left |
| Not updating state when shrinking | Decrement counter BEFORE incrementing left |
| Wrong answer recorded | Record answer inside while loop (before shrinking) |
| Off-by-one errors | Use `right - left + 1` for window size |
| Not initializing state | Initialize hash map/counter to empty |

**Complexity Red Flags:**
- ❌ O(n²) with nested loops (should be O(n))
- ❌ Forgetting left pointer (loses sliding window property)
- ❌ Recomputing state from scratch each iteration

---

## Edge Cases & Optimization Tips

**Edge Cases:**
- Empty input: return 0 or ""
- Window size = 1: still valid, test manually
- Window size = array length: find that window
- All elements same: window can be entire array
- No valid window exists: return -1 or ""
- Window never reaches size k: important for fixed windows

**Optimization Tips:**
- Use hash map for character frequency (faster than sorted)
- Use collections.Counter for Python (cleaner code)
- Use set for presence tracking (yes/no only)
- Use deque if order matters (for queue behavior)

**Complexity Analysis:**
- Each element visited at most twice (once by right pointer, once by left pointer)
- Total work: 2n = O(n)
- Space: O(min(n, alphabet_size)) for hash map

---

## Sliding Window Checklist

- ✓ Identified sliding window pattern (longest/shortest/count/fixed)
- ✓ Used two pointers (left, right) with single pass
- ✓ Expanded right to add new elements
- ✓ Shrank left to maintain validity property
- ✓ Updated state correctly (add before, remove after)
- ✓ Recorded answer at right time (inside while loop)
- ✓ Verified on small examples (n=1,2,3)
- ✓ Time complexity is O(n), not O(n²)
- ✓ Handled edge cases (empty, k > n)
- ✓ Traced through one full example by hand

---

## 🏃 Run the Code

Working Python implementation and test suite:

```bash
# Run the test suite (from repo root)
pytest tests/patterns/test_sliding_window.py -v
```

**Implementation:** [`python/patterns/sliding_window.py`](../../python/patterns/sliding_window.py)
**Tests:** [`tests/patterns/test_sliding_window.py`](../../tests/patterns/test_sliding_window.py)

> All 5 pattern modules have 218 passing tests total. Run `pytest tests/patterns/ -v` to run all.

