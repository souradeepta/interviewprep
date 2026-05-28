# Advanced Trees — AVL, Red-Black, B-Tree, Segment Tree

**Level:** L4-L5
**Time to read:** ~30 min

When a plain BST isn't enough. Each variant solves a specific bottleneck: balance guarantees, disk I/O efficiency, or range queries.

---

## Quick Summary

Four specialized tree structures, each solving a distinct problem: AVL keeps height strictly ≤ 1.44 log n via rotations (best for read-heavy workloads); Red-Black relaxes balance for faster writes (used in most language standard libraries); B-Tree minimizes disk reads by packing many keys per node (databases, filesystems); Segment Tree enables O(log n) range queries and point updates (competitive programming, interval problems).

---

## Operations & Complexity Table

| Operation        | AVL Tree     | Red-Black Tree | B-Tree (order m)       | Segment Tree         |
|------------------|-------------|----------------|------------------------|----------------------|
| Search           | O(log n)    | O(log n)       | O(log_m n)             | O(log n)             |
| Insert           | O(log n)    | O(log n)       | O(log_m n)             | O(log n)             |
| Delete           | O(log n)    | O(log n)       | O(log_m n)             | O(log n)             |
| Range query      | O(log n+k)  | O(log n+k)     | O(log_m n + k/m)       | O(log n)             |
| Point update     | O(log n)    | O(log n)       | O(log_m n)             | O(log n)             |
| Space            | O(n)        | O(n)           | O(n)                   | O(4n)                |
| Height           | ≤ 1.44 log n| ≤ 2 log(n+1)   | ≤ log_⌈m/2⌉ n         | Exactly log₂ n       |
| Rotations/insert | ≤ 2         | ≤ 2            | 0 (split instead)      | N/A                  |

---

## Memory Layout / Internal Structure

```
AVL Tree — balance factor stored per node:
          30 (bf=0)
         /          \
      20 (bf=0)    40 (bf=1)
      /    \       /
   10(bf=0) 25(bf=0) 35(bf=0)

  bf = height(right) - height(left)
  Invariant: |bf| ≤ 1 at every node
  Left-heavy (bf=-1), Right-heavy (bf=+1), Balanced (bf=0)

Red-Black Tree — color bit per node:
         B:30
        /     \
      R:20    B:40
      /  \    /
   B:10 B:25 R:35

  Rules:
  1. Every node is Red or Black
  2. Root is Black
  3. Red nodes have Black children (no two reds in a row)
  4. All paths from node to null have equal Black depth
  Height ≤ 2 log(n+1)

B-Tree (order 5, max 4 keys per node):
  Each node: [ 10 | 20 | 30 | 40 ]
             /    |    |    |    \
         <10  10-20 20-30 30-40  >40
  
  Designed for disk pages:
  - 1 node = 1 disk page (4KB)
  - 4KB page / 8 bytes per key ≈ 500 keys per node
  - 1 billion keys in ~2-3 levels → 2-3 disk reads

Segment Tree (array representation):
  Array: [1, 3, 5, 7, 9, 11]  (n=6)
  
  Stored as 1-indexed array of size ~4n:
  Index:    1
           2   3
          4 5 6 7
         ...
  
  Node i: covers range
  Left child = 2i, Right child = 2i+1
  Parent = i // 2
```

---

## Trade-offs vs Alternatives

| Scenario                        | Best Choice       | Why                                              |
|---------------------------------|-------------------|--------------------------------------------------|
| std::map / Java TreeMap         | Red-Black Tree    | Fewer rotations on insert; library-implemented   |
| Read-heavy in-memory lookup     | AVL Tree          | Stricter balance → shorter height → faster search|
| Database index (disk-based)     | B+ Tree           | High fanout → minimal disk I/O                  |
| Static range sum queries        | Prefix Sum Array  | O(1) query, simpler                              |
| Dynamic range sum (updates)     | Segment Tree      | O(log n) update + query                         |
| Range min/max with updates      | Segment Tree      | Supports any associative operation               |
| Interval overlap queries        | Interval Tree     | Specialized for overlap detection                |

```
Decision tree:
                        Need balanced BST?
                       /                  \
              Yes (in-memory)          Yes (on-disk / large)
                /        \                      |
          Read-heavy?   Write-heavy?         B-Tree / B+Tree
              |               |
           AVL Tree     Red-Black Tree

                        Need range queries?
                       /                   \
               Static data?            Dynamic (updates)?
                   |                         |
             Prefix Sum Array          Segment Tree
```

---

## When NOT to Use

- **AVL in write-heavy code** — up to O(log n) rotations per delete; Red-Black is faster for inserts.
- **Red-Black for interval/range** — use segment tree; Red-Black doesn't natively aggregate ranges.
- **B-Tree for in-memory** — high fanout wastes memory; plain BST or AVL is faster in RAM.
- **Segment Tree for static data** — prefix sum array gives O(1) query with O(n) build and no extra structure.
- **Implementing AVL/Red-Black from scratch in interviews** — use Python's `sortedcontainers.SortedList` or Java's `TreeMap`. Interviewers rarely ask for full implementation; they want to know WHEN and WHY.

---

## Core Operations (Code)

```python
# ── Segment Tree — most interview-relevant advanced tree ──────────────────────

class SegmentTree:
    """
    Range sum query + point update in O(log n).
    Array-based (no explicit nodes), 1-indexed internally.
    """

    def __init__(self, nums: list[int]):
        self.n = len(nums)
        self.tree = [0] * (4 * self.n)
        if nums:
            self._build(nums, 1, 0, self.n - 1)

    def _build(self, nums, node, start, end):
        if start == end:
            self.tree[node] = nums[start]
        else:
            mid = (start + end) // 2
            self._build(nums, 2 * node,     start, mid)
            self._build(nums, 2 * node + 1, mid + 1, end)
            self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def update(self, idx: int, val: int) -> None:
        # Point update: set nums[idx] = val, O(log n)
        self._update(1, 0, self.n - 1, idx, val)

    def _update(self, node, start, end, idx, val):
        if start == end:
            self.tree[node] = val
        else:
            mid = (start + end) // 2
            if idx <= mid:
                self._update(2 * node,     start, mid,     idx, val)
            else:
                self._update(2 * node + 1, mid + 1, end,   idx, val)
            self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def query(self, lo: int, hi: int) -> int:
        # Range sum query: sum(nums[lo..hi]), O(log n)
        return self._query(1, 0, self.n - 1, lo, hi)

    def _query(self, node, start, end, lo, hi) -> int:
        if hi < start or end < lo:          # completely outside
            return 0
        if lo <= start and end <= hi:       # completely inside
            return self.tree[node]
        mid = (start + end) // 2
        return (self._query(2 * node,     start, mid,     lo, hi) +
                self._query(2 * node + 1, mid + 1, end,   lo, hi))


# ── Fenwick Tree (BIT) — simpler alternative for prefix sums ─────────────────

class FenwickTree:
    """
    Prefix sum with point updates. O(log n) both operations.
    Simpler than segment tree when only prefix sums needed.
    """

    def __init__(self, n: int):
        self.tree = [0] * (n + 1)   # 1-indexed

    def update(self, i: int, delta: int) -> None:
        # Add delta to index i (1-indexed)
        while i < len(self.tree):
            self.tree[i] += delta
            i += i & (-i)          # move to next responsible node

    def prefix_sum(self, i: int) -> int:
        # Sum of [1..i] (1-indexed)
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)          # move to parent
        return s

    def range_sum(self, lo: int, hi: int) -> int:
        # Sum of [lo..hi] (1-indexed)
        return self.prefix_sum(hi) - self.prefix_sum(lo - 1)


# ── AVL Rotation sketch (interview awareness, not full impl) ──────────────────

def rotate_right(z):
    """
    Right rotation around z (z is unbalanced, left-heavy):
          z                y
         / \              / \
        y   T4    →      x   z
       / \              /\  / \
      x   T3           T1 T2 T3 T4
    """
    y = z.left
    T3 = y.right
    y.right = z
    z.left = T3
    # Update heights: z first (now lower), then y
    z.height = 1 + max(height(z.left), height(z.right))
    y.height = 1 + max(height(y.left), height(y.right))
    return y   # new root of this subtree
```

---

## 3 Worked Problems

---

### Problem 1 — Range Sum Query — Mutable (LeetCode #307)

**Clarifying Questions**
- How many updates vs queries? (Both could be frequent)
- Is the array large? (Up to 3×10⁴ elements, up to 3×10⁴ operations)
- What operation — sum? (Yes, range sum and point update)

**Brute Force**

Store array, recompute range sum each query.

```python
class NumArray_Brute:
    def __init__(self, nums):
        self.nums = nums

    def update(self, i, val):
        self.nums[i] = val                  # O(1)

    def sumRange(self, left, right):
        return sum(self.nums[left:right+1]) # O(n) — too slow
```

**Optimization**

Segment tree gives O(log n) for both update and query.

```python
class NumArray:
    def __init__(self, nums: list[int]):
        self.n = len(nums)
        self.tree = [0] * (2 * self.n)
        # Build: fill leaves, then compute internal nodes
        for i, v in enumerate(nums):
            self.tree[self.n + i] = v
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def update(self, index: int, val: int) -> None:
        pos = index + self.n
        self.tree[pos] = val
        while pos > 1:
            pos //= 2
            self.tree[pos] = self.tree[2 * pos] + self.tree[2 * pos + 1]

    def sumRange(self, left: int, right: int) -> int:
        lo, hi = left + self.n, right + self.n
        total = 0
        while lo <= hi:
            if lo % 2 == 1:    # lo is right child, include it
                total += self.tree[lo]
                lo += 1
            if hi % 2 == 0:    # hi is left child, include it
                total += self.tree[hi]
                hi -= 1
            lo //= 2
            hi //= 2
        return total
```

**Edge Cases**
- Single element: `sumRange(0, 0)` → just that element
- Update to same value → still correct, no special case
- Full range sum: `sumRange(0, n-1)` → returns `tree[1]`

**Complexity**
- Build: O(n)
- Update: O(log n)
- Query: O(log n)
- Space: O(n) — `2n` array

**Follow-ups**
- "Range minimum instead of sum?" → Change `+` to `min` in build/update.
- "Range update (add delta to range)?" → Lazy propagation segment tree.

---

### Problem 2 — Implement Trie (Prefix Tree) (LeetCode #208)

*See `docs/06-data-structures/tries/README.md` for full treatment. Summary below.*

**Clarifying Questions**
- Only lowercase letters? (Yes, a-z)
- Case-sensitive? (Lowercase only)
- Max word length? (~2000 chars)

**Optimal Solution**

```python
class TrieNode:
    def __init__(self):
        self.children = {}      # char → TrieNode
        self.is_end  = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def startsWith(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True
```

**Complexity**
- Time per operation: O(m) where m = word length
- Space: O(ALPHABET_SIZE × m × n) worst case

---

### Problem 3 — Count of Smaller Numbers After Self (LeetCode #315)

**Clarifying Questions**
- Input range of nums[i]? (-10⁴ to 10⁴)
- Array length? (Up to 10⁵)
- Is a merge sort or BST approach acceptable? (Yes)

**Brute Force**

For each index i, count elements to the right that are smaller.

```python
def count_smaller_brute(nums):
    return [sum(1 for j in range(i+1, len(nums)) if nums[j] < nums[i])
            for i in range(len(nums))]
    # O(n²) time — TLE for large n
```

**Optimization**

Use a Fenwick Tree (BIT) with coordinate compression. Process from right to left: for each element, query prefix sum (count of smaller already inserted), then update.

```python
def count_smaller(nums: list[int]) -> list[int]:
    # Coordinate compression: map values to 1..len(sorted_unique)
    sorted_unique = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(sorted_unique)}
    size = len(sorted_unique)

    bit = [0] * (size + 1)

    def update(i):
        while i <= size:
            bit[i] += 1
            i += i & (-i)

    def query(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    result = []
    for v in reversed(nums):
        r = rank[v]
        result.append(query(r - 1))   # count elements with rank < r
        update(r)

    return result[::-1]
```

**Edge Cases**
- All same values → all counts are 0
- Already sorted descending → all counts are n - i - 1
- Single element → [0]

**Complexity**
- Time: O(n log n) — n operations × O(log n) BIT
- Space: O(n) — BIT + rank mapping

**Follow-ups**
- "Count of larger numbers after self?" → Query suffix sum instead.
- "Reverse pairs?" → LeetCode #493; similar merge sort / BIT approach.

---

## Interview Q&A

**Q1: Why does Red-Black tree outperform AVL for inserts in practice?**

A:
```
AVL rotations per insert: up to O(log n) rotations going up to root
Red-Black rotations per insert: at most 2 rotations (then recoloring up)

Recoloring (changing a bit) is O(1) per node and very cache-friendly.
Rotations require pointer updates — more expensive.

Result: Red-Black has smaller constant factors for insert/delete.
AVL has strictly shorter height (≤ 1.44 log n vs ≤ 2 log(n+1)),
so AVL is faster for search-heavy workloads.

Standard libraries (Java TreeMap, C++ std::map) use Red-Black because
most real workloads mix inserts and lookups.
```

---

**Q2: Why does a database use B-Trees instead of Red-Black trees?**

A:
```
B-Tree designed for disk:
  - Disk read = page (4KB or 16KB)
  - B-Tree node = 1 page → holds 500-2000 keys per node
  - Tree height for 1B records: log_500(1B) ≈ 3-4 levels
  - 3-4 disk reads to find any record

Red-Black Tree on disk:
  - Each node holds 1 key (+ 2 pointers + color bit)
  - Height for 1B records: ~30 levels
  - 30 disk reads — 10x slower

Key insight: Disk I/O cost >> in-memory pointer cost.
B-Tree maximizes keys per disk read via high fanout.
```

---

**Q3: Segment tree vs prefix sum array — when to use each?**

A:
```
Prefix sum array:
  Build:  O(n)
  Query:  O(1)
  Update: O(n)   ← must rebuild
  Use when: static array, many queries, few/no updates

Segment tree:
  Build:  O(n)
  Query:  O(log n)
  Update: O(log n)
  Use when: array is modified frequently AND range queries needed

Rule: if updates are rare, prefix sum wins. If both updates and
queries are frequent, segment tree wins. Fenwick tree is a simpler
O(log n) alternative when only prefix sums (not arbitrary ranges) needed.
```

---

**Q4: What are the four AVL rotation cases?**

A:
```
After inserting into an AVL tree, fix the first unbalanced node z:

1. Left-Left (z is left-heavy, y is left-heavy):
   → Single right rotation at z

2. Right-Right (z is right-heavy, y is right-heavy):
   → Single left rotation at z

3. Left-Right (z is left-heavy, y is right-heavy):
   → Left rotation at y (converts to Left-Left)
   → Right rotation at z

4. Right-Left (z is right-heavy, y is left-heavy):
   → Right rotation at y (converts to Right-Right)
   → Left rotation at z

Memory aid: "same direction = single rotation, different direction = double"
```

---

**Q5: What are the 5 Red-Black tree properties?**

A:
1. Every node is Red or Black.
2. Root is Black.
3. Every null (leaf) is Black.
4. Red nodes have only Black children (no two consecutive reds on any path).
5. All paths from any node to its null descendants have the same number of Black nodes (Black-height invariant).

Property 5 ensures the tree can't be too unbalanced — the longest path (alternating Red-Black) is at most twice the shortest path (all Black).

---

**Q6: What is lazy propagation in a segment tree?**

A: Lazy propagation defers range updates. Instead of updating all O(n) nodes for a range update (e.g., "add 5 to all elements in [l, r]"), store a `lazy` value at each node. When traversing, push the lazy value down to children only when needed (during query or further update). This makes range update + range query both O(log n) instead of O(n) update.

Use when: "add delta to subarray" or "multiply subarray" combined with range queries.

---

**Q7: B-Tree vs B+ Tree — what's the difference?**

A:
```
B-Tree:
  - Data stored in internal nodes AND leaf nodes
  - In-order traversal must visit all levels
  - Range scan requires jumping between levels

B+ Tree (used in most real databases — InnoDB, PostgreSQL):
  - Data ONLY in leaf nodes; internal nodes hold keys as guides
  - Leaf nodes linked in a doubly-linked list
  - Range scan = follow leaf pointers (sequential I/O)
  - Internal nodes can hold more keys (no data payload) → higher fanout

Practical impact: B+ Tree range queries are much faster because
sequential leaf scan = sequential disk reads = full disk bandwidth.
```

---

**Q8: When would you use a Fenwick tree vs a segment tree?**

A:
```
Fenwick Tree (BIT):
  - Simpler code (~10 lines)
  - Only supports prefix operations (sum, XOR)
  - Point update only
  - O(log n) both
  - Choose when: prefix sums / frequency counts with point updates

Segment Tree:
  - More complex (~30-50 lines)
  - Supports arbitrary range operations (sum, min, max, GCD)
  - Range updates with lazy propagation
  - O(log n) both
  - Choose when: range min/max, arbitrary range updates needed

If the problem is solvable with prefix sums → Fenwick.
If you need range min/max or range updates → Segment Tree.
```

---

## Interview Tips

- **You rarely implement AVL/Red-Black from scratch.** Interviewers care that you know WHEN to use each (Red-Black for general purpose, AVL for read-heavy, B-Tree for disk). Focus on the trade-off explanation, not implementation details.
- **Segment tree is interview-implementable.** Know the array-based iterative version (2n array). It's ~20 lines and comes up in hard array problems.
- **Fenwick tree is the shortcut.** For "range sum with point updates," Fenwick is 10 lines and impresses with brevity. Memorize the `update` and `prefix_sum` loops.
- **B-Tree = database question trigger.** Whenever the interviewer asks "how does a database index work?", mention B+ Tree, high fanout, disk page = one node, ~3-4 I/Os for billion rows.
- **Lazy propagation.** Know the concept even if you can't implement it cold. "For range updates on a segment tree, I'd add a lazy array and push down during traversal" is enough.
