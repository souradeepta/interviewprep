# Prefix Sum — Problems

## Easy

---

### Problem 1: Range Sum Query — Immutable  [Easy]  [LC #303]

**1. Clarifying questions to ask**
- Multiple queries on the same array? Yes — that is exactly the point; precompute once and answer each query in O(1).
- The array is immutable (no updates)? Yes — if updates were needed, use a Fenwick tree or segment tree.
- Indices `left` and `right` are inclusive, 0-based? Yes per LC.
- Is the array guaranteed non-empty? Yes.

**2. Brute force**
For each `sumRange(left, right)` call, iterate from `left` to `right` and sum. Time O(n) per query, O(n·q) for q queries. Acceptable for a single query; unacceptable for many queries on large arrays.

**3. Optimization**
Precompute a prefix sum array of size `n+1` in the constructor. Each query becomes a single subtraction.

```
nums = [-2, 0, 3, -5, 2, -1]
        0   1  2   3  4   5

Build prefix (size 7):
prefix[0] = 0
prefix[1] = 0 + (-2) = -2
prefix[2] = -2 + 0  = -2
prefix[3] = -2 + 3  = 1
prefix[4] = 1 + (-5) = -4
prefix[5] = -4 + 2  = -2
prefix[6] = -2 + (-1) = -3

prefix = [0, -2, -2, 1, -4, -2, -3]

Queries:
  sumRange(0, 2) = prefix[3] - prefix[0] = 1 - 0  = 1   ✓  (-2+0+3=1)
  sumRange(2, 5) = prefix[6] - prefix[2] = -3-(-2) = -1  ✓  (3-5+2-1=-1)
  sumRange(0, 5) = prefix[6] - prefix[0] = -3 - 0 = -3   ✓
```

**4. Edge cases**
- `left == right`: single element query → `prefix[left+1] - prefix[left] = nums[left]`
- `left == 0`: `prefix[right+1] - prefix[0] = prefix[right+1]` — the zero sentinel makes this work without special-casing
- Large array, many queries: O(n) build, O(1) per query — no matter how many queries, total is O(n + q)
- Negative numbers: prefix sum handles negatives identically to positives

**5. Final code**
```python
class NumArray:
    def __init__(self, nums: list[int]):
        self.prefix = [0] * (len(nums) + 1)
        for i, n in enumerate(nums):
            self.prefix[i + 1] = self.prefix[i] + n

    def sumRange(self, left: int, right: int) -> int:
        return self.prefix[right + 1] - self.prefix[left]
```

**Complexity:** `__init__` O(n) time and space; `sumRange` O(1) time, O(1) space

**6. Follow-up questions**
- What if the array were mutable (point updates)? Prefix sum recomputation after each update is O(n). Use a Fenwick tree (Binary Indexed Tree) for O(log n) updates and O(log n) queries.
- What if you need range sum on a 2D matrix? See LC #304 — extend to a 2D prefix sum (Problem 5 in this set).
- Can you compute this without extra space? Not while maintaining O(1) query time — the prefix array is necessary for O(1) lookups.

---

## Medium

---

### Problem 2: Subarray Sum Equals K  [Medium]  [LC #560]

**1. Clarifying questions to ask**
- Count the number of subarrays (not find them)? Yes — return a count.
- Can the array contain negative numbers? Yes — this rules out sliding window, which requires monotone sums.
- Can k be zero or negative? Yes.
- Can there be duplicate subarrays (same elements, different positions)? Yes — count them separately.

**2. Brute force**
For every pair `(i, j)`, compute `sum(nums[i..j])`. If it equals `k`, increment count. Time O(n²) with running sum, O(n³) naively. Space O(1).

**3. Optimization**
Running prefix sum + hash map. At each index `j`, we have `prefix_sum = nums[0] + ... + nums[j]`. We want to count how many previous indices `i` have `prefix_sum[i] = prefix_sum[j] - k`. The hash map stores the frequency of each prefix sum seen so far.

```
nums = [1, 2, 3],  k = 3

freq = {0: 1}   ← initial: empty prefix sum of 0 appears once

i=0 val=1: prefix_sum=1
           look up freq[1 - 3] = freq[-2] = 0 → count += 0
           freq = {0:1, 1:1}

i=1 val=2: prefix_sum=3
           look up freq[3 - 3] = freq[0] = 1 → count += 1  (subarray [0..1] = [1,2])
           freq = {0:1, 1:1, 3:1}

i=2 val=3: prefix_sum=6
           look up freq[6 - 3] = freq[3] = 1 → count += 1  (subarray [2..2] = [3])
           freq = {0:1, 1:1, 3:1, 6:1}

count = 2  ✓  ([1,2] and [3])
```

Why initialize `freq = {0: 1}`? When `prefix_sum == k` (the subarray starts at index 0), we need `freq[prefix_sum - k] = freq[0] = 1`. Without this, subarrays starting at index 0 are missed.

**4. Edge cases**
- `k == 0`: subarrays that sum to zero; the `{0:1}` initialization still works correctly
- All negatives: sliding window fails; prefix sum + hash map works correctly
- Single element equals `k`: one subarray found
- `nums = [1]`, `k = 0`: prefix_sum=1, look up freq[-1]=0 → count=0
- Duplicate prefix sums (multiple subarrays with same sum): the hash map counts all of them

**5. Final code**
```python
def subarray_sum_equals_k(nums: list[int], k: int) -> int:
    count = 0
    prefix_sum = 0
    freq: dict[int, int] = {0: 1}
    for num in nums:
        prefix_sum += num
        count += freq.get(prefix_sum - k, 0)
        freq[prefix_sum] = freq.get(prefix_sum, 0) + 1
    return count
```

**Complexity:** Time O(n), Space O(n) for the hash map

**6. Follow-up questions**
- Why can't we use sliding window? Sliding window works only when array values are non-negative (sum is monotone). With negatives, expanding the window can decrease the sum; you can't decide whether to shrink or expand based solely on whether the sum exceeds k.
- What if we want the actual subarrays, not the count? Store the prefix sum → index mapping; when a match is found, reconstruct the range `[prev_index+1 .. current_index]`.
- LC #523 (Continuous Subarray Sum)? Same idea but with `prefix_sum % k` — see Problem 4 in this set.
- What if you want the longest subarray with sum k? See Problem 6 in this set — use first-occurrence map instead of frequency map.

---

### Problem 3: Product of Array Except Self  [Medium]  [LC #238]

**1. Clarifying questions to ask**
- Return array where `result[i]` = product of all elements except `nums[i]`? Yes.
- No division allowed? Yes — this is the key constraint.
- Can the array contain zeros? Yes — the algorithm handles zeros.
- Output guaranteed to fit in 32-bit integer? Yes per LC.

**2. Brute force**
For each index `i`, multiply all other elements. Time O(n²), Space O(1). Division shortcut (total product ÷ nums[i]) fails with zeros and is not allowed by the problem.

**3. Optimization — Prefix Product + Suffix Product**
Two passes: left and right. For each index `i`:
- `left_product[i]` = product of all elements to the LEFT of `i`
- `right_product[i]` = product of all elements to the RIGHT of `i`
- `result[i] = left_product[i] * right_product[i]`

Space-optimize by computing left products into the result array, then multiplying in right products in a second pass using a single running variable.

```
nums = [1, 2, 3, 4]

Left pass (result[i] = product of nums[0..i-1]):
result[0] = 1             (no elements to the left)
result[1] = 1             (nums[0] = 1)
result[2] = 1*2 = 2       (nums[0]*nums[1])
result[3] = 1*2*3 = 6     (nums[0]*nums[1]*nums[2])

After left pass: result = [1, 1, 2, 6]

Right pass (multiply result[i] by product of nums[i+1..n-1]):
right_product = 1

i=3: result[3] *= 1 = 6,  right_product = 1*4 = 4
i=2: result[2] *= 4 = 8,  right_product = 4*3 = 12
i=1: result[1] *= 12 = 12, right_product = 12*2 = 24
i=0: result[0] *= 24 = 24, right_product = 24*1 = 24

result = [24, 12, 8, 6]  ✓
```

**4. Edge cases**
- Array contains one zero: the zero index gets `product_of_all_others` (nonzero); every other index gets 0 (because the zero is included in their product)
- Array contains two or more zeros: every position gets 0
- Single element: `result[0]` = 1 (empty product to both left and right)
- Negative numbers: handled identically — only signs matter, not values
- All ones: result is all ones

**5. Final code**
```python
def product_of_array_except_self(nums: list[int]) -> list[int]:
    n = len(nums)
    result = [1] * n
    left_product = 1
    for i in range(n):
        result[i] = left_product
        left_product *= nums[i]
    right_product = 1
    for i in range(n - 1, -1, -1):
        result[i] *= right_product
        right_product *= nums[i]
    return result
```

**Complexity:** Time O(n), Space O(1) excluding the output array

**6. Follow-up questions**
- Why does this work without division? Each `result[i]` is the product of all elements except `nums[i]`. Left pass computes the "prefix product up to but not including i"; right pass multiplies in the "suffix product from i+1 onward". No division needed.
- What if division were allowed? Compute total product, divide by `nums[i]` for each index. Handle zero: if one zero exists, only that position gets a nonzero result. Two or more zeros: all positions get zero.
- Can we do this in one pass? Not simply — you need both left and right context simultaneously. The two-pass approach is optimal.
- What if overflow is a concern? Use Python (arbitrary precision) or Java `long` / `BigInteger` as needed.

---

### Problem 4: Continuous Subarray Sum  [Medium]  [LC #523]

**1. Clarifying questions to ask**
- Subarray length must be at least 2? Yes — a single element does not count.
- Return boolean — does any such subarray exist? Yes.
- `k` is a positive integer? Yes per LC.
- What does "multiple of k" mean? `sum % k == 0`, including k itself.

**2. Brute force**
Check all subarrays of length ≥ 2. Compute their sum and check divisibility. Time O(n²), Space O(1).

**3. Optimization**
Prefix sum modulo k + hash map. Key insight: if `prefix[j] % k == prefix[i] % k` and `j - i >= 2`, then `sum(i+1..j) = prefix[j] - prefix[i]` is divisible by k.

Store the first index where each remainder is seen. If the same remainder appears again at index `j >= first_index + 2`, the subarray is valid.

```
nums = [23, 2, 4, 6, 7],  k = 6

remainder_map = {0: -1}  ← sentinel: remainder 0 at index -1 (empty prefix)

i=0 val=23: prefix_sum=23, rem=23%6=5
            5 not in map → remainder_map[5] = 0
            map = {0:-1, 5:0}

i=1 val=2:  prefix_sum=25, rem=25%6=1
            1 not in map → remainder_map[1] = 1
            map = {0:-1, 5:0, 1:1}

i=2 val=4:  prefix_sum=29, rem=29%6=5
            5 in map at index 0 → length = 2-0 = 2 >= 2 → return True

Subarray: nums[1..2] = [2, 4], sum=6, 6%6=0  ✓
```

Use first-occurrence (do NOT update the map if a remainder is already present). This ensures the maximum possible subarray length is considered.

**4. Edge cases**
- No valid subarray: return False
- Entire array sums to a multiple of k: subarray is the whole array (length n ≥ 2 if n ≥ 2)
- `nums = [0, 0]`, `k = 1`: sum=0, 0%1=0 → valid (length 2)
- `nums = [5, 0, 0, 0]`, `k = 3`: `[0, 0, 0]` sum=0 is valid
- Large k (k > sum of array): no valid subarray if no prefix sum difference is divisible by k
- First two elements sum to k: should return True — the `{0: -1}` sentinel handles this: at i=1, `prefix_sum % k == 0`, look up 0 → found at -1, length = 1-(-1) = 2 ≥ 2 → True

**5. Final code**
```python
def check_subarray_sum(nums: list[int], k: int) -> bool:
    remainder_map: dict[int, int] = {0: -1}   # remainder → first index seen
    prefix_sum = 0
    for i, num in enumerate(nums):
        prefix_sum += num
        rem = prefix_sum % k
        if rem in remainder_map:
            if i - remainder_map[rem] >= 2:    # length at least 2
                return True
        else:
            remainder_map[rem] = i             # first occurrence only
    return False
```

**Complexity:** Time O(n), Space O(min(n, k)) — at most k distinct remainders

**6. Follow-up questions**
- Why not update the map on repeated remainders? We want the earliest occurrence of each remainder to maximize the subarray length. Updating would shorten the potential length and could cause us to miss valid subarrays.
- LC #560 vs. LC #523? LC #560 counts exact sum = k; LC #523 checks divisibility. Same framework: prefix sum + hash map. Key difference: here the key is `prefix_sum % k`, not `prefix_sum` itself.
- What if the subarray can be length 1? Remove the `>= 2` check. The sentinel `{0: -1}` still handles zero-sum subarrays starting at index 0.
- What if k can be 0? Division by zero — add a guard: if `k == 0`, check if any subarray of length ≥ 2 has sum 0 (use a separate set-based approach).

---

### Problem 5: Range Sum Query 2D  [Medium]  [LC #304]

**1. Clarifying questions to ask**
- Multiple queries after one build? Yes — same motivation as LC #303, but 2D.
- Matrix is immutable? Yes — no updates.
- Queries use inclusive coordinates `(row1, col1)` to `(row2, col2)`? Yes, 0-indexed.
- Can values be negative? Yes.

**2. Brute force**
For each query, iterate over the rectangle and sum all elements. Time O(m·n) per query. Unacceptable for many queries on large matrices.

**3. Optimization — 2D Prefix Sum**
Build a 2D prefix array of size `(m+1) × (n+1)` where `prefix[i][j]` = sum of all elements in the rectangle from `(0,0)` to `(i-1, j-1)`.

Build formula (inclusion-exclusion):
```
prefix[i][j] = matrix[i-1][j-1]
             + prefix[i-1][j]
             + prefix[i][j-1]
             - prefix[i-1][j-1]
```

Query formula for rectangle `(r1, c1)` to `(r2, c2)`:
```
sum = prefix[r2+1][c2+1]
    - prefix[r1][c2+1]
    - prefix[r2+1][c1]
    + prefix[r1][c1]
```

```
matrix:        prefix (size 4×4 for 3×3 matrix):
  3  0  1        0   0   0   0
  5  6  3   →    0   3   3   4
  1  2  0        0   8  14  18
                 0   9  17  21

Query (1,1) to (2,2) = matrix rows 1-2, cols 1-2:
  = prefix[3][3] - prefix[1][3] - prefix[3][1] + prefix[1][1]
  = 21          -  4            -  9            +  3
  = 11

Verify: matrix[1][1]+matrix[1][2]+matrix[2][1]+matrix[2][2]
      = 6 + 3 + 2 + 0 = 11  ✓
```

Inclusion-exclusion visual:
```
prefix[r2+1][c2+1]  = full rectangle from (0,0)
- prefix[r1][c2+1]  = strip above the query rectangle
- prefix[r2+1][c1]  = strip to the left of the query rectangle
+ prefix[r1][c1]    = add back corner (subtracted twice)
```

**4. Edge cases**
- Single cell query `(r, c, r, c)`: formula still works — all terms collapse to `matrix[r][c]`
- Entire matrix query: `prefix[m][n] - 0 - 0 + 0 = total sum`
- Row or column with all zeros: no special handling needed
- Single row or column matrix: degenerates to 1D prefix sum

**5. Final code**
```python
class NumMatrix:
    def __init__(self, matrix: list[list[int]]):
        m, n = len(matrix), len(matrix[0])
        self.prefix = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                self.prefix[i][j] = (matrix[i-1][j-1]
                                    + self.prefix[i-1][j]
                                    + self.prefix[i][j-1]
                                    - self.prefix[i-1][j-1])

    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
        return (self.prefix[row2+1][col2+1]
                - self.prefix[row1][col2+1]
                - self.prefix[row2+1][col1]
                + self.prefix[row1][col1])
```

**Complexity:** `__init__` O(m·n) time and space; `sumRegion` O(1) time

**6. Follow-up questions**
- Memory optimization? The prefix matrix cannot be eliminated if queries must be O(1). However, you can compute it in-place by treating the matrix itself as the prefix array (mutating the input).
- What if there are updates? Use a 2D Fenwick tree (Binary Indexed Tree) for O(log m · log n) updates and queries.
- Can you derive the formula without memorizing it? Think inclusion-exclusion: you want the area of the rectangle. The full prefix covers too much — subtract the strip above and the strip to the left. But the top-left corner was subtracted twice, so add it back.
- Extension to 3D? Same pattern — inclusion-exclusion with 8 terms (±prefix at each corner of the 3D box).

---

### Problem 6: Maximum Size Subarray Sum Equals k  [Medium]  [LC #325]

**1. Clarifying questions to ask**
- Find the length of the longest subarray with sum exactly k (not just any subarray)? Yes.
- Array can contain negatives? Yes — this rules out binary search on prefix sums (not monotone).
- Return 0 if no such subarray? Yes.
- Duplicate prefix sums possible? Yes — use first-occurrence map to maximize length.

**2. Brute force**
All pairs `(i, j)`, compute sum, track maximum length where sum == k. Time O(n²), Space O(1).

**3. Optimization — Prefix Sum + First-Occurrence Hash Map**
Track running prefix sum. Use a hash map to store the FIRST time each prefix sum is seen. When `prefix_sum - k` is in the map, the subarray from `(first_occurrence + 1)` to the current index has sum `k`. Maximize the length.

The key difference from LC #560: use FIRST occurrence (for maximum length), not frequency count (for total count).

```
nums = [1, -1, 5, -2, 3],  k = 3

first_seen = {0: -1}  ← prefix sum 0 first seen at index -1

i=0 val=1:  prefix=1
            look up 1-3=-2: not in map
            first_seen[1] = 0
            map = {0:-1, 1:0}

i=1 val=-1: prefix=0
            look up 0-3=-3: not in map
            0 already in map (index -1), skip update
            map = {0:-1, 1:0}

i=2 val=5:  prefix=5
            look up 5-3=2: not in map
            first_seen[5] = 2
            map = {0:-1, 1:0, 5:2}

i=3 val=-2: prefix=3
            look up 3-3=0: in map at index -1
            length = 3-(-1) = 4   ← candidate
            first_seen[3] = 3
            map = {0:-1, 1:0, 5:2, 3:3}

i=4 val=3:  prefix=6
            look up 6-3=3: in map at index 3
            length = 4-3 = 1   (shorter, no update)
            first_seen[6] = 4

max_len = 4  (subarray nums[0..3] = [1,-1,5,-2], sum=3)  ✓
```

**4. Edge cases**
- No valid subarray: return 0
- Entire array sums to k: `prefix_sum - k == 0`, found in map at -1, length = n
- k = 0: subarrays that sum to zero; prefix sums that repeat indicate zero-sum subarrays
- First occurrence at index -1 (the sentinel): handles subarrays starting at index 0
- Duplicate prefix sums: DO NOT update the map — keep the first occurrence to ensure maximum length

**5. Final code**
```python
def max_subarray_len(nums: list[int], k: int) -> int:
    first_seen: dict[int, int] = {0: -1}   # prefix_sum → first index seen
    prefix_sum = 0
    max_len = 0
    for i, num in enumerate(nums):
        prefix_sum += num
        if prefix_sum - k in first_seen:
            max_len = max(max_len, i - first_seen[prefix_sum - k])
        if prefix_sum not in first_seen:   # first occurrence only
            first_seen[prefix_sum] = i
    return max_len
```

**Complexity:** Time O(n), Space O(n) for the hash map

**6. Follow-up questions**
- Why store first occurrence here but frequency in LC #560? LC #560 counts subarrays — every occurrence of the needed prefix sum contributes a separate subarray, so we count all. LC #325 maximizes length — the earliest occurrence of the prefix sum gives the longest subarray, so we keep only the first.
- What if the array is non-negative? Prefix sum is monotone, so binary search works: O(n log n). But the hash map approach also works and is O(n) — prefer it.
- LC #525 (Contiguous Array, equal 0s and 1s)? Same algorithm: replace each `0` with `-1`, then find the longest subarray with sum 0. The first-occurrence map is identical.
- What if you want the maximum sum (not length)? That is Kadane's algorithm — a DP problem, not a prefix sum problem.
