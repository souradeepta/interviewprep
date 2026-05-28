# Binary Search Pattern

**Level:** L4
**Time to read:** ~20 min
**Prerequisites:** [Arrays](../../06-data-structures/arrays/README.md)
**Related:** [Two-Pointer](../two-pointer/README.md)

## Quick Summary

Binary search repeatedly halves the search space to locate a target or find the boundary where a condition flips from false to true. Transforms O(n) linear scans into O(log n). Key signal phrases: "sorted array", "find target", "find minimum/maximum satisfying condition", "rotated array", "feasibility — can we do X in Y?".

## When to Use It

Signal phrases that strongly indicate binary search:

- "Find target in sorted array" — classic index search
- "Find first/last occurrence" — boundary binary search
- "Find minimum in rotated sorted array" — inflection point search
- "Minimum speed/capacity/time to finish" — binary search on the answer
- "Is it possible to achieve X with constraint Y?" — feasibility search
- "Find peak element" — condition-flip binary search

**Not a fit when:** the collection is unsorted and cannot be sorted (use hash map), you need all matches (use linear scan), or the comparison function is not monotone (no clear left/right decision).

## How It Works

### Core Operation: Halving the Search Space

```
arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
       0  1  2   3   4   5   6   7   8   9

target = 23
l=0, r=9 → mid=4 → arr[4]=16 < 23 → l = mid+1 = 5
l=5, r=9 → mid=7 → arr[7]=56 > 23 → r = mid-1 = 6
l=5, r=6 → mid=5 → arr[5]=23 = 23 → FOUND at index 5
```

Three comparisons instead of six linear steps. Benefit compounds at scale: 1M elements → ~20 comparisons.

### Variant 1: Classic — Find Exact Target

Terminate when `left > right`. If `nums[mid] == target`, return `mid`. Narrow left half if `nums[mid] < target`, right half otherwise.

```python
def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:          # ← note: <= to include single-element range
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

Termination: `left <= right`, so the loop processes every non-empty range.

### Variant 2: Boundary Search — Find Leftmost (or Rightmost) Where Condition is True

Used when there are multiple valid positions and you want the first (or last) one. The condition is monotone: `False, False, ..., True, True, ...`.

```
Condition C(x): "nums[x] >= target"

arr  = [5, 7, 7, 8, 8, 10]
C(x) = [F, F, F, T, T,  T]   ← target = 8

Binary search finds the boundary: index 3 (leftmost True)
```

Template (leftmost boundary):

```python
def find_left_boundary(nums, target):
    left, right = 0, len(nums)    # ← right = n (open interval)
    while left < right:           # ← note: strictly <
        mid = (left + right) // 2
        if condition(nums, mid, target):
            right = mid           # mid could be the answer; keep it
        else:
            left = mid + 1        # mid is definitely not the answer
    return left                   # left == right at termination
```

Rightmost boundary: flip to `left = mid + 1` when condition true, `right = mid - 1` when false, return `right`.

### Decision Tree

```
Is the array sorted (or is there a monotone condition)?
├── YES → Am I looking for an exact value?
│         ├── YES → Classic binary search (left <= right)
│         └── NO  → Am I looking for first/last occurrence?
│                   ├── YES → Boundary binary search (left < right, open interval)
│                   └── NO  → Is the array rotated?
│                             ├── YES → Rotated binary search
│                             └── NO  → Binary search on the answer space
└── NO  → Binary search does not apply
```

## The "Search Space" Mental Model

Binary search is not just for arrays — it works on any monotone function over a range of values.

**Key insight:** if you can write a function `feasible(x)` that returns `True` or `False` and is monotone (once True, always True as x increases), you can binary search on the answer.

```
Problem: "What is the minimum speed K such that Koko can eat all bananas in H hours?"

feasible(K) = True if Koko can finish in H hours at speed K
            = False otherwise

K:            1   2   3   4   5   6   7
feasible(K):  F   F   F   T   T   T   T
                          ↑
              Binary search finds this boundary
```

The search space is the *value of K*, not an index in an array. This unlocks a wide class of problems:

| Problem Type | Search Space | Condition |
|---|---|---|
| Sorted array | indices 0..n-1 | `nums[mid] >= target` |
| Koko eating bananas | speed 1..max(piles) | `can_finish(speed, h)` |
| Ship packages | capacity max..sum | `can_ship(capacity, days)` |
| Sqrt(x) | value 1..x//2 | `mid*mid <= x` |
| Split array largest sum | value max..sum | `can_split(limit, m)` |

## Complexity

| Variant | Time | Space | Notes |
|---|---|---|---|
| Classic search | O(log n) | O(1) | Exact target |
| Boundary search | O(log n) | O(1) | First/last occurrence |
| Search on answer | O(log(range) * check) | O(1) | check = O(n) typically |
| Rotated array | O(log n) | O(1) | No extra scan needed |
| Two sorted arrays (median) | O(log(min(m,n))) | O(1) | Partition-based |

## Common Mistakes

**1. Infinite loop from wrong termination condition**

```python
# WRONG — can loop forever when left == right
while left < right:
    mid = (left + right) // 2
    if nums[mid] < target:
        left = mid       # ← mid == left when l and r are adjacent → infinite loop
    ...

# CORRECT
left = mid + 1            # always makes progress
```

**2. Off-by-one in boundary search**

```python
# For leftmost boundary: right starts at len(nums), not len(nums)-1
# This is because the target might not exist and left converges to n
left, right = 0, len(nums)   # open right boundary

# For rightmost boundary: check return value
# If left == len(nums) or nums[left] != target → not found
```

**3. Integer overflow in mid calculation (Java/C++)**

```python
# Python: integers are arbitrary precision — no overflow
mid = (left + right) // 2    # safe in Python

// Java/C++: int overflow when left + right > INT_MAX
int mid = left + (right - left) / 2;   // safe form
```

**4. Using `<=` vs `<` in the while loop**

- Classic (exact target): `while left <= right` — processes the single-element range
- Boundary search: `while left < right` — stops when converged; `left == right` is the answer

**5. Forgetting that `right = mid` (not `mid - 1`) in boundary search**

When `condition(mid)` is true, `mid` could be the answer itself — you cannot exclude it. Use `right = mid`.

## Run the Code

```bash
# From repo root
pytest tests/patterns/test_binary_search.py -v
```

**Implementation:** [`python/patterns/binary_search.py`](../../../python/patterns/binary_search.py)
**Tests:** [`tests/patterns/test_binary_search.py`](../../../tests/patterns/test_binary_search.py)

## Problems

8 problems with full think-process walk-throughs: [problems.md](problems.md)

| # | Problem | Difficulty | LeetCode |
|---|---|---|---|
| 1 | Binary Search | Easy | #704 |
| 2 | Search Insert Position | Easy | #35 |
| 3 | Find Minimum in Rotated Sorted Array | Medium | #153 |
| 4 | Search in Rotated Sorted Array | Medium | #33 |
| 5 | Find First and Last Position of Element in Sorted Array | Medium | #34 |
| 6 | Koko Eating Bananas | Medium | #875 |
| 7 | Capacity to Ship Packages Within D Days | Medium | #1011 |
| 8 | Median of Two Sorted Arrays | Hard | #4 |
