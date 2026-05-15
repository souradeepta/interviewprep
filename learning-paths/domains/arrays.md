---
domain: arrays
difficulty: "⭐-⭐⭐"
estimated_time: "6-8 hours"
prerequisites: []
covered_in_stages: [phone-screen, technical-round]
problem_count: 7
key_concepts: [two-pointers, sliding-window, binary-search, prefix-sums]
---

# Arrays

## Overview

Arrays are the most fundamental data structure in interviews. Master them first — concepts from arrays unlock trees, graphs, and advanced algorithms. This domain covers manipulation, searching, and fundamental patterns.

## Key Concepts

### Two Pointers
**When:** Find pair, reverse, remove duplicates, merge  
**How:** One pointer at start, one at end, move inward (or same direction for sorted arrays)

### Sliding Window
**When:** Longest/shortest substring, subarray sum, max/min in window  
**How:** Maintain a window with two pointers, expand right, contract left when condition breaks

### Binary Search
**When:** Search in sorted array, find boundary, answer search  
**How:** Divide search space in half repeatedly, O(log n) time

### Prefix Sums
**When:** Range queries, subarray sums  
**How:** Precompute cumulative sums for O(1) range queries

## Problem Sequence

### Easy (30-45 min each)

1. **Reverse Array** (15 min) ⭐
   - **Problem:** Reverse an array in-place
   - **Pattern:** Two pointers
   - **Solutions:** [Python](../../python/basic/array.py) [Java](../../java/basic/)

2. **Remove Duplicates** (20 min) ⭐
   - **Problem:** Remove duplicates from sorted array in-place
   - **Pattern:** Two pointers
   - **Solutions:** [Python](../../python/basic/array.py) [Java](../../java/basic/)

3. **Two Sum** (30 min) ⭐⭐
   - **Problem:** Find two numbers that sum to target
   - **Pattern:** Hash map OR two pointers (if sorted)
   - **Solutions:** [Python](../../python/basic/array.py) [Java](../../java/basic/)

### Medium (45-60 min each)

4. **3Sum** (45 min) ⭐⭐
   - **Problem:** Find all unique triplets summing to zero
   - **Pattern:** Two pointers + loop
   - **Solutions:** [Python](../../python/advanced/) [Java](../../java/advanced/)

5. **Longest Substring Without Repeating** (45 min) ⭐⭐
   - **Problem:** Find length of longest substring with all unique characters
   - **Pattern:** Sliding window + hash map
   - **Solutions:** [Python](../../python/basic/array.py) [Java](../../java/basic/)

6. **Maximum Subarray Sum** (45 min) ⭐⭐
   - **Problem:** Find contiguous subarray with maximum sum
   - **Pattern:** Kadane's algorithm / DP
   - **Solutions:** [Python](../../python/algorithms/) [Java](../../java/algorithms/)

7. **Search in Rotated Sorted Array** (60 min) ⭐⭐
   - **Problem:** Find target in rotated sorted array
   - **Pattern:** Binary search (modified)
   - **Solutions:** [Python](../../python/advanced/) [Java](../../java/advanced/)

## Pattern Summary

| Pattern | Problems | Use Cases |
|---------|----------|-----------|
| Two Pointers | Reverse, Remove Duplicates, Two Sum | In-place, pair finding |
| Hash Map | Two Sum, Longest Substring | Quick lookups, dedup |
| Sliding Window | Longest Substring | Contiguous sequences |
| Binary Search | Search Rotated | Sorted/partially sorted |
| Kadane's Algorithm | Max Subarray | Optimal subproblems |

## Tips for Success

1. **Understand the problem deeply** — Do you need in-place? Return indices or values?
2. **Test edge cases** — Empty array, single element, all same, negatives
3. **Consider space trade-off** — Can you use a hash map to avoid nested loops?
4. **Practice two pointers** — Most array problems use this pattern
5. **Trace through examples** — Walk through your logic before coding

## Related Topics

- Linked Lists (similar pointer techniques)
- Dynamic Programming (subarray optimization)
- Trees (array representation)
- Graphs (adjacency matrix)

## Advanced Variants (Optional)

- Median of two sorted arrays
- Range sum query (prefix sums)
- Product of array except self
- Trapping rain water
