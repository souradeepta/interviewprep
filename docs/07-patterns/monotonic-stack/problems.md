# Monotonic Stack — Problems

## Medium

---

### Problem 1: Daily Temperatures  [Medium]  [LC #739]

**1. Clarifying questions to ask**
- Return a list of wait times (number of days), not the actual warmer temperature? Yes.
- If no warmer day exists to the right, return 0 for that day? Yes.
- Are temperatures guaranteed to be integers in a valid range? Yes (per LC, 30–100 °F).
- Is the input guaranteed non-empty? Assume yes.

**2. Brute force**
For each day `i`, scan every day `j > i` until `temperatures[j] > temperatures[i]`. Return `j - i`. Time O(n²), Space O(1).

**3. Optimization**
Decreasing monotonic stack of indices. Maintain the invariant that temperatures at stacked indices are non-increasing. When a new temperature is warmer than the top of the stack, that top index has found its answer.

```
temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
                 0   1   2   3   4   5   6   7

i=0 T=73: stack=[] → push 0.            stack=[0]
i=1 T=74: 74 > T[0]=73 → pop 0, result[0]=1-0=1
          stack=[] → push 1.             stack=[1]
i=2 T=75: 75 > T[1]=74 → pop 1, result[1]=2-1=1
          stack=[] → push 2.             stack=[2]
i=3 T=71: 71 < T[2]=75 → push 3.        stack=[2,3]
i=4 T=69: 69 < T[3]=71 → push 4.        stack=[2,3,4]
i=5 T=72: 72 > T[4]=69 → pop 4, result[4]=5-4=1
          72 > T[3]=71 → pop 3, result[3]=5-3=2
          72 < T[2]=75 → push 5.         stack=[2,5]
i=6 T=76: 76 > T[5]=72 → pop 5, result[5]=6-5=1
          76 > T[2]=75 → pop 2, result[2]=6-2=4
          stack=[] → push 6.             stack=[6]
i=7 T=73: 73 < T[6]=76 → push 7.        stack=[6,7]

End: indices 6,7 remain in stack → result[6]=result[7]=0

result = [1, 1, 4, 2, 1, 1, 0, 0]
```

The distance is `i - idx` where `i` is the current day and `idx` is the popped day.

**4. Edge cases**
- Strictly decreasing temperatures: stack fills up, nothing is ever popped; all results are 0
- Single element: no warmer day; result is `[0]`
- Strictly increasing temperatures: every element is immediately popped by the next; all waits are 1 except the last
- Duplicate temperatures: `74 > 74` is false — equals do not pop; use strictly greater

**5. Final code**
```python
def daily_temperatures(temperatures: list[int]) -> list[int]:
    result = [0] * len(temperatures)
    stack: list[int] = []              # indices, temperatures decreasing
    for i, temp in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < temp:
            idx = stack.pop()
            result[idx] = i - idx      # days waited
        stack.append(i)
    return result
```

**Complexity:** Time O(n), Space O(n)

**6. Follow-up questions**
- What if you need the actual warmer temperature, not the days? Store `temperatures[i]` at `result[idx]` instead of `i - idx`.
- What if you want days until COOLER temperature? Flip comparison to `temperatures[stack[-1]] > temp` — use an increasing stack.
- Can you do this with O(1) space? No — you need to store the pending indices somewhere; the stack is unavoidable.

---

### Problem 2: Next Greater Element I  [Easy]  [LC #496]

**1. Clarifying questions to ask**
- `nums1` is a subset of `nums2`? Yes — all elements of `nums1` appear in `nums2`.
- All elements are distinct? Yes per LC — this allows a simple hash map lookup.
- "Next greater" means the first element to the right in `nums2` that is larger? Yes.
- If no greater element exists, return -1 for that position? Yes.

**2. Brute force**
For each element in `nums1`, find its position in `nums2`, then scan right for the first greater element. Time O(m·n) where m=len(nums1), n=len(nums2). Space O(1).

**3. Optimization**
Precompute "next greater element" for every element in `nums2` using a decreasing monotonic stack. Store results in a hash map. Then for each element in `nums1`, look up the answer in O(1).

```
nums1 = [4, 1, 2]
nums2 = [1, 3, 4, 2]

Build next_greater map from nums2:
i=0 val=1: stack=[] → push 1.           stack=[1]
i=1 val=3: 3>1 → pop 1, map[1]=3
           stack=[] → push 3.           stack=[3]
i=2 val=4: 4>3 → pop 3, map[3]=4
           stack=[] → push 4.           stack=[4]
i=3 val=2: 2<4 → push 2.               stack=[4,2]
End: 4 and 2 never beaten → map[4]=-1, map[2]=-1

map = {1:3, 3:4, 4:-1, 2:-1}

Answer for nums1:
  nums1[0]=4 → map[4] = -1
  nums1[1]=1 → map[1] = 3
  nums1[2]=2 → map[2] = -1

result = [-1, 3, -1]
```

The key insight: precompute once for `nums2` (O(n)), then answer all `nums1` queries in O(m).

**4. Edge cases**
- `nums1` has one element: one lookup in the map
- The greatest element in `nums2`: maps to -1 (never beaten)
- `nums1 == nums2`: every element looked up — same as computing NGE for the whole array
- Element at the end of `nums2`: no greater element to the right → -1

**5. Final code**
```python
def next_greater_element(nums1: list[int], nums2: list[int]) -> list[int]:
    next_greater: dict[int, int] = {}
    stack: list[int] = []              # values, decreasing
    for val in nums2:
        while stack and stack[-1] < val:
            next_greater[stack.pop()] = val
        stack.append(val)
    while stack:                       # remaining have no greater element
        next_greater[stack.pop()] = -1
    return [next_greater[x] for x in nums1]
```

Note: this variant stores values (not indices) in the stack because elements are distinct and we key the map by value.

**Complexity:** Time O(n + m), Space O(n) for the hash map

**6. Follow-up questions**
- What if elements are not distinct? Store indices in the stack and key the map by index rather than value.
- What is LC #503? The same problem on a circular array (Next Greater Element II) — requires two passes.
- Can we skip building the full map and only compute for elements in `nums1`? Use a set of `nums1` values to filter: only add to the map when the popped value is in the set. Same asymptotic complexity, smaller map in practice.

---

### Problem 3: Next Greater Element II  [Medium]  [LC #503]

**1. Clarifying questions to ask**
- The array is circular — after the last element, we wrap back to the first? Yes.
- Still return -1 if an element has no greater in the full circular scan? Yes.
- Elements can be duplicates here (unlike LC #496)? Yes — so we must store indices, not values.
- Is the result array the same length as the input? Yes.

**2. Brute force**
For each index `i`, scan `(i+1) % n`, `(i+2) % n`, ... up to `n-1` steps. Return the first value greater than `nums[i]`. Time O(n²), Space O(1).

**3. Optimization**
Simulate the circular array by iterating `2n` indices (`i` from 0 to 2n-1), using `i % n` to wrap around. Run the standard decreasing-stack algorithm. Skip pushing during the second pass (indices ≥ n are "phantom" — only used to resolve remaining stack entries, not added themselves).

```
nums = [1, 2, 1]   n=3
Iterate i=0..5 with index = i % 3

i=0 idx=0 val=1: stack=[] → push 0.        stack=[0]
i=1 idx=1 val=2: 2>nums[0]=1 → pop 0, result[0]=2
                 stack=[] → push 1.         stack=[1]
i=2 idx=2 val=1: 1<nums[1]=2 → push 2.     stack=[1,2]
i=3 idx=0 val=1: 1<nums[2]=1 → no pop.     stack=[1,2]
i=4 idx=1 val=2: 2>nums[2]=1 → pop 2, result[2]=2
                 2>nums[1]=2? NO (not strictly greater)
                 i>=n so don't push.        stack=[1]
i=5 idx=2 val=1: 1<nums[1]=2 → no pop.     stack=[1]

End: index 1 still in stack → result[1]=-1

result = [2, -1, 2]
```

During the second pass (`i >= n`), only pop from the stack — never push new indices. This prevents the same index from being "answered" twice.

**4. Edge cases**
- All same values (e.g., `[3,3,3]`): nothing is ever greater; all results are -1
- Strictly increasing (e.g., `[1,2,3]`): in the second pass, `3` resolves `2`? No — `nums[2]=3 > nums[1]=2`, so result[1]=3. `nums[0]=1 < 3`... wait, in second pass i=3, idx=0, val=1 — 1 is not > nums[2]=3 so index 2 stays. Actually result[2] stays -1 if we never find a greater. Verify: for `[1,2,3]` → `[2, 3, -1]`.
- Single element: result is `[-1]` (circular scan always returns to itself, never finds greater)
- `[5, 4, 3, 2, 1]`: result[1..4] = 5 (wrap around to 5); result[0]=-1 (5 is the global max)

**5. Final code**
```python
def next_greater_element_ii(nums: list[int]) -> list[int]:
    n = len(nums)
    result = [-1] * n
    stack: list[int] = []              # indices, nums[idx] decreasing
    for i in range(2 * n):
        idx = i % n
        while stack and nums[stack[-1]] < nums[idx]:
            result[stack.pop()] = nums[idx]
        if i < n:                      # only push during first pass
            stack.append(idx)
    return result
```

**Complexity:** Time O(n) — 2n iterations, each index pushed/popped at most once, Space O(n)

**6. Follow-up questions**
- Why only push during the first pass? If we push during the second pass, an index could be pushed at `i=n+k` and later popped — but it already had its answer (or stayed -1) from the first pass. Pushing again would corrupt the result.
- What if the array has all distinct elements? We could store values but indices are always safer and work with duplicates too.
- Previous greater element (circular)? Iterate in reverse (2n to 0) with an increasing stack. Or equivalently, iterate forward but use `>` for the pop condition.

---

## Hard

---

### Problem 4: Largest Rectangle in Histogram  [Hard]  [LC #84]

**1. Clarifying questions to ask**
- Each bar has width 1? Yes per LC — the rectangle can span multiple adjacent bars of the same or greater height.
- Heights are non-negative integers? Yes.
- Can the input be empty? Assume non-empty (or return 0 for empty).
- Return the area as an integer? Yes.

**2. Brute force**
For every pair `(i, j)`, the rectangle height is `min(heights[i..j])` and width is `j - i + 1`. Track the maximum area. Time O(n²) with prefix-min precomputation, O(n³) naively. Space O(n).

**3. Optimization**
Increasing monotonic stack. For each bar, we want to know: how far left and right can it extend as the minimum bar? The stack tells us this: when we pop a bar (because a shorter bar arrived), the shorter bar is its right boundary, and the new stack top is its left boundary.

Append a sentinel height `0` at the end to flush all remaining bars from the stack.

```
heights = [2, 1, 5, 6, 2, 3]  →  append 0  →  [2,1,5,6,2,3,0]
           0  1  2  3  4  5                      0 1 2 3 4 5 6

i=0 h=2: stack=[] → push 0.                  stack=[0]
i=1 h=1: 1 < heights[0]=2 → pop 0
           height=2, stack empty → width=1, area=2
         push 1.                              stack=[1]
i=2 h=5: 5>1, push.                          stack=[1,2]
i=3 h=6: 6>5, push.                          stack=[1,2,3]
i=4 h=2: 2 < heights[3]=6 → pop 3
           height=6, left=stack[-1]=2, width=4-2-1=1, area=6
         2 < heights[2]=5 → pop 2
           height=5, left=stack[-1]=1, width=4-1-1=2, area=10  ← max
         2 > heights[1]=1, push 4.           stack=[1,4]
i=5 h=3: 3>2, push.                          stack=[1,4,5]
i=6 h=0 (sentinel):
         0 < heights[5]=3 → pop 5
           height=3, left=stack[-1]=4, width=6-4-1=1, area=3
         0 < heights[4]=2 → pop 4
           height=2, left=stack[-1]=1, width=6-1-1=4, area=8
         0 < heights[1]=1 → pop 1
           height=1, stack empty → width=6, area=6
         stack=[]

max_area = 10  (rectangle spanning bars 2 and 3, height=5, width=2)
```

Width formula: when stack is non-empty after a pop, `width = i - stack[-1] - 1`. When empty, `width = i` (the bar extends from index 0 to i-1).

**4. Edge cases**
- Single bar: result is that bar's height
- All bars the same height: one big rectangle spanning the full array
- Strictly decreasing: nothing pops until the sentinel; each bar's width is determined by the sentinel flush
- Heights contain zeros: zero-height bars are immediately popped when anything non-zero arrives; they contribute area 0

**5. Final code**
```python
def largest_rectangle_in_histogram(heights: list[int]) -> int:
    stack: list[int] = []
    max_area = 0
    for i, h in enumerate(heights + [0]):   # sentinel 0 flushes stack
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area
```

**Complexity:** Time O(n), Space O(n)

**6. Follow-up questions**
- What does the sentinel accomplish? Without it, bars remaining in the stack at loop end would not be processed. The sentinel `0` is shorter than everything, forcing all remaining bars to pop.
- Why append `i` to the original `heights` list instead of using modular indexing? The sentinel is appended to the copy `heights + [0]` — the original list is not mutated. The index `i` for the sentinel is `len(heights)`, so `width = i = n` when the stack is empty, which correctly gives full-width area.
- Divide and conquer O(n log n) alternative? Split at the minimum bar, recurse on left and right subarrays. Average O(n log n), worst O(n²) on sorted input. The stack approach is always O(n).
- LC #85 (Maximal Rectangle in a 2D matrix)? Reduce each row to a histogram problem: for each cell, compute the height of consecutive 1s above it, then run this histogram algorithm on each row.

---

### Problem 5: Sum of Subarray Minimums  [Medium]  [LC #907]

**1. Clarifying questions to ask**
- Sum the minimums of ALL contiguous subarrays? Yes.
- Return the answer modulo 10^9 + 7? Yes.
- Can the array contain duplicates? Yes — requires careful handling of equal elements to avoid double-counting.
- Array length up to 3×10^4, values up to 3×10^4? Yes per LC.

**2. Brute force**
Generate all subarrays, find the minimum of each, sum them up. Time O(n²) or O(n³), Space O(1). TLE for large inputs.

**3. Optimization — Contribution Technique**
Instead of "for each subarray, find its minimum", ask: "for each element `A[i]`, how many subarrays have `A[i]` as their minimum?"

For element `A[i]`:
- `left[i]` = number of subarrays extending to the left where `A[i]` is still the minimum = distance to the previous element that is **strictly smaller** (use `>=` for pop to handle duplicates correctly, preventing double-count).
- `right[i]` = distance to the next element that is **strictly smaller** (use `>` for pop).
- Contribution = `A[i] * left[i] * right[i]`

Use a monotonic stack to compute both boundaries in O(n).

```
A = [3, 1, 2, 4]

Previous smaller (strict): use decreasing stack, pop on >=
  i=0 val=3: stack=[] → left[0]=0-(-1)=1 (no PSE, sentinel at -1)  push 0
  i=1 val=1: 1<3, pop 0; stack empty → left[1]=1-(-1)=2            push 1
  i=2 val=2: 2>1 → left[2]=2-1=1                                   push 1,2
  i=3 val=4: 4>2 → left[3]=3-2=1                                   push 1,2,3

left = [1, 2, 1, 1]  (distance from element to its left boundary, inclusive)

Next smaller or equal (strict less): use increasing stack, pop on >
  i=0 val=3: stack=[] → push 0
  i=1 val=1: 1<3 → pop 0, right[0]=1-0=1. push 1
  i=2 val=2: 2>1 → push 2
  i=3 val=4: 4>2 → push 3
  End: right[1]=4-1=3, right[2]=4-2=2, right[3]=4-3=1

right = [1, 3, 2, 1]

Contribution:
  A[0]=3: 3 * 1 * 1 = 3   (subarrays: [3])
  A[1]=1: 1 * 2 * 3 = 6   (subarrays: [1],[3,1],[1,2],[3,1,2],[1,2,4],[3,1,2,4])
  A[2]=2: 2 * 1 * 2 = 4   (subarrays: [2],[2,4])
  A[3]=4: 4 * 1 * 1 = 4   (subarrays: [4])

Total = 3 + 6 + 4 + 4 = 17
```

To handle duplicates: for equal elements, let the LEFT boundary use strict less (`>=` pops), and the RIGHT boundary use less-or-equal (`>` pops). This ensures each subarray's minimum is counted exactly once.

**4. Edge cases**
- Single element: result is that element (only one subarray)
- All equal elements: each element is the minimum of subarrays extending half-left and half-right — contribution formula handles this cleanly
- Large values: apply `% (10**9 + 7)` to the final sum (or accumulate with mod)
- Strictly decreasing array: each element is the minimum only in the subarray ending at it (right boundary = 1 for all)

**5. Final code**
```python
def sum_subarray_minimums(arr: list[int]) -> int:
    MOD = 10**9 + 7
    n = len(arr)
    left = [0] * n      # distance to previous strictly smaller
    right = [0] * n     # distance to next smaller or equal

    stack: list[int] = []
    for i in range(n):
        while stack and arr[stack[-1]] >= arr[i]:  # pop on >=, handles duplicates
            stack.pop()
        left[i] = i - stack[-1] if stack else i + 1
        stack.append(i)

    stack = []
    for i in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] > arr[i]:   # pop on >, strict
            stack.pop()
        right[i] = stack[-1] - i if stack else n - i
        stack.append(i)

    return sum(arr[i] * left[i] * right[i] for i in range(n)) % MOD
```

**Complexity:** Time O(n), Space O(n)

**6. Follow-up questions**
- Why asymmetric pop conditions (`>=` left, `>` right)? For duplicates `[3, 1, 1, 2]`, both `1`s are the minimum of some subarrays. If both boundaries use `>=`, the left `1` gets zero credit for subarrays between them; if both use `>`, both get full credit (double-count). The asymmetry ensures exactly one of the two `1`s "owns" subarrays with equal minimums.
- Can you do this in one pass? Yes — compute left boundaries as you go, right boundaries require a second pass (or process right-to-left on the first stack's remaining elements after the loop).
- LC #2104 (Sum of Subarray Ranges)? The range of a subarray is `max - min`. Same contribution technique, compute sum-of-maxima (decreasing stack) and sum-of-minima (this problem) separately, then subtract.

---

### Problem 6: Trapping Rain Water  [Hard]  [LC #42]

**1. Clarifying questions to ask**
- 1D elevation map, width of each bar is 1? Yes.
- Return total units of water trapped? Yes.
- Heights are non-negative integers? Yes.
- Array length at least 1? Yes — though with fewer than 3 bars, no water can be trapped.

**2. Brute force**
For each position `i`, find `max_left = max(height[0..i])` and `max_right = max(height[i..n-1])`. Water at `i` is `min(max_left, max_right) - height[i]`. Sum over all positions. Time O(n²) or O(n) with prefix/suffix max arrays.

**3. Optimization — Monotonic Stack (Layer-by-Layer)**
Two-pointer is the most well-known O(n)/O(1) approach. The stack-based approach fills water **horizontally, layer by layer**, which is a natural fit for the monotonic stack pattern.

Maintain a decreasing stack. When a taller bar arrives, it forms the right wall of a "trough". The popped bar is the bottom of the trough, and the new stack top is the left wall.

```
height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
          0  1  2  3  4  5  6  7  8  9 10 11

i=0 h=0: push 0.                     stack=[0]
i=1 h=1: 1>h[0]=0 → pop 0 (bottom)
           left=stack top: stack empty → break (no left wall)
         push 1.                     stack=[1]
i=2 h=0: 0<1, push 2.               stack=[1,2]
i=3 h=2: 2>h[2]=0 → pop 2 (bottom=idx 2, h=0)
           left=stack[-1]=1, left_h=h[1]=1
           width = 3-1-1 = 1
           bounded_h = min(h[1]=1, h[3]=2) - h[2]=0 = 1
           water += 1*1 = 1
         2>h[1]=1 → pop 1 (bottom=idx 1, h=1)
           stack empty → break
         push 3.                     stack=[3]
i=4 h=1: 1<2, push 4.               stack=[3,4]
i=5 h=0: 0<1, push 5.               stack=[3,4,5]
i=6 h=1: 1>h[5]=0 → pop 5 (bottom=5, h=0)
           left=stack[-1]=4, left_h=1
           width=6-4-1=1, bounded_h=min(1,1)-0=1, water+=1 → total=2
         1==h[4]=1, not strictly greater, push 6.  stack=[3,4,6]
i=7 h=3: 3>h[6]=1 → pop 6 (bottom=6,h=1)
           left=4, width=7-4-1=2, bounded_h=min(1,3)-1=0, water+=0
         3>h[4]=1 → pop 4 (bottom=4,h=1)
           left=3, width=7-3-1=3, bounded_h=min(2,3)-1=1, water+=3 → total=5
         3>h[3]=2 → pop 3 (bottom=3,h=2)
           stack empty → break
         push 7.                     stack=[7]
i=8 h=2: 2<3, push 8.               stack=[7,8]
i=9 h=1: 1<2, push 9.               stack=[7,8,9]
i=10 h=2: 2>h[9]=1 → pop 9 (bottom=9,h=1)
            left=8, width=10-8-1=1, bounded_h=min(2,2)-1=1, water+=1 → total=6
          2==h[8]=2, not greater, push 10.   stack=[7,8,10]
i=11 h=1: 1<2, push 11.

End: remaining stack, no more water fills.
Total = 6  ✓
```

Key formula at each pop: `bounded_height = min(height[left], height[right]) - height[bottom]`; `water += width * bounded_height`.

**4. Edge cases**
- Fewer than 3 elements: no trapping possible, return 0
- Monotonically increasing or decreasing: no troughs, return 0
- All same height: no troughs, return 0
- Two tall bars with a valley: single trough, classic case

**5. Final code**
```python
def trapping_rain_water_stack(height: list[int]) -> int:
    stack: list[int] = []
    water = 0
    for i, h in enumerate(height):
        while stack and height[stack[-1]] < h:
            bottom = stack.pop()
            if not stack:
                break                  # no left wall
            left = stack[-1]
            width = i - left - 1
            bounded_height = min(height[left], h) - height[bottom]
            water += width * bounded_height
        stack.append(i)
    return water
```

**Complexity:** Time O(n), Space O(n)

**6. Follow-up questions**
- Two-pointer approach vs. stack? Two-pointer: O(1) space, scans left and right simultaneously, fills column by column. Stack: O(n) space, fills layer by layer (horizontal slices). Both O(n) time — two-pointer is preferred in interviews for its space efficiency.
- Which approach is easier to derive under pressure? Two-pointer if you know the invariant; stack approach is more systematic if you already know the monotonic stack pattern.
- 3D version (LC #407 Trapping Rain Water II)? Use a min-heap (priority queue) with BFS from the boundary inward — the stack approach does not extend to 2D.
- What is the difference between this and LC #84? In LC #84, we maximize area of a solid rectangle. Here we maximize/sum water filled between bars. The stack direction is opposite: LC #84 uses an increasing stack (pops when shorter arrives); here we use a decreasing stack (pops when taller arrives).
