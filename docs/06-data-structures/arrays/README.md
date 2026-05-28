# Arrays — Contiguous Memory, O(1) Random Access

**Level:** L3
**Time to read:** ~20 min

The foundational data structure. Everything else is built on top of or compared against arrays.

---

## Quick Summary

An array stores elements in contiguous memory locations, enabling O(1) access by index. Use when you need fast random access, cache-friendly traversal, or a compact fixed-size buffer. Key property: index math gives you any element instantly, but insertions/deletions in the middle shift everything.

---

## Operations & Complexity Table

| Operation        | Time (avg)   | Time (worst) | Space  | Notes                                  |
|------------------|-------------|-------------|--------|----------------------------------------|
| Access by index  | O(1)        | O(1)        | O(1)   | Direct address = base + index * size   |
| Search (unsorted)| O(n)        | O(n)        | O(1)   | Must scan all elements                 |
| Search (sorted)  | O(log n)    | O(log n)    | O(1)   | Binary search                          |
| Insert at end    | O(1)*       | O(n)        | O(1)   | *Amortized; O(n) on resize             |
| Insert at index  | O(n)        | O(n)        | O(1)   | Shift all elements right               |
| Delete at end    | O(1)        | O(1)        | O(1)   | No shift needed                        |
| Delete at index  | O(n)        | O(n)        | O(1)   | Shift all elements left                |
| Append (dynamic) | O(1)*       | O(n)        | O(1)   | *Amortized over n appends              |

---

## Memory Layout / Internal Structure

```
Static Array (fixed size, stack or heap)
───────────────────────────────────────────────────────
Index:   [0]   [1]   [2]   [3]   [4]   [5]
Value:   [ 10] [ 20] [ 30] [ 40] [ 50] [ 60]
Address: 1000  1004  1008  1012  1016  1020
         ↑
         base address
         element_i = base + i * element_size (4 bytes for int)

Dynamic Array (Python list / Java ArrayList)
───────────────────────────────────────────────────────
Logical:  [10] [20] [30] (size=3)
Physical: [10] [20] [30] [__] [__] [__] (capacity=6)
                          ↑
                          unused capacity (reserved for growth)

Resize Event:
old: [10] [20] [30] [40]  ← capacity full (4)
                ↓ alloc new 2× capacity
new: [10] [20] [30] [40] [__] [__] [__] [__]  (capacity=8)
```

---

## Trade-offs vs Alternatives

| Feature             | Array         | Linked List    | Hash Table      |
|---------------------|---------------|----------------|-----------------|
| Random access       | O(1)          | O(n)           | O(1) avg        |
| Search (unsorted)   | O(n)          | O(n)           | O(1) avg        |
| Insert at end       | O(1) amort.   | O(1)           | O(1) avg        |
| Insert at position  | O(n)          | O(1)*          | N/A             |
| Delete at position  | O(n)          | O(1)*          | O(1) avg        |
| Memory (overhead)   | Low           | High (pointers)| High (buckets)  |
| Cache locality      | Excellent     | Poor           | Moderate        |
| Ordered iteration   | O(n)          | O(n)           | N/A (unordered) |
| Sorted operations   | O(log n)      | O(n)           | N/A             |

*O(1) only if you already hold a reference to the node

```
When to choose each:
┌─────────────────────────────────────────────────────────────┐
│ Need random access?         → Array                         │
│ Frequent mid-list insert?   → Linked List                   │
│ Key-value lookup?           → Hash Table                    │
│ Sorted + binary search?     → Array (or BST)                │
│ Fixed size, cache critical? → Array                         │
└─────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **Frequent insertions/deletions at arbitrary positions** — every insert at index i shifts n-i elements; use a linked list or deque.
- **Unknown or highly variable size** — static arrays waste memory; even dynamic arrays double-allocate. Use a linked list or dynamic collection.
- **Key-based lookups (non-integer keys)** — use a hash map; scanning an array for a key is O(n).
- **Priority-based retrieval** — use a heap; arrays don't maintain order on insert.
- **Union/Find on disjoint sets** — use union-find structure, not raw array.

---

## Core Operations (Code)

```python
# ── Dynamic Array basics (Python list internals exposed) ──────────────────

# O(1) amortized append
arr = []
for i in range(10):
    arr.append(i)          # triggers resize at 0,1,2,4,8... capacities

# O(1) access
val = arr[3]               # direct memory address lookup

# O(n) insert at index
arr.insert(2, 99)          # shifts arr[2:] one position right

# O(n) delete at index
arr.pop(2)                 # shifts arr[3:] one position left

# ── Prefix Sum (pattern used in many problems) ────────────────────────────
def build_prefix(nums: list[int]) -> list[int]:
    prefix = [0] * (len(nums) + 1)
    for i, v in enumerate(nums):
        prefix[i + 1] = prefix[i] + v
    return prefix

def range_sum(prefix: list[int], l: int, r: int) -> int:
    # sum of nums[l..r] inclusive, O(1) after O(n) build
    return prefix[r + 1] - prefix[l]

# ── Two-pointer pattern ───────────────────────────────────────────────────
def two_sum_sorted(nums: list[int], target: int) -> tuple[int, int]:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target:
            return lo, hi
        elif s < target:
            lo += 1
        else:
            hi -= 1
    return -1, -1

# ── Sliding window pattern ────────────────────────────────────────────────
def max_subarray_sum_k(nums: list[int], k: int) -> int:
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best
```

---

## 3 Worked Problems

---

### Problem 1 — Two Sum (LeetCode #1)

**Clarifying Questions**
- Are there duplicate values? Can multiple pairs sum to target?
- Can I use the same element twice? (No — "two different indices")
- Is the array sorted? (Not stated, assume unsorted)
- What should I return if no solution exists? (Problem guarantees exactly one)

**Brute Force**
```python
def two_sum_brute(nums, target):
    # Check every pair — O(n²) time, O(1) space
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
```

**Optimization**

For each element x, we need to know if `target - x` already exists. A hash map gives O(1) lookup, turning O(n²) → O(n).

```python
def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}               # value → index
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            return [seen[complement], i]
        seen[x] = i
    return []               # guaranteed not reached per problem
```

**Edge Cases**
- Duplicate values: `[3, 3]`, target=6 — works because we check `seen` before writing `seen[x]`.
- Negative numbers: complement math still correct.
- Single element: loop won't find pair (problem guarantees solution exists).

**Complexity**
- Time: O(n) — single pass
- Space: O(n) — hash map

**Follow-ups**
- "What if sorted?" → Two-pointer, O(n) time O(1) space.
- "Return all pairs?" → Collect instead of early return.
- "3Sum?" → Sort + two-pointer for each fixed element, O(n²).

---

### Problem 2 — Best Time to Buy and Sell Stock (LeetCode #121)

**Clarifying Questions**
- Can we make multiple transactions? (No — exactly one buy/sell)
- Must we buy before we sell? (Yes)
- What if prices only decrease? (Return 0 — no transaction)

**Brute Force**
```python
def max_profit_brute(prices):
    # Try every (buy, sell) pair — O(n²) time
    best = 0
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            best = max(best, prices[j] - prices[i])
    return best
```

**Optimization**

Track the minimum price seen so far. For each day, the best profit if we sell today is `price - min_so_far`.

```python
def max_profit(prices: list[int]) -> int:
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        if price < min_price:
            min_price = price
        elif price - min_price > max_profit:
            max_profit = price - min_price
    return max_profit
```

**Edge Cases**
- All prices equal: profit = 0.
- Single price: profit = 0.
- Monotonically decreasing: min never lets profit go positive.

**Complexity**
- Time: O(n) — single pass
- Space: O(1)

**Follow-ups**
- "Multiple transactions?" → Greedy — add every positive day-to-day difference (LeetCode #122).
- "At most k transactions?" → DP with k states (LeetCode #188).
- "With cooldown?" → DP with extra state (LeetCode #309).

---

### Problem 3 — Maximum Subarray (LeetCode #53)

**Clarifying Questions**
- Must subarray be non-empty? (Yes — at least 1 element)
- Are all values negative? (Yes possible — return the largest single element)
- What's the expected approach — O(n log n) or O(n)? (O(n) Kadane's expected)

**Brute Force**
```python
def max_subarray_brute(nums):
    # Compute sum of every subarray — O(n²)
    best = float('-inf')
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            best = max(best, total)
    return best
```

**Optimization (Kadane's Algorithm)**

Key insight: at each index, either extend the current subarray or start fresh. If the running sum drops below 0, starting fresh is always better.

```python
def max_subarray(nums: list[int]) -> int:
    current = best = nums[0]
    for num in nums[1:]:
        current = max(num, current + num)   # extend or restart
        best = max(best, current)
    return best

# Variant: also return the subarray indices
def max_subarray_with_indices(nums: list[int]) -> tuple[int, int, int]:
    current = best = nums[0]
    start = end = best_start = 0
    for i, num in enumerate(nums[1:], 1):
        if num > current + num:
            current = num
            start = i
        else:
            current += num
        if current > best:
            best = current
            best_start = start
            end = i
    return best, best_start, end
```

**Edge Cases**
- All negative: `[-3, -1, -2]` → returns -1 (largest single element).
- Single element: handled by initialization.
- All same value: running sum grows correctly.

**Complexity**
- Time: O(n) — single pass
- Space: O(1)

**Follow-ups**
- "Maximum subarray product?" → Track both min and max (LeetCode #152).
- "Circular array?" → max(kadane, total_sum - min_subarray) (LeetCode #918).
- "Divide and conquer approach?" → O(n log n), useful for segment trees.

---

## Interview Q&A

**Q1 (Easy): What is the difference between a static and dynamic array?**

A static array has a fixed size determined at creation; accessing beyond it is undefined behavior (C) or an error. A dynamic array (Python list, Java ArrayList) starts with a small capacity and doubles when full. The amortized cost of append remains O(1) because the total work for n appends is O(n): you copy 1 element, then 2, then 4 ... summing to 2n.

---

**Q2 (Easy): Why is array random access O(1)?**

Elements are stored contiguously. The CPU computes `address = base + index * element_size` — a single multiplication and addition. There are no pointers to follow, so access time is constant regardless of array size.

---

**Q3 (Medium): Explain amortized O(1) for dynamic array append.**

In the worst case, a single append triggers a resize that copies n elements — O(n). But resizes happen at sizes 1, 2, 4, 8, ... n. The total copy work is 1+2+4+...+n = 2n. Spread over n operations, each costs 2 on average — O(1) amortized. The "charge" model: each append pays for itself plus sets aside credit for a future copy.

---

**Q4 (Medium): Why do arrays have better cache performance than linked lists?**

Arrays occupy contiguous memory, so traversal prefetches adjacent elements into cache lines (typically 64 bytes = 16 ints). Linked list nodes are scattered in heap memory; each `->next` dereference is likely a cache miss. For iterating 1M integers: array ~10ms (cache hits), linked list ~100ms+ (cache misses). This matters for most practical algorithms.

---

**Q5 (Medium): What resize factor should a dynamic array use and why?**

Common choices: 2× (Java ArrayList, CPython uses ~1.125× growth). The factor trades off:
- **Space waste** — factor 2 can waste up to 50% capacity
- **Number of resizes** — smaller factor means more frequent copies
- **Amortized cost** — any constant factor > 1 gives O(1) amortized

Python uses a fractional growth (~12.5%) to minimize memory waste for small lists; Java uses 1.5× for ArrayList. In practice, 1.5–2× is the sweet spot.

---

**Q6 (Medium): When would you choose an array over a linked list for a stack/queue?**

For a stack: always prefer an array (or Python list). Push/pop at the end are O(1) with zero allocation overhead, and cache performance is excellent.

For a queue: use `collections.deque` (a doubly-linked list internally in CPython) if you need O(1) dequeue from the front. A plain array-backed queue needs a circular buffer or you pay O(n) for front removal.

---

**Q7 (Hard): Design a data structure supporting get/set by index and O(1) amortized insert/delete at arbitrary position.**

You can't beat O(n) for arbitrary insert/delete in a contiguous array. Options:
- **Rope** (for strings): balanced BST of array chunks, O(log n) insert/delete.
- **Order-statistic tree**: O(log n) rank-based access + insert/delete.
- **Skip list**: O(log n) expected for all operations.
- **Segmented array**: fixed-size buckets; insert within a bucket O(√n), rebalance bucket splits.

Trade-off: O(1) and arbitrary insert/delete are mutually exclusive without auxiliary structures.

---

**Q8 (Hard): Given a 1D array of prices representing a stock ticker, implement a range-minimum query answering "minimum price in window [l, r]" in O(1) after O(n log n) preprocessing.**

Use a Sparse Table:
```python
import math

def build_sparse_table(nums):
    n = len(nums)
    k = math.floor(math.log2(n)) + 1
    st = [[float('inf')] * n for _ in range(k)]
    st[0] = nums[:]
    for j in range(1, k):
        for i in range(n - (1 << j) + 1):
            st[j][i] = min(st[j-1][i], st[j-1][i + (1 << (j-1))])
    return st

def query_min(st, l, r):
    j = math.floor(math.log2(r - l + 1))
    return min(st[j][l], st[j][r - (1 << j) + 1])

# Build: O(n log n), query: O(1), space: O(n log n)
```
This is the basis for RMQ used in LCA algorithms and competitive programming.

---

## Interview Tips

- **Always clarify sorted/unsorted** — it changes complexity from O(n) to O(log n) for search.
- **Mention amortized** — interviewers test whether you distinguish worst-case vs amortized for dynamic arrays.
- **Cache locality is a real answer** — saying "arrays are cache-friendly" with a concrete reason (contiguous memory, prefetcher) impresses L4+ interviewers.
- **Two-pointer and sliding window** are the canonical array patterns; be fluent in both.
- **Prefix sums** unlock O(1) range queries — memorize the build + query pattern.
- **For resize factor questions** — always say "any constant > 1 guarantees O(1) amortized" then give a trade-off.
