# Searching Algorithms

Nine algorithms for locating elements in sorted arrays, rotated arrays, and unsorted sequences — ranging from the foundational binary search and its variants to specialized techniques like exponential search and interpolation search, all running in O(log n) or better.

---

## Algorithms Covered

| Algorithm                | Best   | Average      | Worst    | Space      |
|--------------------------|:------:|:------------:|:--------:|:----------:|
| Binary Search (iterative)| O(1)   | O(log n)     | O(log n) | O(1)       |
| Binary Search (recursive)| O(1)   | O(log n)     | O(log n) | O(log n)   |
| Binary Search First      | O(1)   | O(log n)     | O(log n) | O(1)       |
| Binary Search Last       | O(1)   | O(log n)     | O(log n) | O(1)       |
| Search Rotated Array     | O(1)   | O(log n)     | O(log n) | O(1)       |
| Find Peak Element        | O(1)   | O(log n)     | O(log n) | O(1)       |
| Ternary Search           | O(1)   | O(log₃ n)    | O(log n) | O(1)       |
| Exponential Search       | O(1)   | O(log n)     | O(log n) | O(1)       |
| Interpolation Search     | O(1)   | O(log log n) | O(n)     | O(1)       |

---

## Binary Search (Iterative)

Maintain a `[lo, hi]` search window over a sorted array. Each iteration computes the midpoint and compares `arr[mid]` to the target, halving the window by moving `lo` or `hi`. The window closes when `lo > hi` (target not found) or `arr[mid] == target` (found). Iterative version uses O(1) space.

```
arr = [1, 3, 5, 7, 9, 11, 13, 15]   target = 7
idx:   0  1  2  3  4   5   6   7

lo=0, hi=7 → mid = 0 + (7-0)//2 = 3
  arr[3] = 7 == target → return 3

---

target = 11
lo=0, hi=7 → mid=3, arr[3]=7  < 11 → lo = 4
lo=4, hi=7 → mid=5, arr[5]=11 == 11 → return 5

---

target = 6 (not in array)
lo=0, hi=7 → mid=3, arr[3]=7  > 6  → hi = 2
lo=0, hi=2 → mid=1, arr[1]=3  < 6  → lo = 2
lo=2, hi=2 → mid=2, arr[2]=5  < 6  → lo = 3
lo=3 > hi=2 → return -1
```

**Key insight:** Use `mid = lo + (hi - lo) // 2` rather than `(lo + hi) // 2` to avoid integer overflow in languages with fixed-width integers (Java, C++). The loop invariant is: if target exists, it is in `arr[lo..hi]`.

**When to use:** Default search on any sorted array. Prefer iterative over recursive (O(1) vs O(log n) space, no stack overflow risk).

---

## Binary Search (Recursive)

Functionally identical to the iterative version but expresses the halving via recursive calls. Each call reduces the problem to one sub-range and returns when the base case (empty range) or a match is found. Consumes O(log n) call-stack space.

```
arr = [2, 4, 6, 8, 10, 12]   target = 10

Call 1: lo=0, hi=5 → mid=2, arr[2]=6 < 10
  → recurse(lo=3, hi=5)

Call 2: lo=3, hi=5 → mid=4, arr[4]=10 == 10
  → return 4

Unwind: Call 1 returns 4
Result: 4

---

target = 5 (not in array)
Call 1: lo=0, hi=5 → mid=2, arr[2]=6 > 5
  → recurse(lo=0, hi=1)
Call 2: lo=0, hi=1 → mid=0, arr[0]=2 < 5
  → recurse(lo=1, hi=1)
Call 3: lo=1, hi=1 → mid=1, arr[1]=4 < 5
  → recurse(lo=2, hi=1)
Call 4: lo=2 > hi=1 → return -1
```

**Key insight:** The recurrence T(n) = T(n/2) + O(1) solves to O(log n) by the Master Theorem. Python's default recursion limit is 1000, so the iterative version is safer for large arrays (n > 2^1000 is unreachable, but tail recursion is not optimized in CPython).

**When to use:** When the recursive formulation is clearer or when extending the algorithm with extra per-call state (e.g., tracking the search path). For plain lookup, prefer the iterative version.

---

## Binary Search — First Occurrence

Finds the leftmost index where `target` appears in a sorted array that may contain duplicates. When a match is found at `mid`, the candidate is recorded and the search continues left (`hi = mid - 1`) rather than returning immediately.

```
arr = [1, 2, 2, 2, 3, 3, 4, 5]   target = 2
idx:   0  1  2  3  4  5  6  7

lo=0, hi=7 → mid=3, arr[3]=2 == target
  result=3, hi=2  (keep searching left)

lo=0, hi=2 → mid=1, arr[1]=2 == target
  result=1, hi=0  (keep searching left)

lo=0, hi=0 → mid=0, arr[0]=1 < target
  lo=1

lo=1 > hi=0 → loop ends

Return result=1  ← first occurrence
```

**Key insight:** The `result` variable acts as a running candidate. Every time `arr[mid] == target`, we update the candidate and search left. This is equivalent to finding the leftmost position where `arr[pos] >= target` (lower-bound), which also solves the insertion-point problem.

**When to use:** Counting occurrences (`last - first + 1`), range queries on sorted arrays, lower-bound computation. LeetCode: "Find First and Last Position of Element in Sorted Array" (LC 34).

---

## Binary Search — Last Occurrence

Mirror of First Occurrence. When a match is found at `mid`, record it and continue right (`lo = mid + 1`) to find a later occurrence.

```
arr = [1, 2, 2, 2, 3, 3, 4, 5]   target = 3
idx:   0  1  2  3  4  5  6  7

lo=0, hi=7 → mid=3, arr[3]=2 < target → lo=4

lo=4, hi=7 → mid=5, arr[5]=3 == target
  result=5, lo=6  (keep searching right)

lo=6, hi=7 → mid=6, arr[6]=4 > target → hi=5

lo=6 > hi=5 → loop ends

Return result=5  ← last occurrence of 3

Count of 3: last(3) - first(3) + 1 = 5 - 4 + 1 = 2  ✓
```

**Key insight:** Together, First and Last Occurrence give you `count = last - first + 1` and also implement `lower_bound` / `upper_bound` from C++ STL. Upper-bound variant: replace `arr[mid] == target` with `arr[mid] > target` and always continue left.

**When to use:** Frequency counting in sorted arrays, implementing C++-style `upper_bound`, range deletion, LeetCode 34.

---

## Search in Rotated Sorted Array

A sorted array has been rotated at an unknown pivot (e.g., `[0,1,2,4,5,6,7]` becomes `[4,5,6,7,0,1,2]`). At every midpoint, at least one half of the array is guaranteed to be sorted. Determine which half is sorted, check whether the target falls within it, and discard the other half.

```
arr = [4, 5, 6, 7, 0, 1, 2]   target = 0
idx:   0  1  2  3  4  5  6

lo=0, hi=6 → mid=3, arr[3]=7 ≠ 0
  arr[lo]=4 ≤ arr[mid]=7 → left half [4..7] is sorted
  target=0 NOT in [4..7) → search right half: lo=4

lo=4, hi=6 → mid=5, arr[5]=1 ≠ 0
  arr[lo]=0 ≤ arr[mid]=1 → left half [0..1] is sorted
  target=0 IN [0..1) → search left half: hi=4

lo=4, hi=4 → mid=4, arr[4]=0 == target → return 4

---

target = 3 (not present)
lo=0, hi=6 → mid=3, arr[3]=7 ≠ 3
  left half [4..7] sorted, 3 not in range → lo=4
lo=4, hi=6 → mid=5, arr[5]=1 ≠ 3
  left half [0..1] sorted, 3 not in range → hi=4
lo=4, hi=4 → mid=4, arr[4]=0 ≠ 3 → lo=5
lo=5 > hi=4 → return -1
```

**Key insight:** The check `arr[lo] <= arr[mid]` identifies the sorted half — not which half contains the target. Once the sorted half is identified, a simple range check `arr[lo] <= target < arr[mid]` determines where the target could be.

**When to use:** LeetCode 33 (no duplicates). With duplicates (LC 81), add a case for `arr[lo] == arr[mid] == arr[hi]` → shrink both ends → degrades to O(n) worst case.

---

## Find Peak Element

Find any index `i` such that `arr[i] > arr[i-1]` and `arr[i] > arr[i+1]` (boundaries treated as -infinity). The key observation: if `arr[mid] < arr[mid+1]`, the values are ascending, so there must be a peak to the right of `mid`. If `arr[mid] > arr[mid+1]`, there must be a peak at `mid` or to its left.

```
arr = [1, 2, 1, 3, 5]
idx:   0  1  2  3  4

lo=0, hi=4 → mid=2
  arr[2]=1 < arr[3]=3 → ascending → peak to the right → lo=3

lo=3, hi=4 → mid=3
  arr[3]=3 < arr[4]=5 → ascending → peak to the right → lo=4

lo=4, hi=4 → lo == hi → return 4
arr[4]=5 is a peak (arr[3]=3 < 5, right boundary = -inf)

---

arr = [3, 2, 1]  (strictly descending)
lo=0, hi=2 → mid=1
  arr[1]=2 > arr[2]=1 → descending → peak at mid or left → hi=1

lo=0, hi=1 → mid=0
  arr[0]=3 > arr[1]=2 → hi=0

lo=0, hi=0 → return 0  (arr[0]=3 is a peak, left boundary=-inf)
```

**Key insight:** Any local maximum qualifies; the algorithm never eliminates a half that could contain a peak. The invariant "there exists a peak in `arr[lo..hi]`" is maintained at every step because we always move toward the ascending side.

**When to use:** LeetCode 162. Any problem requiring a local maximum in O(log n). Extends to 2D matrix peak finding (LC 1901).

---

## Ternary Search

Divide the search space into three equal parts using two midpoints `mid1 = lo + (hi-lo)//3` and `mid2 = hi - (hi-lo)//3`. Check both, then eliminate one-third: if target < arr[mid1], discard the right two-thirds; if target > arr[mid2], discard the left two-thirds; otherwise search the middle third.

```
arr = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]   target = 10
idx:   0  1  2  3  4   5   6   7   8   9

lo=0, hi=9 → third=3, mid1=3, mid2=6
  arr[3]=6, arr[6]=12
  6 < 10 ≤ 12 → target in middle third [mid1+1..mid2-1]
  lo=4, hi=5

lo=4, hi=5 → third=0, mid1=4, mid2=5
  arr[4]=8, arr[5]=10
  arr[mid2]=10 == target → return 5

---

Why ternary is NOT faster than binary:
  Binary  : 1 comparison, eliminates 1/2 of range per step
            → ceil(log₂ n) steps
  Ternary : 2 comparisons, eliminates 1/3 of range per step
            → ceil(log_{3/2} n) steps ≈ 1.71 * log₂(n) steps
            → 2 * 1.71 = 3.42 comparisons per halving-equivalent

  Binary total comparisons: log₂(n)
  Ternary total comparisons: ~2.16 * log₂(n)   ← more comparisons!
```

**Key insight:** Despite splitting into thirds, ternary search makes more total comparisons than binary search because each step requires 2 comparisons to eliminate only 1/3 (vs. 1 comparison to eliminate 1/2). Ternary search is genuinely useful for finding the maximum of a unimodal function where binary search does not directly apply.

**When to use:** Finding the maximum of a unimodal function (mathematical optimization). For sorted-array lookup, binary search is strictly better.

---

## Exponential Search

Find an upper bound for the target by repeatedly doubling a bound index (1, 2, 4, 8, ...) until `arr[bound] >= target` or `bound` exceeds the array size. Then apply binary search within `[bound//2, min(bound, n-1)]`. Optimal when the target is near the start of the array.

```
arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ... , 1000]
target = 7

Phase 1 — Find range by doubling:
  bound=1: arr[1]=2 ≤ 7 → double
  bound=2: arr[2]=3 ≤ 7 → double
  bound=4: arr[4]=5 ≤ 7 → double
  bound=8: arr[8]=9 > 7 → stop

Range found: [bound//2, bound] = [4, 8]

Phase 2 — Binary search in arr[4..8]:
  lo=4, hi=8 → mid=6, arr[6]=7 == target → return 6

---

target = 1 (at index 0):
  arr[0] = 1 == target → return 0 immediately  (O(1) best case)

---

Complexity for element at index i:
  Phase 1: O(log i) doublings to reach bound >= i
  Phase 2: O(log i) binary search in range of size i
  Total  : O(log i) ≤ O(log n)
```

**Key insight:** When the element is near the beginning (small index i), exponential search takes O(log i) steps rather than O(log n). This is asymptotically better when `i << n`. It also works for unbounded/infinite sorted arrays where n is unknown — you can double indefinitely until a bound is found.

**When to use:** Sorted arrays of unknown or very large size; when the target is expected to be near the beginning; searching sorted streams or files. LC 702 (Search in a Sorted Array of Unknown Size).

---

## Interpolation Search

Instead of always probing the midpoint, estimate the probable position of the target using linear interpolation — analogous to how humans search a phone book. The probe formula is: `pos = lo + (target - arr[lo]) * (hi - lo) // (arr[hi] - arr[lo])`.

```
arr = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]   target = 70
idx:    0   1   2   3   4   5   6   7   8    9

Probe:
  pos = 0 + (70-10) * (9-0) // (100-10)
      = 0 + 60 * 9 // 90
      = 0 + 6 = 6
  arr[6] = 70 == target → return 6  ← found in ONE step!

---

Binary search for comparison:
  mid = (0+9)//2 = 4, arr[4]=50 < 70 → lo=5
  mid = (5+9)//2 = 7, arr[7]=80 > 70 → hi=6
  mid = (5+6)//2 = 5, arr[5]=60 < 70 → lo=6
  mid = (6+6)//2 = 6, arr[6]=70       → return 6   (3 steps)

---

Worst case (exponential distribution): [1, 2, 4, 8, 16, 32, 64, 128]
target = 3:
  pos = 0 + (3-1)*(7-0)//(128-1) = 0 + 2*7//127 = 0
  arr[0]=1 < 3 → lo=1
  pos = 1 + (3-2)*(7-1)//(128-2) = 1 + 6//126 = 1
  arr[1]=2 < 3 → lo=2
  ... one element per step → O(n) total
```

**Key insight:** The probe formula is accurate when values are uniformly distributed — it estimates the position by linear interpolation between `arr[lo]` and `arr[hi]`. With uniform data, each probe eliminates all but a square-root-sized sub-range, giving O(log log n) probes. With non-uniform data (e.g., exponential), each probe may only eliminate one element, giving O(n) worst case.

**When to use:** Large sorted tables of uniformly distributed integer keys (timestamps at fixed intervals, sequence numbers). Guard against division by zero when `arr[lo] == arr[hi]`. Do not use when data distribution is unknown.

---

## Choosing the Right Algorithm

| Situation                                         | Pick                      |
|---------------------------------------------------|---------------------------|
| General sorted array lookup                       | Binary Search (iterative) |
| Sorted array, find first/last of duplicate values | Binary Search First/Last  |
| Sorted array, rotated at unknown pivot            | Search Rotated Array      |
| Find any local maximum in unsorted array          | Find Peak Element         |
| Sorted array of unknown size / infinite stream    | Exponential Search        |
| Uniform distribution, very large sorted table    | Interpolation Search      |
| Find maximum of unimodal function                 | Ternary Search            |
| Teaching or exploring recursive call stacks       | Binary Search (recursive) |

**Decision rules:**
- Default to iterative binary search — O(log n), O(1) space, no edge cases.
- If duplicates matter, use First or Last occurrence, not plain binary search.
- For rotated arrays, always identify the sorted half before checking target range.
- Interpolation and ternary are theoretical curiosities unless you can guarantee the data distribution.

---

## Common Interview Questions

- **What is the loop invariant for binary search, and why must the condition be `lo <= hi` (not `lo < hi`)?** The invariant is: if target exists in the array, it is in `arr[lo..hi]`. Using `lo <= hi` ensures single-element ranges are still checked; `lo < hi` would skip them and miss targets at the last element.
- **How do you find the insertion position for a value in a sorted array?** Use the First Occurrence algorithm but replace `arr[mid] == target` with `arr[mid] >= target` — this gives the leftmost position where the value could be inserted (equivalent to `bisect_left` in Python).
- **LC 33: Search in Rotated Sorted Array. Trace through the algorithm for `arr=[4,5,6,7,0,1,2]`, `target=0`.** At each step, identify which half is sorted (compare arr[lo] to arr[mid]), then check if target falls within the sorted half.
- **Why can ternary search NOT replace binary search for sorted-array lookup?** Ternary search makes 2 comparisons per step to eliminate 1/3 of the range. Binary search makes 1 comparison per step to eliminate 1/2. Total comparisons: binary O(log₂ n), ternary O(2 * log_{3/2} n) ≈ 2.16 log₂ n — binary wins.
- **Prove that a peak element always exists in any array.** By induction or the mountain argument: if `arr[0] >= arr[1]`, index 0 is a peak. If `arr[n-1] >= arr[n-2]`, index n-1 is a peak. Otherwise, scan — anywhere the direction changes from ascending to descending is a peak.
- **When does interpolation search degrade to O(n), and how do you detect it in practice?** It degrades when data is clustered (e.g., many identical values) or follows a non-linear distribution (exponential, Pareto). In practice, cap the number of iterations or fall back to binary search after a fixed number of misses.
- **What is exponential search's advantage over binary search on an unbounded array?** For an element at position i, exponential search finds the right range in O(log i) steps, then binary searches O(log i). Total: O(log i). Binary search on the full array would need O(log n) — worse when i << n.
- **How do you count the occurrences of a value in a sorted array in O(log n)?** Use `binary_search_last(arr, val) - binary_search_first(arr, val) + 1`. If `binary_search_first` returns -1, the count is 0.
