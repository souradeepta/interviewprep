# Binary Search Mastery: Searching, Boundaries, and Variants

Master binary search patterns for efficient searching and finding boundaries.

---

## Standard Binary Search

**Core Template:**

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1  # Target is to the right
        else:
            right = mid - 1  # Target is to the left
    
    return -1  # Not found
```

**Execution Example:**

```
Array: [1, 3, 5, 7, 9], target = 5
left=0, right=4
  mid=2: arr[2]=5 → FOUND! return 2

Array: [1, 3, 5, 7, 9], target = 6
left=0, right=4
  mid=2: arr[2]=5 < 6, left=3
left=3, right=4
  mid=3: arr[3]=7 > 6, right=2
left=3, right=2 → exit loop, return -1
```

**Key Points:**
- `left <= right` ensures we check all elements
- `mid = (left + right) // 2` is safe (avoid overflow in languages with fixed int size)
- Three cases: found (==), go right (<), go left (>)
- Time: O(log n), Space: O(1)
- Prerequisite: array must be **sorted**

---

## Finding Boundaries

### Find First Position (Lower Bound)

```python
def find_first(arr, target):
    left, right = 0, len(arr)
    
    while left < right:
        mid = (left + right) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid
    
    return left if left < len(arr) and arr[left] == target else -1

# Returns index of first occurrence or -1
# [1, 1, 1, 2, 2, 3] → find_first(2) = 3
```

### Find Last Position (Upper Bound)

```python
def find_last(arr, target):
    left, right = 0, len(arr)
    
    while left < right:
        mid = (left + right) // 2
        if arr[mid] <= target:
            left = mid + 1
        else:
            right = mid
    
    return left - 1 if left > 0 and arr[left - 1] == target else -1

# Returns index of last occurrence or -1
# [1, 1, 1, 2, 2, 3] → find_last(2) = 4
```

---

## Binary Search Variants

### Search in Rotated Sorted Array

```python
def search_rotated(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        
        # Left half is sorted
        if arr[left] <= arr[mid]:
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # Right half is sorted
        else:
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1

# [4,5,6,7,0,1,2] → find 0: check which half is sorted, then recurse
```

### Search in Unknown Size Array

```python
def search_unknown_size(reader, target):
    # First, find the right boundary (exponential search)
    left, right = 0, 1
    while reader.get(right) < target:
        left = right
        right *= 2
    
    # Now do binary search in [left, right]
    while left <= right:
        mid = (left + right) // 2
        if reader.get(mid) == target:
            return mid
        elif reader.get(mid) < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Time: O(log n), Space: O(1)
```

### Find Peak Element

```python
def find_peak(arr):
    left, right = 0, len(arr) - 1
    
    while left < right:
        mid = (left + right) // 2
        if arr[mid] > arr[mid + 1]:
            right = mid  # Peak is in left half (including mid)
        else:
            left = mid + 1  # Peak is in right half
    
    return left

# [1,2,3,1] → 3 is peak (index 2)
# [1,2,1,2,1] → could be 2 (index 1 or 3)
```

### Sqrt Using Binary Search

```python
def my_sqrt(x):
    if x == 0:
        return 0
    
    left, right = 1, x
    
    while left <= right:
        mid = (left + right) // 2
        if mid * mid == x:
            return mid
        elif mid * mid < x:
            left = mid + 1
        else:
            right = mid - 1
    
    return right  # Return floor of sqrt

# my_sqrt(8) = 2 (since 2² < 8 < 3²)
```

---

## Interview Tips & Common Mistakes

**How to Identify Binary Search in Interview:**

```
Keywords:
✓ "sorted" - strong indicator
✓ "find/search" - consider binary search
✓ "rotated" - definitely binary search variant
✓ "log time" - binary search hint
✓ "unknown size" - exponential search first

Not suitable:
✗ Unsorted array - must sort first (O(n log n)) or use linear (O(n))
✗ Linked list - no random access, use linear instead
✗ Small n (<1000) - binary search overhead not worth it
```

**Common Mistakes to Avoid:**

| Mistake | Impact | Fix |
|---------|--------|-----|
| `left = mid` in right half | Infinite loop! | Always use `mid ± 1` |
| Forgetting `left <= right` | Miss some elements | Use `<=` for inclusive check |
| Wrong mid comparison | Goes wrong direction | Think: if arr[mid] < target, left half is ruled out |
| Not handling not found | Returns wrong value | Check `left == right` at end or return -1 |
| Boundary off-by-one | Off-by-one in result | Test with target at edges (first/last element) |

**Interview Checklist Before Coding:**

```
1. Is the array sorted? If not, sort first (O(n log n))
2. Which binary search variant: standard, boundary, rotation, etc.?
3. What should I return if target not found? -1? left? right?
4. Edge cases: empty array? single element? duplicates?
5. Will I need `<=` or `<` in while loop?
```

---

## Binary Search Patterns

| Problem | Pattern | Key Insight |
|---------|---------|-----------|
| Find exact value | Standard | Three cases: ==, <, > |
| Find first position | Left boundary | `arr[mid] < target` → `left = mid + 1` |
| Find last position | Right boundary | `arr[mid] <= target` → `left = mid + 1` |
| Find in rotated | Check sorted half | One half always sorted |
| Find peak | Compare with neighbor | Peak has arr[i] > arr[i+1] |
| Find in unknown size | Exponential then binary | Find boundary, then search |

---

## Real Interview Problems

### Problem 1: Two Sum II (Sorted Array)

```python
def twoSum(numbers, target):
    left, right = 0, len(numbers) - 1
    
    while left < right:
        total = numbers[left] + numbers[right]
        if total == target:
            return [left + 1, right + 1]  # 1-indexed
        elif total < target:
            left += 1
        else:
            right -= 1
    
    return []

# Input: [2, 7, 11, 15], target = 9
# Output: [1, 2] (indices of 2 and 7)
# Time: O(n), Space: O(1)
# Note: Two-pointer is faster than binary search here!
```

### Problem 2: Time-Based Key-Value Store

```python
class TimeMap:
    def __init__(self):
        self.store = {}  # key → [(timestamp, value), ...]
    
    def set(self, key, value, timestamp):
        if key not in self.store:
            self.store[key] = []
        self.store[key].append((timestamp, value))
    
    def get(self, key, timestamp):
        if key not in self.store:
            return ""
        
        # Binary search for largest timestamp <= given timestamp
        values = self.store[key]
        left, right = 0, len(values) - 1
        result = ""
        
        while left <= right:
            mid = (left + right) // 2
            if values[mid][0] <= timestamp:
                result = values[mid][1]
                left = mid + 1
            else:
                right = mid - 1
        
        return result

# set("foo", "bar", 1)
# set("foo", "baz", 3)
# get("foo", 4) → "baz"
# get("foo", 2) → "bar"
```

### Problem 3: Capacity To Ship Packages Within D Days

```python
def shipWithinDays(weights, days):
    def can_ship(capacity):
        days_needed = 1
        current_load = 0
        for weight in weights:
            if weight > capacity:
                return False
            if current_load + weight > capacity:
                days_needed += 1
                current_load = weight
            else:
                current_load += weight
        return days_needed <= days
    
    left = max(weights)  # Min capacity: can load one heavy package
    right = sum(weights)  # Max capacity: load everything at once
    
    while left < right:
        mid = (left + right) // 2
        if can_ship(mid):
            right = mid  # Can ship with less capacity, try smaller
        else:
            left = mid + 1  # Need more capacity
    
    return left

# weights = [1,2,3,4,5,6,7,8,9,10], days = 5
# Need capacity ≥ 15 to ship in 5 days
# Time: O(n · log(sum)), Space: O(1)
```

## Edge Cases

```python
def test_binary_search():
    # Empty array
    assert binary_search([], 5) == -1
    
    # Single element
    assert binary_search([5], 5) == 0
    assert binary_search([5], 1) == -1
    
    # Target not in array
    assert binary_search([1,3,5], 4) == -1
    
    # Target at boundaries
    assert binary_search([1,3,5], 1) == 0
    assert binary_search([1,3,5], 5) == 2
    
    # Duplicates (find first vs last)
    assert find_first([1,1,1,2,2,3], 1) == 0
    assert find_last([1,1,1,2,2,3], 1) == 2
```

---

## Binary Search Checklist

- ✓ Verified array is sorted (or has monotonic property)
- ✓ Chose correct variant (standard, boundary, rotation, search space, etc.)
- ✓ Loop condition: `<=` or `<` ?
- ✓ Mid calculation: `(left + right) // 2` to avoid overflow
- ✓ Update logic: `left = mid + 1` or `right = mid - 1`
- ✓ Handled edge cases (empty, one element, target not found, duplicates)
- ✓ Time complexity is O(log n)
- ✓ Tested on small examples and edge cases
- ✓ Verified sorted property before implementing binary search

