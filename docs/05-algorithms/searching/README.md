# Searching Algorithms

**Level:** L3-L4
**Time to read:** ~15 min

Three search algorithms plus the binary search variant taxonomy — the foundation of O(log n) thinking in interviews.

> For deep pattern coverage of binary search variants (lower bound, upper bound, rotated arrays, 2D matrices), see `docs/07-patterns/binary-search/`.

---

## Comparative Trade-off Table

| Algorithm | Time | Space | Requires Sorted? | When to use |
|-----------|------|-------|-----------------|-------------|
| Linear Search | O(n) | O(1) | No | Unsorted data, small n, one-off search |
| Binary Search (iterative) | O(log n) | O(1) | Yes | Sorted array, repeated queries |
| Binary Search (recursive) | O(log n) | O(log n) | Yes | Same — but risks stack overflow on huge n |
| Exponential Search | O(log i) | O(1) | Yes | Unbounded/infinite sorted arrays |
| Interpolation Search | O(log log n) avg | O(1) | Yes (uniform dist) | Uniformly distributed sorted data |

**i** = index of target in exponential search.

### Decision Framework

```
Data sorted?
  NO  → Linear Search (only option without preprocessing)
  YES → Can you afford O(n) space for a hash map?
          YES → Hash map: O(1) lookup after O(n) build
          NO  → Binary Search: O(log n), O(1) space

Searching repeatedly in the same sorted array?
  YES → Binary Search every time (no need to rebuild)

Array is unbounded (unknown size)?
  YES → Exponential Search: double the index until overshoot, then binary search

Data is uniformly distributed integers?
  YES → Interpolation Search can achieve O(log log n)
  NO  → Stick with Binary Search (safer guarantees)
```

---

## Algorithm Breakdowns

### Linear Search
Scan every element from left to right, return the index when the target is found. Requires no preprocessing and works on any iterable. Only choice when data is unsorted and building a sorted copy or hash map is too expensive.

**Complexity:** Time O(n) | Space O(1) | Requires sorted: No

```python
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
```

---

### Binary Search (Iterative)
Maintain `lo` and `hi` pointers; at each step compare the middle element to the target and halve the search space. Iterative form uses O(1) space and avoids recursion depth limits. The most common interview implementation — memorize this template.

**Complexity:** Time O(log n) | Space O(1) | Requires sorted: Yes

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2   # Avoids overflow (vs (lo+hi)//2)
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

**Key invariant:** `lo <= hi`. When loop exits, target is not in array.

---

### Binary Search (Recursive)
Same logic as iterative but expressed recursively. Each call reduces the search space by half. O(log n) stack frames — can overflow for n > 10⁷ in languages without tail-call optimization (Python default recursion limit is 1000).

**Complexity:** Time O(log n) | Space O(log n) call stack | Requires sorted: Yes

```python
def binary_search_recursive(arr, target, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo > hi:
        return -1
    mid = lo + (hi - lo) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, hi)
    else:
        return binary_search_recursive(arr, target, lo, mid - 1)
```

---

### Binary Search Variants

These variants appear constantly in interviews. The key is to change what "success" means:

**Find leftmost (first) occurrence:**
```python
def lower_bound(arr, target):
    """Return index of first element >= target."""
    lo, hi = 0, len(arr)
    while lo < hi:            # Note: hi = len(arr), not len-1
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid          # Don't exclude mid; it might be the answer
    return lo                 # lo == hi at termination
```

**Find rightmost (last) occurrence:**
```python
def upper_bound(arr, target):
    """Return index of first element > target."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

**Search on answer (binary search on result space):**
```python
# Template: binary search when you can check feasibility
def binary_search_on_answer(lo, hi, feasible):
    """Find smallest value x in [lo, hi] where feasible(x) is True."""
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

---

## Worked Problems

### Problem 1: Binary Search (LeetCode #704)

**Clarifying Questions:**
- Is the array sorted? → Yes, ascending order
- Can there be duplicates? → No (distinct integers per constraints)
- Return -1 if not found? → Yes

**Brute Force:** Linear scan O(n) — works but misses the point.

**Optimization:** Standard binary search O(log n).

**Edge Cases:**
- Target smaller than all elements → lo eventually > hi, return -1
- Target larger than all elements → same
- Single element array → mid = lo = hi = 0, check once

**Code:**
```python
def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

**Time:** O(log n) | **Space:** O(1)

**Follow-ups:**
- What if array has duplicates and you need first occurrence? → Lower bound variant
- What if array is rotated? → LeetCode #33, check which half is sorted first
- Can you do this with Python's bisect? → `bisect.bisect_left(nums, target)`

---

### Problem 2: First Bad Version (LeetCode #278)

**Clarifying Questions:**
- Are all versions after the first bad one also bad? → Yes (monotone property — key insight)
- Is n large? → Up to 2³¹ - 1 (use lo + (hi-lo)//2 to avoid overflow)
- API calls to isBadVersion are expensive? → Yes, minimize them

**Brute Force:** Call isBadVersion(1), isBadVersion(2), ... — O(n) calls.

**Optimization:** Binary search on the boundary between good and bad versions — O(log n) calls.

**Edge Cases:**
- Version 1 is bad → answer is 1
- Last version is the only bad one → must search to n

**Code:**
```python
def firstBadVersion(n):
    lo, hi = 1, n
    while lo < hi:          # lo < hi (not <=) because we want boundary
        mid = lo + (hi - lo) // 2
        if isBadVersion(mid):
            hi = mid        # Mid might be first bad; keep it
        else:
            lo = mid + 1    # Mid is good; first bad is to the right
    return lo               # lo == hi == first bad version
```

**Why `lo < hi` instead of `lo <= hi`:** We're finding a boundary, not an exact match. When lo == hi, we've converged to the answer.

**Follow-ups:**
- What is the general pattern here? → "Find first True in FFFFTTTT" — lower bound on boolean array
- What if bad versions are not contiguous? → Binary search doesn't apply; need linear scan
- How many API calls does this make? → At most ⌈log₂ n⌉ ≈ 31 for n = 2³¹

---

### Problem 3: Peak Index in Mountain Array (LeetCode #852)

**Clarifying Questions:**
- Is the array guaranteed to have exactly one peak? → Yes (mountain array definition)
- Can peak be at index 0 or n-1? → No (mountain array: arr[0] < arr[1] and arr[n-2] > arr[n-1])
- What if multiple peaks? → Not possible per constraints

**Brute Force:** Linear scan for max element — O(n).

**Optimization:** Binary search on slope — if arr[mid] < arr[mid+1], peak is to the right; otherwise left. O(log n).

**Edge Cases:**
- Array of length 3 → mid = 1, which must be the peak
- Peak near start or end → binary search handles naturally

**Code:**
```python
def peakIndexInMountainArray(arr):
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < arr[mid + 1]:
            lo = mid + 1    # Still climbing; peak is to the right
        else:
            hi = mid        # Descending or at peak; peak is here or left
    return lo               # lo == hi == peak index
```

**Key insight:** We're searching for where the slope changes from positive to negative — a binary search on the derivative.

**Follow-ups:**
- Find peak in array that may have multiple peaks (LeetCode #162 — Find Peak Element)? → Same binary search: compare mid with mid+1
- What if array is not strictly increasing/decreasing? → Need different approach; binary search requires the monotone property
- Can you solve it without accessing arr[mid+1]? → Compare arr[mid-1] and arr[mid] instead, same logic

---

## Common Mistakes

**1. Integer overflow in mid calculation**
```python
# BAD: Can overflow in languages with fixed-width integers
mid = (lo + hi) // 2

# GOOD: Overflow-safe
mid = lo + (hi - lo) // 2
# Python ints don't overflow, but write the safe version anyway
# — interviewers evaluate habits, not just correctness
```

**2. Wrong loop condition for boundary search**
```python
# BAD: <= exits when lo > hi, but boundary search needs lo == hi
while lo <= hi:  # Wrong for lower_bound / upper_bound

# GOOD: < exits when lo == hi (converged to answer)
while lo < hi:
```

**3. Moving hi incorrectly in lower bound**
```python
# BAD: Excludes mid, which might be the answer
hi = mid - 1

# GOOD: Keep mid in range (it could be the leftmost target)
hi = mid
```

**4. Not handling empty array**
```python
def binary_search(arr, target):
    if not arr:
        return -1           # Guard clause before lo/hi setup
    lo, hi = 0, len(arr) - 1
    ...
```

**5. Forgetting that binary search requires sorted input**
Binary search on an unsorted array produces wrong answers silently — no exception. Always verify or sort first.

**6. Using binary search for first occurrence without the right variant**
```python
# This finds ANY occurrence of target, not the FIRST:
while lo <= hi:
    if arr[mid] == target:
        return mid          # Wrong if duplicates exist

# Use lower_bound variant for first occurrence
```

---

## Interview Q&A

**Q1: What is the time complexity of binary search and why?**
O(log n). Each iteration halves the search space: after k iterations, the remaining range is n/2^k elements. When n/2^k = 1, we have k = log₂ n. The log base doesn't matter for Big O — it's a constant factor.

**Q2: Can binary search work on non-integer domains?**
Yes. Binary search works on any monotone function, not just arrays. "Binary search on answer" applies to continuous domains (floating point) — e.g., find square root to precision ε by binary searching on the real interval [0, n]. Terminate when hi - lo < ε.

**Q3: When should you use linear search over binary search?**
When the array is unsorted and sorting is too expensive. When n is very small (< 20) and linear search fits in cache better. When you're searching a linked list (no O(1) random access). When you need to find all occurrences while scanning (linear is simpler).

**Q4: Explain the difference between lower_bound and upper_bound.**
lower_bound returns the index of the first element ≥ target. upper_bound returns the index of the first element > target. Count of a value in sorted array = upper_bound(target) - lower_bound(target). Python's `bisect_left` = lower_bound, `bisect_right` = upper_bound.

**Q5: How do you binary search a 2D sorted matrix?**
Treat the m×n matrix as a 1D array of length m×n. For index `mid`, map to row = mid // n and col = mid % n. Complexity: O(log(m×n)) = O(log m + log n).

```python
def searchMatrix(matrix, target):
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        val = matrix[mid // n][mid % n]
        if val == target: return True
        elif val < target: lo = mid + 1
        else: hi = mid - 1
    return False
```

**Q6: What's "binary search on the answer" and when do you use it?**
Instead of searching for a value in an array, you binary search on the range of possible answers. Applicable when: (1) there's a clear answer range, (2) you can write a feasibility function `f(x)` that is monotone (False...False...True...True), (3) you want the smallest/largest feasible x. Examples: LeetCode #875 (Koko Eating Bananas), #1011 (Capacity to Ship Packages).
