# Two Pointer Techniques: Converging and Diverging Strategies

**Level:** L3-L4
**Time to read:** ~20 min

Master two pointer patterns for efficient array and string manipulation.

**When to Use Two Pointers:**
- Array/string problem with **two indices** moving
- Goal: find pairs, compare elements, partition
- Usually sorted input (or can be sorted)
- Want O(n) time, O(1) space (better than nested loops)

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

## Real Interview Examples

### Example 1: Container With Most Water

```python
def maxArea(heights):
    left, right = 0, len(heights) - 1
    max_area = 0
    
    while left < right:
        # Calculate area with current pointers
        width = right - left
        height = min(heights[left], heights[right])
        area = width * height
        max_area = max(max_area, area)
        
        # Move the pointer pointing to shorter line
        # (moving taller one won't help)
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1
    
    return max_area

# Example: [1,8,6,2,5,4,8,3,7], answer = 49
# left=0 (height=1), right=8 (height=7)
# area = min(1,7) × 8 = 8, move left (taller)
# left=1 (height=8), right=8 (height=7)
# area = min(8,7) × 7 = 49, move right (taller)
# Answer: 49
# Time: O(n), Space: O(1)
```

### Example 2: Trapping Rain Water

```python
def trap(heights):
    if not heights:
        return 0
    
    left, right = 0, len(heights) - 1
    left_max, right_max = 0, 0
    water = 0
    
    while left < right:
        if heights[left] < heights[right]:
            if heights[left] >= left_max:
                left_max = heights[left]
            else:
                water += left_max - heights[left]
            left += 1
        else:
            if heights[right] >= right_max:
                right_max = heights[right]
            else:
                water += right_max - heights[right]
            right -= 1
    
    return water

# Example: [0,1,0,2,1,0,1,3,2,1,2,1]
# Water trapped = 6 units
# Time: O(n), Space: O(1)
```

### Example 3: 3Sum

```python
def threeSum(nums):
    nums.sort()  # Sort first: O(n log n)
    result = []
    
    for i in range(len(nums) - 2):
        # Skip duplicates
        if i > 0 and nums[i] == nums[i-1]:
            continue
        
        # Avoid positive numbers (can't sum to 0)
        if nums[i] > 0:
            break
        
        # Two sum with two pointers
        left, right = i + 1, len(nums) - 1
        while left < right:
            current_sum = nums[i] + nums[left] + nums[right]
            
            if current_sum == 0:
                result.append([nums[i], nums[left], nums[right]])
                
                # Skip duplicates
                while left < right and nums[left] == nums[left+1]:
                    left += 1
                while left < right and nums[right] == nums[right-1]:
                    right -= 1
                
                left += 1
                right -= 1
            elif current_sum < 0:
                left += 1
            else:
                right -= 1
    
    return result

# Example: [-1,0,1,2,-1,-4]
# Answer: [[-1,-1,2], [-1,0,1]]
# Time: O(n²), Space: O(1) (excluding output)
```

---

## Interview Tips & Common Mistakes

**When NOT to Use Two Pointers:**

❌ Unsorted array and can't sort (e.g., stream of data)
❌ Need all pairs (requires nested loops)
❌ Problem requires exact values (may work with converging, but check)

**Common Mistakes:**

| Mistake | Fix |
|---------|-----|
| Not sorting when needed | Check if sorted required for correctness |
| Forgetting to skip duplicates | Check `nums[left] == nums[left+1]` |
| Wrong pointer movement direction | Think: which pointer should move? |
| Off-by-one in loop condition | Use `left < right` for converging, `fast < n` for same-direction |
| Comparing pointers at wrong positions | Compare `arr[left]` and `arr[right]`, not left/right values |

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

## Two Pointer Decision Tree

**Is array sorted?**
- YES → Can use converging or same-direction
- NO → Sort first (O(n log n)) or use converging with careful logic

**Looking for:**
- Pairs/triplets → Converging from ends
- Remove elements → Same direction (slow/fast)
- Palindromes → Diverging from center
- Partitioning → Three pointers (Dutch flag)

**What's the space constraint?**
- O(1) space → Two pointers essential
- O(n) allowed → Could also use hash map/set

---

## Two Pointer Checklist

- ✓ Identified which two pointer pattern applies (converging/diverging/same-direction/partition)
- ✓ Initialized pointers correctly (ends, center, or slow/fast)
- ✓ Loop condition is correct and doesn't infinite loop
- ✓ Pointer movement logic achieves progress towards answer
- ✓ Handled duplicates (skip when needed)
- ✓ Tested on edge cases (empty, one element, all same, target at edges)
- ✓ Time complexity O(n), Space O(1)
- ✓ Verified solution doesn't modify input (if not allowed)

