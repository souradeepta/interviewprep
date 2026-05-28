# Two-Pointer Pattern

**Level:** L3-L4
**Time to read:** ~25 min
**Prerequisites:** [Arrays](../../06-data-structures/arrays/README.md)
**Related:** [Sliding Window](../sliding-window/README.md), [Fast/Slow Pointers](../sliding-window/README.md)

## Quick Summary

Two pointers traverse an array/string/linked list from different positions simultaneously, eliminating the need for nested loops. Reduces O(n²) brute-force solutions to O(n). Key signal phrases: "pair that sums to X", "palindrome", "remove duplicates in-place", "two arrays merge".

## When to Use It

Signal phrases that strongly indicate two-pointer:
- "Find a pair/triplet that sums to target"
- "Check if palindrome"
- "Remove duplicates in-place"
- "Merge two sorted arrays"
- "Partition an array around a pivot"
- "Find intersection of two arrays"

**Not a fit when:** the array is unsorted and you need to find non-adjacent pairs, or when you need all subsets/combinations (use backtracking instead).

## How It Works

### Variant 1: Opposite Ends (Sorted Array)

```
arr = [1, 3, 5, 7, 9, 11]
       L                R     → check arr[L] + arr[R]
          L          R        → move pointers inward
```

Start left=0, right=n-1. Move left right if sum too small, move right left if sum too big.

### Variant 2: Same Direction (Fast/Slow)

```
arr = [0, 0, 1, 1, 2, 3]
       W  R                   → W=write, R=read
             W     R          → W advances when arr[R] is new
```

Used for removing duplicates, partitioning, or cycle detection in linked lists.

### Variant 3: Two-Array Merge

```
arr1 = [1, 3, 5]    arr2 = [2, 4, 6]
        i                    j
→ compare arr1[i] vs arr2[j], take the smaller
```

### Variant 4: Dutch National Flag (3 Pointers)

```
arr = [2, 0, 1, 2, 0, 1]
       low mid         high
       ↑ 0s go here    ↑ 2s go here
       mid scans forward, low/high are boundaries
```

Used when partitioning into three groups (e.g., 0/1/2, red/white/blue).

## Decision Tree

```
Is the array sorted (or can you sort it)?
├── YES → Can you move inward from both ends?
│         ├── YES → Opposite-ends two-pointer
│         └── NO  → Sliding window or binary search
└── NO  → Do you need to partition / remove in-place?
          ├── YES → Fast/slow (read/write) two-pointer
          └── NO  → Hash map or sorting approach
```

## Complexity

| Variant | Time | Space | Notes |
|---------|------|-------|-------|
| Opposite ends | O(n) | O(1) | Requires sorted array |
| Fast/slow | O(n) | O(1) | Works on any array |
| Two-array merge | O(n+m) | O(1) write / O(n+m) new | |
| 3Sum (outer loop + two-pointer) | O(n²) | O(1) | Better than O(n³) brute |
| Dutch national flag | O(n) | O(1) | Exactly one pass |

## Common Mistakes

- **Not sorting first** when using opposite-ends variant — the algorithm requires sorted order
- **Off-by-one on termination**: use `while left < right`, NOT `left <= right` (they'd point to same element)
- **Moving both pointers simultaneously** when you should only move one
- **Forgetting to skip duplicates** in 3Sum/4Sum variants
- **Using two-pointer on linked list cycle** with `left` and `right` — use `slow` and `fast` instead
- **Swapping instead of overwriting** in remove-duplicates: you only need `nums[slow] = nums[fast]`, not a swap

## Run the Code

```bash
# From repo root
pytest tests/patterns/test_two_pointer.py -v
```

**Implementation:** [`python/patterns/two_pointer.py`](../../../python/patterns/two_pointer.py)
**Tests:** [`tests/patterns/test_two_pointer.py`](../../../tests/patterns/test_two_pointer.py)

## Problems

10 problems with full think-process walk-throughs: [problems.md](problems.md)

| # | Problem | Difficulty | LeetCode |
|---|---------|-----------|---------|
| 1 | Two Sum II — Input Array Is Sorted | Easy | #167 |
| 2 | Valid Palindrome | Easy | #125 |
| 3 | Move Zeroes | Easy | #283 |
| 4 | Remove Duplicates from Sorted Array | Easy | #26 |
| 5 | Reverse String | Easy | #344 |
| 6 | 3Sum | Medium | #15 |
| 7 | Container With Most Water | Medium | #11 |
| 8 | Sort Colors | Medium | #75 |
| 9 | Trapping Rain Water | Hard | #42 |
| 10 | Linked List Cycle II | Medium | #142 |
