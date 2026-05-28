# Binary Search — Problems

## Easy

---

### Problem 1: Binary Search  [Easy]  [LC #704]

**1. Clarifying questions to ask**
- Is the array guaranteed to be sorted in ascending order? Yes, per the problem.
- Can there be duplicate values? No, LC #704 guarantees distinct integers.
- What should I return if the target is not found? Return -1.
- Can the array be empty? Yes — handle the empty case.

**2. Brute force**
Linear scan: iterate through every element and check `nums[i] == target`. Time O(n), Space O(1). Works but completely ignores the sorted structure.

**3. Optimization**
The array is sorted, so for any `mid`, if `nums[mid] < target`, the target must be in the right half; if `nums[mid] > target`, it must be in the left half. Halve the search space each iteration.

```
nums = [-1, 0, 3, 5, 9, 12],  target = 9

l=0, r=5 → mid=2 → nums[2]=3 < 9  → l = 3
l=3, r=5 → mid=4 → nums[4]=9 = 9  → return 4
```

**4. Edge cases**
- Empty array: `left > right` immediately, return -1
- Target smaller than all elements: `right` moves to -1, loop exits
- Target larger than all elements: `left` moves to n, loop exits
- Single-element array where element equals target: found on first iteration
- Single-element array where element does not equal target: loop runs once, exits

**5. Final code**
```python
def search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

**Complexity:** Time O(log n), Space O(1)

**6. Follow-up questions**
- What if there are duplicates? Return any matching index — the algorithm still works but `left` and `right` may not converge to the leftmost/rightmost occurrence. Use boundary search (Problem 5) for that.
- Why `left <= right` and not `left < right`? With `<`, a single-element range (`left == right`) would be skipped. The `<=` form ensures every non-empty range is examined.
- How many iterations in the worst case? `floor(log2(n)) + 1`. For n=10^9, that is ~30 iterations.

---

### Problem 2: Search Insert Position  [Easy]  [LC #35]

**1. Clarifying questions to ask**
- Is the array sorted with distinct values? Yes, LC #35 guarantees both.
- If target exists, return its index? Yes.
- If target does not exist, return where it would be inserted to maintain sorted order? Yes.
- O(log n) required? Yes, that is the implied constraint.

**2. Brute force**
Linear scan from left: find the first index where `nums[i] >= target`. If none found, return `n`. Time O(n), Space O(1).

**3. Optimization**
This is exactly the "leftmost boundary" binary search — find the leftmost index where `nums[mid] >= target`. The answer is either the position of the existing element or the insertion point.

```
nums = [1, 3, 5, 6],  target = 5
l=0, r=3 → mid=1 → nums[1]=3 < 5  → l = 2
l=2, r=3 → mid=2 → nums[2]=5 >= 5 → r = 2
l=2, r=2 → left == right → return 2   (target found at index 2)

nums = [1, 3, 5, 6],  target = 2
l=0, r=3 → mid=1 → nums[1]=3 >= 2 → r = 1
l=0, r=1 → mid=0 → nums[0]=1 < 2  → l = 1
l=1, r=1 → left == right → return 1   (insert between index 0 and 1)

nums = [1, 3, 5, 6],  target = 7
l=0, r=3 → mid=1 → nums[1]=3 < 7  → l = 2
l=2, r=3 → mid=2 → nums[2]=5 < 7  → l = 3
l=3, r=3 → mid=3 → nums[3]=6 < 7  → l = 4
l=4, r=3 → left > right → return left = 4  (insert at end)
```

**4. Edge cases**
- Target smaller than all elements: `right` shrinks to -1, `left` stays at 0 → return 0 (insert at front)
- Target larger than all elements: `left` grows to n → return n (insert at end)
- Target equal to first element: returns 0
- Target equal to last element: returns n-1

**5. Final code**
```python
def search_insert(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return left   # left is the insertion point when target not found
```

**Complexity:** Time O(log n), Space O(1)

**6. Follow-up questions**
- Why does `left` give the correct insertion point? After the loop, `left > right` and `left - 1` is the last index where `nums[i] < target`. So `left` is exactly the first index where `nums[i] >= target` (or `n` if all elements are smaller).
- How does this relate to Python's `bisect_left`? This is exactly what `bisect_left(nums, target)` does. Understanding the underlying algorithm is what interviewers want.
- Can this be extended to arrays with duplicates? Yes — `left` returns the leftmost valid insertion position, consistent with `bisect_left`.

---

## Medium

---

### Problem 3: Find Minimum in Rotated Sorted Array  [Medium]  [LC #153]

**1. Clarifying questions to ask**
- Guaranteed no duplicates? Yes, LC #153 guarantees distinct values.
- What counts as "rotated"? The array was originally sorted, then some prefix was moved to the end (rotation by k positions).
- Is an un-rotated array valid input? Yes — it is a rotation by 0.
- Can the array have only one element? Yes — return it.

**2. Brute force**
Linear scan for the minimum. Time O(n), Space O(1). Ignores the structure.

**3. Optimization**
A rotated sorted array has exactly one inflection point — where the sequence drops. Everything to the left of the minimum is the "upper plateau" (large values), everything to the right is the "lower slope" (small values).

Key observation: compare `nums[mid]` to `nums[right]`.
- If `nums[mid] > nums[right]`: the minimum is in the right half (mid is on the upper plateau).
- If `nums[mid] <= nums[right]`: the minimum is in the left half including mid (mid is on the lower slope or IS the minimum).

```
nums = [4, 5, 6, 7, 0, 1, 2]
                        ↑ inflection point / minimum

l=0, r=6 → mid=3 → nums[3]=7 > nums[6]=2 → l = 4  (min is right of mid)
l=4, r=6 → mid=5 → nums[5]=1 <= nums[6]=2 → r = 5  (min is at or left of mid)
l=4, r=5 → mid=4 → nums[4]=0 <= nums[5]=1 → r = 4  (min is at or left of mid)
l=4, r=4 → left == right → return nums[4] = 0
```

Not-rotated case `[1, 2, 3, 4, 5]`: every `nums[mid] <= nums[right]`, so `right` keeps shrinking to 0. Correct.

**4. Edge cases**
- Single element: `left == right` immediately, return `nums[0]`
- Two elements: one comparison resolves it correctly
- Not rotated (ascending): `right` converges to 0, returns `nums[0]`
- Rotated by 1 (last element moved to front): minimum is `nums[0]`

**5. Final code**
```python
def find_min(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:            # stop when converged; left IS the answer
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1         # min is strictly right of mid
        else:
            right = mid            # min is at mid or left of mid; keep mid
    return nums[left]
```

**Complexity:** Time O(log n), Space O(1)

**6. Follow-up questions**
- LC #154: array may contain duplicates — what changes? When `nums[mid] == nums[right]`, you cannot determine which half; fall back to `right -= 1`. Worst case degrades to O(n).
- Why `while left < right` (not `<=`)? The loop terminates when `left == right`, which is the minimum position. Using `<=` would go one step past and need a guard.
- Why compare with `nums[right]` and not `nums[left]`? Comparing to `nums[right]` cleanly determines which side the inflection is on. Comparing to `nums[left]` is ambiguous when the array is not rotated (`nums[left]` could be the minimum itself).

---

### Problem 4: Search in Rotated Sorted Array  [Medium]  [LC #33]

**1. Clarifying questions to ask**
- Distinct values guaranteed? Yes, for LC #33.
- Return the index if found, -1 if not? Yes.
- What if the array has only one element? Return 0 if it matches target, -1 otherwise.
- Is O(log n) required? Yes.

**2. Brute force**
Linear scan. Time O(n), Space O(1).

**3. Optimization**
At any `mid`, at least one half of the array is guaranteed to be sorted (no inflection in it). Determine which half is sorted, then check if the target falls in that sorted half's range.

```
Decision at each mid:
  Is nums[left] <= nums[mid]?
  ├── YES → left half is sorted
  │         Is nums[left] <= target < nums[mid]?
  │         ├── YES → target is in left half → r = mid - 1
  │         └── NO  → target must be in right half → l = mid + 1
  └── NO  → right half is sorted
            Is nums[mid] < target <= nums[right]?
            ├── YES → target is in right half → l = mid + 1
            └── NO  → target must be in left half → r = mid - 1
```

Walkthrough:
```
nums = [4, 5, 6, 7, 0, 1, 2],  target = 0

l=0, r=6 → mid=3 → nums[3]=7
  nums[0]=4 <= nums[3]=7 → left half [4,5,6,7] is sorted
  Is 4 <= 0 < 7? NO → target in right half → l = 4

l=4, r=6 → mid=5 → nums[5]=1
  nums[4]=0 <= nums[5]=1 → left half [0,1] is sorted
  Is 0 <= 0 < 1? YES → target in left half → r = 4

l=4, r=4 → mid=4 → nums[4]=0 == target → return 4
```

**4. Edge cases**
- Single element: compare directly, return 0 or -1
- Target is the minimum (inflection point): algorithm locates it correctly
- Rotation by n (not rotated): `nums[left] <= nums[mid]` always true, reduces to classic binary search
- Target not present: `left > right`, return -1

**5. Final code**
```python
def search_rotated(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:          # left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:                                 # right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

**Complexity:** Time O(log n), Space O(1)

**6. Follow-up questions**
- LC #81: what if duplicates are allowed? When `nums[left] == nums[mid] == nums[right]`, you cannot tell which half is sorted. The safe fallback: `left += 1; right -= 1`. Worst case O(n).
- Why check `nums[left] <= nums[mid]` with `<=` not `<`? When `left == mid` (two-element range), the left half is trivially sorted (single element). The `<=` handles this correctly.
- Can you combine this with Find Minimum (LC #153) to first find the rotation pivot, then do two classic binary searches? Yes — O(log n) + O(log n) = O(log n) total. Slightly more code but arguably clearer.

---

### Problem 5: Find First and Last Position of Element in Sorted Array  [Medium]  [LC #34]

**1. Clarifying questions to ask**
- The array is sorted in non-decreasing order — so duplicates are possible? Yes, that is the entire point of the problem.
- Return `[-1, -1]` if the target is not found? Yes.
- Is O(log n) required? Yes — O(n) linear scan is too slow.
- Can the array be empty? Yes — return `[-1, -1]`.

**2. Brute force**
Linear scan: find first index where `nums[i] == target`, then scan forward for the last. Time O(n), Space O(1). Correct but not O(log n).

**3. Optimization**
Run two binary searches:
1. **Leftmost boundary**: find the first index where `nums[i] >= target` and check if it equals target.
2. **Rightmost boundary**: find the last index where `nums[i] <= target` and check if it equals target.

```
nums = [5, 7, 7, 8, 8, 10],  target = 8

Leftmost (find first index where nums[i] >= 8):
l=0, r=5 → mid=2 → nums[2]=7 < 8  → l = 3
l=3, r=5 → mid=4 → nums[4]=8 >= 8 → r = 4
l=3, r=4 → mid=3 → nums[3]=8 >= 8 → r = 3
l=3, r=3 → converged → left=3

nums[3]=8 == target → first = 3

Rightmost (find last index where nums[i] <= 8):
l=0, r=5 → mid=2 → nums[2]=7 <= 8 → l = 3  (check right half for more 8s)
l=3, r=5 → mid=4 → nums[4]=8 <= 8 → l = 5  (check right half)
l=5, r=5 → mid=5 → nums[5]=10 > 8 → r = 4
l=5, r=4 → left > right → return right=4

nums[4]=8 == target → last = 4

Result: [3, 4]
```

**4. Edge cases**
- Target not in array: leftmost boundary points to a position where `nums[pos] != target` → return `[-1, -1]`
- All elements equal target: returns `[0, n-1]`
- Single occurrence: both boundaries converge to the same index
- Empty array: return `[-1, -1]`

**5. Final code**
```python
def search_range(nums: list[int], target: int) -> list[int]:
    def find_bound(is_first: bool) -> int:
        left, right = 0, len(nums) - 1
        bound = -1
        while left <= right:
            mid = (left + right) // 2
            if nums[mid] == target:
                bound = mid
                if is_first:
                    right = mid - 1   # keep searching left for earlier occurrence
                else:
                    left = mid + 1    # keep searching right for later occurrence
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        return bound

    return [find_bound(True), find_bound(False)]
```

**Complexity:** Time O(log n), Space O(1) — two binary searches, each O(log n)

**6. Follow-up questions**
- Why two separate binary searches instead of one? After finding any occurrence of target at `mid`, you cannot determine in O(1) whether it is the first or last — you need to continue searching in one direction. Two searches are cleaner and still O(log n).
- Is there an O(log n) single-pass approach? No — the first and last positions require independent searches. You can combine early termination for the "not found" case, but two passes are standard.
- How does this extend to "count occurrences of target"? `last - first + 1` if both are not -1, else 0.

---

### Problem 6: Koko Eating Bananas  [Medium]  [LC #875]

**1. Clarifying questions to ask**
- Can Koko eat bananas from multiple piles per hour? No — she picks one pile per hour and eats up to K bananas from it.
- If the pile has fewer than K bananas, she still takes the full hour? Yes.
- Must we find the minimum valid K? Yes.
- What are the constraints on pile sizes and H? `1 <= piles[i] <= 10^9`, `len(piles) <= H <= 10^14`.

**2. Brute force**
Try every speed K from 1 to max(piles). For each K, compute total hours needed. Return the first K where hours <= H. Time O(max(piles) * n), too slow.

**3. The "search on answer space" insight**

The key unlock: this is NOT a search over array indices. It is a search over the answer itself.

Define `feasible(K)` = "can Koko eat all piles at speed K within H hours?". This function is monotone:
- If K is fast enough, so is K+1 (more speed never hurts).
- If K is too slow, K-1 is also too slow.

So the feasibility values look like:

```
K:            1   2   3   4   5   6   7
feasible(K):  F   F   F   T   T   T   T
                          ↑
              We want the leftmost True → minimum valid K
```

**Search space:**
- Lower bound: K=1 (minimum meaningful speed)
- Upper bound: K=max(piles) (at this speed, each pile takes exactly 1 hour; H >= n is guaranteed)

For each candidate K, compute `sum(ceil(pile / K) for pile in piles)` in O(n). Binary search runs O(log(max(piles))) iterations.

```
piles = [3, 6, 7, 11],  H = 8

K=1: ceil(3/1)+ceil(6/1)+ceil(7/1)+ceil(11/1) = 3+6+7+11 = 27 > 8 → too slow
K=6: ceil(3/6)+ceil(6/6)+ceil(7/6)+ceil(11/6) = 1+1+2+2 = 6 <= 8  → fast enough
K=3: ceil(3/3)+ceil(6/3)+ceil(7/3)+ceil(11/3) = 1+2+3+4 = 10 > 8  → too slow
K=4: ceil(3/4)+ceil(6/4)+ceil(7/4)+ceil(11/4) = 1+2+2+3 = 8 <= 8  → fast enough
K=3 → F, K=4 → T → leftmost True is K=4
Answer: 4
```

**4. Edge cases**
- Single pile: answer is `ceil(pile / H)` — binary search finds this
- H == len(piles): must eat one pile per hour at full speed → answer is max(piles)
- All piles size 1: answer is 1
- Very large pile values: `math.ceil(p / mid)` handles correctly; no overflow in Python

**5. Final code**
```python
import math

def min_eating_speed(piles: list[int], h: int) -> int:
    left, right = 1, max(piles)
    while left < right:
        mid = (left + right) // 2
        hours = sum(math.ceil(p / mid) for p in piles)
        if hours <= h:
            right = mid        # mid might be the answer; don't exclude it
        else:
            left = mid + 1     # mid is too slow; exclude it
    return left
```

**Complexity:** Time O(n log(max(piles))), Space O(1)

**6. Follow-up questions**
- Why `while left < right` instead of `left <= right`? We are doing boundary (leftmost True) search. When `left == right`, we have converged on the answer — no need to iterate again.
- Why `right = mid` (not `mid - 1`) when feasible? `mid` could be the optimal answer; we must not exclude it.
- Why `left = mid + 1` when not feasible? `mid` is definitely too slow; the answer is strictly to the right.
- What if pile values can be 0? `ceil(0 / K) = 0` — correctly contributes 0 hours. The algorithm handles it.
- Name three other "binary search on answer" problems: Capacity to Ship (LC #1011), Split Array Largest Sum (LC #410), Minimum Days to Make m Bouquets (LC #1482).

---

### Problem 7: Capacity to Ship Packages Within D Days  [Medium]  [LC #1011]

**1. Clarifying questions to ask**
- Packages must be shipped in order (no reordering)? Yes — the belt is FIFO.
- A package too heavy for the ship capacity is invalid input? Yes — capacity >= max(weights) is guaranteed.
- Find minimum capacity to ship all packages in exactly D days? At most D days.
- Constraints? `1 <= weights[i] <= 500`, `1 <= len(weights) <= 500`, `1 <= days <= len(weights)`.

**2. Brute force**
Try every capacity from max(weights) to sum(weights). For each capacity, simulate shipping and count days. Return the first capacity that works. Time O(sum * n), too slow.

**3. The "search on answer space" insight (same pattern as Koko)**

Define `feasible(capacity)` = "can we ship all packages within D days at this capacity?".

Why is this monotone? More capacity → can load more per day → finishes in fewer or equal days. Once it is feasible, increasing capacity stays feasible.

```
feasible(capacity):  F   F   F   T   T   T   T
                              ↑
                    Leftmost True = minimum capacity
```

**Search space:**
- Lower bound: `max(weights)` — a single package must fit; any less and we cannot even load the heaviest item
- Upper bound: `sum(weights)` — load everything in one day; definitely feasible

**Simulation (the feasibility check):**
Greedily load as many packages as possible per day without exceeding capacity. Count days needed.

```
weights = [1,2,3,4,5,6,7,8,9,10],  days = 5

Try capacity = 15:
  Day 1: 1+2+3+4+5 = 15 ✓  (adding 6 would be 21 > 15)
  Day 2: 6+7 = 13 ✓         (adding 8 would be 21 > 15)
  Day 3: 8 = 8               (adding 9 would be 17 > 15)
  Day 4: 9 = 9               (adding 10 would be 19 > 15)
  Day 5: 10 = 10
  Total days = 5 <= 5 → feasible ✓

Try capacity = 14:
  Day 1: 1+2+3+4 = 10, adding 5 → 15 > 14, stop. Day 1 = 10
  Day 2: 5+6 = 11, adding 7 → 18 > 14. Day 2 = 11
  Day 3: 7 = 7, adding 8 → 15 > 14. Day 3 = 7
  Day 4: 8 = 8, adding 9 → 17 > 14. Day 4 = 8
  Day 5: 9 = 9, adding 10 → 19 > 14. Day 5 = 9
  Day 6: 10 = 10
  Total days = 6 > 5 → not feasible ✗

Binary search homes in on 15.
```

**4. Edge cases**
- `days == 1`: must ship all at once; answer is `sum(weights)`
- `days == len(weights)`: one package per day; answer is `max(weights)`
- Single package: answer is `weights[0]` (any valid capacity >= weights[0])
- All equal weights: answer is `ceil(n / days) * weight_per_item`

**5. Final code**
```python
def ship_within_days(weights: list[int], days: int) -> int:
    def can_ship(capacity: int) -> bool:
        day_count, current_load = 1, 0
        for w in weights:
            if current_load + w > capacity:
                day_count += 1
                current_load = 0
            current_load += w
        return day_count <= days

    left, right = max(weights), sum(weights)
    while left < right:
        mid = (left + right) // 2
        if can_ship(mid):
            right = mid        # mid could be optimal; keep it
        else:
            left = mid + 1     # mid is too small; exclude it
    return left
```

**Complexity:** Time O(n log(sum - max)), Space O(1)

**6. Follow-up questions**
- How does this differ from Koko Eating Bananas structurally? Identical structure: binary search on answer, feasibility check is a greedy simulation, leftmost True boundary. The only difference is what the search space represents (speed vs. capacity) and how the feasibility check works (ceiling division vs. greedy packing).
- Why is `left = max(weights)` the correct lower bound? If capacity < max(weights), we cannot even place the heaviest single package — immediately infeasible regardless of days.
- Can we have floating-point capacities? No — packages have integer weights, so integer capacities are sufficient. Binary search on integers is exact.
- What if packages can be reordered? Then this becomes a bin-packing problem, which is NP-hard. The in-order constraint is what makes the greedy check efficient.

---

## Hard

---

### Problem 8: Median of Two Sorted Arrays  [Hard]  [LC #4]

**1. Clarifying questions to ask**
- Both arrays are sorted in non-decreasing order? Yes.
- What if one or both arrays are empty? Handle gracefully — if one is empty, median is just the other array's median.
- Return a float? Yes — median is `(a + b) / 2.0` when total length is even.
- O(log(m+n)) required? Yes — that is the hard constraint. O(m+n) merge approach is too slow.

**2. Brute force**
Merge both sorted arrays (merge step of merge sort), then find the median in the merged array. Time O(m+n), Space O(m+n). Correct but violates the O(log) requirement.

**3. O(m+n) stepping stone**
Two pointers on both arrays; advance the smaller head. Count to the median position. Time O(m+n), Space O(1). Better, but still linear.

**4. Optimization: binary search on the partition point**

Key insight: the median divides the combined array into two equal halves. We need to find a partition of `nums1` (at index `i`) and a partition of `nums2` (at index `j = half_len - i`) such that:

- Everything to the left of both partitions is the "left half" of the merged result.
- Everything to the right is the "right half".

For this to be a valid median partition, two cross-conditions must hold:
- `nums1[i-1] <= nums2[j]`  (left side of nums1 does not exceed right side of nums2)
- `nums2[j-1] <= nums1[i]`  (left side of nums2 does not exceed right side of nums1)

If `nums1[i-1] > nums2[j]`: partition `i` is too far right → move `i` left.
If `nums2[j-1] > nums1[i]`: partition `i` is too far left → move `i` right.

```
Binary search on i ∈ [0, len(nums1)]
j = (m + n + 1) // 2 - i   (ensures left half has correct size)
```

Always binary search on the smaller array to keep it O(log(min(m,n))).

Worked example:
```
nums1 = [1, 3],    m = 2
nums2 = [2, 4, 6], n = 3
Total = 5 (odd), half_len = (5+1)//2 = 3

Binary search i in [0, 2]:
  i=1 → j=3-1=2
  left1 = nums1[0]=1,  right1 = nums1[1]=3
  left2 = nums2[1]=4,  right2 = nums2[2]=6

  Check: left1(1) <= right2(6) ✓
  Check: left2(4) <= right1(3) ✗  → 4 > 3, need to move i right

  i=2 → j=3-2=1
  left1 = nums1[1]=3,  right1 = +inf (i == m)
  left2 = nums2[0]=2,  right2 = nums2[1]=4

  Check: left1(3) <= right2(4) ✓
  Check: left2(2) <= right1(inf) ✓  → valid partition!

  Total length is odd → median = max(left1, left2) = max(3, 2) = 3
```

Full partition diagram:
```
nums1: [1 | 3]    ← partition after index 1 (i=2 means left half includes [1,3])
nums2: [2 | 4, 6] ← partition after index 0

Left half:  [1, 2, 3]  (all ≤ right half)
Right half: [4, 6]

Median = max(1, 2, 3) = 3   (5 total elements → middle = 3rd)
```

**5. Edge cases**
- One array empty: `i` binary searches over [0,0], `j` covers the other array entirely
- Arrays of length 1: handled correctly by boundary checks
- All elements of nums1 < all elements of nums2: `i = len(nums1)`, partition at the end
- All elements of nums1 > all elements of nums2: `i = 0`, partition at the start
- Even total length: median is `(max(left1, left2) + min(right1, right2)) / 2.0`
- Duplicate values spanning both arrays: the `<=` comparisons handle correctly

**6. Final code**
```python
def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    # Ensure nums1 is the smaller array for O(log(min(m,n)))
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    half_len = (m + n + 1) // 2

    left, right = 0, m
    while left <= right:
        i = (left + right) // 2     # partition index in nums1
        j = half_len - i            # partition index in nums2

        # Elements just left and right of each partition
        left1  = nums1[i - 1] if i > 0 else float('-inf')
        right1 = nums1[i]     if i < m else float('inf')
        left2  = nums2[j - 1] if j > 0 else float('-inf')
        right2 = nums2[j]     if j < n else float('inf')

        if left1 <= right2 and left2 <= right1:
            # Valid partition found
            if (m + n) % 2 == 1:
                return float(max(left1, left2))
            else:
                return (max(left1, left2) + min(right1, right2)) / 2.0
        elif left1 > right2:
            right = i - 1   # i too far right; move left
        else:
            left = i + 1    # i too far left; move right

    return 0.0  # unreachable for valid inputs
```

**Complexity:** Time O(log(min(m,n))), Space O(1)

**7. Follow-up questions**
- Why binary search on the smaller array? It minimizes the number of iterations. Correctness is the same either way, but O(log(min(m,n))) is tighter than O(log(m)) when n >> m.
- Why `half_len = (m+n+1)//2` with the `+1`? The `+1` ensures that when `m+n` is odd, the left half gets the extra element (the median). It makes the formula work uniformly for both odd and even totals.
- Why `-inf`/`+inf` as sentinels? When `i=0`, the entire nums1 is in the right half — there is no nums1 element in the left half, so treat it as negative infinity (anything is greater). When `i=m`, no nums1 element is in the right half, so treat it as positive infinity.
- What is the connection to "k-th element of two sorted arrays"? Finding the median is a special case of finding the k-th smallest element. The same partition approach generalizes: binary search for the partition where exactly k-1 elements are smaller.
- What makes this problem "Hard"? The O(log) constraint forces a non-obvious approach. Most interview candidates either describe the O(m+n) merge or get stuck on the partition invariant. The ability to derive the two cross-conditions and handle boundary sentinels is the signal.
