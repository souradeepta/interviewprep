# Array & String Problems

## Sliding Window
**When to use:** Fixed or variable-size contiguous window, substring/subarray problems

**Best DS:** Deque, HashMap

**Key Algorithms:** Two-pointer expansion/contraction, hash-based frequency tracking

**Example Problems:**
1. "Longest substring without repeating characters" → HashMap tracks char positions, two pointers for window bounds. Time: O(n)
2. "Sliding window maximum" → Deque keeps indices in decreasing order. Time: O(n)

---

## Prefix Sum
**When to use:** Range sum queries, cumulative value computation, subarray problems

**Best DS:** Array, 2D Array, HashMap

**Key Algorithms:** Prefix array construction O(n), range query O(1)

**Example Problems:**
1. "Range sum query" → Build prefix array, query in O(1). Your repo: `python/basic/array.py`
2. "Subarray sum equals k" → HashMap of prefix sums. Time: O(n)

---

## Two Pointers
**When to use:** Sorted arrays, opposite-end operations, convergence problems

**Best DS:** Array, Linked list

**Key Algorithms:** Pointer convergence, skip duplicates while iterating

**Example Problems:**
1. "Two sum (sorted array)" → One at start, one at end, converge. Time: O(n)
2. "Container with most water" → Area = min(height) × distance; shrink smaller side. Time: O(n)

---

## Binary Search
**When to use:** Sorted arrays, monotonic conditions, find target efficiently

**Best DS:** Sorted array, BST

**Key Algorithms:** Standard binary search, leftmost/rightmost variants, rotated array search

**Example Problems:**
1. "Search in rotated sorted array" → Determine which half is sorted, search recursively. Your repo: `python/advanced/bst.py`. Time: O(log n)
2. "Find first and last position" → Two binary searches for boundaries. Time: O(log n)

---

## Array Rotation
**When to use:** Circular operations, index wrapping, rotation detection

**Best DS:** Array

**Key Algorithms:** Modulo arithmetic, reversal algorithm, pivot finding

**Example Problems:**
1. "Rotate array by k" → Reverse [0, k-1], [k, n-1], [0, n-1]. Time: O(n)
2. "Find minimum in rotated sorted array" → Binary search on rotation pivot. Time: O(log n)

---

## String Matching
**When to use:** Substring search, pattern detection, text processing

**Best DS:** Trie, HashMap, String

**Key Algorithms:** KMP, rolling hash, Trie-based matching

**Example Problems:**
1. "Longest common prefix" → Vertical comparison or Trie. Your repo: `python/advanced/trie.py`. Time: O(n × m)
2. "Implement strStr()" → Rolling hash or character-by-character match. Time: O(n + m)

---

See [Master Index](problem-to-pattern-matcher.md) for all 50+ patterns.
