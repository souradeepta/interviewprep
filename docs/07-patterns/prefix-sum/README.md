# Prefix Sum Pattern

**Level:** L3-L4
**Time to read:** ~15 min
**Prerequisites:** [Arrays](../../06-data-structures/arrays/README.md)
**Related:** [Sliding Window](../sliding-window/README.md)

## Quick Summary

Precompute a cumulative sum array so that any contiguous range sum answers in O(1) instead of O(n). Build once in O(n), query any `sum[i..j]` as `prefix[j+1] - prefix[i]`. Key signal: "sum of subarray", "range sum query", "subarray sum equals k", "prefix", "2D array sum".

## When to Use It

Signal phrases that strongly indicate prefix sum:

- "Sum of elements from index i to j"
- "Subarray sum equals k"
- "Count subarrays with sum equal to / divisible by k"
- "Find pivot index (left sum == right sum)"
- "Range sum query on immutable array"
- "2D matrix range sum"
- "Maximum size subarray with given sum"

**Not a fit when:** the array is mutable (use Fenwick tree / segment tree for dynamic updates), you need non-contiguous subsequences (use DP), or the condition involves products (use prefix products, a separate pattern variant).

## How It Works

### 1D Prefix Sum

Build a prefix array of size `n+1` where `prefix[0] = 0` and `prefix[i] = prefix[i-1] + nums[i-1]`.

```
nums   =  [3, -2,  5,  1, -4,  6]
index      0   1   2   3   4   5

Build prefix (size n+1=7):

prefix[0] = 0
prefix[1] = 0 + nums[0] = 3
prefix[2] = 3 + nums[1] = 1
prefix[3] = 1 + nums[2] = 6
prefix[4] = 6 + nums[3] = 7
prefix[5] = 7 + nums[4] = 3
prefix[6] = 3 + nums[5] = 9

prefix = [0, 3, 1, 6, 7, 3, 9]
```

Range sum query `sum(nums[i..j])` (inclusive, 0-indexed):

```
sum(nums[2..4]) = prefix[5] - prefix[2]
               = 3 - 1
               = 2

Verification: nums[2]+nums[3]+nums[4] = 5+1+(-4) = 2  ✓

Formula: sum(i, j) = prefix[j+1] - prefix[i]
                           ↑             ↑
                     right exclusive   left inclusive offset
```

The `+1` offset in `prefix[j+1]` and the `prefix[0] = 0` sentinel together eliminate all off-by-one edge cases.

### Off-by-One Reference

```
nums   index:   0    1    2    3    4
                v    v    v    v    v
nums        = [ A    B    C    D    E ]
prefix      = [ 0    A   A+B A+B+C ...  ]  ← size n+1
prefix index:   0    1    2    3    4    5

sum(nums[1..3]) = prefix[4] - prefix[1]
               = (A+B+C+D) - A
               = B+C+D  ✓
```

### Prefix Sum + Hash Map (Subarray Sum = k)

When you need to COUNT subarrays with a target sum, combine prefix sum with a hash map.

Key insight: `sum(i..j) = k` iff `prefix[j] - prefix[i-1] = k` iff `prefix[j] - k = prefix[i-1]`.

So for each `j`, look up how many previous prefix sums equal `prefix[j] - k`.

```
nums = [1, 1, 1],  k = 2

prefix running sum + freq map:

Start: freq = {0: 1}   ← the "empty prefix" prefix[0]=0

i=0 val=1: prefix_sum = 1
           look up prefix_sum - k = 1 - 2 = -1  → not in freq, count += 0
           freq = {0:1, 1:1}

i=1 val=1: prefix_sum = 2
           look up 2 - 2 = 0 → freq[0]=1, count += 1  (subarray [0..1])
           freq = {0:1, 1:1, 2:1}

i=2 val=1: prefix_sum = 3
           look up 3 - 2 = 1 → freq[1]=1, count += 1  (subarray [1..2])
           freq = {0:1, 1:1, 2:1, 3:1}

count = 2  ✓
```

The `{0: 1}` initialization handles subarrays that start from index 0 (prefix difference includes the zero prefix).

### 2D Prefix Sum

Build a 2D prefix sum matrix for O(1) rectangle queries.

```
matrix:          prefix (size (m+1) x (n+1)):
  1  2  3          0  0  0  0
  4  5  6    →     0  1  3  6
  7  8  9          0  5 12 21
                   0 12 27 45

prefix[i][j] = matrix[i-1][j-1]
             + prefix[i-1][j]    (row above)
             + prefix[i][j-1]    (column left)
             - prefix[i-1][j-1]  (subtract double-counted corner)

Rectangle sum from (r1,c1) to (r2,c2):
  = prefix[r2+1][c2+1]
  - prefix[r1][c2+1]
  - prefix[r2+1][c1]
  + prefix[r1][c1]

Example: sum of top-left 2x2 = matrix[0..1][0..1]
  = prefix[2][2] - prefix[0][2] - prefix[2][0] + prefix[0][0]
  = 12 - 0 - 0 + 0 = 12
  Verify: 1+2+4+5 = 12  ✓
```

The 2D formula is an inclusion-exclusion: add the big rectangle, subtract the two "strips" above and to the left, add back the corner (subtracted twice).

## Decision Tree

```
Does the problem involve a SUM over a contiguous subarray or range?
├── YES → Is the array immutable (no updates)?
│         ├── YES → Is it 1D?
│         │         ├── Count subarrays with sum = k → Prefix sum + hash map
│         │         ├── Range sum query → Build prefix array, O(1) query
│         │         └── Find subarray / check divisibility → Prefix sum + mod
│         └── Is it 2D?
│                   └── Rectangle sum queries → 2D prefix sum
└── NO  → Does it involve PRODUCT instead of sum?
          ├── YES → Prefix product + suffix product (LC #238 pattern)
          └── NO  → Not a prefix sum problem
                    ├── Dynamic range sum (with updates) → Fenwick tree / BIT
                    └── Max subarray sum → Kadane's algorithm (DP)
```

## Complexity

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| Build 1D prefix array | O(n) | O(n) | One pass, size n+1 |
| Range sum query | O(1) | O(1) | After O(n) build |
| Subarray sum = k (count) | O(n) | O(n) | One pass + hash map |
| Build 2D prefix matrix | O(m·n) | O(m·n) | Size (m+1)×(n+1) |
| 2D rectangle query | O(1) | O(1) | After O(m·n) build |
| Prefix product (no division) | O(n) | O(n) | Two passes: left and right |

## Common Mistakes

- **Off-by-one: prefix array size.** Use size `n+1` with `prefix[0] = 0`, not size `n`. The zero-sentinel eliminates the edge case "subarray starts at index 0".
- **Off-by-one: query formula.** `sum(i, j) = prefix[j+1] - prefix[i]`, not `prefix[j] - prefix[i-1]` (though equivalent, the `j+1` form avoids `-1` indexing).
- **Not initializing `{0: 1}` in the hash map.** The count `{0: 1}` means "there is one way to have an empty prefix with sum 0". Without it, subarrays starting at index 0 (i.e., `prefix[j] - k == 0`) are missed.
- **Confusing prefix sum with prefix product.** For products, you cannot use simple subtraction; instead use left-product and right-product arrays (LC #238 pattern).
- **2D formula: forgetting the `+prefix[r1][c1]` corner term.** Omitting it double-subtracts the top-left corner — a subtle off-by-one that passes most small test cases but fails on larger ones.
- **Modifying the input array (LC #304).** Some solutions use in-place prefix sums in the matrix — this mutates the input. Use a separate prefix matrix.

## Run the Code

```bash
# From repo root
pytest tests/patterns/test_prefix_sum.py -v
```

**Implementation:** [`python/patterns/prefix_sum.py`](../../../python/patterns/prefix_sum.py)
**Tests:** [`tests/patterns/test_prefix_sum.py`](../../../tests/patterns/test_prefix_sum.py)

## Problems

6 problems with full think-process walk-throughs: [problems.md](problems.md)

| # | Problem | Difficulty | LeetCode | Variant |
|---|---------|-----------|---------|---------|
| 1 | Range Sum Query — Immutable | Easy | #303 | Basic prefix array, class-based |
| 2 | Subarray Sum Equals K | Medium | #560 | Prefix sum + hash map counting |
| 3 | Product of Array Except Self | Medium | #238 | Prefix product + suffix product |
| 4 | Continuous Subarray Sum | Medium | #523 | Prefix sum mod k + hash map |
| 5 | Range Sum Query 2D | Medium | #304 | 2D prefix sum, inclusion-exclusion |
| 6 | Maximum Size Subarray Sum Equals k | Medium | #325 | Prefix sum + first-occurrence hash map |
