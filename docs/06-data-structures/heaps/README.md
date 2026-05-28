# Heaps — Priority Queue, O(log n) Insert/Delete, O(1) Peek

**Level:** L4
**Time to read:** ~20 min

When you need the min or max element repeatedly from a dynamic set, a heap beats everything else.

---

## Quick Summary

A heap is a complete binary tree stored as an array satisfying the heap property: in a min-heap, every parent ≤ its children; in a max-heap, every parent ≥ its children. This gives O(1) peek at the min/max and O(log n) insert/delete. Use for priority queues, scheduling, and k-element problems. Key insight: heap doesn't maintain full sorted order — only guarantees the root is the extreme value.

---

## Operations & Complexity Table

| Operation        | Min-Heap / Max-Heap | Notes                                          |
|------------------|--------------------|-------------------------------------------------|
| Peek min/max     | O(1)               | Root element — direct array access             |
| Insert (push)    | O(log n)           | Add at end, sift up                            |
| Delete min/max   | O(log n)           | Swap root with last, sift down                 |
| Delete arbitrary | O(log n)           | Find O(n) + sift O(log n); use when needed     |
| Build heap       | O(n)               | Heapify from bottom — NOT O(n log n)           |
| Heap sort        | O(n log n)         | Build + n extractions                          |
| Merge two heaps  | O(n log n)         | Or O(log n) with Fibonacci heap (theory)       |
| Space            | O(n)               | Compact array, no pointer overhead             |

---

## Memory Layout / Internal Structure

```
Min-Heap as array (1-indexed for simpler math):

Tree view:          Array view:
      1              [_, 1, 3, 5, 7, 9, 8, 6]
     / \              ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
    3   5             0  1  2  3  4  5  6  7  ← index (0 unused)
   / \ / \
  7  9 8  6          Index formulas (1-indexed):
                       Left child of i  = 2i
                       Right child of i = 2i + 1
                       Parent of i      = i // 2

Python heapq uses 0-indexed (shift by 1):
  Left child of i  = 2i + 1
  Right child of i = 2i + 2
  Parent of i      = (i - 1) // 2

Insert 2 into heap:
  Step 1: Add at end → [1, 3, 5, 7, 9, 8, 6, 2]
  Step 2: Sift up (compare with parent):
          2 < parent(9) → swap  → [1, 3, 5, 7, 2, 8, 6, 9]
          2 < parent(3) → swap  → [1, 2, 5, 7, 3, 8, 6, 9]
          2 > parent(1) → stop  ← 2 is in correct position

Delete min (1):
  Step 1: Swap root with last → [9, 2, 5, 7, 3, 8, 6]
  Step 2: Remove last         → [9, 2, 5, 7, 3, 8, 6]
  Step 3: Sift down (9):
          min(children) = min(2,5) = 2 < 9 → swap → [2, 9, 5, 7, 3, 8, 6]
          min(children) = min(7,3) = 3 < 9 → swap → [2, 3, 5, 7, 9, 8, 6]
          9 has no children → done
```

---

## Trade-offs vs Alternatives

| Feature              | Min-Heap      | Sorted Array  | BST (balanced) | Python deque   |
|----------------------|---------------|---------------|----------------|----------------|
| Peek min             | O(1)          | O(1)          | O(log n)       | O(1) w/ sort   |
| Insert               | O(log n)      | O(n) shift    | O(log n)       | O(1) unsorted  |
| Delete min           | O(log n)      | O(1) pop end  | O(log n)       | O(n)           |
| Delete arbitrary     | O(n) + log n  | O(n)          | O(log n)       | O(n)           |
| Ordered iteration    | O(n log n)    | O(n)          | O(n) in-order  | O(n log n)     |
| Build from array     | O(n)          | O(n log n)    | O(n log n)     | O(n log n)     |
| Space                | O(n) compact  | O(n) compact  | O(n) pointers  | O(n)           |
| k largest elements   | O(n log k)    | O(n log n)    | O(n log n)     | O(n log n)     |

```
When to choose heap:
┌─────────────────────────────────────────────────────────────┐
│ Need min or max repeatedly from dynamic set? → Heap         │
│ k smallest / k largest from stream?          → Heap (size k)│
│ Merge k sorted lists?                        → Min-heap     │
│ Task scheduling by priority?                 → Heap         │
│ Need ordered iteration?                      → Sorted array │
│ Need arbitrary delete or floor/ceil?         → BST          │
└─────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **Need ordered iteration** — heap sort is O(n log n) and produces sorted array, but then you should just sort. Use sorted array or BST for frequent in-order traversal.
- **Need arbitrary element deletion by key** — heap delete is O(n) to find + O(log n) to fix. BST handles this in O(log n).
- **Small fixed datasets** — linear scan of 10 elements beats heap overhead.
- **Floor/ceiling/predecessor queries** — heap has no notion of order among non-root elements. Use BST.
- **Frequent arbitrary inserts + deletes with ordering** — prefer BST (Java's `TreeMap`, Python's `sortedcontainers.SortedList`).

---

## Core Operations (Code)

```python
import heapq
from typing import Optional

# ── Python heapq (min-heap only) ──────────────────────────────────────────────

nums = [3, 1, 4, 1, 5, 9, 2, 6]
heapq.heapify(nums)           # O(n) in-place build
heapq.heappush(nums, 7)       # O(log n) insert
smallest = heapq.heappop(nums)   # O(log n) delete min
peek = nums[0]                # O(1) peek (don't pop)

# Max-heap: negate values
max_heap = [-x for x in [3, 1, 4, 1, 5]]
heapq.heapify(max_heap)
largest = -heapq.heappop(max_heap)    # negate back

# K largest elements — maintain min-heap of size k
def k_largest(nums: list[int], k: int) -> list[int]:
    heap = nums[:k]
    heapq.heapify(heap)               # O(k)
    for n in nums[k:]:
        if n > heap[0]:               # larger than current min
            heapq.heapreplace(heap, n)   # pop min + push n, O(log k)
    return heap                       # contains k largest (unsorted)

# ── Manual min-heap implementation ───────────────────────────────────────────

class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, val: int) -> None:
        self.heap.append(val)
        self._sift_up(len(self.heap) - 1)

    def pop(self) -> int:
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()    # move last to root
        self._sift_down(0)
        return root

    def peek(self) -> int:
        return self.heap[0]

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self.heap[i] < self.heap[parent]:
                self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        n = len(self.heap)
        while True:
            smallest = i
            left, right = 2 * i + 1, 2 * i + 2
            if left  < n and self.heap[left]  < self.heap[smallest]: smallest = left
            if right < n and self.heap[right] < self.heap[smallest]: smallest = right
            if smallest == i:
                break
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            i = smallest

# ── Heap with custom comparator (tuples) ─────────────────────────────────────

# Push (priority, item) tuples — heapq compares tuples lexicographically
import heapq
tasks = []
heapq.heappush(tasks, (1, "low_priority_task"))
heapq.heappush(tasks, (3, "high_priority_task"))    # higher urgency
heapq.heappush(tasks, (2, "medium_task"))
priority, task = heapq.heappop(tasks)   # pops (1, ...) — min priority!

# For max-priority queue: negate priority
heapq.heappush(tasks, (-3, "urgent"))   # -3 < -2 → pops first
```

---

## 3 Worked Problems

---

### Problem 1 — Kth Largest Element in an Array (LeetCode #215)

**Clarifying Questions**
- Is the array sorted? (No — unsorted)
- Can there be duplicates? (Yes)
- k is 1-indexed (k=1 = largest)? (Yes)
- Modify original array? (Prefer not to)

**Brute Force**

Sort and index.

```python
def find_kth_largest_brute(nums: list[int], k: int) -> int:
    return sorted(nums, reverse=True)[k - 1]   # O(n log n)
```

**Optimization**

Min-heap of size k: maintain the k largest elements seen. The min of those k is the kth largest.

```python
import heapq

def find_kth_largest(nums: list[int], k: int) -> int:
    # Min-heap of exactly k elements
    # heap[0] = kth largest = smallest of the k largest
    heap = nums[:k]
    heapq.heapify(heap)                          # O(k)
    for n in nums[k:]:
        if n > heap[0]:
            heapq.heapreplace(heap, n)           # pop min + push n, O(log k)
    return heap[0]
```

Alternative: QuickSelect — O(n) average, O(n²) worst case.

```python
import random

def find_kth_largest_quickselect(nums: list[int], k: int) -> int:
    # Partition around pivot, recurse on relevant side
    def partition(lo, hi):
        pivot_idx = random.randint(lo, hi)
        nums[pivot_idx], nums[hi] = nums[hi], nums[pivot_idx]
        pivot = nums[hi]
        store = lo
        for i in range(lo, hi):
            if nums[i] >= pivot:       # group larger elements left
                nums[store], nums[i] = nums[i], nums[store]
                store += 1
        nums[store], nums[hi] = nums[hi], nums[store]
        return store

    lo, hi = 0, len(nums) - 1
    k -= 1   # 0-indexed target
    while lo <= hi:
        p = partition(lo, hi)
        if p == k:   return nums[p]
        if p < k:    lo = p + 1
        else:        hi = p - 1
```

**Edge Cases**
- k = 1 → largest element → `max(nums)`
- k = n → smallest element
- All same values → return that value
- Single element, k=1 → return it

**Complexity**
- Heap: O(n log k) time, O(k) space
- QuickSelect: O(n) avg / O(n²) worst time, O(1) space

**Follow-ups**
- "Streaming (can't store all elements)?" → Heap of size k; discard each element after comparison.
- "Kth smallest?" → Use max-heap of size k; pop when heap[0] > new element.

---

### Problem 2 — Merge K Sorted Lists (LeetCode #23)

**Clarifying Questions**
- What is the input? (List of linked list heads)
- Return type? (Single merged linked list head)
- Can any list be empty? (Yes — handle null heads)
- Values range? (-10⁴ to 10⁴)

**Brute Force**

Collect all values, sort, rebuild list.

```python
def merge_k_sorted_brute(lists):
    vals = []
    for head in lists:
        while head:
            vals.append(head.val)
            head = head.next
    vals.sort()
    dummy = ListNode(0)
    curr = dummy
    for v in vals:
        curr.next = ListNode(v)
        curr = curr.next
    return dummy.next
    # O(N log N) time where N = total nodes
```

**Optimization**

Min-heap: push the head of each list. Pop minimum node, add to result, push that node's next.

```python
import heapq

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    # Push (val, index, node) — index breaks ties (nodes don't compare)
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode(0)
    curr  = dummy
    while heap:
        val, i, node = heapq.heappop(heap)
        curr.next = node
        curr = curr.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next
```

**Edge Cases**
- Empty input `lists = []` → return None
- All lists empty → heap never populated → return dummy.next = None
- One list → just return it; heap pops all from it

**Complexity**
- Time: O(N log k) — N total nodes, each pushed/popped once; heap size ≤ k
- Space: O(k) heap + O(1) pointer manipulation (output in-place)

**Follow-ups**
- "k=2 (two sorted lists)?" → Two-pointer merge; no heap needed; O(n+m).
- "Sort linked list?" → LeetCode #148; merge sort using this merge.

---

### Problem 3 — Task Scheduler (LeetCode #621)

**Clarifying Questions**
- What does n mean? (Cooldown: same task can't repeat within n intervals; can idle)
- Input: `tasks = ['A','A','A','B','B','B'], n = 2`? (Yes)
- Minimize total intervals? (Yes)
- Task order can be rearranged? (Yes)

**Brute Force**

Simulate: at each interval, pick the most frequent task available.

**Optimization**

Greedy with max-heap: always schedule the task with the highest remaining count. Use a queue to track cooling tasks.

```python
from collections import Counter
import heapq
from collections import deque

def least_interval(tasks: list[str], n: int) -> int:
    freq = Counter(tasks)
    # Max-heap (negate counts for Python's min-heap)
    heap = [-cnt for cnt in freq.values()]
    heapq.heapify(heap)

    time = 0
    cooldown_queue = deque()    # (finish_time, count_remaining)

    while heap or cooldown_queue:
        # Release tasks whose cooldown has expired
        if cooldown_queue and cooldown_queue[0][0] == time:
            _, cnt = cooldown_queue.popleft()
            heapq.heappush(heap, cnt)

        if heap:
            cnt = heapq.heappop(heap) + 1   # do task (negate → increment = reduce count)
            if cnt < 0:                      # still has remaining executions
                cooldown_queue.append((time + n + 1, cnt))
        # else: idle this interval

        time += 1

    return time
```

Math shortcut (no simulation needed):

```python
def least_interval_math(tasks: list[str], n: int) -> int:
    freq = sorted(Counter(tasks).values(), reverse=True)
    max_freq = freq[0]
    # How many tasks tie for max frequency?
    max_count = freq.count(max_freq)
    # Total intervals = max(formula, len(tasks))
    return max(len(tasks), (max_freq - 1) * (n + 1) + max_count)
```

**Edge Cases**
- n=0 → no cooldown; just `len(tasks)`
- All unique tasks → no cooldown needed; `len(tasks)`
- Single task type, high n → significant idle time

**Complexity**
- Simulation: O(T log T) where T = total tasks
- Math: O(T) — sort frequencies

**Follow-ups**
- "Rearrange string k distance apart?" → LeetCode #358; same greedy pattern.
- "Return actual schedule?" → Build the simulation result string.

---

## Interview Q&A

**Q1: Why is building a heap O(n) and not O(n log n)?**

A: Intuitively, bottom-up heapify (Floyd's algorithm) does less work per node: leaves (n/2 nodes) need 0 sift-down work, their parents (n/4 nodes) need at most 1 swap, grandparents (n/8) need at most 2 swaps. The total work is n/2×0 + n/4×1 + n/8×2 + ... = O(n) (geometric series). In contrast, inserting n elements one by one is each O(log k) as the heap grows, summing to O(n log n).

---

**Q2: Heap vs BST — which should you use for a priority queue?**

A:
```
Heap:
  - O(1) peek min/max
  - O(log n) insert/delete-min
  - O(n) arbitrary delete
  - Simpler: compact array, no pointers
  - No ordering guarantees beyond root
  Use when: you only need min/max repeatedly

BST (balanced):
  - O(log n) for everything including arbitrary delete
  - Ordered iteration
  - Floor/ceiling/range queries
  - More complex: pointer-based
  Use when: need arbitrary key operations + ordering

99% of "priority queue" use cases → heap (simpler, faster constants)
```

---

**Q3: How do you implement a max-heap in Python?**

A: Python's `heapq` only provides min-heap. Two strategies: (1) Negate values — push `-x`, pop and negate the result. (2) Wrap in a custom class with `__lt__` reversed. Negation is simpler for integers. For objects, use `(-priority, item)` tuples.

```python
max_heap = []
heapq.heappush(max_heap, -5)
heapq.heappush(max_heap, -1)
heapq.heappush(max_heap, -3)
largest = -heapq.heappop(max_heap)   # 5
```

---

**Q4: What is heapify and how does it work?**

A: `heapify` converts an arbitrary array into a valid heap in O(n). It works bottom-up: start from the last non-leaf node (index n//2 - 1) and call sift-down on each node going up to the root. Each sift-down fixes the heap property for a subtree. This is more efficient than inserting elements one by one because most nodes (the leaves, ~n/2) require no work at all.

---

**Q5: How do you find the kth largest element using a heap?**

A: Maintain a min-heap of exactly k elements. For each new element: if it's larger than the heap minimum (heap[0]), replace the minimum with it (heapreplace). After processing all n elements, the heap contains the k largest, and heap[0] is the kth largest. Time: O(n log k). Space: O(k). This is optimal for streaming data where you can't store all n elements.

---

**Q6: What is the space complexity of heap sort?**

A: O(1) extra space — heap sort is in-place. Build a max-heap in the original array (O(n)), then repeatedly swap the root (max) with the last element and sift down on the reduced heap. The sorted array builds in-place from right to left. Heap sort has O(n log n) time and O(1) space, but poor cache performance (sift-down accesses non-contiguous memory) so in practice it's slower than merge sort or quicksort.

---

**Q7: When does a heap perform worse than expected?**

A: (1) Arbitrary deletion — need O(n) to find the element first, then O(log n) to fix. (2) Iteration in sorted order — need O(n log n) heap sort; a sorted array is better. (3) Range queries — heap has no spatial structure; BST or segment tree is better. (4) When elements are removed and re-inserted frequently with changing priorities — a "decrease-key" operation (Fibonacci heap feature) is O(1) amortized but Python's heapq doesn't support it; workaround is lazy deletion with a visited set.

---

**Q8: Explain the lazy deletion pattern for heaps.**

A: When you need to "update" or "cancel" a task in a heap (which doesn't support efficient arbitrary deletion), push the updated version and mark the old version as invalid. When popping, skip invalid entries. Track validity with a set of cancelled entries or a dictionary of current values.

```python
# Lazy deletion example: skip stale entries
cancelled = set()
heap = []
heapq.heappush(heap, (priority, task_id))

# "Cancel" task:
cancelled.add(task_id)

# Pop valid task:
while heap:
    p, tid = heapq.heappop(heap)
    if tid not in cancelled:
        # process valid task
        break
```

---

## Interview Tips

- **Heap = priority queue.** In interviews, "use a priority queue" means heap. Know Python's `heapq` cold: `heapify`, `heappush`, `heappop`, `heapreplace`, `nlargest`, `nsmallest`.
- **k-element problems → heap of size k.** "K largest", "K smallest", "K most frequent" — all follow the same pattern: heap of size k, replace when beaten.
- **Merge k sorted = min-heap.** Memorize the pattern: push all heads, pop min, push next.
- **Negate for max-heap.** Python only gives min-heap; negate integer values. For objects, use `(-val, obj)` tuples.
- **State the O(n) build insight.** Saying "heapify is O(n) because bottom-up sifting does less work per node" signals depth beyond basic usage.
